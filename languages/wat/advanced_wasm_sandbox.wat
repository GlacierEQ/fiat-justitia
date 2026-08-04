;; WebAssembly — Advanced Example: Capability- and Fuel-Bounded Tool Sandbox
;;
;; What: A compact execution boundary that permits a 32-bit memory write only
;;       when the caller supplies the required capability, a valid address, and
;;       positive execution fuel.
;; Where: Plugin runtimes, browser/edge tools, and zero-trust agent extensions.
;; When: Use when portable untrusted code must operate inside explicit host
;;       authority and bounded linear memory.
;; Why: WebAssembly validates bytecode before execution and exposes only the
;;      memory, functions, and imports selected by the host.
;; How: A capability bitmask, address bounds, and fuel gate every mutation;
;;      observable globals record attempts, successes, and the last status.

(module
  (memory (export "memory") 1 1)

  (global $attempts (mut i32) (i32.const 0))
  (global $successes (mut i32) (i32.const 0))
  (global $last_status (mut i32) (i32.const 0))

  (func $record (param $status i32) (result i32)
    global.get $attempts
    i32.const 1
    i32.add
    global.set $attempts

    local.get $status
    i32.eqz
    if
      global.get $successes
      i32.const 1
      i32.add
      global.set $successes
    end

    local.get $status
    global.set $last_status
    local.get $status)

  ;; Status codes:
  ;;   0  success
  ;;  -1  missing WRITE capability (bit 1)
  ;;  -2  address would escape the single 64 KiB memory page
  ;;  -3  execution fuel exhausted
  (func (export "execute")
        (param $capability i32)
        (param $offset i32)
        (param $value i32)
        (param $fuel i32)
        (result i32)
    local.get $capability
    i32.const 2
    i32.and
    i32.eqz
    if (result i32)
      i32.const -1
    else
      local.get $fuel
      i32.const 0
      i32.le_s
      if (result i32)
        i32.const -3
      else
        local.get $offset
        i32.const 65532
        i32.gt_u
        if (result i32)
          i32.const -2
        else
          local.get $offset
          local.get $value
          i32.store
          i32.const 0
        end
      end
    end
    call $record)

  (func (export "read_i32") (param $offset i32) (result i32)
    local.get $offset
    i32.load)

  (func (export "attempts") (result i32)
    global.get $attempts)

  (func (export "successes") (result i32)
    global.get $successes)

  (func (export "last_status") (result i32)
    global.get $last_status)

  (func (export "reset_audit")
    i32.const 0
    global.set $attempts
    i32.const 0
    global.set $successes
    i32.const 0
    global.set $last_status))
