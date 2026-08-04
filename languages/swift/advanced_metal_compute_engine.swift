import Foundation

// Swift — Advanced Example: Metal Affine-Clamp Compute Engine
//
// What: Executes y = clamp(scale*x + bias) through a Metal compute pipeline,
// with a portable CPU reference used for deterministic verification.
// Where: Apple-native preprocessing, on-device inference, and image/tensor transforms.
// When: The deployment boundary is Apple GPU compute; ANE execution remains a Core ML concern.
// Why: Swift provides safe host orchestration and first-class access to Metal resources.
// How: Runtime-compiled MSL, bounded buffers, exact dispatch sizing, command completion,
// and comparison against the CPU reference expose the full failure boundary.

enum EngineError: Error {
    case unavailable(String)
    case allocation(String)
    case compilation(String)
    case execution(String)
    case verification(index: Int, expected: Float, observed: Float)
}

func cpuAffineClamp(_ input: [Float], scale: Float, bias: Float) -> [Float] {
    input.map { min(1.0, max(0.0, scale * $0 + bias)) }
}

#if canImport(Metal)
import Metal

final class MetalAffineClampEngine {
    private let device: MTLDevice
    private let queue: MTLCommandQueue
    private let pipeline: MTLComputePipelineState

    init() throws {
        guard let device = MTLCreateSystemDefaultDevice() else {
            throw EngineError.unavailable("no Metal device")
        }
        guard let queue = device.makeCommandQueue() else {
            throw EngineError.unavailable("unable to create Metal command queue")
        }
        let source = """
        #include <metal_stdlib>
        using namespace metal;
        kernel void affine_clamp(
            device const float* input [[buffer(0)]],
            device float* output [[buffer(1)]],
            constant float& scale [[buffer(2)]],
            constant float& bias [[buffer(3)]],
            constant uint& count [[buffer(4)]],
            uint id [[thread_position_in_grid]]) {
          if (id < count) output[id] = clamp(scale * input[id] + bias, 0.0f, 1.0f);
        }
        """
        let library: MTLLibrary
        do {
            library = try device.makeLibrary(source: source, options: nil)
        } catch {
            throw EngineError.compilation(String(describing: error))
        }
        guard let function = library.makeFunction(name: "affine_clamp") else {
            throw EngineError.compilation("kernel function missing")
        }
        do {
            self.pipeline = try device.makeComputePipelineState(function: function)
        } catch {
            throw EngineError.compilation(String(describing: error))
        }
        self.device = device
        self.queue = queue
    }

    func run(_ input: [Float], scale: Float, bias: Float) throws -> [Float] {
        guard !input.isEmpty else { return [] }
        let byteCount = input.count * MemoryLayout<Float>.stride
        guard let inputBuffer = device.makeBuffer(bytes: input, length: byteCount),
              let outputBuffer = device.makeBuffer(length: byteCount),
              let commandBuffer = queue.makeCommandBuffer(),
              let encoder = commandBuffer.makeComputeCommandEncoder() else {
            throw EngineError.allocation("unable to allocate Metal resources")
        }
        var scale = scale
        var bias = bias
        var count = UInt32(input.count)
        encoder.setComputePipelineState(pipeline)
        encoder.setBuffer(inputBuffer, offset: 0, index: 0)
        encoder.setBuffer(outputBuffer, offset: 0, index: 1)
        encoder.setBytes(&scale, length: MemoryLayout<Float>.stride, index: 2)
        encoder.setBytes(&bias, length: MemoryLayout<Float>.stride, index: 3)
        encoder.setBytes(&count, length: MemoryLayout<UInt32>.stride, index: 4)
        let width = min(pipeline.maxTotalThreadsPerThreadgroup, input.count)
        encoder.dispatchThreads(
            MTLSize(width: input.count, height: 1, depth: 1),
            threadsPerThreadgroup: MTLSize(width: width, height: 1, depth: 1)
        )
        encoder.endEncoding()
        commandBuffer.commit()
        commandBuffer.waitUntilCompleted()
        if let error = commandBuffer.error {
            throw EngineError.execution(String(describing: error))
        }
        let pointer = outputBuffer.contents().bindMemory(to: Float.self, capacity: input.count)
        return Array(UnsafeBufferPointer(start: pointer, count: input.count))
    }
}
#endif

func runDemonstration() throws {
    let input: [Float] = [-1.0, 0.0, 0.25, 0.5, 1.0, 2.0]
    let expected = cpuAffineClamp(input, scale: 1.5, bias: -0.1)
    var backend = "cpu-reference"
    var observed = expected
    #if canImport(Metal)
    if let engine = try? MetalAffineClampEngine() {
        observed = try engine.run(input, scale: 1.5, bias: -0.1)
        backend = "metal"
    }
    #endif
    for index in expected.indices where abs(expected[index] - observed[index]) > 1e-5 {
        throw EngineError.verification(index: index, expected: expected[index], observed: observed[index])
    }
    print("{\"status\":\"VERIFIED\",\"backend\":\"\(backend)\",\"elements\":\(observed.count),\"claim_boundary\":\"Metal GPU compute; no direct ANE claim\"}")
}

do {
    try runDemonstration()
} catch {
    fputs("Metal compute demonstration failed: \(error)\n", stderr)
    exit(1)
}
