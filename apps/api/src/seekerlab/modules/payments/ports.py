from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExpectedTransfer:
    sender: str
    recipient: str
    mint: str
    amount_atomic: int


class PaymentVerifier(Protocol):
    """Future RPC adapter. No signing or private keys on the backend.

    Verify cluster, successful finalized transaction, token mint, sender,
    recipient and atomic amount; a signature alone is not proof of payment.
    Add a database unique constraint on transaction signatures when implemented.
    """

    def verify(self, signature: str, expected: ExpectedTransfer) -> bool: ...
