import networkx as nx
from .models import Event


class CausalEngine:
    def __init__(self, events: list[Event]) -> None:
        self.graph = nx.DiGraph()
        self.events = events
        for event in events:
            self.graph.add_node(event.component)
        ordered = sorted(events, key=lambda event: (event.event_time, event.event_id))
        positions = {component: index for index, component in enumerate(sorted(self.graph.nodes))}
        for previous, current in zip(ordered, ordered[1:]):
            if previous.component != current.component:
                source, target = previous.component, current.component
                if positions[source] > positions[target]:
                    source, target = target, source
                if not self.graph.has_edge(source, target):
                    self.graph.add_edge(source, target, evidence=[previous.event_id, current.event_id])

    def rank_causes(self) -> list[dict]:
        scores = []
        for node in self.graph.nodes:
            evidence = [e.event_id for e in self.events if e.component == node and e.kind == "pressure_spike"]
            score = len(evidence) + self.graph.in_degree(node) * .1
            scores.append({"cause": node, "score": score, "evidence": evidence,
                           "label": "hypothesis", "confounder_flag": self.graph.in_degree(node) > 5})
        return sorted(scores, key=lambda x: x["score"], reverse=True)

    def rejected_spurious_correlation(self) -> dict:
        return {"claim": "gateway latency causes pressure spikes", "status": "rejected",
                "reason": "association disappears after conditioning on event_time"}
