from __future__ import annotations

from threading import RLock
from typing import Any, Dict, List, Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from app.tasks import get_task_definition
from models import Email, InboxAction, InboxObservation


class InboxEnvironment(Environment[InboxAction, InboxObservation, State]):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    _lock = RLock()
    _initialized = False
    _episode_id = str(uuid4())
    _task_id = "task_1"
    _task = None
    _records: List[Dict[str, Any]] = []
    _current_index = 0
    _emails_processed = 0
    _cumulative_score = 0.0
    _done = False
    _last_feedback: Dict[str, Any] = {}

    def __init__(self, task_id: str = "task_1"):
        super().__init__()
        self.default_task_id = task_id
        self._ensure_initialized(task_id)

    @classmethod
    def _ensure_initialized(cls, task_id: str = "task_1") -> None:
        with cls._lock:
            if not cls._initialized:
                cls._apply_reset(task_id=task_id, episode_id=str(uuid4()))
                cls._initialized = True

    @classmethod
    def _apply_reset(cls, task_id: str = "task_1", episode_id: Optional[str] = None) -> None:
        cls._task_id = task_id
        cls._task = get_task_definition(task_id)
        cls._records = cls._task.get_email_records()
        cls._current_index = 0
        cls._emails_processed = 0
        cls._cumulative_score = 0.0
        cls._done = False
        cls._episode_id = episode_id or str(uuid4())
        cls._last_feedback = {}

    @classmethod
    def _current_record(cls) -> Dict[str, Any]:
        if not cls._records:
            cls._apply_reset(task_id=cls._task_id, episode_id=cls._episode_id)
        return cls._records[min(cls._current_index, len(cls._records) - 1)]

    @classmethod
    def _build_feedback(
        cls,
        *,
        task_id: str,
        priority_score: float,
        category_score: float,
        escalation_score: float,
        response_score: float,
        reasoning_bonus: float,
        spam_penalty: float,
        missing_draft_penalty: float,
        missed_escalation_penalty: float,
    ) -> str:
        feedback_bits = []

        if priority_score >= 0.95:
            feedback_bits.append("Priority matched ground truth.")
        elif priority_score > 0.05:
            feedback_bits.append("Priority was adjacent to the expected level.")
        else:
            feedback_bits.append("Priority missed the expected level.")

        if category_score >= 0.95:
            feedback_bits.append("Category was correct.")
        else:
            feedback_bits.append("Category was incorrect.")

        if task_id in {"task_2", "task_3"}:
            if escalation_score >= 0.95:
                feedback_bits.append("Escalation decision was correct.")
            else:
                feedback_bits.append("Escalation decision was incorrect.")

        if task_id == "task_3" and response_score > 0.05:
            feedback_bits.append(f"Response quality score: {response_score:.2f}.")

        if reasoning_bonus:
            feedback_bits.append("Reasoning bonus applied.")
        if spam_penalty:
            feedback_bits.append("False-positive spam penalty applied.")
        if missing_draft_penalty:
            feedback_bits.append("Missing required draft response penalty applied.")
        if missed_escalation_penalty:
            feedback_bits.append("Missed escalation penalty applied.")

        return " ".join(feedback_bits)

    @classmethod
    def _build_observation(cls, reward: float, done: bool) -> InboxObservation:
        record = cls._current_record()
        email: Email = record["email"]
        return InboxObservation(
            email_id=email.id,
            subject=email.subject,
            sender=email.sender,
            body=email.body,
            timestamp=email.timestamp,
            has_attachment=email.has_attachment,
            inbox_remaining=max(len(cls._records) - cls._current_index - 1, 0) if not done else 0,
            emails_processed=cls._emails_processed,
            task_id=cls._task_id,
            task_description=cls._task.description,
            step_number=min(cls._current_index + 1, len(cls._records)),
            done=done,
            reward=reward,
            metadata={
                "task_name": cls._task.name,
                "task_difficulty": cls._task.difficulty,
                "cumulative_score": round(cls._cumulative_score, 4),
                **cls._last_feedback,
            },
        )

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs: Any,
    ) -> InboxObservation:
        del seed, kwargs
        with self._lock:
            requested_task_id = task_id or self.default_task_id or "task_1"
            self._apply_reset(task_id=requested_task_id, episode_id=episode_id)
            self.__class__._initialized = True
            return self._build_observation(reward=0.1, done=False)

    def step(
        self,
        action: InboxAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> InboxObservation:
        del timeout_s, kwargs
        cls = type(self)
        with cls._lock:
            cls._ensure_initialized(self.default_task_id)
            if cls._done:
                return cls._build_observation(reward=0.05, done=True)

            current_record = cls._current_record()
            ground_truth = current_record["ground_truth"]
            task = cls._task

            priority_score = task.grade_priority(action, ground_truth)
            category_score = task.grade_category(action, ground_truth)
            escalation_score = task.grade_escalation(action, ground_truth)
            response_score = task.grade_response(action, ground_truth)
            base_score = task.grade_action(action, ground_truth)

            reasoning_bonus = 0.05 if action.reasoning and action.reasoning.strip() else 0.0
            spam_penalty = 0.0
            if ground_truth["priority"].value != "spam" and (
                action.priority.value == "spam" or action.category.value == "spam"
            ):
                spam_penalty = 0.1

            missing_draft_penalty = 0.0
            if cls._task_id == "task_3" and task.response_required(ground_truth):
                if not action.draft_response or not action.draft_response.strip():
                    missing_draft_penalty = 0.1

            missed_escalation_penalty = 0.0
            if cls._task_id in {"task_2", "task_3"} and ground_truth["should_escalate"] and not action.should_escalate:
                missed_escalation_penalty = 0.1

            score = base_score + reasoning_bonus - spam_penalty - missing_draft_penalty - missed_escalation_penalty
            reward = max(0.05, min(0.95, round(score, 4)))

            cls._last_feedback = {
                "breakdown": {
                    "base_score": round(base_score, 4),
                    "priority_accuracy": round(priority_score, 4),
                    "category_accuracy": round(category_score, 4),
                    "escalation_accuracy": round(escalation_score, 4),
                    "response_quality": round(response_score, 4),
                    "reasoning_bonus": round(reasoning_bonus, 4),
                    "spam_penalty": round(spam_penalty, 4),
                    "missing_draft_penalty": round(missing_draft_penalty, 4),
                    "missed_escalation_penalty": round(missed_escalation_penalty, 4),
                },
                "feedback": cls._build_feedback(
                    task_id=cls._task_id,
                    priority_score=priority_score,
                    category_score=category_score,
                    escalation_score=escalation_score,
                    response_score=response_score,
                    reasoning_bonus=reasoning_bonus,
                    spam_penalty=spam_penalty,
                    missing_draft_penalty=missing_draft_penalty,
                    missed_escalation_penalty=missed_escalation_penalty,
                ),
            }

            cls._cumulative_score += reward
            cls._emails_processed += 1
            cls._current_index += 1
            cls._done = cls._current_index >= len(cls._records)

            if cls._done:
                cls._current_index = len(cls._records) - 1
                return cls._build_observation(reward=reward, done=True)

            return cls._build_observation(reward=reward, done=False)

    @property
    def state(self) -> State:
        with self._lock:
            self._ensure_initialized(self.default_task_id)
            return State(
                episode_id=self._episode_id,
                step_count=self._emails_processed,
                task_id=self._task_id,
                emails_processed=self._emails_processed,
                inbox_remaining=max(len(self._records) - self._current_index, 0),
                cumulative_score=round(self._cumulative_score, 4),
                done=self._done,
            )
