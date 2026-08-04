# Mojo — Advanced Example: Bounded SIMD Affine-Clamp Tensor Kernel
#
# What: Applies y = clamp(scale*x + bias) with vectorized loads and stores.
# Where: CPU preprocessing, compact inference kernels, and MLIR-lowered tensor paths.
# When: Python-like authoring must cross into explicit SIMD and ownership-aware memory.
# Why: Mojo exposes compile-time vector width and low-level pointers without abandoning
# readable numerical code.
# How: vectorize partitions the bounded input; UnsafePointer and SIMD operations make
# memory and lane width explicit. This is a CPU SIMD reference, not a TPU claim.

from algorithm import vectorize
from memory import UnsafePointer
from sys.info import simd_width_of

alias dtype = DType.float32
alias simd_width = simd_width_of[dtype]()

fn affine_clamp(
    output: UnsafePointer[Scalar[dtype]],
    input: UnsafePointer[Scalar[dtype]],
    count: Int,
    scale: Scalar[dtype],
    bias: Scalar[dtype],
):
    @parameter
    fn body[width: Int](offset: Int):
        let x = input.load[width=width](offset)
        let transformed = x * scale + bias
        let bounded = transformed.max(0.0).min(1.0)
        output.store[width=width](offset, bounded)

    vectorize[body, simd_width](count)

fn main() raises:
    alias count = 16
    var input = UnsafePointer[Scalar[dtype]].alloc(count)
    var output = UnsafePointer[Scalar[dtype]].alloc(count)
    defer:
        input.free()
        output.free()

    for i in range(count):
        input[i] = (i - 4) / 8.0
    affine_clamp(output, input, count, 1.5, -0.1)
    for i in range(count):
        if output[i] < 0.0 or output[i] > 1.0:
            raise Error("affine-clamp bound failed")
    print("{\"status\":\"VERIFIED\",\"kernel\":\"simd-affine-clamp\",\"elements\":16,\"claim_boundary\":\"CPU SIMD; no TPU claim\"}")
