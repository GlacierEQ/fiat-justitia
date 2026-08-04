"""
Python — Easy Example: Fibonacci Generator
What: Recursive + memoized Fibonacci with type hints.
Where: Universal scripting, ML pipelines, data processing.
When: Rapid prototyping, data science, automation.
Why: Most widely-adopted language for AI/ML with massive ecosystem.
How: CPython interpreter with C extensions for performance-critical paths.
"""

from functools import lru_cache
from typing import Generator


@lru_cache(maxsize=None)
def fibonacci(n: int) -> int:
    """Compute nth Fibonacci number with memoization."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_stream(limit: int) -> Generator[int, None, None]:
    """Yield Fibonacci numbers up to a limit."""
    a, b = 0, 1
    while a <= limit:
        yield a
        a, b = b, a + b


if __name__ == "__main__":
    # First 20 Fibonacci numbers
    for i in range(20):
        print(f"F({i}) = {fibonacci(i)}")

    # Stream up to 1000
    print("\nFibonacci stream up to 1000:")
    print(list(fibonacci_stream(1000)))
