from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class FeedbackReport:
    submission_id: UUID
    summary: str
    reproduction_steps: tuple[str, ...]
    evidence: tuple[str, ...]
    model: str


class FeedbackAnalyzer(Protocol):
    """Future LLM adapter; untrusted feedback is data, never an instruction.

    Reports assist human reviewers and never authorize payments.
    """

    def analyze(self, submission_id: UUID, feedback: str) -> FeedbackReport: ...
