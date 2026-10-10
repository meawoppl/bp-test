// On-demand Wi-Fi checks for the fixture console. Wi-Fi stays off until a
// `wifi` command is issued and `wifi off` shuts it down again.
#include "wifi_test.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <esp_console.h>
#include <esp_event.h>
#include <esp_netif.h>
#include <esp_wifi.h>
#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>

#define MAX_APS 24
#define CONNECT_TIMEOUT_MS 20000

#define BIT_GOT_IP BIT0
#define BIT_FAILED BIT1

static EventGroupHandle_t events;
static esp_netif_t *sta_netif;
static bool started;
static int disconnect_reason;

static const char *auth_name(wifi_auth_mode_t mode)
{
    switch (mode) {
    case WIFI_AUTH_OPEN: return "open";
    case WIFI_AUTH_WEP: return "wep";
    case WIFI_AUTH_WPA_PSK: return "wpa";
    case WIFI_AUTH_WPA2_PSK: return "wpa2";
    case WIFI_AUTH_WPA_WPA2_PSK: return "wpa/wpa2";
    case WIFI_AUTH_WPA2_ENTERPRISE: return "wpa2-ent";
    case WIFI_AUTH_WPA3_PSK: return "wpa3";
    case WIFI_AUTH_WPA2_WPA3_PSK: return "wpa2/wpa3";
    default: return "other";
    }
}

static void on_event(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        disconnect_reason = ((wifi_event_sta_disconnected_t *)data)->reason;
        xEventGroupSetBits(events, BIT_FAILED);
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        xEventGroupSetBits(events, BIT_GOT_IP);
    }
}

static esp_err_t wifi_start(void)
{
    if (started) return ESP_OK;
    if (events == NULL) {
        events = xEventGroupCreate();
        ESP_ERROR_CHECK(esp_netif_init());
        esp_err_t ret = esp_event_loop_create_default();
        if (ret != ESP_OK && ret != ESP_ERR_INVALID_STATE) return ret;
        sta_netif = esp_netif_create_default_wifi_sta();
        ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_event, NULL));
        ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_event, NULL));
    }
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_err_t ret = esp_wifi_init(&cfg);
    if (ret == ESP_OK) ret = esp_wifi_set_storage(WIFI_STORAGE_RAM);
    if (ret == ESP_OK) ret = esp_wifi_set_mode(WIFI_MODE_STA);
    if (ret == ESP_OK) ret = esp_wifi_start();
    if (ret != ESP_OK) {
        printf("wifi start failed: %s\n", esp_err_to_name(ret));
        return ret;
    }
    started = true;
    uint8_t mac[6];
    esp_wifi_get_mac(WIFI_IF_STA, mac);
    printf("wifi on, STA MAC %02x:%02x:%02x:%02x:%02x:%02x\n", mac[0], mac[1], mac[2], mac[3],
           mac[4], mac[5]);
    return ESP_OK;
}

static void wifi_stop(void)
{
    if (!started) return;
    esp_wifi_disconnect();
    esp_wifi_stop();
    esp_wifi_deinit();
    started = false;
    printf("wifi off\n");
}

static int cmd_scan(void)
{
    if (wifi_start() != ESP_OK) return 1;
    wifi_scan_config_t scan = { .show_hidden = false };
    esp_err_t ret = esp_wifi_scan_start(&scan, true);
    if (ret != ESP_OK) {
        printf("scan failed: %s\n", esp_err_to_name(ret));
        return 1;
    }
    uint16_t total = 0, n = MAX_APS;
    esp_wifi_scan_get_ap_num(&total);
    wifi_ap_record_t *aps = calloc(MAX_APS, sizeof(wifi_ap_record_t));
    if (aps == NULL) return 1;
    esp_wifi_scan_get_ap_records(&n, aps);
    printf("WIFI SCAN: %u access points (showing %u, strongest first)\n", total, n);
    printf("  %-32s %5s %3s %-9s %s\n", "ssid", "rssi", "ch", "auth", "bssid");
    for (int i = 0; i < n; i++) {
        const uint8_t *b = aps[i].bssid;
        printf("  %-32s %5d %3d %-9s %02x:%02x:%02x:%02x:%02x:%02x\n", (char *)aps[i].ssid,
               aps[i].rssi, aps[i].primary, auth_name(aps[i].authmode), b[0], b[1], b[2], b[3],
               b[4], b[5]);
    }
    free(aps);
    return 0;
}

static int cmd_connect(const char *ssid, const char *pass)
{
    if (wifi_start() != ESP_OK) return 1;
    wifi_config_t cfg = { 0 };
    strlcpy((char *)cfg.sta.ssid, ssid, sizeof(cfg.sta.ssid));
    if (pass) strlcpy((char *)cfg.sta.password, pass, sizeof(cfg.sta.password));
    esp_wifi_disconnect();
    xEventGroupClearBits(events, BIT_GOT_IP | BIT_FAILED);
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &cfg));

    printf("connecting to \"%s\"...\n", ssid);
    for (int attempt = 1; attempt <= 3; attempt++) {
        xEventGroupClearBits(events, BIT_GOT_IP | BIT_FAILED);
        esp_wifi_connect();
        EventBits_t bits = xEventGroupWaitBits(events, BIT_GOT_IP | BIT_FAILED, pdTRUE, pdFALSE,
                                               pdMS_TO_TICKS(CONNECT_TIMEOUT_MS));
        if (bits & BIT_GOT_IP) {
            esp_netif_ip_info_t ip;
            wifi_ap_record_t ap;
            esp_netif_get_ip_info(sta_netif, &ip);
            esp_wifi_sta_get_ap_info(&ap);
            printf("WIFI CONNECTED: ip " IPSTR " gw " IPSTR ", rssi %d dBm, channel %d (attempt %d)\n",
                   IP2STR(&ip.ip), IP2STR(&ip.gw), ap.rssi, ap.primary, attempt);
            return 0;
        }
        if (bits & BIT_FAILED) {
            printf("attempt %d: disconnected, reason %d\n", attempt, disconnect_reason);
        } else {
            printf("attempt %d: timed out\n", attempt);
        }
    }
    printf("WIFI CONNECT FAILED\n");
    esp_wifi_disconnect();
    return 1;
}

static int wifi_cmd(int argc, char **argv)
{
    if (argc >= 2 && !strcmp(argv[1], "scan")) return cmd_scan();
    if (argc >= 3 && !strcmp(argv[1], "connect")) return cmd_connect(argv[2], argc > 3 ? argv[3] : NULL);
    if (argc >= 2 && !strcmp(argv[1], "off")) {
        wifi_stop();
        return 0;
    }
    printf("wifi scan | connect <ssid> [password] | off\n");
    return 1;
}

void wifi_test_register_commands(void)
{
    const esp_console_cmd_t cmd = {
        .command = "wifi",
        .help = "Wi-Fi check: scan | connect <ssid> [password] | off (off at boot)",
        .func = wifi_cmd,
    };
    ESP_ERROR_CHECK(esp_console_cmd_register(&cmd));
}
