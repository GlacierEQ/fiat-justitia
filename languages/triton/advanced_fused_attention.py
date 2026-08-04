"""Triton — Advanced Example: Bounded Single-Query Fused Attention Kernel.

This is a correctness-checked fused kernel for one query and one attention head.
It intentionally bounds sequence/head dimensions to one Triton program and does
not claim the tiled production FlashAttention algorithm.
"""

import math

import torch
import triton
import triton.language as tl


@triton.jit
def fused_single_query_attention(
    query,
    keys,
    values,
    output,
    scale,
    n_ctx: tl.constexpr,
    d_head: tl.constexpr,
    block_n: tl.constexpr,
    block_d: tl.constexpr,
):
    offsets_n = tl.arange(0, block_n)
    offsets_d = tl.arange(0, block_d)
    query_vector = tl.load(query + offsets_d, mask=offsets_d < d_head, other=0.0)
    key_matrix = tl.load(
        keys + offsets_n[:, None] * d_head + offsets_d[None, :],
        mask=(offsets_n[:, None] < n_ctx) & (offsets_d[None, :] < d_head),
        other=0.0,
    )
    scores = tl.sum(key_matrix * query_vector[None, :], axis=1) * scale
    scores = tl.where(offsets_n < n_ctx, scores, -float("inf"))
    scores = scores - tl.max(scores, axis=0)
    probabilities = tl.exp(scores)
    probabilities = probabilities / tl.sum(probabilities, axis=0)
    value_matrix = tl.load(
        values + offsets_n[:, None] * d_head + offsets_d[None, :],
        mask=(offsets_n[:, None] < n_ctx) & (offsets_d[None, :] < d_head),
        other=0.0,
    )
    result = tl.sum(probabilities[:, None] * value_matrix, axis=0)
    tl.store(output + offsets_d, result, mask=offsets_d < d_head)


def run(query: torch.Tensor, keys: torch.Tensor, values: torch.Tensor) -> torch.Tensor:
    if not query.is_cuda or not keys.is_cuda or not values.is_cuda:
        raise ValueError("all tensors must be CUDA tensors")
    if query.ndim != 1 or keys.ndim != 2 or values.shape != keys.shape:
        raise ValueError("expected query[d], keys[n,d], values[n,d]")
    n_ctx, d_head = keys.shape
    if query.numel() != d_head or not (1 <= n_ctx <= 1024) or not (1 <= d_head <= 256):
        raise ValueError("kernel bounds are n_ctx<=1024 and d_head<=256")
    block_n = triton.next_power_of_2(n_ctx)
    block_d = triton.next_power_of_2(d_head)
    output = torch.empty_like(query)
    fused_single_query_attention[(1,)](
        query,
        keys,
        values,
        output,
        1.0 / math.sqrt(d_head),
        n_ctx=n_ctx,
        d_head=d_head,
        block_n=block_n,
        block_d=block_d,
        num_warps=4,
    )
    return output


def main() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("BLOCKED_HARDWARE: Triton attention requires a supported CUDA GPU")
    torch.manual_seed(7)
    n_ctx, d_head = 128, 64
    query = torch.randn(d_head, device="cuda", dtype=torch.float32)
    keys = torch.randn(n_ctx, d_head, device="cuda", dtype=torch.float32)
    values = torch.randn(n_ctx, d_head, device="cuda", dtype=torch.float32)
    observed = run(query, keys, values)
    reference = torch.softmax((keys @ query) / math.sqrt(d_head), dim=0) @ values
    torch.testing.assert_close(observed, reference, rtol=2e-4, atol=2e-4)
    latency_ms = triton.testing.do_bench(lambda: run(query, keys, values))
    print(
        f'{{"status":"VERIFIED","kernel":"bounded-single-query-fused-attention",'
        f'"n_ctx":{n_ctx},"d_head":{d_head},"latency_ms":{latency_ms:.6f},'
        '"claim_boundary":"one program; not production FlashAttention"}}'
    )


if __name__ == "__main__":
    main()
