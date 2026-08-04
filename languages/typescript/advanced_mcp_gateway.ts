/**
 * TypeScript — Advanced Example: Governed MCP JSON-RPC Gateway
 *
 * What: Typed MCP/JSON-RPC dispatch with runtime validation, mutation policy,
 * bounded rate limits, structured failures, and privacy-preserving receipts.
 * Where: MCP control planes, connector gateways, browser bridges, and edge workers.
 * When: Agents may invoke tools but must not bypass authorization or persist inputs.
 * Why: TypeScript combines protocol contracts with portable asynchronous execution.
 * How: Discriminated response guards, explicit policy checks, Web Crypto hashing,
 * and an allowlisted tool registry produce bounded, auditable behavior.
 */

export type JsonRpcId = string | number | null;

export interface JsonRpcRequest {
  jsonrpc: "2.0";
  id?: JsonRpcId;
  method: string;
  params?: unknown;
}

export interface JsonRpcSuccess<T = unknown> {
  jsonrpc: "2.0";
  id: JsonRpcId;
  result: T;
}

export interface JsonRpcFailure {
  jsonrpc: "2.0";
  id: JsonRpcId;
  error: {
    code: number;
    message: string;
    data?: Record<string, unknown>;
  };
}

export type JsonRpcResponse<T = unknown> = JsonRpcSuccess<T> | JsonRpcFailure;

export interface GatewayContext {
  actor: string;
  approvedMutation: boolean;
  requestReceivedAt?: number;
}

export interface ToolDefinition<TParams = unknown, TResult = unknown> {
  method: string;
  mutating: boolean;
  validate(params: unknown): TParams;
  execute(params: TParams, context: GatewayContext): Promise<TResult> | TResult;
}

export interface AuditReceipt {
  schemaVersion: 1;
  receiptId: string;
  actor: string;
  method: string;
  mutating: boolean;
  authorized: boolean;
  success: boolean;
  paramsHash: string;
  durationMs: number;
  completedAt: string;
  errorCode?: number;
}

export interface GatewayResult<T = unknown> {
  response: JsonRpcResponse<T>;
  receipt: AuditReceipt;
}

class GatewayFault extends Error {
  constructor(
    readonly code: number,
    message: string,
    readonly data?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "GatewayFault";
  }
}

class SlidingWindowRateLimiter {
  private readonly events = new Map<string, number[]>();

  constructor(
    private readonly maxRequests: number,
    private readonly windowMs: number,
  ) {
    if (!Number.isInteger(maxRequests) || maxRequests < 1 || windowMs < 1) {
      throw new Error("Rate limiter requires positive integer bounds");
    }
  }

