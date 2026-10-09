// programming-carrier-v1-test: nonblocking LED test scheduler and console commands.
//
// The console task builds a step program and hands it to the scheduler task
// through a queue. The scheduler applies one step at a time, waits on the queue
// for the step dwell (so stop/pause act immediately), polls GPIO46 and feeds the
// FPGA watchdog.
#include "fixture.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <driver/gpio.h>
#include <esp_console.h>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/task.h>
#include <nvs.h>

#include "carrier_map.h"
#include "fpga_link.h"

#define GPIO45 45
#define GPIO46 46
#define KEEPALIVE_MS 200
#define POLL_MS 50
#define MAX_STEPS 640
#define ALLON_MAX_MS 10000
#define GPIO45_MAX_MS 3000
#define BUTTON_DEBOUNCE_MS 150

// Sequence dwell times are written at human-inspection speed and divided by this.
#define SEQ_SPEEDUP 5
#define SEQ_MS(ms) ((ms) / SEQ_SPEEDUP)

typedef enum {
    PH_BASELINE,
    PH_BANK,
    PH_WALK,
    PH_CHECKER,
    PH_WALKZERO,
    PH_ALLON,
    PH_RGB,
    PH_GPIO45,
    PH_HOLD,
} phase_t;

static const char *const PHASE_NAMES[] = {
    "baseline", "bank", "walk", "checker", "walkzero", "allon", "rgb", "gpio45", "hold",
};

typedef struct {
    uint64_t on;        // bit n set = CARRIER_CHANNELS[n] active
    uint16_t dwell_ms;  // 0 = hold until stop
    uint8_t phase;
    uint8_t gpio45;     // GPIO45 opt-in level for this step
} step_t;

typedef struct {
    step_t *steps;
    int len;
} program_t;

typedef enum { OP_RUN, OP_STOP, OP_PAUSE, OP_RESUME, OP_STEP } op_t;

typedef struct {
    op_t op;
    program_t program;
} cmd_t;

typedef enum { ST_IDLE, ST_RUNNING, ST_PAUSED, ST_HOLD } state_t;
static const char *const STATE_NAMES[] = { "idle", "running", "paused", "hold" };

static const char *TAG = "fixture";

static QueueHandle_t cmd_queue;
static bool fpga_ok;
static bool armed;
static bool repeat;
static uint16_t walk_dwell_ms = SEQ_MS(300);

// Scheduler-owned state; read without locking by `status`.
static volatile state_t state = ST_IDLE;
static program_t program;
static volatile int cur_step;
static volatile int gpio46_level;
static volatile uint32_t gpio46_presses;
static volatile uint32_t steps_applied;
static volatile uint32_t readback_failures;
static volatile uint32_t watchdog_trips;
static uint16_t ch_readback_fail[CARRIER_CHANNEL_COUNT];
static uint32_t marks_ok, marks_bad;

// ---------------------------------------------------------------- channels

static bool ch_regular(int i)
{
    const carrier_channel_t *ch = &CARRIER_CHANNELS[i];
    if (ch->cls != CH_OUTPUT) return false;
    return ch->kind == KIND_ESP || fpga_ok;
}

static bool ch_rgb(int i)
{
    return CARRIER_CHANNELS[i].cls == CH_RGB && fpga_ok;
}

static uint64_t bank_mask(int bank)
{
    uint64_t m = 0;
    for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
        if (ch_regular(i) && strcmp(CARRIER_CHANNELS[i].buffer, CARRIER_BANKS[bank]) == 0) {
            m |= 1ULL << i;
        }
    }
    return m;
}

static int find_bank(const char *name)
{
    for (int b = 0; b < CARRIER_BANK_COUNT; b++) {
        if (strcasecmp(name, CARRIER_BANKS[b]) == 0) return b;
    }
    return -1;
}

static int find_channel(const char *name)
{
    for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
        const carrier_channel_t *ch = &CARRIER_CHANNELS[i];
        const char *bare = strchr(ch->signal, '_');
        if (strcasecmp(name, ch->signal) == 0 || strcasecmp(name, ch->led) == 0 ||
            (bare && strcasecmp(name, bare + 1) == 0)) {
            return i;
        }
    }
    return -1;
}

