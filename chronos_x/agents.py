import json
from .models import Action


def run_agents(causes: list[dict], recommendation: dict) -> list[dict]:
    agents = ["investigator", "predictor", "optimizer", "safety", "red_team"]
    messages = []
    for name in agents:
        action = recommendation["action"]
        if name == "red_team":
            action = Action.CONTINUE_MONITORING.value
        messages.append({"agent": name, "action": action, "confidence": .9 if name != "red_team" else .4,
                         "evidence": causes[:2], "validated": name != "red_team"})
    return json.loads(json.dumps(messages))
