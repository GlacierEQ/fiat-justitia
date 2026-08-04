// CUDA — Advanced Example: Audited Reference Scaled Dot-Product Attention.
// This is an auditable correctness reference, not a claim to implement the
// production FlashAttention algorithm. Evidence class: hardware_gated.

#include <cuda_runtime.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

__global__ void reference_attention(
    const float* q, const float* k, const float* v, float* out,
    int sequence, int dimension) {
    const int query_index = blockIdx.x;
    if (query_index >= sequence || threadIdx.x != 0) return;

    extern __shared__ float scores[];
    const float scale = rsqrtf(static_cast<float>(dimension));
    float max_score = -INFINITY;
    for (int key_index = 0; key_index < sequence; ++key_index) {
        float dot = 0.0f;
        for (int d = 0; d < dimension; ++d) {
            dot += q[query_index * dimension + d] * k[key_index * dimension + d];
        }
        scores[key_index] = dot * scale;
        max_score = fmaxf(max_score, scores[key_index]);
    }

    float denominator = 0.0f;
    for (int key_index = 0; key_index < sequence; ++key_index) {
        scores[key_index] = expf(scores[key_index] - max_score);
        denominator += scores[key_index];
    }

    for (int d = 0; d < dimension; ++d) {
        float value = 0.0f;
        for (int key_index = 0; key_index < sequence; ++key_index) {
            value += (scores[key_index] / denominator) * v[key_index * dimension + d];
        }
        out[query_index * dimension + d] = value;
    }
}

static bool cuda_ok(cudaError_t status, const char* operation) {
    if (status == cudaSuccess) return true;
    std::fprintf(stderr, "%s failed: %s\n", operation, cudaGetErrorString(status));
    return false;
}

int main() {
    constexpr int sequence = 4;
    constexpr int dimension = 4;
    std::vector<float> host(sequence * dimension, 0.25f);
    float *q = nullptr, *k = nullptr, *v = nullptr, *out = nullptr;
    const size_t bytes = host.size() * sizeof(float);
    int exit_code = EXIT_FAILURE;

    if (!cuda_ok(cudaMalloc(&q, bytes), "cudaMalloc(q)")) goto cleanup;
    if (!cuda_ok(cudaMalloc(&k, bytes), "cudaMalloc(k)")) goto cleanup;
    if (!cuda_ok(cudaMalloc(&v, bytes), "cudaMalloc(v)")) goto cleanup;
    if (!cuda_ok(cudaMalloc(&out, bytes), "cudaMalloc(out)")) goto cleanup;
    if (!cuda_ok(cudaMemcpy(q, host.data(), bytes, cudaMemcpyHostToDevice), "cudaMemcpy(q)")) goto cleanup;
    if (!cuda_ok(cudaMemcpy(k, host.data(), bytes, cudaMemcpyHostToDevice), "cudaMemcpy(k)")) goto cleanup;
    if (!cuda_ok(cudaMemcpy(v, host.data(), bytes, cudaMemcpyHostToDevice), "cudaMemcpy(v)")) goto cleanup;

    reference_attention<<<sequence, 1, sequence * sizeof(float)>>>(q, k, v, out, sequence, dimension);
    if (!cuda_ok(cudaGetLastError(), "reference_attention launch")) goto cleanup;
    if (!cuda_ok(cudaDeviceSynchronize(), "reference_attention execution")) goto cleanup;
    if (!cuda_ok(cudaMemcpy(host.data(), out, bytes, cudaMemcpyDeviceToHost), "cudaMemcpy(out)")) goto cleanup;

    for (float value : host) {
        if (!std::isfinite(value) || std::fabs(value - 0.25f) > 1e-5f) {
            std::fprintf(stderr, "attention output validation failed: %.9f\n", value);
            goto cleanup;
        }
    }
    std::printf(
        "{\"status\":\"VERIFIED\",\"algorithm\":\"reference-scaled-dot-product-attention\",\"sequence\":%d,\"dimension\":%d,\"attention_0\":%.6f,\"claim_boundary\":\"not FlashAttention\"}\n",
        sequence, dimension, host[0]
    );
    exit_code = EXIT_SUCCESS;

cleanup:
    if (q != nullptr) cudaFree(q);
    if (k != nullptr) cudaFree(k);
    if (v != nullptr) cudaFree(v);
    if (out != nullptr) cudaFree(out);
    return exit_code;
}