  consume(actor: string, now = Date.now()): void {
    const cutoff = now - this.windowMs;
    const active = (this.events.get(actor) ?? []).filter((time) => time > cutoff);
    if (active.length >= this.maxRequests) {
      throw new GatewayFault(-32029, "Rate limit exceeded", {
        retryAfterMs: Math.max(1, active[0]! + this.windowMs - now),
      });
    }
    active.push(now);
    this.events.set(actor, active);
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isFailure<T>(response: JsonRpcResponse<T>): response is JsonRpcFailure {
  return "error" in response;
}

function validateRequest(value: unknown): JsonRpcRequest {
  if (!isRecord(value) || value.jsonrpc !== "2.0") {
    throw new GatewayFault(-32600, "Invalid JSON-RPC request");
  }
  if (typeof value.method !== "string" || value.method.trim().length === 0) {
    throw new GatewayFault(-32600, "Request method must be a non-empty string");
  }
  if (
    value.id !== undefined &&
    value.id !== null &&
    typeof value.id !== "string" &&
    typeof value.id !== "number"
  ) {
    throw new GatewayFault(-32600, "Request id must be a string, number, or null");
  }
  return {
    jsonrpc: "2.0",
    id: value.id as JsonRpcId | undefined,
    method: value.method,
    params: value.params,
  };
}

function canonicalize(value: unknown): string {
  if (value === undefined) return "undefined";
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;
  const record = value as Record<string, unknown>;
  const fields = Object.keys(record)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${canonicalize(record[key])}`);
  return `{${fields.join(",")}}`;
}

async function sha256(value: unknown): Promise<string> {
  const bytes = new TextEncoder().encode(canonicalize(value));
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function randomReceiptId(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  return [...bytes]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function responseId(input: unknown): JsonRpcId {
  if (!isRecord(input)) return null;
  const id = input.id;
  return typeof id === "string" || typeof id === "number" || id === null
    ? id
    : null;
}

export class McpGateway {
  private readonly tools = new Map<string, ToolDefinition<unknown, unknown>>();
  private readonly limiter: SlidingWindowRateLimiter;

  constructor(options: { maxRequestsPerMinute?: number } = {}) {
    this.limiter = new SlidingWindowRateLimiter(
      options.maxRequestsPerMinute ?? 120,
      60_000,
    );
  }

  register<TParams, TResult>(definition: ToolDefinition<TParams, TResult>): void {
    const method = definition.method.trim();
    if (!method || this.tools.has(method)) {
      throw new Error(`Tool method must be unique and non-empty: ${method}`);
    }
    this.tools.set(method, definition as ToolDefinition<unknown, unknown>);
  }

  async handle(input: unknown, context: GatewayContext): Promise<GatewayResult> {
    const started = performance.now();
    let method = "<invalid>";
    let mutating = false;
    let authorized = false;
    let paramsHash = await sha256(null);
    let response: JsonRpcResponse;

    try {
      if (!context.actor.trim()) {
        throw new GatewayFault(-32001, "Authenticated actor is required");
      }
      this.limiter.consume(context.actor);

      const request = validateRequest(input);
      method = request.method;
      paramsHash = await sha256(request.params ?? null);
      const tool = this.tools.get(method);
      if (!tool) {
        throw new GatewayFault(-32601, "Method not found", { method });
      }

      mutating = tool.mutating;
      if (mutating && context.approvedMutation !== true) {
        throw new GatewayFault(-32003, "Mutation requires explicit approval", {
          method,
        });
      }
      authorized = true;

      const validated = tool.validate(request.params);
      const result = await tool.execute(validated, context);
      response = { jsonrpc: "2.0", id: request.id ?? null, result };
    } catch (error) {
      const fault = error instanceof GatewayFault
        ? error
        : new GatewayFault(-32603, "Internal gateway error");
      response = {
        jsonrpc: "2.0",
        id: responseId(input),
        error: {
          code: fault.code,
          message: fault.message,
          data: fault.data,
        },
      };
    }

    const errorCode = isFailure(response) ? response.error.code : undefined;
    const success = errorCode === undefined;
    return {
      response,
      receipt: {
        schemaVersion: 1,
        receiptId: randomReceiptId(),
        actor: context.actor || "<missing>",
        method,
        mutating,
        authorized,
        success,
        paramsHash,
        durationMs: Math.max(
          0,
          Math.round((performance.now() - started) * 100) / 100,
        ),
        completedAt: new Date().toISOString(),
        ...(errorCode === undefined ? {} : { errorCode }),
      },
    };
  }
}

export function createDemonstrationGateway(): McpGateway {
  const gateway = new McpGateway({ maxRequestsPerMinute: 30 });

  gateway.register<{ value: string }, { normalized: string }>({
    method: "text.normalize",
    mutating: false,
    validate(params) {
      if (!isRecord(params) || typeof params.value !== "string") {
        throw new GatewayFault(-32602, "value must be a string");
      }
      return { value: params.value };
    },
    execute(params) {
      return { normalized: params.value.trim().replace(/\s+/g, " ") };
    },
  });

  gateway.register<{ repository: string }, { queued: true }>({
    method: "repository.publish",
    mutating: true,
    validate(params) {
      if (
        !isRecord(params) ||
        typeof params.repository !== "string" ||
        !/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(params.repository)
      ) {
        throw new GatewayFault(-32602, "repository must use owner/name format");
      }
      return { repository: params.repository };
    },
    execute() {
      return { queued: true };
    },
  });

  return gateway;
}
