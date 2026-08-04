-- Lua — Advanced Example: Capability-Table Sandbox with Receipts
--
-- What: Executes guest functions against an explicit allowlisted capability table,
--       rejects unknown capabilities, and emits deterministic receipts.
-- Where: Plugin hosts, game mod runtimes, agent tool sandboxes, and config engines.
-- When: Use when untrusted or third-party script must run under host-controlled power.
-- Why: Lua's small core and first-class environments make capability isolation practical.
-- How: A frozen capability table, pcall-protected dispatch, and SHA-style stable digests
--       without external libraries.

local function stable_digest(s)
  -- FNV-1a 32-bit — dependency-free deterministic hash for demonstration receipts.
  local hash = 2166136261
  for i = 1, #s do
    hash = (hash ~ s:byte(i)) & 0xFFFFFFFF
    hash = (hash * 16777619) & 0xFFFFFFFF
  end
  return string.format("%08x", hash)
end

local function make_sandbox(capabilities)
  local frozen = {}
  for name, fn in pairs(capabilities) do
    frozen[name] = fn
  end
  return setmetatable({}, {
    __index = frozen,
    __newindex = function()
      error("capability table is frozen", 2)
    end,
  })
end

local function dispatch(sandbox, capability, payload)
  local fn = sandbox[capability]
  if type(fn) ~= "function" then
    return {
      status = "rejected",
      reason = "capability_not_allowed",
      capability = capability,
    }
  end
  local ok, result = pcall(fn, payload)
  if not ok then
    return {
      status = "rejected",
      reason = "capability_fault",
      detail = tostring(result),
    }
  end
  local digest = stable_digest(tostring(capability) .. "|" .. tostring(result))
  return {
    status = "accepted",
    capability = capability,
    result = result,
    receipt = digest,
  }
end

local capabilities = {
  echo = function(payload)
    return "echo:" .. tostring(payload)
  end,
  length = function(payload)
    return #tostring(payload)
  end,
}

local sandbox = make_sandbox(capabilities)

local accepted = dispatch(sandbox, "echo", "tower")
local accepted2 = dispatch(sandbox, "length", "tower")
local rejected = dispatch(sandbox, "os.execute", "rm -rf /")

if accepted.status ~= "accepted" or accepted2.status ~= "accepted" then
  error("allowed capabilities failed")
end
if rejected.status ~= "rejected" or rejected.reason ~= "capability_not_allowed" then
  error("forbidden capability was not rejected")
end

-- Freeze enforcement
local freeze_ok, freeze_err = pcall(function()
  sandbox.new_power = function() end
end)
if freeze_ok then
  error("capability table was mutable")
end

print(string.format(
  '{"status":"VERIFIED","language":"lua","accepted":2,"rejected":1,"freeze_enforced":true,"receipt":"%s"}',
  accepted.receipt
))
