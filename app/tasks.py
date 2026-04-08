from dataclasses import dataclass
from typing import Dict, List

from app.email_data import get_task_email_records
from app.models import Action, Priority


PRIORITY_ORDER = {
    Priority.LOW: 0,
    Priority.MEDIUM: 1,
    Priority.HIGH: 2,
    Priority.URGENT: 3,
}


def clamp_score(score: float) -> float:
    """Ensure score is strictly between 0 and 1 as required by validator."""
    return max(0.05, min(0.95, float(score)))


@dataclass(frozen=True)
class TaskDefinition:
    id: str
    name: str
    difficulty: str
    description: str
    email_count: int

    def get_email_records(self) -> List[Dict[str, object]]:
        return get_task_email_records(self.id)

    def grade_priority(self, action: Action, ground_truth: Dict[str, object]) -> float:
        expected = ground_truth["priority"]
        actual = action.priority
        if actual == expected:
            return clamp_score(1.0)
        if actual == Priority.SPAM or expected == Priority.SPAM:
            return clamp_score(0.0)
        if abs(PRIORITY_ORDER[actual] - PRIORITY_ORDER[expected]) == 1:
            return clamp_score(0.5)
        return clamp_score(0.0)

    def grade_category(self, action: Action, ground_truth: Dict[str, object]) -> float:
        return clamp_score(1.0 if action.category == ground_truth["category"] else 0.0)

    def grade_escalation(self, action: Action, ground_truth: Dict[str, object]) -> float:
        return clamp_score(1.0 if action.should_escalate == ground_truth["should_escalate"] else 0.0)

    def response_required(self, ground_truth: Dict[str, object]) -> bool:
        return ground_truth["priority"] in {Priority.URGENT, Priority.HIGH}

    def grade_response(self, action: Action, ground_truth: Dict[str, object]) -> float:
        if not self.response_required(ground_truth):
            return clamp_score(1.0)
        draft = (action.draft_response or "").lower()
        key_phrases = [phrase.lower() for phrase in ground_truth.get("key_phrases", [])]
        if not draft or not key_phrases:
            return clamp_score(0.0)
        matches = sum(1 for phrase in key_phrases if phrase in draft)
        return clamp_score(min(1.0, matches / len(key_phrases)))

    def grade_action(self, action: Action, ground_truth: Dict[str, object]) -> float:
        raise NotImplementedError


class PriorityClassificationTask(TaskDefinition):
    def grade_action(self, action: Action, ground_truth: Dict[str, object]) -> float:
        priority_score = self.grade_priority(action, ground_truth)
        category_score = self.grade_category(action, ground_truth)
        return clamp_score((priority_score * 0.6) + (category_score * 0.4))


class TriageEscalationTask(TaskDefinition):
    def grade_action(self, action: Action, ground_truth: Dict[str, object]) -> float:
        priority_score = self.grade_priority(action, ground_truth)
        category_score = self.grade_category(action, ground_truth)
        escalation_score = self.grade_escalation(action, ground_truth)
        return clamp_score((priority_score * 0.4) + (category_score * 0.3) + (escalation_score * 0.3))


class FullTriageTask(TaskDefinition):
    def grade_action(self, action: Action, ground_truth: Dict[str, object]) -> float:
        priority_score = self.grade_priority(action, ground_truth)
        category_score = self.grade_category(action, ground_truth)
        escalation_score = self.grade_escalation(action, ground_truth)
        response_score = self.grade_response(action, ground_truth)

        if self.response_required(ground_truth):
            return clamp_score(
                (priority_score * 0.3)
                + (category_score * 0.2)
                + (escalation_score * 0.2)
                + (response_score * 0.3)
            )

        non_response_total = (priority_score * 0.3) + (category_score * 0.2) + (escalation_score * 0.2)
        return clamp_score(non_response_total / 0.7)


TASKS: Dict[str, TaskDefinition] = {
    "task_1": PriorityClassificationTask(
        id="task_1",
        name="Priority Classification",
        difficulty="easy",
        description="Classify 10 emails by priority and category.",
        email_count=10,
    ),
    "task_2": TriageEscalationTask(
        id="task_2",
        name="Triage and Escalation",
        difficulty="medium",
        description="Triage 15 emails and decide whether each one should be escalated.",
        email_count=15,
    ),
    "task_3": FullTriageTask(
        id="task_3",
        name="Full Triage with Response Drafting",
        difficulty="hard",
        description="Fully triage 20 emails and draft responses for urgent or high-priority cases.",
        email_count=20,
    ),
}


def get_task_definition(task_id: str) -> TaskDefinition:
    if task_id not in TASKS:
        raise KeyError(f"Unknown task_id: {task_id}")
    return TASKS[task_id]


def list_tasks() -> List[Dict[str, object]]:
    return [
        {
            "id": task.id,
            "name": task.name,
            "difficulty": task.difficulty,
            "description": task.description,
            "max_steps": task.email_count,
        }
        for task in TASKS.values()
    ]
