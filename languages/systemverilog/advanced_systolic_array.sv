// SystemVerilog — Advanced Example: 2x2 Systolic Multiply-Accumulate Mesh
// What: Four assertion-bearing processing elements with explicit dataflow.
// Where: Accelerator verification, FPGA prototypes, and cycle-accurate teaching.
// When: RTL structure and executable temporal invariants must be reviewed together.
// Why: SystemVerilog combines synthesizable logic with assertions and strong typing.
// How: Activations move right, weights move down, and each PE accumulates only on valid.

module processing_element #(
  parameter int WIDTH = 16,
  parameter int ACC_WIDTH = 40
) (
  input  logic clk,
  input  logic reset_n,
  input  logic clear,
  input  logic valid_in,
  input  logic signed [WIDTH-1:0] a_in,
  input  logic signed [WIDTH-1:0] b_in,
  output logic valid_out,
  output logic signed [WIDTH-1:0] a_out,
  output logic signed [WIDTH-1:0] b_out,
  output logic signed [ACC_WIDTH-1:0] accumulator
);
  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
      a_out <= '0;
      b_out <= '0;
      accumulator <= '0;
      valid_out <= 1'b0;
    end else begin
      valid_out <= valid_in;
      if (clear) accumulator <= '0;
      if (valid_in) begin
        a_out <= a_in;
        b_out <= b_in;
        accumulator <= (clear ? '0 : accumulator) + a_in * b_in;
      end
    end
  end

  property accumulator_changes_only_when_enabled;
    @(posedge clk) disable iff (!reset_n)
      (!valid_in && !clear) |=> $stable(accumulator);
  endproperty
  assert property (accumulator_changes_only_when_enabled);
endmodule

module systolic_array #(
  parameter int WIDTH = 16,
  parameter int ACC_WIDTH = 40
) (
  input logic clk,
  input logic reset_n,
  input logic clear,
  input logic valid_in,
  input logic signed [WIDTH-1:0] a_row0,
  input logic signed [WIDTH-1:0] a_row1,
  input logic signed [WIDTH-1:0] b_col0,
  input logic signed [WIDTH-1:0] b_col1,
  output logic signed [ACC_WIDTH-1:0] c00,
  output logic signed [ACC_WIDTH-1:0] c01,
  output logic signed [ACC_WIDTH-1:0] c10,
  output logic signed [ACC_WIDTH-1:0] c11
);
  logic signed [WIDTH-1:0] a00_to_01, a10_to_11;
  logic signed [WIDTH-1:0] b00_to_10, b01_to_11;
  logic v00, v01, v10;

  processing_element #(.WIDTH(WIDTH), .ACC_WIDTH(ACC_WIDTH)) pe00 (
    .clk, .reset_n, .clear, .valid_in, .a_in(a_row0), .b_in(b_col0),
    .valid_out(v00), .a_out(a00_to_01), .b_out(b00_to_10), .accumulator(c00));
  processing_element #(.WIDTH(WIDTH), .ACC_WIDTH(ACC_WIDTH)) pe01 (
    .clk, .reset_n, .clear, .valid_in(v00), .a_in(a00_to_01), .b_in(b_col1),
    .valid_out(v01), .a_out(), .b_out(b01_to_11), .accumulator(c01));
  processing_element #(.WIDTH(WIDTH), .ACC_WIDTH(ACC_WIDTH)) pe10 (
    .clk, .reset_n, .clear, .valid_in(v00), .a_in(a_row1), .b_in(b00_to_10),
    .valid_out(v10), .a_out(a10_to_11), .b_out(), .accumulator(c10));
  processing_element #(.WIDTH(WIDTH), .ACC_WIDTH(ACC_WIDTH)) pe11 (
    .clk, .reset_n, .clear, .valid_in(v10 & v01), .a_in(a10_to_11), .b_in(b01_to_11),
    .valid_out(), .a_out(), .b_out(), .accumulator(c11));
endmodule
