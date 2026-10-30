from fastapi.testclient import TestClient
from chronos_x.api import app
from chronos_x.models import Action
from chronos_x.simulator import IndustrialSimulator
from chronos_x.ledger import EventLedger
from chronos_x.defense import assess_attack
from chronos_x.benchmark import ablation, benchmark

client = TestClient(app)

def test_t1_simulator_seeded():
    a = IndustrialSimulator(7).generate()
    b = IndustrialSimulator(7).generate()
    assert a == b and len(a) == 1000

def test_t2_ledger_dedup_and_histories():
    events = IndustrialSimulator().generate()
    ledger = EventLedger()
    assert ledger.ingest(events + events) == 1000
    assert len(ledger.alternative_histories()) == 2

def test_t3_causal_hypotheses():
    response = client.post("/scenarios/T3/reconstruct")
    assert response.status_code == 200
    assert response.json()["causes"][0]["label"] == "hypothesis"

def test_t4_rollout_contract():
    result = client.post("/simulate", json={"action": Action.SHUTDOWN_REACTOR.value, "runs": 100}).json()
    assert result["runs"] == 100 and len(result["ci95"]) == 2

def test_t5_optimizer():
    result = client.post("/decide", json={"action": Action.ACTIVATE_BACKUP_COOLING.value}).json()
    assert "recommended" in result["optimization"]

def test_t6_safety_certificate():
    result = client.post("/decide", json={"action": Action.CONTINUE_MONITORING.value}).json()
    assert result["safety"]["decision"] == "FAIL"

def test_t7_attack_metrics():
    assert 0 <= assess_attack(IndustrialSimulator().generate())["precision"] <= 1

def test_t8_api_events():
    event = IndustrialSimulator().generate()[0].model_dump()
    assert client.post("/events", json=[event]).status_code == 200

def test_benchmark_and_ablations():
    summary = benchmark()
    assert summary["events"] == 1000 and set(summary["risks"]) == {a.value for a in Action}
    assert set(ablation()) == {"full", "no_causal_model", "no_adversarial_checks"}
