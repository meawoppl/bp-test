// Oversampled SPI mode-0 slave with fixed 40-bit frames.
//
// Frame (MSB first): [8-bit command][32-bit data]. A frame is accepted only
// when exactly 40 bits were clocked before CS rises; o_frame_valid then
// pulses for one i_clk cycle with o_command/o_data held stable.
//
// MISO returns 0xAF while the command byte is clocked in, then the 32-bit
// i_read_data word selected by that command. i_read_data is sampled after
// the eighth bit, so the caller must present it combinationally from the
// o_rx_command output.
//
// SCK must be below i_clk / 8 (6 MHz for 48 MHz i_clk).
module spi_frame_slave (
    input wire i_clk,

    input wire i_cs_n,
    input wire i_sck,
    input wire i_mosi,
    output wire o_miso,

    output wire [7:0] o_rx_command,
    input wire [31:0] i_read_data,

    output reg [7:0] o_command,
    output reg [31:0] o_data,
    output reg o_frame_valid
);
    localparam MAGIC = 8'hAF;

    reg [2:0] cs_sync = 3'b111;
    reg [2:0] sck_sync = 3'b000;
    reg [1:0] mosi_sync = 2'b00;

    always @(posedge i_clk) begin
        cs_sync <= {cs_sync[1:0], i_cs_n};
        sck_sync <= {sck_sync[1:0], i_sck};
        mosi_sync <= {mosi_sync[0], i_mosi};
    end

    wire cs_active = ~cs_sync[1];
    wire cs_fall = cs_sync[2] & ~cs_sync[1];
    wire cs_rise = ~cs_sync[2] & cs_sync[1];
    wire sck_rise = ~sck_sync[2] & sck_sync[1];
    wire sck_fall = sck_sync[2] & ~sck_sync[1];

    reg [5:0] bit_count = 0;
    reg [39:0] rx_shift = 0;
    reg [31:0] tx_shift = 0;
    reg miso_bit = 0;

    assign o_rx_command = rx_shift[7:0];
    assign o_miso = miso_bit;

    initial begin
        o_command = 0;
        o_data = 0;
        o_frame_valid = 0;
    end

    always @(posedge i_clk) begin
        o_frame_valid <= 1'b0;

        if (cs_fall) begin
            bit_count <= 0;
            tx_shift <= {MAGIC[6:0], 25'd0};
            miso_bit <= MAGIC[7];
        end else if (cs_active) begin
            if (sck_rise) begin
                rx_shift <= {rx_shift[38:0], mosi_sync[1]};
                if (bit_count != 6'd63)
                    bit_count <= bit_count + 1'b1;
            end else if (sck_fall) begin
                if (bit_count == 6'd8) begin
                    // Command byte complete: present the selected word.
                    miso_bit <= i_read_data[31];
                    tx_shift <= {i_read_data[30:0], 1'b0};
                end else begin
                    miso_bit <= tx_shift[31];
                    tx_shift <= {tx_shift[30:0], 1'b0};
                end
            end
        end

        if (cs_rise && bit_count == 6'd40) begin
            o_command <= rx_shift[39:32];
            o_data <= rx_shift[31:0];
            o_frame_valid <= 1'b1;
        end
    end
endmodule
