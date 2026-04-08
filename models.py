from enum import Enum
from typing import Optional

from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field


class Priority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SPAM = "spam"


class Category(str, Enum):
    CUSTOMER_SUPPORT = "customer_support"
    BILLING = "billing"
    TECHNICAL = "technical"
    SALES = "sales"
    INTERNAL = "internal"
    SPAM = "spam"


class Email(BaseModel):
    id: str
    subject: str
    sender: str
    body: str
    timestamp: str
    has_attachment: bool = False
    thread_id: Optional[str] = None


class InboxAction(Action):
    priority: Priority = Field(..., description="Priority assigned to the current email.")
    category: Category = Field(..., description="Category assigned to the current email.")
    should_escalate: bool = Field(..., description="Whether the email should be escalated.")
    draft_response: Optional[str] = Field(
        default=None,
        description="Optional draft response, used on higher-difficulty tasks.",
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Optional explanation for the triage choice.",
    )


class InboxObservation(Observation):
    email_id: str = Field(..., description="Stable ID for the current email.")
    subject: str = Field(..., description="Email subject line.")
    sender: str = Field(..., description="Email sender address.")
    body: str = Field(..., description="Email body text.")
    timestamp: str = Field(..., description="Email timestamp.")
    has_attachment: bool = Field(default=False, description="Whether the email includes an attachment.")
    inbox_remaining: int = Field(..., description="How many emails remain after this one.")
    emails_processed: int = Field(..., description="How many emails have been processed.")
    task_id: str = Field(..., description="Current task identifier.")
    task_description: str = Field(..., description="Description of the current task.")
    step_number: int = Field(..., description="1-based step number in the episode.")
