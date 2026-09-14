from decimal import Decimal
from enum import StrEnum


class Currency(StrEnum):
    USDC = "USDC"
    SKR = "SKR"


class CampaignStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class DomainError(Exception):
    pass


class NotFound(DomainError):
    pass


class Conflict(DomainError):
    pass


class Forbidden(DomainError):
    pass


def validate_reward(amount: Decimal) -> None:
    """Advertised token units, NOT a conversion to on-chain atomic units."""
    if not amount.is_finite() or amount <= 0 or amount > Decimal("100000"):
        raise DomainError("Reward must be greater than zero and at most 100000")
    if amount != amount.quantize(Decimal("0.000001")):
        raise DomainError("At most six decimal places are supported in advertised rewards")


def ensure_can_submit(status: str, submitted: int, capacity: int, duplicate: bool) -> None:
    if duplicate:
        raise Conflict("You already submitted feedback for this campaign")
    if status != CampaignStatus.OPEN:
        raise Conflict("This campaign is closed")
    if submitted >= capacity:
        raise Conflict("This campaign has no remaining places")


def clean_feedback(feedback: str) -> str:
    feedback = feedback.strip()
    if not 20 <= len(feedback) <= 5000:
        raise DomainError("Feedback must contain between 20 and 5000 characters")
    return feedback