static void print_channel(const carrier_channel_t *ch)
{
    const char *pkg = ch->kind == KIND_ESP ? "U1" : "U2";
    printf("%s %s [%s] %s-%d pkg %s-%d", ch->led, ch->signal, ch->buffer, ch->conn,
           ch->conn_pin, pkg, ch->pkg_pin);
    if (ch->active_low) printf(" (sink: red monitor lit LOW; check module D1)");
}

static void describe(uint64_t on)
{
    int n = __builtin_popcountll(on);
    if (n == 0) {
        printf("all eligible outputs off");
        return;
    }
    if (n == 1) {
        printf("ON ");
        print_channel(&CARRIER_CHANNELS[__builtin_ctzll(on)]);
        return;
    }
    printf("%d on:", n);
    for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
        if (on & (1ULL << i)) printf(" %s", CARRIER_CHANNELS[i].led);
    }
}

// ---------------------------------------------------------------- outputs

static void esp_outputs_configure(void)
{
    for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
        const carrier_channel_t *ch = &CARRIER_CHANNELS[i];
        if (ch->kind != KIND_ESP) continue;
        if (ch->cls == CH_OUTPUT || ch->cls == CH_OPT_IN) {
            // Detaches UART0 from 43/44 and JTAG from 39-42.
            gpio_reset_pin(ch->index);
            gpio_set_pull_mode(ch->index, GPIO_FLOATING);
            gpio_set_level(ch->index, 0);
            gpio_set_direction(ch->index, GPIO_MODE_INPUT_OUTPUT);
        }
    }
    // GPIO46 is input only; the carrier pull-down defines "released".
    gpio_reset_pin(GPIO46);
    gpio_set_direction(GPIO46, GPIO_MODE_INPUT);
    gpio_set_pull_mode(GPIO46, GPIO_FLOATING);
    // GPIO0 (BOOT) and EN are never touched.
}

// Apply a pattern. Returns false on an FPGA link fault.
static bool apply(uint64_t on, int gpio45)
{
    uint32_t mask = 0;
    uint8_t rgb = 0;
    int esp_fail = 0;

    for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
        const carrier_channel_t *ch = &CARRIER_CHANNELS[i];
        bool bit = (on >> i) & 1;
        if (ch->kind == KIND_ESP && ch->cls == CH_OUTPUT) {
            gpio_set_level(ch->index, bit);
        } else if (ch->kind == KIND_FPGA && bit) {
            mask |= 1u << ch->index;
        } else if (ch->kind == KIND_RGB && bit) {
            rgb |= 1u << ch->index;
        }
    }
    gpio_set_level(GPIO45, gpio45);

    // Pin readback: the pad input path, not the lamp.
    for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
        const carrier_channel_t *ch = &CARRIER_CHANNELS[i];
        if (ch->kind != KIND_ESP) continue;
        int expect;
        if (ch->cls == CH_OUTPUT) expect = (on >> i) & 1;
        else if (ch->cls == CH_OPT_IN) expect = gpio45;
        else continue;
        if (gpio_get_level(ch->index) != expect) {
            esp_fail++;
            ch_readback_fail[i]++;
            printf("  READBACK MISMATCH ");
            print_channel(ch);
            printf(": expected %d\n", expect);
        }
    }

    bool fpga_match = true;
    if (fpga_ok) {
        esp_err_t ret = fpga_link_apply(mask, rgb, &fpga_match);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "FPGA link fault: %s", esp_err_to_name(ret));
            return false;
        }
        if (!fpga_match) {
            printf("  READBACK MISMATCH FPGA mask/rgb (wrote 0x%08lx/%u)\n", (unsigned long)mask, rgb);
            for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
                if (CARRIER_CHANNELS[i].kind != KIND_ESP) ch_readback_fail[i]++;
            }
        }
    }

    steps_applied++;
    if (esp_fail || !fpga_match) readback_failures++;
    return true;
}

static void safe_state(void)
{
    if (!apply(0, 0)) {
        ESP_LOGE(TAG, "FPGA did not acknowledge safe state; its watchdog will clear outputs");
    }
}

