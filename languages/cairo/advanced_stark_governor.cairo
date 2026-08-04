// Advanced Exhibit: Cairo STARK-Provable State Governor
struct StateReceipt {
    case_id: felt,
    action_hash: felt,
    approved: felt,
}

func verify_state_transition(receipt: StateReceipt) -> (valid: felt) {
    if (receipt.approved == 1) {
        return (valid=1);
    }
    return (valid=0);
}
