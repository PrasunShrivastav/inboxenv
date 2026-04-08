from pathlib import Path

from fastapi.routing import APIRoute
from openenv.core.env_server.http_server import create_app
from pydantic import BaseModel, Field

from app.tasks import TASKS
from models import InboxAction, InboxObservation
from server.inbox_environment import InboxEnvironment


ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"


class GraderMetadata(BaseModel):
    name: str
    description: str
    weight: float | None = None
    condition: str | None = None


class RewardAdjustmentMetadata(BaseModel):
    name: str
    value: float
    condition: str


class TaskMetadata(BaseModel):
    id: str
    name: str
    difficulty: str
    description: str
    max_steps: int
    graders: list[GraderMetadata]
    reward_adjustments: list[RewardAdjustmentMetadata] = Field(default_factory=list)


class MetadataResponse(BaseModel):
    name: str
    description: str
    readme_content: str | None = None
    version: str | None = None
    author: str | None = None
    documentation_url: str | None = None
    tasks: list[TaskMetadata]


class TasksResponse(BaseModel):
    tasks: list[TaskMetadata]


TASK_GRADERS: dict[str, list[GraderMetadata]] = {
    "task_1": [
        GraderMetadata(
            name="priority",
            description="Grades whether the submitted priority matches the ground truth priority.",
            weight=0.6,
        ),
        GraderMetadata(
            name="category",
            description="Grades whether the submitted category matches the ground truth category.",
            weight=0.4,
        ),
    ],
    "task_2": [
        GraderMetadata(
            name="priority",
            description="Grades whether the submitted priority matches the ground truth priority.",
            weight=0.4,
        ),
        GraderMetadata(
            name="category",
            description="Grades whether the submitted category matches the ground truth category.",
            weight=0.3,
        ),
        GraderMetadata(
            name="escalation",
            description="Grades whether the escalation decision matches the ground truth escalation requirement.",
            weight=0.3,
        ),
    ],
    "task_3": [
        GraderMetadata(
            name="priority",
            description="Grades whether the submitted priority matches the ground truth priority.",
            weight=0.3,
        ),
        GraderMetadata(
            name="category",
            description="Grades whether the submitted category matches the ground truth category.",
            weight=0.2,
        ),
        GraderMetadata(
            name="escalation",
            description="Grades whether the escalation decision matches the ground truth escalation requirement.",
            weight=0.2,
        ),
        GraderMetadata(
            name="response_quality",
            description="Grades draft quality by keyword overlap against required response key phrases.",
            weight=0.3,
            condition="Applied only when the current email requires a response.",
        ),
    ],
}


TASK_REWARD_ADJUSTMENTS: dict[str, list[RewardAdjustmentMetadata]] = {
    "task_1": [
        RewardAdjustmentMetadata(
            name="reasoning_bonus",
            value=0.05,
            condition="Applied when the action includes non-empty reasoning.",
        ),
        RewardAdjustmentMetadata(
            name="spam_penalty",
            value=-0.1,
            condition="Applied when a non-spam email is incorrectly marked as spam.",
        ),
    ],
    "task_2": [
        RewardAdjustmentMetadata(
            name="reasoning_bonus",
            value=0.05,
            condition="Applied when the action includes non-empty reasoning.",
        ),
        RewardAdjustmentMetadata(
            name="spam_penalty",
            value=-0.1,
            condition="Applied when a non-spam email is incorrectly marked as spam.",
        ),
        RewardAdjustmentMetadata(
            name="missed_escalation_penalty",
            value=-0.1,
            condition="Applied when escalation was required but the action does not escalate.",
        ),
    ],
    "task_3": [
        RewardAdjustmentMetadata(
            name="reasoning_bonus",
            value=0.05,
            condition="Applied when the action includes non-empty reasoning.",
        ),
        RewardAdjustmentMetadata(
            name="spam_penalty",
            value=-0.1,
            condition="Applied when a non-spam email is incorrectly marked as spam.",
        ),
        RewardAdjustmentMetadata(
            name="missed_escalation_penalty",
            value=-0.1,
            condition="Applied when escalation was required but the action does not escalate.",
        ),
        RewardAdjustmentMetadata(
            name="missing_draft_penalty",
            value=-0.1,
            condition="Applied when a response was required but no draft response was provided.",
        ),
    ],
}


def _read_readme() -> str | None:
    if not README_PATH.exists():
        return None
    return README_PATH.read_text(encoding="utf-8")


def _build_task_metadata() -> list[TaskMetadata]:
    return [
        TaskMetadata(
            id=task.id,
            name=task.name,
            difficulty=task.difficulty,
            description=task.description,
            max_steps=task.email_count,
            graders=TASK_GRADERS[task.id],
            reward_adjustments=TASK_REWARD_ADJUSTMENTS[task.id],
        )
        for task in TASKS.values()
    ]


def _remove_route(path: str) -> None:
    app.router.routes = [
        route
        for route in app.router.routes
        if not isinstance(route, APIRoute) or route.path != path
    ]
    app.openapi_schema = None


app = create_app(
    InboxEnvironment,
    InboxAction,
    InboxObservation,
    env_name="inboxenv",
    max_concurrent_envs=10,
)

_remove_route("/metadata")


@app.get("/metadata", response_model=MetadataResponse)
def metadata() -> MetadataResponse:
    return MetadataResponse(
        name="InboxEnvironment",
        description="Email triage and prioritization environment with task-specific graders.",
        readme_content=_read_readme(),
        version="1.0.0",
        author=None,
        documentation_url=None,
        tasks=_build_task_metadata(),
    )


@app.get("/tasks", response_model=TasksResponse)
def tasks() -> TasksResponse:
    return TasksResponse(tasks=_build_task_metadata())


def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
