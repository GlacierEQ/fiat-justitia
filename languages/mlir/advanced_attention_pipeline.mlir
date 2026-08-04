// Destination-style scaled score computation suitable for canonicalization
// and subsequent loop/vector lowering.
module {
  func.func @scaled_scores(
      %q: tensor<4x8xf32>,
      %k_transposed: tensor<8x4xf32>,
      %scale: f32) -> tensor<4x4xf32> {
    %zero = arith.constant 0.0 : f32
    %score_init = tensor.empty() : tensor<4x4xf32>
    %score_zero = linalg.fill
      ins(%zero : f32)
      outs(%score_init : tensor<4x4xf32>) -> tensor<4x4xf32>
    %scores = linalg.matmul
      ins(%q, %k_transposed : tensor<4x8xf32>, tensor<8x4xf32>)
      outs(%score_zero : tensor<4x4xf32>) -> tensor<4x4xf32>

    %scaled_init = tensor.empty() : tensor<4x4xf32>
    %scaled = linalg.generic {
        indexing_maps = [
          affine_map<(d0, d1) -> (d0, d1)>,
          affine_map<(d0, d1) -> (d0, d1)>
        ],
        iterator_types = ["parallel", "parallel"]
      }
      ins(%scores : tensor<4x4xf32>)
      outs(%scaled_init : tensor<4x4xf32>) {
        ^bb0(%value: f32, %unused: f32):
          %product = arith.mulf %value, %scale : f32
          linalg.yield %product : f32
      } -> tensor<4x4xf32>
    return %scaled : tensor<4x4xf32>
  }
}
