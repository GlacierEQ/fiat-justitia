//! Rust — Advanced Example: Typed Action Safety Governor
//!
//! What: A deterministic policy kernel for tool execution decisions.
//! Where: MCP gateways, evidence pipelines, privileged CLIs, agent runtimes.
//! When: Untrusted requests must be constrained before any side effect occurs.
//! Why: Rust's enums, ownership, and exhaustive matching make policy gaps visible.
//! How: Canonicalized paths, bounded inputs, explicit mutation approval, structured
//!      decisions, and tests that exercise denial paths as first-class behavior.

use std::fmt;
use std::path::{Component, Path, PathBuf};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ActionKind {
    Read,
    Write,
    Delete,
    Execute,
    Publish,
}

impl ActionKind {
    pub fn is_mutating(self) -> bool {
        !matches!(self, Self::Read)
    }

    pub fn requires_elevated_approval(self) -> bool {
        matches!(self, Self::Delete | Self::Execute | Self::Publish)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ActionRequest {
    pub actor: String,
    pub action: ActionKind,
    pub target: PathBuf,
    pub payload_bytes: usize,
    pub recursion_depth: usize,
    pub approved_mutation: bool,
    pub approved_elevated_action: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct GovernorConfig {
    pub allowed_roots: Vec<PathBuf>,
    pub max_payload_bytes: usize,
    pub max_recursion_depth: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DenialReason {
    MissingActor,
    NoAllowedRoots,
    PathTraversal,
    TargetOutsideAllowedRoots,
    PayloadTooLarge { actual: usize, maximum: usize },
    RecursionTooDeep { actual: usize, maximum: usize },
    MutationApprovalRequired,
    ElevatedApprovalRequired,
}

impl fmt::Display for DenialReason {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::MissingActor => write!(f, "authenticated actor is required"),
            Self::NoAllowedRoots => write!(f, "no allowed roots are configured"),
            Self::PathTraversal => write!(f, "target contains a parent traversal component"),
            Self::TargetOutsideAllowedRoots => write!(f, "target is outside every allowed root"),
            Self::PayloadTooLarge { actual, maximum } => {
                write!(f, "payload size {actual} exceeds maximum {maximum}")
            }
            Self::RecursionTooDeep { actual, maximum } => {
                write!(f, "recursion depth {actual} exceeds maximum {maximum}")
            }
            Self::MutationApprovalRequired => write!(f, "mutation approval is required"),
            Self::ElevatedApprovalRequired => write!(f, "elevated action approval is required"),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PolicyDecision {
    pub allowed: bool,
    pub normalized_target: Option<PathBuf>,
    pub reason: Option<DenialReason>,
    pub policy_version: &'static str,
}

impl PolicyDecision {
    fn allow(target: PathBuf) -> Self {
        Self {
            allowed: true,
            normalized_target: Some(target),
            reason: None,
            policy_version: "safety-governor/1",
        }
    }

    fn deny(reason: DenialReason) -> Self {
        Self {
            allowed: false,
            normalized_target: None,
            reason: Some(reason),
            policy_version: "safety-governor/1",
        }
    }
}

#[derive(Debug, Clone)]
pub struct SafetyGovernor {
    config: GovernorConfig,
}

impl SafetyGovernor {
    pub fn new(config: GovernorConfig) -> Result<Self, DenialReason> {
        if config.allowed_roots.is_empty() {
            return Err(DenialReason::NoAllowedRoots);
        }
        let allowed_roots = config
            .allowed_roots
            .into_iter()
            .map(|root| normalize_without_io(&root))
            .collect::<Result<Vec<_>, _>>()?;
        Ok(Self {
            config: GovernorConfig {
                allowed_roots,
                ..config
            },
        })
    }

    pub fn evaluate(&self, request: &ActionRequest) -> PolicyDecision {
        if request.actor.trim().is_empty() {
            return PolicyDecision::deny(DenialReason::MissingActor);
        }
        if request.payload_bytes > self.config.max_payload_bytes {
            return PolicyDecision::deny(DenialReason::PayloadTooLarge {
                actual: request.payload_bytes,
                maximum: self.config.max_payload_bytes,
            });
        }
        if request.recursion_depth > self.config.max_recursion_depth {
            return PolicyDecision::deny(DenialReason::RecursionTooDeep {
                actual: request.recursion_depth,
                maximum: self.config.max_recursion_depth,
            });
        }
        if request.action.is_mutating() && !request.approved_mutation {
            return PolicyDecision::deny(DenialReason::MutationApprovalRequired);
        }
        if request.action.requires_elevated_approval() && !request.approved_elevated_action {
            return PolicyDecision::deny(DenialReason::ElevatedApprovalRequired);
        }

        let normalized = match normalize_without_io(&request.target) {
            Ok(path) => path,
            Err(reason) => return PolicyDecision::deny(reason),
        };
        if !self
            .config
            .allowed_roots
            .iter()
            .any(|root| normalized == *root || normalized.starts_with(root))
        {
            return PolicyDecision::deny(DenialReason::TargetOutsideAllowedRoots);
        }

        PolicyDecision::allow(normalized)
    }
}

fn normalize_without_io(path: &Path) -> Result<PathBuf, DenialReason> {
    let mut normalized = PathBuf::new();
    for component in path.components() {
        match component {
            Component::ParentDir => return Err(DenialReason::PathTraversal),
            Component::CurDir => {}
            other => normalized.push(other.as_os_str()),
        }
    }
    Ok(normalized)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn governor() -> SafetyGovernor {
        SafetyGovernor::new(GovernorConfig {
            allowed_roots: vec![PathBuf::from("/srv/evidence")],
            max_payload_bytes: 1024,
            max_recursion_depth: 4,
        })
        .expect("valid governor")
    }

    fn request(action: ActionKind, target: &str) -> ActionRequest {
        ActionRequest {
            actor: "operator.casey".to_string(),
            action,
            target: PathBuf::from(target),
            payload_bytes: 64,
            recursion_depth: 1,
            approved_mutation: false,
            approved_elevated_action: false,
        }
    }

    #[test]
    fn allows_read_inside_root() {
        let decision = governor().evaluate(&request(
            ActionKind::Read,
            "/srv/evidence/case-1009/index.json",
        ));
        assert!(decision.allowed);
        assert_eq!(
            decision.normalized_target,
            Some(PathBuf::from("/srv/evidence/case-1009/index.json"))
        );
    }

    #[test]
    fn denies_parent_traversal_before_root_evaluation() {
        let decision = governor().evaluate(&request(
            ActionKind::Read,
            "/srv/evidence/../secrets/token.txt",
        ));
        assert_eq!(decision.reason, Some(DenialReason::PathTraversal));
    }

    #[test]
    fn denies_write_without_mutation_approval() {
        let decision = governor().evaluate(&request(
            ActionKind::Write,
            "/srv/evidence/case-1009/manifest.json",
        ));
        assert_eq!(
            decision.reason,
            Some(DenialReason::MutationApprovalRequired)
        );
    }

    #[test]
    fn delete_requires_both_approval_levels() {
        let mut candidate = request(ActionKind::Delete, "/srv/evidence/quarantine/item");
        candidate.approved_mutation = true;
        let denied = governor().evaluate(&candidate);
        assert_eq!(denied.reason, Some(DenialReason::ElevatedApprovalRequired));

        candidate.approved_elevated_action = true;
        assert!(governor().evaluate(&candidate).allowed);
    }

    #[test]
    fn bounded_inputs_fail_closed() {
        let mut candidate = request(ActionKind::Read, "/srv/evidence/item");
        candidate.payload_bytes = 1025;
        assert!(matches!(
            governor().evaluate(&candidate).reason,
            Some(DenialReason::PayloadTooLarge { .. })
        ));

        candidate.payload_bytes = 1;
        candidate.recursion_depth = 5;
        assert!(matches!(
            governor().evaluate(&candidate).reason,
            Some(DenialReason::RecursionTooDeep { .. })
        ));
    }
}
