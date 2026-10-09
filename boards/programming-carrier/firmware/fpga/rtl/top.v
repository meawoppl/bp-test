// programming-carrier-v1-test FPGA fixture image, ABI v1.
//
// Exposes a 30-bit regular-output mask and three RGB sink enables to the
// ESP32-S2 over the module-internal SPI link. See ../../README.md for the
// frame format. Outputs start low/released and return there if no valid
// frame arrives for WATCHDOG_MS.
module top (
    input wire SPI_SCK,
    input wire SPI_SS_N,
    input wire SPI_SI,
    output wire SPI_SO,

    output wire [29:0] fpga_out,
    output wire RGB0,
    output wire RGB1,
    output wire RGB2
);
    localparam [31:0] FIXTURE_ID = 32'h50435431;  // "PCT1"
    localparam [31:0] ABI_VERSION = 32'h0001_0000;
    localparam WATCHDOG_MS = 1000;

    localparam CMD_NOP = 4'h0;
    localparam CMD_ID = 4'h1;
    localparam CMD_VERSION = 4'h2;
    localparam CMD_MASK = 4'h3;
    localparam CMD_RGB = 4'h4;
    localparam CMD_STATUS = 4'h5;
    localparam CMD_UPTIME = 4'h6;

    // 48 MHz internal oscillator; no external clock on module v1.
    wire clk;
    SB_HFOSC #(.CLKHF_DIV("0b00")) osc (
        .CLKHFPU(1'b1),
        .CLKHFEN(1'b1),
        .CLKHF(clk)
    );

    // Hold logic in reset for a few cycles after configuration.
    reg [3:0] por = 0;
    wire rst = ~por[3];
    always @(posedge clk)
        if (rst) por <= por + 1'b1;

    // 1 ms tick and uptime counter.
    reg [15:0] tick_div = 0;
    reg tick_ms = 0;
    reg [31:0] uptime_ms = 0;
    always @(posedge clk) begin
        tick_ms <= 1'b0;
        if (tick_div == 16'd47999) begin
            tick_div <= 0;
            tick_ms <= 1'b1;
            uptime_ms <= uptime_ms + 1'b1;
        end else begin
            tick_div <= tick_div + 1'b1;
        end
    end

    reg [29:0] out_mask = 0;
    reg [2:0] rgb_en = 0;
    reg [15:0] frame_count = 0;
    reg [15:0] wd_ms = 0;
    reg wd_tripped = 0;

    wire [7:0] rx_command;
    wire [7:0] command;
    wire [31:0] data;
    wire frame_valid;
    reg [31:0] read_data;

    always @(*) begin
        case (rx_command[3:0])
            CMD_ID: read_data = FIXTURE_ID;
            CMD_VERSION: read_data = ABI_VERSION;
            CMD_MASK: read_data = {2'b00, out_mask};
            CMD_RGB: read_data = {29'd0, rgb_en};
            CMD_STATUS: read_data = {frame_count, 15'd0, wd_tripped};
            CMD_UPTIME: read_data = uptime_ms;
            default: read_data = 32'h0;
        endcase
    end

    spi_frame_slave spi (
        .i_clk(clk),
        .i_cs_n(SPI_SS_N),
        .i_sck(SPI_SCK),
        .i_mosi(SPI_SI),
        .o_miso(SPI_SO),
        .o_rx_command(rx_command),
        .i_read_data(read_data),
        .o_command(command),
        .o_data(data),
        .o_frame_valid(frame_valid)
    );

    always @(posedge clk) begin
        if (rst) begin
            out_mask <= 0;
            rgb_en <= 0;
            wd_ms <= 0;
            wd_tripped <= 0;
        end else if (frame_valid) begin
            frame_count <= frame_count + 1'b1;
            wd_ms <= 0;
            if (command[7]) begin
                case (command[3:0])
                    CMD_MASK: out_mask <= data[29:0];
                    CMD_RGB: rgb_en <= data[2:0];
                    CMD_STATUS: wd_tripped <= 1'b0;  // write clears the sticky flag
                    default: ;
                endcase
            end
        end else if (tick_ms) begin
            if (wd_ms == WATCHDOG_MS - 1) begin
                if (out_mask != 0 || rgb_en != 0)
                    wd_tripped <= 1'b1;
                out_mask <= 0;
                rgb_en <= 0;
            end else begin
                wd_ms <= wd_ms + 1'b1;
            end
        end
    end

    assign fpga_out = out_mask;

    // RGB sinks: "on" sinks the shared line low, "off" releases it to the
    // carrier 100k pull-up. Half-current mode, 2 mA per channel.
    SB_RGBA_DRV #(
        .CURRENT_MODE("0b1"),
        .RGB0_CURRENT("0b000001"),
        .RGB1_CURRENT("0b000001"),
        .RGB2_CURRENT("0b000001")
    ) rgb_driver (
        .CURREN(1'b1),
        .RGBLEDEN(1'b1),
        .RGB0PWM(rgb_en[0]),
        .RGB1PWM(rgb_en[1]),
        .RGB2PWM(rgb_en[2]),
        .RGB0(RGB0),
        .RGB1(RGB1),
        .RGB2(RGB2)
    );
endmodule
