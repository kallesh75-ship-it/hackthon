from fastapi import FastAPI
from .models import DecisionRequest, Event, SimulationRequest
from .simulator import IndustrialSimulator
from .ledger import EventLedger
from .causal import CausalEngine
from .rollouts import rollout
from .optimizer import optimize
from .safety import verify
from .agents import run_agents
from .defense import assess_attack
from .benchmark import benchmark

app = FastAPI(title="CHRONOS-X")
simulator = IndustrialSimulator()
ledger = EventLedger()

@app.post("/events")
def post_events(events: list[Event]) -> dict:
    return {"accepted": ledger.ingest(events), "total": len(ledger.replay())}

@app.post("/scenarios/{scenario_id}/reconstruct")
def reconstruct(scenario_id: str) -> dict:
    events = ledger.replay() or simulator.generate()
    engine = CausalEngine(events)
    ranked = engine.rank_causes()
    return {"scenario_id": scenario_id, "causes": engine.rank_causes(),
            "histories": [len(h) for h in EventLedgerWith(events).alternative_histories()],
            "rejected": engine.rejected_spurious_correlation()}

@app.get("/causes")
def causes() -> list[dict]:
    return CausalEngine(ledger.replay() or simulator.generate()).rank_causes()

@app.post("/simulate")
def simulate(request: SimulationRequest) -> dict:
    return rollout(simulator, request.action, request.runs, request.seed)

@app.post("/decide")
def decide(request: DecisionRequest) -> dict:
    optimization = optimize(simulator)
    return {"safety": verify(request.action), "optimization": optimization,
            "agents": run_agents([], optimization["recommended"])}

@app.get("/audit")
def audit() -> dict:
    events = ledger.replay() or simulator.generate()
    return {"events": len(events), "deterministic": events == sorted(events, key=lambda e: (-e.trust_score, e.event_time, e.event_id)),
            "attack_defense": assess_attack(events), "benchmark": benchmark()}


class EventLedgerWith(EventLedger):
    def __init__(self, events: list[Event]) -> None:
        super().__init__()
        self.ingest(events)