// ---------------------------------------------------------------- programs

static bool push(program_t *p, uint64_t on, uint16_t ms, phase_t phase)
{
    if (p->steps == NULL || p->len >= MAX_STEPS) return false;
    p->steps[p->len++] = (step_t){ .on = on, .dwell_ms = ms, .phase = phase };
    return true;
}

static void build_banks(program_t *p)
{
    for (int b = 0; b < CARRIER_BANK_COUNT; b++) {
        uint64_t m = bank_mask(b);
        if (!m) continue;
        push(p, m, SEQ_MS(1000), PH_BANK);
        push(p, 0, SEQ_MS(300), PH_BANK);
    }
}

static void build_walk(program_t *p, bool forward, bool reverse)
{
    for (int pass = 0; pass < 2; pass++) {
        if ((pass == 0 && !forward) || (pass == 1 && !reverse)) continue;
        for (int k = 0; k < CARRIER_CHANNEL_COUNT; k++) {
            int i = pass == 0 ? k : CARRIER_CHANNEL_COUNT - 1 - k;
            if (!ch_regular(i)) continue;
            push(p, 1ULL << i, walk_dwell_ms, PH_WALK);
            push(p, 0, walk_dwell_ms / 2, PH_WALK);
        }
    }
}

static void build_checker(program_t *p)
{
    for (int b = 0; b < CARRIER_BANK_COUNT; b++) {
        uint64_t m = bank_mask(b), even = 0, odd = 0;
        if (!m) continue;
        int pos = 0;
        for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
            if (m & (1ULL << i)) {
                if (pos++ & 1) odd |= 1ULL << i;
                else even |= 1ULL << i;
            }
        }
        for (int r = 0; r < 3; r++) {
            push(p, even, SEQ_MS(250), PH_CHECKER);
            push(p, odd, SEQ_MS(250), PH_CHECKER);
        }
        push(p, 0, SEQ_MS(300), PH_CHECKER);
    }
}

static void build_walkzero(program_t *p)
{
    for (int b = 0; b < CARRIER_BANK_COUNT; b++) {
        uint64_t m = bank_mask(b);
        if (__builtin_popcountll(m) < 2) continue;
        for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
            if (m & (1ULL << i)) push(p, m & ~(1ULL << i), walk_dwell_ms, PH_WALKZERO);
        }
        push(p, 0, SEQ_MS(300), PH_WALKZERO);
    }
}

static void build_rgb(program_t *p)
{
    static const uint8_t combos[] = { 1, 2, 4, 3, 6, 5, 7 };
    if (!fpga_ok) return;
    for (size_t c = 0; c < sizeof(combos); c++) {
        uint64_t on = 0;
        for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
            if (ch_rgb(i) && (combos[c] >> CARRIER_CHANNELS[i].index) & 1) on |= 1ULL << i;
        }
        push(p, on, SEQ_MS(1000), PH_RGB);
        push(p, 0, SEQ_MS(300), PH_RGB);
    }
}

static program_t program_new(void)
{
    return (program_t){ .steps = calloc(MAX_STEPS, sizeof(step_t)), .len = 0 };
}

static program_t build_full(void)
{
    program_t p = program_new();
    push(&p, 0, SEQ_MS(2000), PH_BASELINE);
    build_banks(&p);
    build_walk(&p, true, true);
    build_checker(&p);
    build_walkzero(&p);
    build_rgb(&p);
    push(&p, 0, SEQ_MS(500), PH_BASELINE);
    return p;
}

// Arming persists in NVS so SW3 can start the sequence without a host.
static void armed_store(bool value)
{
    nvs_handle_t nvs;
    armed = value;
    if (nvs_open("fixture", NVS_READWRITE, &nvs) == ESP_OK) {
        nvs_set_u8(nvs, "armed", value);
        nvs_commit(nvs);
        nvs_close(nvs);
    }
}

