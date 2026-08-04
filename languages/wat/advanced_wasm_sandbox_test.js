"use strict";

/**
 * Host-side behavioral proof for advanced_wasm_sandbox.wat.
 *
 * The host verifies that capability denial, exhausted fuel, and out-of-bounds
 * requests return explicit status codes and cannot mutate sandbox memory.
 */

const fs = require("node:fs");
const crypto = require("node:crypto");

function requireCondition(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function main() {
  const wasmPath = process.argv[2];
  if (!wasmPath) {
    throw new Error("usage: node advanced_wasm_sandbox_test.js <module.wasm>");
  }

  const bytes = fs.readFileSync(wasmPath);
  const moduleHash = crypto.createHash("sha256").update(bytes).digest("hex");
  const { instance } = await WebAssembly.instantiate(bytes, {});
  const api = instance.exports;

  for (const name of [
    "memory",
    "execute",
    "read_i32",
    "attempts",
    "successes",
    "last_status",
    "reset_audit",
  ]) {
    requireCondition(name in api, `missing export: ${name}`);
  }

  const WRITE = 2;
  const offset = 16;

  api.reset_audit();
  requireCondition(api.execute(WRITE, offset, 0x12345678, 10) === 0,
    "authorized write did not succeed");
  requireCondition(api.read_i32(offset) === 0x12345678,
    "authorized write did not reach linear memory");

  requireCondition(api.execute(0, offset, 0x11111111, 10) === -1,
    "missing capability was not rejected");
  requireCondition(api.read_i32(offset) === 0x12345678,
    "denied capability mutated memory");

  requireCondition(api.execute(WRITE, 65534, 0x22222222, 10) === -2,
    "out-of-bounds write was not rejected");
  requireCondition(api.read_i32(offset) === 0x12345678,
    "out-of-bounds request changed an authorized cell");

  requireCondition(api.execute(WRITE, offset, 0x33333333, 0) === -3,
    "exhausted fuel was not rejected");
  requireCondition(api.read_i32(offset) === 0x12345678,
    "fuel rejection mutated memory");

  requireCondition(api.attempts() === 4, "audit attempt count is incorrect");
  requireCondition(api.successes() === 1, "audit success count is incorrect");
  requireCondition(api.last_status() === -3, "last status did not record failure");
  requireCondition(api.memory.buffer.byteLength === 65536,
    "sandbox memory escaped its declared one-page maximum");

  console.log(JSON.stringify({
    status: "SUCCEEDED",
    module_sha256: moduleHash,
    memory_bytes: api.memory.buffer.byteLength,
    attempts: api.attempts(),
    successes: api.successes(),
    denied_capability: true,
    denied_out_of_bounds: true,
    denied_exhausted_fuel: true,
  }));
}

main().catch((error) => {
  console.error(`WebAssembly sandbox proof failed: ${error.message}`);
  process.exitCode = 1;
});
