from __future__ import annotations

from threading import Lock
from typing import Dict, List, Optional

from app.models import Action, Observation, ResetResult, Reward, StateResult, StepResult
from app.tasks import get_task_definition


class InboxEnvironment:
    def __init__(self, task_id: str = "task_1"):
        self._lock = Lock()
        self.last_action: Optional[Action] = None
        self.last_reward: Optional[Reward] = None
        self.task_id = task_id
        self.task = get_task_definition(task_id)
        self.records: List[Dict[str, object]] = []
        self.current_index = 0
        self.emails_processed = 0
        self.cumulative_score = 0.0
        self.done = False
        self.reset(task_id)

    def reset(self, task_id: Optional[str] = None) -> ResetResult:
        with self._lock:
            if task_id is not None:
                self.task_id = task_id
                self.task = get_task_definition(task_id)

            self.records = self.task.get_email_records()
            self.current_index = 0
            self.emails_processed = 0
            self.cumulative_score = 0.0
            self.done = False
            self.last_action = None
            self.last_reward = None

            observation = self._build_observation()
            return ResetResult(
                observation=observation,
                task_id=self.task_id,
                task_description=self.task.description,
            )

    def step(self, action: Action) -> StepResult:
        with self._lock:
            if self.done:
                raise ValueError("Episode already completed. Call reset() to start a new task.")

            current_record = self.records[self.current_index]
            current_email = current_record["email"]
            if action.email_id != current_email.id:
                raise ValueError(
                    f"Action email_id {action.email_id} does not match current email {current_email.id}."
                )

            reward = self._compute_reward(action, current_record["ground_truth"], self.task_id)
            self.last_action = action
            self.last_reward = reward
            self.cumulative_score += reward.value
            self.current_index += 1
            self.emails_processed += 1
            self.done = self.current_index >= len(self.records)

            next_observation = None if self.done else self._build_observation()
            info = {
                "task_id": self.task_id,
                "task_name": self.task.name,
                "current_email_id": current_email.id,
                "current_email_subject": current_email.subject,
                "emails_total": len(self.records),
                "emails_processed": self.emails_processed,
                "cumulative_score": round(self.cumulative_score, 4),
            }
            return StepResult(observation=next_observation, reward=reward, done=self.done, info=info)

    def state(self) -> StateResult:
        with self._lock:
            return StateResult(
                task_id=self.task_id,
                step_number=self.current_index + (0 if self.done else 1),
                emails_processed=self.emails_processed,
                inbox_remaining=max(len(self.records) - self.current_index, 0),
                cumulative_score=round(self.cumulative_score, 4),
                done=self.done,
            )

    def _build_observation(self) -> Observation:
        current_record = self.records[self.current_index]
        return Observation(
            current_email=current_record["email"],
            inbox_remaining=len(self.records) - self.current_index - 1,
            emails_processed=self.emails_processed,
            current_score=round(self.cumulative_score, 4),
            task_id=self.task_id,
            task_description=self.task.description,
            step_number=self.current_index + 1,
        )

    def _compute_reward(self, action: Action, ground_truth: Dict[str, object], task_id: str) -> Reward:
        priority_score = self.task.grade_priority(action, ground_truth)
        category_score = self.task.grade_category(action, ground_truth)
        escalation_score = self.task.grade_escalation(action, ground_truth)
        response_score = self.task.grade_response(action, ground_truth)
        base_score = self.task.grade_action(action, ground_truth)

        reasoning_bonus = 0.05 if action.reasoning and action.reasoning.strip() else 0.0
        spam_penalty = 0.0
        if ground_truth["priority"].value != "spam" and (
            action.priority.value == "spam" or action.category.value == "spam"
        ):
            spam_penalty = 0.1

        missing_draft_penalty = 0.0
        if task_id == "task_3" and self.task.response_required(ground_truth):
            if not action.draft_response or not action.draft_response.strip():
                missing_draft_penalty = 0.1

        missed_escalation_penalty = 0.0
        if task_id in {"task_2", "task_3"} and ground_truth["should_escalate"] and not action.should_escalate:
            missed_escalation_penalty = 0.1

        computed_reward = base_score + reasoning_bonus - spam_penalty - missing_draft_penalty - missed_escalation_penalty
        reward_value = max(0.05, min(0.95, round(computed_reward, 4)))

        breakdown = {
            "base_score": round(base_score, 4),
            "priority_accuracy": round(priority_score, 4),
            "category_accuracy": round(category_score, 4),
            "escalation_accuracy": round(escalation_score, 4),
            "response_quality": round(response_score, 4),
            "reasoning_bonus": round(reasoning_bonus, 4),
            "spam_penalty": round(spam_penalty, 4),
            "missing_draft_penalty": round(missing_draft_penalty, 4),
            "missed_escalation_penalty": round(missed_escalation_penalty, 4),
        }

        feedback_bits = []
        if priority_score == 1.0:
            feedback_bits.append("Priority matched ground truth.")
        elif priority_score == 0.5:
            feedback_bits.append("Priority was adjacent to the expected level.")
        else:
            feedback_bits.append("Priority missed the expected level.")

        if category_score == 1.0:
            feedback_bits.append("Category was correct.")
        else:
            feedback_bits.append("Category was incorrect.")

        if task_id in {"task_2", "task_3"}:
            feedback_bits.append(
                "Escalation decision was correct." if escalation_score == 1.0 else "Escalation decision was incorrect."
            )

        if task_id == "task_3" and self.task.response_required(ground_truth):
            feedback_bits.append(f"Response quality score: {response_score:.2f}.")

        if reasoning_bonus:
            feedback_bits.append("Reasoning bonus applied.")
        if spam_penalty:
            feedback_bits.append("False-positive spam penalty applied.")
        if missing_draft_penalty:
            feedback_bits.append("Missing required draft response penalty applied.")
        if missed_escalation_penalty:
            feedback_bits.append("Missed escalation penalty applied.")

        return Reward(value=reward_value, breakdown=breakdown, feedback=" ".join(feedback_bits))


class InboxEnvironmentStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._environments: Dict[str, InboxEnvironment] = {}

    def get(self, session_id: str = "default") -> InboxEnvironment:
        with self._lock:
            if session_id not in self._environments:
                self._environments[session_id] = InboxEnvironment()
            return self._environments[session_id]


ENV_STORE = InboxEnvironmentStore()
