from .models import Action
from .optimizer import optimize
from .simulator import IndustrialSimulator
from .rollouts import rollout


def benchmark(seed: int = 7) -> dict:
    simulator = IndustrialSimulator(seed=seed)
    risks = {action.value: rollout(simulator, action) for action in Action}
    decision = optimize(simulator)
    return {"seed": seed, "components": simulator.components, "events": simulator.events,
            "risks": risks, "recommended": decision["recommended"]["action"],
            "greedy": decision["baselines"]["greedy"]["action"]}


def ablation(seed: int = 7) -> dict:
    simulator = IndustrialSimulator(seed=seed)
    full = optimize(simulator)["recommended"]
    no_causal = min((rollout(simulator, action) for action in Action),
                    key=lambda result: result["mean_loss"])
    no_adversarial = min((rollout(simulator, action) for action in Action),
                         key=lambda result: result["objective"] if "objective" in result else result["mean_loss"])
    return {"full": full["action"], "no_causal_model": no_causal["action"],
            "no_adversarial_checks": no_adversarial["action"]}