static void armed_load(void)
{
    nvs_handle_t nvs;
    uint8_t value = 0;
    if (nvs_open("fixture", NVS_READONLY, &nvs) == ESP_OK) {
        nvs_get_u8(nvs, "armed", &value);
        nvs_close(nvs);
    }
    armed = value;
}

// ---------------------------------------------------------------- scheduler

static void log_step(void)
{
    const step_t *s = &program.steps[cur_step];
    // Skip gaps between lit steps to keep the log readable.
    if (s->on == 0 && !s->gpio45 && cur_step != 0 && cur_step != program.len - 1) return;
    printf("[%s %d/%d] ", PHASE_NAMES[s->phase], cur_step + 1, program.len);
    if (s->gpio45) printf("GPIO45 HIGH (D35 opt-in strap test); ");
    describe(s->on);
    printf("\n");
}

static void enter_idle(const char *why)
{
    safe_state();
    free(program.steps);
    program = (program_t){ 0 };
    state = ST_IDLE;
    printf("fixture: %s; outputs safe (EN D10, BOOT D11 and power D1/D2 stay lit)\n", why);
}

static TickType_t start_step(void)
{
    const step_t *s = &program.steps[cur_step];
    log_step();
    if (!apply(s->on, s->gpio45)) {
        enter_idle("FPGA link fault");
        return 0;
    }
    return xTaskGetTickCount() + pdMS_TO_TICKS(s->dwell_ms);
}

static TickType_t advance(void)
{
    cur_step++;
    if (cur_step >= program.len) {
        if (!repeat) {
            enter_idle("sequence complete");
            return 0;
        }
        cur_step = 0;
    }
    return start_step();
}

static void handle(cmd_t *cmd, TickType_t *deadline)
{
    switch (cmd->op) {
    case OP_RUN:
        free(program.steps);
        program = cmd->program;
        cur_step = 0;
        state = program.steps[0].dwell_ms == 0 ? ST_HOLD : ST_RUNNING;
        *deadline = start_step();
        break;
    case OP_STOP:
        if (state != ST_IDLE) enter_idle("stopped");
        else safe_state();
        break;
    case OP_PAUSE:
        if (state == ST_RUNNING) {
            state = ST_PAUSED;
            printf("fixture: paused at step %d; current pattern held\n", cur_step + 1);
        }
        break;
    case OP_RESUME:
        if (state == ST_PAUSED) {
            state = ST_RUNNING;
            *deadline = advance();
        }
        break;
    case OP_STEP:
        if (state == ST_PAUSED) {
            advance();
            if (state != ST_IDLE) state = ST_PAUSED;
        }
        break;
    }
}

static void scheduler_task(void *arg)
{
    TickType_t deadline = 0;
    TickType_t last_keepalive = 0;
    TickType_t last_edge = 0;
    gpio46_level = gpio_get_level(GPIO46);

    for (;;) {
        TickType_t wait = pdMS_TO_TICKS(POLL_MS);
        if (state == ST_RUNNING) {
            int32_t remaining = (int32_t)(deadline - xTaskGetTickCount());
            if (remaining < 0) remaining = 0;
            if ((TickType_t)remaining < wait) wait = remaining;
        }

        cmd_t cmd;
        if (xQueueReceive(cmd_queue, &cmd, wait)) {
            handle(&cmd, &deadline);
        }

        TickType_t now = xTaskGetTickCount();
        if (state == ST_RUNNING && (int32_t)(now - deadline) >= 0) {
            deadline = advance();
        }

        int level = gpio_get_level(GPIO46);
        if (level != gpio46_level && (now - last_edge) >= pdMS_TO_TICKS(BUTTON_DEBOUNCE_MS)) {
            last_edge = now;
            gpio46_level = level;
            printf("INPUT GPIO46/SW3 read %s (%s)\n", level ? "HIGH" : "LOW",
                   level ? "pressed" : "released");
            if (level) {
                gpio46_presses++;
                // SW3 press: start the full sequence when idle, stop anything running.
                if (state != ST_IDLE) {
                    enter_idle("stopped by SW3");
                } else if (!armed) {
                    printf("SW3 ignored: not armed (`fixture arm " FIXTURE_ARM_TOKEN "`)\n");
                } else {
                    cmd_t start = { .op = OP_RUN, .program = build_full() };
                    printf("fixture: SW3 started full sequence, %d steps; press SW3 again to stop\n",
                           start.program.len);
                    handle(&start, &deadline);
                }
            }
        }

        if (fpga_ok && (now - last_keepalive) >= pdMS_TO_TICKS(KEEPALIVE_MS)) {
            last_keepalive = now;
            uint32_t status = 0;
            if (fpga_link_status(&status, NULL) != ESP_OK) {
                ESP_LOGE(TAG, "FPGA keepalive failed");
            } else if (status & 1) {
                watchdog_trips++;
                ESP_LOGW(TAG, "FPGA watchdog had tripped; outputs were cleared");
                fpga_link_xfer(FPGA_CMD_WRITE | FPGA_CMD_STATUS, 0, NULL);
                if (state != ST_IDLE) enter_idle("FPGA watchdog trip");
            }
        }
    }
}

