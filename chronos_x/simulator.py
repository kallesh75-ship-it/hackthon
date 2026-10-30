from dataclasses import dataclass
import numpy as np
from .models import Action, Event


@dataclass
class IndustrialSimulator:
    seed: int = 7
    components: int = 50
    events: int = 1000

    def generate(self) -> list[Event]:
        rng = np.random.default_rng(self.seed)
        root = int(rng.integers(0, min(5, self.components)))
        output: list[Event] = []
        for i in range(self.events):
            component = root if i < self.events // 5 else int(rng.integers(0, self.components))
            root_event = component == root and i % 4 == 0
            event_time = float(i / 10 + rng.normal(0, 0.02))
            output.append(Event(
                event_id=f"e-{i:04d}", event_time=event_time,
                arrival_time=event_time + float(rng.uniform(0, 4)),
                source="sensor" if i % 17 else "gateway",
                trust_score=float(rng.uniform(.75, 1) if i % 19 else rng.uniform(.2, .6)),
                signature_valid=i % 23 != 0, component=f"C{component:02d}",
                kind="pressure_spike" if root_event else ("temperature_rise" if i % 3 else "vibration"),
                value=float(rng.normal(1.0 if root_event else .2, .1)),
                payload={"root_cause": root_event, "synthetic": True},
            ))
        return output

    def do(self, action: Action, seed: int | None = None) -> dict[str, float]:
        rng = np.random.default_rng(self.seed if seed is None else seed)
        base = {"mean_loss": 100.0, "deadline_violation_rate": .65}
        effects = {
            Action.SHUTDOWN_REACTOR: (.42, .18),
            Action.ISOLATE_NETWORK: (.55, .28),
            Action.ACTIVATE_BACKUP_COOLING: (.30, .10),
            Action.CONTINUE_MONITORING: (1.0, .65),
        }
        loss_factor, violation = effects[action]
        return {"loss": float(max(0, rng.normal(base["mean_loss"] * loss_factor, 6))),
                "deadline_violation": float(rng.random() < violation)}
