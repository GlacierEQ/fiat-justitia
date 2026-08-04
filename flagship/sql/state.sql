CREATE TABLE IF NOT EXISTS tower_mission (
  mission_id TEXT PRIMARY KEY,
  objective TEXT NOT NULL,
  input_sha256 TEXT NOT NULL
    CHECK (length(input_sha256) = 64 AND input_sha256 NOT GLOB '*[^0-9A-Fa-f]*'),
  plan_sha256 TEXT NOT NULL
    CHECK (length(plan_sha256) = 64 AND plan_sha256 NOT GLOB '*[^0-9A-Fa-f]*'),
  authority_status TEXT NOT NULL CHECK (authority_status IN ('SUCCEEDED', 'BLOCKED')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tower_event (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  mission_id TEXT NOT NULL REFERENCES tower_mission(mission_id),
  stage TEXT NOT NULL,
  status TEXT NOT NULL,
  evidence_sha256 TEXT NOT NULL
    CHECK (length(evidence_sha256) = 64 AND evidence_sha256 NOT GLOB '*[^0-9A-Fa-f]*')
);