esp_err_t fixture_init(bool fpga_available)
{
    fpga_ok = fpga_available;
    armed_load();
    esp_outputs_configure();
    safe_state();

    cmd_queue = xQueueCreate(4, sizeof(cmd_t));
    if (cmd_queue == NULL) return ESP_ERR_NO_MEM;
    if (xTaskCreate(scheduler_task, "fixture", 4096, NULL, 5, NULL) != pdPASS) {
        return ESP_ERR_NO_MEM;
    }
    return ESP_OK;
}

// ---------------------------------------------------------------- commands

static void send(op_t op, program_t p)
{
    cmd_t cmd = { .op = op, .program = p };
    xQueueSend(cmd_queue, &cmd, portMAX_DELAY);
}

static void run(program_t p)
{
    if (p.len == 0) {
        free(p.steps);
        printf("nothing eligible to run\n");
        return;
    }
    printf("fixture: %d steps; `fixture stop` at any time\n", p.len);
    send(OP_RUN, p);
}

static program_t hold(uint64_t on)
{
    program_t p = program_new();
    push(&p, on, 0, PH_HOLD);
    return p;
}

static void cmd_status(void)
{
    size_t bin_size;
    char bin_hash[17];
    const step_t *s = (state != ST_IDLE && program.steps) ? &program.steps[cur_step] : NULL;

    printf("identity:   %s\n", FIXTURE_IDENTITY);
    printf("armed:      %s\n", armed ? "yes" : "no (fixture arm " FIXTURE_ARM_TOKEN ")");
    printf("state:      %s", STATE_NAMES[state]);
    if (s) printf(" — %s step %d/%d", PHASE_NAMES[s->phase], cur_step + 1, program.len);
    printf("\nrepeat:     %s, walk dwell %u ms\n", repeat ? "on" : "off", walk_dwell_ms);
    fpga_link_bitstream_info(&bin_size, bin_hash);
    printf("bitstream:  %u bytes, sha256 %s…\n", (unsigned)bin_size, bin_hash);
    if (fpga_ok) {
        uint32_t st = 0, up = 0;
        esp_err_t ret = fpga_link_status(&st, &up);
        printf("fpga:       %s, frames %lu, uptime %lu ms, watchdog trips %lu\n",
               esp_err_to_name(ret), (unsigned long)(st >> 16), (unsigned long)up,
               (unsigned long)watchdog_trips);
    } else {
        printf("fpga:       UNAVAILABLE (ESP-only tests)\n");
    }
    printf("gpio46:     %s, %lu presses since boot\n", gpio46_level ? "HIGH" : "LOW",
           (unsigned long)gpio46_presses);
    printf("applied:    %lu steps, %lu with readback mismatch\n",
           (unsigned long)steps_applied, (unsigned long)readback_failures);
    for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
        if (ch_readback_fail[i]) {
            printf("  readback failures x%u: ", ch_readback_fail[i]);
            print_channel(&CARRIER_CHANNELS[i]);
            printf("\n");
        }
    }
    printf("observed:   %lu ok, %lu bad (fixture mark ok|bad <note>)\n",
           (unsigned long)marks_ok, (unsigned long)marks_bad);
}

