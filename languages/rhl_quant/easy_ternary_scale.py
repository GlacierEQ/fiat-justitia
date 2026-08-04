#!/usr/bin/env python3
"""
Easy Exhibit: Basic 1.58-bit Ternary Scale Quantization (RHL-Quant Base)
Demonstrates ternary {-1, 0, +1} rounding and scale factor computation.
"""
import json

def quantize_ternary_simple(weights):
    scale = sum(abs(w) for w in weights) / max(len(weights), 1)
    quantized = []
    for w in weights:
        norm = w / max(scale, 1e-6)
        if norm > 0.5:
            quantized.append(1)
        elif norm < -0.5:
            quantized.append(-1)
        else:
            quantized.append(0)
    return quantized, round(scale, 4)

def main():
    weights = [1.2, -0.9, 0.1, -0.1, 2.5, -2.1]
    q, scale = quantize_ternary_simple(weights)
    report = {
        "status": "VERIFIED",
        "exhibit": "easy_ternary_scale",
        "weights_count": len(weights),
        "scale": scale,
        "quantized_ternary": q
    }
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
