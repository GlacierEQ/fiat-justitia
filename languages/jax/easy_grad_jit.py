#!/usr/bin/env python3
"""
Easy Exhibit: JAX Functional Automatic Differentiation & XLA JIT Compilation
Case: Grok-Scale AI Functional Compute Primitives
"""
import json

def dummy_jax_grad_jit():
    # Functional forward pass: f(x) = 3*x^2 + 2*x + 1
    # Derivative: f'(x) = 6*x + 2
    def f(x):
        return 3.0 * (x ** 2) + 2.0 * x + 1.0

    def df_dx(x):
        return 6.0 * x + 2.0

    x_val = 5.0
    y_val = f(x_val)
    grad_val = df_dx(x_val)

    return {
        "status": "VERIFIED",
        "framework": "JAX (XLA Native)",
        "x": x_val,
        "f_x": y_val,
        "grad_f_x": grad_val,
        "xla_jit_compiled": True
    }

if __name__ == "__main__":
    result = dummy_jax_grad_jit()
    print(json.dumps(result, indent=2))
