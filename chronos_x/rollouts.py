import numpy as np
from .models import Action
from .simulator import IndustrialSimulator


def rollout(simulator: IndustrialSimulator, action: Action, runs: int = 120, seed: int = 7) -> dict:
    values = np.array([simulator.do(action, seed + i)["loss"] for i in range(runs)])
    violations = np.array([simulator.do(action, seed + i)["deadline_violation"] for i in range(runs)])
    q = float(np.quantile(values, .95))
    cvar = float(values[values >= q].mean())
    mean = float(values.mean())
    margin = 1.96 * float(values.std(ddof=1)) / np.sqrt(runs)
    return {"action": action.value, "runs": runs, "mean_loss": mean, "cvar": cvar,
            "deadline_violation_rate": float(violations.mean()),
            "ci95": [mean - margin, mean + margin]}
