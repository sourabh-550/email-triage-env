"""
Typed Pydantic models for the Email Triage OpenEnv environment.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class Observation(BaseModel):
    """What the agent sees at each step."""

    email_id: str = Field(description="Unique identifier for the email")
    email_text: str = Field(description="Full body text of the email")
    sender: str = Field(description="Email address or name of the sender")
    subject: str = Field(description="Subject line of the email")
    urgency: Literal["low", "medium", "high"] = Field(
        description="Urgency level inferred from email metadata"
    )
    previous_action: Optional[str] = Field(
        default=None,
        description="The label applied in the previous step, if any",
    )
    step_number: int = Field(description="Current step index (0-based)")
    total_steps: int = Field(description="Total number of emails in this task")


class Action(BaseModel):
    """What the agent decides to do with an email."""

    label: Literal["spam", "important", "promotion"] = Field(
        description="Classification label to apply to the email"
    )
    optional_response: Optional[str] = Field(
        default=None,
        description="Short reply or note (max 200 chars). Required for important emails.",
        max_length=200,
    )


class Reward(BaseModel):
    """Structured reward breakdown for a single step."""

    classification_score: float = Field(
        description="Score for correct label (0.0 or 0.7)"
    )
    urgency_score: float = Field(
        description="Score for correct urgency handling (0.0 or 0.2)"
    )
    response_score: float = Field(
        description="Score for response quality (0.0 or 0.1)"
    )
    total: float = Field(description="Total reward for this step (-0.2 to 1.0)")
    feedback: str = Field(description="Human-readable explanation of the reward")


class StepResult(BaseModel):
    """Full result returned from a single environment step."""

    observation: Optional[Observation] = Field(
        default=None,
        description="Next observation (None if episode is done)",
    )
    reward: Reward
    done: bool = Field(description="True if the episode has ended")
    info: dict = Field(default_factory=dict)


class EpisodeState(BaseModel):
    """Current full state of the environment."""

    task_name: str
    step_number: int
    total_steps: int
    cumulative_score: float
    done: bool
    current_observation: Optional[Observation]
    history: list = Field(default_factory=list)