static void cmd_banks(void)
{
    static const char *const CLS[] = { "out", "observe", "opt-in", "input", "rgb-sink" };
    for (int b = 0; b < CARRIER_BANK_COUNT; b++) {
        printf("%s:\n", CARRIER_BANKS[b]);
        for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
            const carrier_channel_t *ch = &CARRIER_CHANNELS[i];
            if (strcmp(ch->buffer, CARRIER_BANKS[b]) != 0) continue;
            printf("  %-8s ", CLS[ch->cls]);
            print_channel(ch);
            if (ch->kind != KIND_ESP && !fpga_ok) printf(" [FPGA unavailable]");
            printf("\n");
        }
    }
}

static int usage(void)
{
    printf("fixture status | banks | arm " FIXTURE_ARM_TOKEN " | disarm\n"
           "fixture start | walk [fwd|rev] | checkerboard | walkzero | bankseq\n"
           "fixture bank <U3..U10> | hold <signal|Dnn> | rgb <0|1|2|all>\n"
           "fixture allon [ms<=%d] | gpio45 [ms<=%d] | input46\n"
           "fixture stop | pause | resume | step | repeat on|off | dwell <ms>\n"
           "fixture mark ok|bad [note]\n",
           ALLON_MAX_MS, GPIO45_MAX_MS);
    return 1;
}

static bool require_armed(void)
{
    if (!armed) {
        printf("not armed: confirm this is the programming carrier v1 (not an application board),\n"
               "then run `fixture arm " FIXTURE_ARM_TOKEN "`\n");
    }
    return armed;
}

