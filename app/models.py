from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from models import Category, Email, Priority


class Observation(BaseModel):
    current_email: Email
    inbox_remaining: int
    emails_processed: int
    current_score: float
    task_id: str
    task_description: str
    step_number: int


class Action(BaseModel):
    email_id: str
    priority: Priority
    category: Category
    should_escalate: bool
    draft_response: Optional[str] = None
    reasoning: Optional[str] = None


class Reward(BaseModel):
    value: float
    breakdown: Dict[str, float]
    feedback: str


class StepResult(BaseModel):
    observation: Optional[Observation]
    reward: Reward
    done: bool
    info: Dict[str, Any]


class ResetResult(BaseModel):
    observation: Observation
    task_id: str
    task_description: str


class StateResult(BaseModel):
    task_id: str
    step_number: int
    emails_processed: int
    inbox_remaining: int
    cumulative_score: float
    done: bool
