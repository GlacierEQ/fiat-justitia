declare const require: (name: string) => any;
declare const process: { argv: string[] };
const { createHash } = require("node:crypto");
const { readFileSync, writeFileSync } = require("node:fs");

interface MissionEnvelope {
  mission_id: string;
  objective: string;
  required_capabilities: string[];
  preferred_interfaces: string[];
  maximum_action: "read" | "plan" | "write_internal" | "external";
  input_sha256?: string;
}

const MISSION_FIELDS = new Set([
  "mission_id",
  "objective",
  "required_capabilities",
  "preferred_interfaces",
  "maximum_action",
]);

function requireNonEmptyString(value: unknown, field: string): string {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return value.trim();
}

function requireStringArray(value: unknown, field: string): string[] {
  if (!Array.isArray(value) || value.length === 0 || value.some((item) => typeof item !== "string" || item.trim().length === 0)) {
    throw new Error(`${field} must be a non-empty array of non-empty strings`);
  }
  return (value as string[]).map((item) => item.trim());
}

function validate(value: unknown): MissionEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error("mission must be an object");
  }
  const raw = value as Record<string, unknown>;
  const unknownFields = Object.keys(raw).filter((field) => !MISSION_FIELDS.has(field));
  if (unknownFields.length > 0) {
    throw new Error(`mission contains unsupported fields: ${unknownFields.sort().join(", ")}`);
  }
  const mission_id = requireNonEmptyString(raw.mission_id, "mission_id");
  const objective = requireNonEmptyString(raw.objective, "objective");
  const required_capabilities = requireStringArray(raw.required_capabilities, "required_capabilities");
  const preferred_interfaces = requireStringArray(raw.preferred_interfaces, "preferred_interfaces");
  const maximum_action = raw.maximum_action;
  if (typeof maximum_action !== "string" || !["read", "plan", "write_internal", "external"].includes(maximum_action)) {
    throw new Error("unsupported maximum_action");
  }
  return {
    mission_id,
    objective,
    required_capabilities,
    preferred_interfaces,
    maximum_action: maximum_action as MissionEnvelope["maximum_action"],
  };
}

function canonicalMission(mission: MissionEnvelope): string {
  // Explicit ASCII field order is shared with flagship/run_pipeline.py. Unknown
  // fields are rejected before hashing, so no unsigned extension can cross the
  // authority boundary unnoticed.
  return JSON.stringify({
    maximum_action: mission.maximum_action,
    mission_id: mission.mission_id,
    objective: mission.objective,
    preferred_interfaces: mission.preferred_interfaces,
    required_capabilities: mission.required_capabilities,
  });
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];
if (!inputPath || !outputPath) throw new Error("usage: ingress <input.json> <output.json>");
const mission = validate(JSON.parse(readFileSync(inputPath, "utf8")));
mission.input_sha256 = createHash("sha256").update(canonicalMission(mission), "utf8").digest("hex");
writeFileSync(outputPath, JSON.stringify(mission, null, 2) + "\n");
console.log(JSON.stringify({ stage: "ingress", mission_id: mission.mission_id, input_sha256: mission.input_sha256 }));
