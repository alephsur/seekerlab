from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VerifiedSeeker:
    wallet_address: str
    sgt_mint_address: str


class SeekerVerifier(Protocol):
    """Future adapter: authenticated wallet, mainnet SGT ownership, non-zero balance.

    The SGT mint, not the wallet address, is the key for one claim per device.
    This port has no production implementation in the starter.
    """

    def verify(self, wallet_address: str) -> VerifiedSeeker | None: ...
