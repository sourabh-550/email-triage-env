"""
Core OpenEnv environment for Email Classification & Triage.
Implements: reset(), step(action), state()
"""

from typing import Optional
from env.models import Observation, Action, Reward, StepResult, EpisodeState
from env.tasks import ALL_TASKS, grade_step


class EmailTriageEnv:
    """
    OpenEnv-compliant environment that simulates an email inbox manager.

    An agent receives one email at a time as an Observation, decides how to
    label it (and optionally reply), and receives a structured Reward.
    """

    VALID_TASKS = list(ALL_TASKS.keys())

    def __init__(self, task_name: str = "easy"):
        if task_name not in self.VALID_TASKS:
            raise ValueError(f"Unknown task '{task_name}'. Choose from {self.VALID_TASKS}")

        self.task_name = task_name
        self._task = ALL_TASKS[task_name]
        self._dataset = self._task["dataset"]

        self._step_index: int = 0
        self._done: bool = False
        self._cumulative_score: float = 0.0
        self._history: list[dict] = []
        self._previous_label: Optional[str] = None

    # ------------------------------------------------------------------
    # OpenEnv spec
    # ------------------------------------------------------------------

    def reset(self) -> Observation:
        """Reset the environment to the beginning of the task."""
        self._step_index = 0
        self._done = False
        self._cumulative_score = 0.0
        self._history = []
        self._previous_label = None
        return self._make_observation(0)

    def step(self, action: Action) -> StepResult:
        """
        Apply an action to the current email and advance to the next.

        Args:
            action: An Action with a label and optional_response.

        Returns:
            StepResult with next Observation, Reward, and done flag.
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new one.")

        current_email = self._dataset[self._step_index]

        # Grade the action against the expected output
        grade = grade_step(current_email, action.model_dump())
        reward = Reward(
            classification_score=grade["classification_score"],
            urgency_score=grade["urgency_score"],
            response_score=grade["response_score"],
            total=grade["total"],
            feedback=grade["feedback"],
        )

        # Record history
        self._history.append(
            {
                "step": self._step_index,
                "email_id": current_email["email_id"],
                "action": action.model_dump(),
                "reward": reward.model_dump(),
            }
        )

        self._cumulative_score += max(0.0, reward.total)
        self._previous_label = action.label
        self._step_index += 1

        # Check if we've processed all emails
        if self._step_index >= len(self._dataset):
            self._done = True
            next_obs = None
        else:
            next_obs = self._make_observation(self._step_index)

        return StepResult(
            observation=next_obs,
            reward=reward,
            done=self._done,
            info={
                "email_id": current_email["email_id"],
                "expected_label": current_email["expected_label"],
                "task": self.task_name,
            },
        )

    def state(self) -> EpisodeState:
        """Return the full current state of the environment."""
        current_obs = None
        if not self._done and self._step_index < len(self._dataset):
            current_obs = self._make_observation(self._step_index)

        return EpisodeState(
            task_name=self.task_name,
            step_number=self._step_index,
            total_steps=len(self._dataset),
            cumulative_score=round(self._cumulative_score, 4),
            done=self._done,
            current_observation=current_obs,
            history=self._history,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_observation(self, index: int) -> Observation:
        email = self._dataset[index]
        return Observation(
            email_id=email["email_id"],
            email_text=email["email_text"],
            sender=email["sender"],
            subject=email["subject"],
            urgency=email["urgency"],
            previous_action=self._previous_label,
            step_number=index,
            total_steps=len(self._dataset),
        )