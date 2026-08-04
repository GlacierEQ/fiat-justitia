use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{collections::HashSet, env, fs, process};

#[derive(Deserialize)]
struct Plan {
    mission_id: String,
    technology_ids: Vec<String>,
    tower_registry_sha256: String,
    input_sha256: String,
    maximum_action: String,
    unmatched_capabilities: Vec<String>,
}

#[derive(Serialize)]
struct Decision {
    mission_id: String,
    allowed: bool,
    reason: String,
    plan_sha256: String,
    expected_registry_sha256: String,
    observed_registry_sha256: String,
    expected_input_sha256: String,
    observed_input_sha256: String,
    maximum_action: String,
}

fn is_sha256(value: &str) -> bool {
    value.len() == 64 && value.bytes().all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}

fn action_rank(value: &str) -> Option<u8> {
    match value {
        "read" => Some(0),
        "plan" => Some(1),
        "write_internal" => Some(2),
        "external" => Some(3),
        "destructive" => Some(4),
        _ => None,
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 7 {
        eprintln!(
            "usage: tower-governor <plan.json> <decision.json> <expected-registry-sha256> \
             <expected-input-sha256> <expected-maximum-action> <allowed-technology-ids-csv>"
        );
        process::exit(2);
    }
    let bytes = fs::read(&args[1]).expect("read plan");
    let plan: Plan = serde_json::from_slice(&bytes).expect("parse plan");
    let expected_registry_sha256 = args[3].trim().to_ascii_lowercase();
    let observed_registry_sha256 = plan.tower_registry_sha256.trim().to_ascii_lowercase();
    let expected_input_sha256 = args[4].trim().to_ascii_lowercase();
    let observed_input_sha256 = plan.input_sha256.trim().to_ascii_lowercase();
    let expected_maximum_action = args[5].trim().to_ascii_lowercase();
    let observed_maximum_action = plan.maximum_action.trim().to_ascii_lowercase();
    let allowed_technologies: HashSet<&str> = args[6]
        .split(',')
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .collect();
    let digest = hex::encode(Sha256::digest(&bytes));

    let registry_matches = is_sha256(&expected_registry_sha256)
        && is_sha256(&observed_registry_sha256)
        && expected_registry_sha256 == observed_registry_sha256;
    let input_matches = is_sha256(&expected_input_sha256)
        && is_sha256(&observed_input_sha256)
        && expected_input_sha256 == observed_input_sha256;
    let action_allowed = action_rank(&expected_maximum_action)
        .zip(action_rank(&observed_maximum_action))
        .map(|(expected, observed)| {
            expected == observed && observed <= action_rank("write_internal").unwrap()
        })
        .unwrap_or(false);
    let technologies_governed = !plan.technology_ids.is_empty()
        && plan
            .technology_ids
            .iter()
            .all(|technology| allowed_technologies.contains(technology.as_str()))
        && plan.technology_ids.iter().collect::<HashSet<_>>().len() == plan.technology_ids.len();
    let coverage_complete = plan.unmatched_capabilities.is_empty();
    let mission_valid = !plan.mission_id.trim().is_empty();
    let allowed = mission_valid
        && registry_matches
        && input_matches
        && action_allowed
        && technologies_governed
        && coverage_complete;

    let reason = if allowed {
        "mission, capability coverage, technology membership, action boundary, ingress hash, and canonical registry gates passed"
    } else if !registry_matches {
        "plan registry hash does not match the canonical Tower registry"
    } else if !input_matches {
        "plan input hash does not match the TypeScript-bound mission"
    } else if !action_allowed {
        "plan action exceeds or differs from the authorized flagship action boundary"
    } else if !technologies_governed {
        "plan contains empty, duplicate, or ungoverned technology identifiers"
    } else if !coverage_complete {
        "plan does not cover every required capability"
    } else {
        "plan failed Tower authority preconditions"
    };

    let decision = Decision {
        mission_id: plan.mission_id,
        allowed,
        reason: reason.into(),
        plan_sha256: digest,
        expected_registry_sha256,
        observed_registry_sha256,
        expected_input_sha256,
        observed_input_sha256,
        maximum_action: observed_maximum_action,
    };
    fs::write(&args[2], serde_json::to_vec_pretty(&decision).unwrap()).expect("write decision");
    println!("{}", serde_json::to_string(&decision).unwrap());
    if !allowed {
        process::exit(3);
    }
}
