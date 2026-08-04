package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
)

type Decision struct {
	MissionID  string `json:"mission_id"`
	Allowed    bool   `json:"allowed"`
	Reason     string `json:"reason"`
	PlanSHA256 string `json:"plan_sha256"`
}

type Event struct {
	MissionID      string `json:"mission_id"`
	Stage          string `json:"stage"`
	Status         string `json:"status"`
	EvidenceSHA256 string `json:"evidence_sha256"`
}

func fail(err error) {
	fmt.Fprintln(os.Stderr, err)
	os.Exit(1)
}

func main() {
	if len(os.Args) != 3 {
		fail(fmt.Errorf("usage: telemetry <decision.json> <event.json>"))
	}
	raw, err := os.ReadFile(os.Args[1])
	if err != nil {
		fail(err)
	}
	var decision Decision
	if err := json.Unmarshal(raw, &decision); err != nil {
		fail(err)
	}
	if decision.MissionID == "" || decision.PlanSHA256 == "" {
		fail(fmt.Errorf("decision is missing mission_id or plan_sha256"))
	}
	sum := sha256.Sum256(raw)
	status := "BLOCKED"
	if decision.Allowed {
		status = "SUCCEEDED"
	}
	event := Event{decision.MissionID, "authority", status, hex.EncodeToString(sum[:])}
	out, err := json.MarshalIndent(event, "", "  ")
	if err != nil {
		fail(err)
	}
	if err := os.WriteFile(os.Args[2], append(out, '\n'), 0o644); err != nil {
		fail(err)
	}
	fmt.Println(string(out))
}
