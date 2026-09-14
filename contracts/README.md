# Solana contracts

This version does not deploy custom programs: the initial planned payment uses an SPL
transfer authorized by the developer. It does not include an empty Rust crate or claim
that funds are locked or guaranteed.

If the pilot confirms the need for a deposited budget, add an Anchor workspace here
with explicit rules for deposits, payment approval, cancellation, returning uncommitted
funds, and dispute resolution. That decision requires defining who can release funds
and what happens if one of the parties does not respond.
