from .models import Action


def verify(action: Action, evidence_available: bool = True) -> dict:
    if not evidence_available:
        return {"decision": "UNKNOWN", "action": action.value,
                "certificate": {"signature": "synthetic-policy-v1", "constraints": []},
                "counterexample": None, "abstain": True}
    safe = action != Action.CONTINUE_MONITORING
    return {"decision": "PASS" if safe else "FAIL", "action": action.value,
            "certificate": {"signature": "synthetic-policy-v1", "constraints": ["deadline", "resource", "exclusivity"]},
            "counterexample": None if safe else "deadline violation probability exceeds policy threshold",
            "abstain": False}