static int fixture_cmd(int argc, char **argv)
{
    if (argc < 2) return usage();
    const char *sub = argv[1];
    const char *arg = argc > 2 ? argv[2] : NULL;

    if (!strcmp(sub, "status")) { cmd_status(); return 0; }
    if (!strcmp(sub, "banks")) { cmd_banks(); return 0; }
    if (!strcmp(sub, "stop")) { send(OP_STOP, (program_t){ 0 }); return 0; }
    if (!strcmp(sub, "pause")) { send(OP_PAUSE, (program_t){ 0 }); return 0; }
    if (!strcmp(sub, "resume")) { send(OP_RESUME, (program_t){ 0 }); return 0; }
    if (!strcmp(sub, "step")) { send(OP_STEP, (program_t){ 0 }); return 0; }
    if (!strcmp(sub, "input46")) {
        printf("GPIO46 reads %s now. Press and release SW3; every edge is logged as INPUT.\n",
               gpio46_level ? "HIGH" : "LOW");
        return 0;
    }
    if (!strcmp(sub, "repeat") && arg) { repeat = !strcmp(arg, "on"); return 0; }
    if (!strcmp(sub, "dwell") && arg) {
        int ms = atoi(arg);
        if (ms < 10 || ms > 5000) { printf("dwell 10..5000 ms\n"); return 1; }
        walk_dwell_ms = ms;
        return 0;
    }
    if (!strcmp(sub, "mark") && arg) {
        bool ok = !strcmp(arg, "ok");
        if (ok) marks_ok++;
        else marks_bad++;
        printf("OBSERVED %s at %s step %d: ", ok ? "OK" : "BAD",
               program.steps ? PHASE_NAMES[program.steps[cur_step].phase] : "idle", cur_step + 1);
        if (program.steps) describe(program.steps[cur_step].on);
        for (int i = 3; i < argc; i++) printf("%s%s", i == 3 ? " — " : " ", argv[i]);
        printf("\n");
        return 0;
    }
    if (!strcmp(sub, "arm")) {
        if (!arg || strcmp(arg, FIXTURE_ARM_TOKEN)) {
            printf("refused: type `fixture arm " FIXTURE_ARM_TOKEN "` to confirm the fixture\n");
            return 1;
        }
        armed_store(true);
        printf("armed: %s on programming carrier v1 (persists across resets; SW3 starts/stops)\n",
               FIXTURE_IDENTITY);
        return 0;
    }
    if (!strcmp(sub, "disarm")) {
        armed_store(false);
        send(OP_STOP, (program_t){ 0 });
        printf("disarmed\n");
        return 0;
    }

    // Everything below can illuminate LEDs.
    program_t p;
    if (!strcmp(sub, "start")) {
        if (!require_armed()) return 1;
        p = build_full();
        printf("all-on and GPIO45 are opt-in: `fixture allon`, `fixture gpio45`\n");
        run(p);
    } else if (!strcmp(sub, "walk")) {
        if (!require_armed()) return 1;
        p = program_new();
        build_walk(&p, !arg || strcmp(arg, "rev"), !arg || strcmp(arg, "fwd"));
        run(p);
    } else if (!strcmp(sub, "bankseq")) {
        if (!require_armed()) return 1;
        p = program_new();
        build_banks(&p);
        run(p);
    } else if (!strcmp(sub, "checkerboard")) {
        if (!require_armed()) return 1;
        p = program_new();
        build_checker(&p);
        run(p);
    } else if (!strcmp(sub, "walkzero")) {
        if (!require_armed()) return 1;
        p = program_new();
        build_walkzero(&p);
        run(p);
    } else if (!strcmp(sub, "bank") && arg) {
        if (!require_armed()) return 1;
        int b = find_bank(arg);
        if (b < 0 || !bank_mask(b)) { printf("no eligible outputs in bank %s\n", arg); return 1; }
        run(hold(bank_mask(b)));
    } else if (!strcmp(sub, "hold") && arg) {
        if (!require_armed()) return 1;
        int i = find_channel(arg);
        if (i < 0 || !(ch_regular(i) || ch_rgb(i))) {
            printf("%s is not a drivable channel (see `fixture banks`)\n", arg);
            return 1;
        }
        run(hold(1ULL << i));
    } else if (!strcmp(sub, "rgb") && arg) {
        if (!require_armed()) return 1;
        uint64_t on = 0;
        for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
            if (ch_rgb(i) && (!strcmp(arg, "all") || atoi(arg) == CARRIER_CHANNELS[i].index)) {
                on |= 1ULL << i;
            }
        }
        if (!on) { printf("rgb 0|1|2|all (FPGA required)\n"); return 1; }
        run(hold(on));
    } else if (!strcmp(sub, "allon")) {
        if (!require_armed()) return 1;
        int ms = arg ? atoi(arg) : 2000;
        if (ms <= 0 || ms > ALLON_MAX_MS) { printf("allon 1..%d ms\n", ALLON_MAX_MS); return 1; }
        uint64_t on = 0;
        for (int i = 0; i < CARRIER_CHANNEL_COUNT; i++) {
            if (ch_regular(i)) on |= 1ULL << i;
        }
        printf("ALL regular outputs on for %d ms — watch USB current and the carrier LDO\n", ms);
        p = program_new();
        push(&p, on, ms, PH_ALLON);
        push(&p, 0, 100, PH_ALLON);
        run(p);
    } else if (!strcmp(sub, "gpio45")) {
        if (!require_armed()) return 1;
        int ms = arg ? atoi(arg) : 1000;
        if (ms <= 0 || ms > GPIO45_MAX_MS) { printf("gpio45 1..%d ms\n", GPIO45_MAX_MS); return 1; }
        printf("GPIO45 strap HIGH for %d ms, then LOW. Do not reset during this test.\n", ms);
        p = program_new();
        push(&p, 0, ms, PH_GPIO45);
        p.steps[0].gpio45 = 1;
        push(&p, 0, 100, PH_GPIO45);
        run(p);
    } else {
        return usage();
    }
    return 0;
}

void fixture_register_commands(void)
{
    const esp_console_cmd_t cmd = {
        .command = "fixture",
        .help = "Carrier LED test: status, banks, arm, start, walk, bank, hold, rgb, stop, ...",
        .func = fixture_cmd,
    };
    ESP_ERROR_CHECK(esp_console_cmd_register(&cmd));
    const esp_console_cmd_t alias = {
        .command = "f",
        .help = "Alias for fixture",
        .func = fixture_cmd,
    };
    ESP_ERROR_CHECK(esp_console_cmd_register(&alias));
}
