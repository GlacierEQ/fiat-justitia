module counter #(parameter WIDTH = 8) (
  input  logic clk,
  input  logic reset_n,
  output logic [WIDTH-1:0] value
);
  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) value <= '0;
    else value <= value + 1'b1;
  end
endmodule
