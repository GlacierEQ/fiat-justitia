// Verilog — Advanced Example: Weight-Stationary Dot-Product Array
//
// What: Computes a four-lane signed dot product with registered weights,
// widened accumulation, explicit valid timing, and synchronous clear.
// Where: FPGA inference datapaths, DSP front ends, and accelerator building blocks.
// When: A fixed coefficient vector is reused across a stream of activation vectors.
// Why: Verilog exposes exact registers, multiplier lanes, and cycle boundaries.
// How: Weights load independently; a widened sum is committed only on valid input.
// This is a truthful dot-product primitive, not a full matrix-multiplication claim.

module weight_stationary_dot_array #(
    parameter WIDTH = 16,
    parameter ACC_WIDTH = 40
) (
    input  wire                         clk,
    input  wire                         reset_n,
    input  wire                         clear,
    input  wire                         load_weights,
    input  wire                         valid_in,
    input  wire signed [WIDTH-1:0]      activations [0:3],
    input  wire signed [WIDTH-1:0]      weights_in [0:3],
    output reg  signed [ACC_WIDTH-1:0]  result,
    output reg                          valid_out
);
    reg signed [WIDTH-1:0] weights [0:3];
    reg signed [ACC_WIDTH-1:0] dot_sum;
    integer i;

    always @* begin
        dot_sum = {ACC_WIDTH{1'b0}};
        for (i = 0; i < 4; i = i + 1)
            dot_sum = dot_sum + $signed(activations[i]) * $signed(weights[i]);
    end

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            result <= {ACC_WIDTH{1'b0}};
            valid_out <= 1'b0;
            for (i = 0; i < 4; i = i + 1)
                weights[i] <= {WIDTH{1'b0}};
        end else begin
            valid_out <= 1'b0;
            if (clear)
                result <= {ACC_WIDTH{1'b0}};
            if (load_weights)
                for (i = 0; i < 4; i = i + 1)
                    weights[i] <= weights_in[i];
            if (valid_in) begin
                result <= dot_sum;
                valid_out <= 1'b1;
            end
        end
    end
endmodule
