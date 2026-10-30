from collections import defaultdict
from .models import Event


class EventLedger:
    def __init__(self) -> None:
        self._events: dict[str, Event] = {}

    def ingest(self, events: list[Event]) -> int:
        before = len(self._events)
        for event in events:
            if event.event_id not in self._events:
                self._events[event.event_id] = event
        return len(self._events) - before

    def replay(self) -> list[Event]:
        return sorted(self._events.values(), key=lambda e: (-e.trust_score, e.event_time, e.event_id))

    def alternative_histories(self) -> list[list[Event]]:
        ordered = self.replay()
        conflicts = [e for e in ordered if not e.signature_valid or e.trust_score < .5]
        return [ordered, [e for e in ordered if e not in conflicts]]
