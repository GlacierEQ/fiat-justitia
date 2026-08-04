// Verilog — Easy Example: 4-bit Counter with Enable and Reset
// What: Synchronous 4-bit up-counter with enable and async reset.
// Where: FPGA/ASIC digital logic, hardware state machines.
// When: Implementing timing, sequencing, or control FSMs in hardware.
// Why: The foundational HDL for digital circuit design and verification.
// How: Register-transfer level (RTL) description synthesized to gate-level logic.

module counter_4bit (
    input  wire       clk,
    input  wire       rst_n,     // Active-low async reset
    input  wire       enable,
    output reg  [3:0] count,
    output wire       overflow
);

    assign overflow = (count == 4'hF) & enable;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 4'b0000;
        end else if (enable) begin
            count <= count + 4'b0001;
        end
    end

endmodule

// Testbench
module counter_4bit_tb;
    reg        clk, rst_n, enable;
    wire [3:0] count;
    wire       overflow;

    counter_4bit uut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .count(count),
        .overflow(overflow)
    );

    initial clk = 0;
    always #5 clk = ~clk;  // 100MHz clock

    initial begin
        rst_n = 0; enable = 0;
        #20 rst_n = 1;
        #10 enable = 1;
        #200;
        $display("Final count: %d, overflow: %b", count, overflow);
        $finish;
    end

    initial begin
        $monitor("t=%0t clk=%b rst_n=%b en=%b count=%d ovf=%b",
                 $time, clk, rst_n, enable, count, overflow);
    end
endmodule
