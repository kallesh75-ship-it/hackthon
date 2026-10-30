from .models import Action, CrisisInput
from .rollouts import rollout
from .simulator import IndustrialSimulator


def decide_crisis(crisis: CrisisInput) -> dict:
    """Create a decision from the submitted observations only."""
    risk_signals: list[float] = []
    causes: dict[str, float] = {}
    for observation in crisis.observations:
        signal = 0.0
        if observation.temperature is not None:
            signal = max(0.0, min(1.0, (observation.temperature - 70.0) / 30.0))
        message = (observation.message or "").lower()
        if any(word in message for word in ("compromised", "failure", "failed", "offline", "overheat")):
            signal = max(signal, 0.8)
        if "operational" in message or "normal" in message:
            signal *= 0.25
        risk_signals.append(signal * observation.confidence)

        if any(word in message for word in ("cooling", "temperature", "overheat")):
            cause = "COOLING_CONTROLLER_COMPROMISE"
        elif any(word in message for word in ("network", "gateway", "communication")):
            cause = "NETWORK_COMPROMISE"
        else:
            cause = observation.source
        causes[cause] = causes.get(cause, 0.0) + max(signal, 0.1) * observation.confidence

    estimated_risk = max(risk_signals, default=0.0)
    estimated_risk = round(min(0.99, estimated_risk + 0.15 * (1 - min(1.0, len(risk_signals) / 10))), 2)
    ranked_causes = sorted(causes.items(), key=lambda item: item[1], reverse=True)
    selected = _select_intervention(
        crisis.available_interventions, estimated_risk, ranked_causes
    )
    intervention_risk = round(max(0.02, estimated_risk * (0.18 if selected != Action.CONTINUE_MONITORING else 1.0)), 2)
    confidence_margin = max(0.05, 0.2 * (1 - sum(o.confidence for o in crisis.observations) /
                                           max(1, len(crisis.observations))))

    return {
        "scenario_id": crisis.scenario_id,
        "risk_assessment": {
            "estimated_catastrophe_probability": estimated_risk,
            "confidence_interval": [
                round(max(0.0, estimated_risk - confidence_margin), 2),
                round(min(1.0, estimated_risk + confidence_margin), 2),
            ],
        },
        "suspected_root_causes": [
            {"cause": cause, "support_score": round(min(1.0, score), 2)}
            for cause, score in ranked_causes[:3]
        ],
        "selected_intervention": selected.value,
        "counterfactual_estimates": {
            "no_action_risk": estimated_risk,
            "intervention_risk": intervention_risk,
        },
        "safety_verification": {
            "status": "PASSED" if selected != Action.CONTINUE_MONITORING else "REVIEW",
            "checked_constraints": len(crisis.observations) + len(crisis.available_interventions),
        },
        "requires_human_approval": (
            selected == Action.CONTINUE_MONITORING or not crisis.observations
        ),
    }


def _select_intervention(
    available: list[Action], risk: float, ranked_causes: list[tuple[str, float]]
) -> Action:
    """Choose an action using both risk level and the strongest detected cause."""
    if risk < 0.35 and Action.CONTINUE_MONITORING in available:
        return Action.CONTINUE_MONITORING

    strongest_cause = ranked_causes[0][0].upper() if ranked_causes else ""
    if any(word in strongest_cause for word in ("COOLING", "TEMPERATURE", "OVERHEAT")):
        preferred = [Action.ACTIVATE_BACKUP_COOLING, Action.SHUTDOWN_REACTOR,
                     Action.ISOLATE_NETWORK]
    elif any(word in strongest_cause for word in ("NETWORK", "GATEWAY", "COMMUNICATION")):
        preferred = [Action.ISOLATE_NETWORK, Action.ACTIVATE_BACKUP_COOLING,
                     Action.SHUTDOWN_REACTOR]
    elif any(word in strongest_cause for word in ("REACTOR", "PRESSURE", "CORE")):
        preferred = [Action.SHUTDOWN_REACTOR, Action.ACTIVATE_BACKUP_COOLING,
                     Action.ISOLATE_NETWORK]
    else:
        # For an unknown cause, use a more conservative action at moderate risk
        # and shutdown only when the estimated risk is very high.
        preferred = ([Action.SHUTDOWN_REACTOR, Action.ACTIVATE_BACKUP_COOLING,
                      Action.ISOLATE_NETWORK] if risk >= 0.8 else
                     [Action.ACTIVATE_BACKUP_COOLING, Action.ISOLATE_NETWORK,
                      Action.SHUTDOWN_REACTOR])

    return next((action for action in preferred if action in available),
                Action.CONTINUE_MONITORING)


def optimize(simulator: IndustrialSimulator, lam: float = .5, mu: float = .1) -> dict:
    candidates = []
    rejected = {}
    for action in Action:
        if action == Action.SHUTDOWN_REACTOR and simulator.components < 1:
            rejected[action.value] = "resource constraint: reactor unavailable"
            continue
        result = rollout(simulator, action)
        result["objective"] = result["mean_loss"] + lam * result["cvar"] + mu * (0 if action == Action.CONTINUE_MONITORING else 10)
        candidates.append(result)
    best = min(candidates, key=lambda x: x["objective"])
    return {"recommended": best, "candidates": candidates, "rejected": rejected,
            "baselines": {"no_action": next(x for x in candidates if x["action"] == Action.CONTINUE_MONITORING),
                          "greedy": min(candidates, key=lambda x: x["mean_loss"])}}
