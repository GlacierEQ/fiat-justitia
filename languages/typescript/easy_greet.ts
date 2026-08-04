/**
 * TypeScript — Easy Example: Typed Greeting
 * What: A small typed function with an explicit return contract.
 * Where: Browser, Node.js, and MCP-facing interface code.
 * When: JavaScript interoperability is required without surrendering static checks.
 * Why: TypeScript catches shape and return-type errors before runtime.
 * How: Structural typing and compile-time checking erase to portable JavaScript.
 */
export function greet(name: string): string {
  const normalized = name.trim();
  if (!normalized) {
    throw new Error("name must not be empty");
  }
  return `Hello, ${normalized}!`;
}

console.log(greet("Tower"));
