from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class Action(str, Enum):
    SHUTDOWN_REACTOR = "SHUTDOWN_REACTOR"
    ISOLATE_NETWORK = "ISOLATE_NETWORK"
    ACTIVATE_BACKUP_COOLING = "ACTIVATE_BACKUP_COOLING"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"


class Event(BaseModel):
    event_id: str
    event_time: float
    arrival_time: float
    source: str
    trust_score: float = Field(ge=0, le=1)
    signature_valid: bool
    component: str
    kind: str
    value: float
    payload: dict[str, Any] = Field(default_factory=dict)


class SimulationRequest(BaseModel):
    action: Action
    runs: int = Field(default=120, ge=100, le=5000)
    seed: int = 7


class DecisionRequest(BaseModel):
    action: Action
    seed: int = 7


class CrisisObservation(BaseModel):
    source: str
    confidence: float = Field(ge=0, le=1)
    timestamp: str
    temperature: float | None = None
    message: str | None = None


class CrisisInput(BaseModel):
    scenario_id: str
    current_time: str
    catastrophe_deadline_minutes: int = Field(gt=0)
    observations: list[CrisisObservation]
    available_interventions: list[Action]
