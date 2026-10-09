`timescale 1ns / 1ps

// Mode-0 frames at 1 MHz against a 48 MHz system clock: checks the 0xAF
// preamble, command-selected readback, write latching and short-frame rejection.
module spi_frame_slave_tb;
    reg clk = 0;
    always #10.4 clk = ~clk;

    reg cs_n = 1, sck = 0, mosi = 0;
    wire miso;
    wire [7:0] rx_command;
    wire [7:0] command;
    wire [31:0] data;
    wire frame_valid;

    reg [31:0] read_data;
    always @(*) read_data = {24'hC0FFEE, rx_command};

    spi_frame_slave dut (
        .i_clk(clk), .i_cs_n(cs_n), .i_sck(sck), .i_mosi(mosi), .o_miso(miso),
        .o_rx_command(rx_command), .i_read_data(read_data),
        .o_command(command), .o_data(data), .o_frame_valid(frame_valid)
    );

    integer frames = 0;
    always @(posedge clk) if (frame_valid) frames = frames + 1;

    reg [39:0] rx;
    integer errors = 0;

    task xfer(input [39:0] tx, input integer nbits);
        integer i;
        begin
            cs_n = 0;
            #1000;
            for (i = 0; i < nbits; i = i + 1) begin
                mosi = tx[39 - i];
                #500 sck = 1;
                rx = {rx[38:0], miso};
                #500 sck = 0;
            end
            #1000 cs_n = 1;
            #2000;
        end
    endtask

    initial begin
        xfer({8'h83, 32'h2AAA_5555}, 40);
        if (rx[39:32] !== 8'hAF) begin
            $display("FAIL preamble %h", rx[39:32]); errors = errors + 1;
        end
        if (rx[31:0] !== 32'hC0FFEE83) begin
            $display("FAIL readback %h", rx[31:0]); errors = errors + 1;
        end
        if (frames !== 1 || command !== 8'h83 || data !== 32'h2AAA_5555) begin
            $display("FAIL write frames=%0d cmd=%h data=%h", frames, command, data); errors = errors + 1;
        end

        xfer({8'h81, 32'hFFFF_FFFF}, 39);
        if (frames !== 1 || data !== 32'h2AAA_5555) begin
            $display("FAIL short frame accepted"); errors = errors + 1;
        end

        xfer({8'h01, 32'h0}, 40);
        if (rx[31:0] !== 32'hC0FFEE01 || frames !== 2) begin
            $display("FAIL second frame %h frames=%0d", rx[31:0], frames); errors = errors + 1;
        end

        if (errors == 0) $display("PASS");
        else $display("FAIL");
        $finish;
    end
endmodule
