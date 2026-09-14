# Initial architecture

## Modular monolith

One API, one database, and one Android application. Business rules live in
`campaigns/domain.py`, use cases in `service.py`, SQL queries in `repository.py`,
and HTTP handling in `routes.py`. This separation leaves room to grow without
introducing queues, microservices, or a CQRS framework before they are needed.

| Module | Current responsibility | Next integration |
| --- | --- | --- |
| campaigns | Campaigns and text submissions | Acceptance/rejection, attachments, and budget |
| identity | SIWS tester identities and sessions; local builder identity | SGT and real developer identities |
| analysis | `FeedbackAnalyzer` port | Evidence-backed LLM analysis and background execution |
| payments | `PaymentVerifier` port | Mobile transaction construction and backend RPC verification |

## Consistency

Submitting feedback locks the campaign row with `SELECT ... FOR UPDATE` in PostgreSQL.
Within the same transaction, duplicates, status, and available slots are checked;
the submission is inserted and the counter is incremented. The
`(campaign_id, tester_id)` uniqueness constraint and capacity check add database-level
defense. Closing a campaign acquires the same lock.

SQLite can validate API flows but does not reproduce this row-level lock.
PostgreSQL concurrency must be verified before opening public testing.
The project does not claim to have validated real concurrency in this release.

Amounts are handled as `Decimal` and `Numeric(18,6)` to avoid floating-point errors
in the backend. The client uses `Number` only when displaying a label. Payment
implementation must use `bigint` and verified mint decimals; display formatting must
not be reused to construct transfers.

## Identity and network

The MWA integration connects the app to a wallet on devnet and does not sign payments.
Wallet connection and backend authentication are explicit, separate user actions. The
API issues a short-lived SIWS challenge bound to its configured domain, URI, chain, and
expiration. It verifies the exact canonical message and Ed25519 signature before
atomically consuming the nonce and issuing opaque access and rotating refresh tokens.
Only token hashes are stored. Mobile session material is stored with Expo SecureStore.

SIWS identities currently receive the tester role. The local builder token is still
available only when development authentication is enabled; production rejects that mode.
Real developer enrollment and authorization belong to the campaigns increment.

The real SGT resides on mainnet. Its verification will be a read operation independent
of test transactions on devnet. Verification must check a nonzero balance, the mint
authority, and the authentic group, and record the SGT mint to prevent reuse after
wallet changes. An SGT does not guarantee human uniqueness or work quality.

## Payments and AI

There is no escrow, custodial treasury, simulated payment system, or enabled LLM provider.
Future transfers will be authorized by the developer's wallet and verified by the backend.
An AI report must never authorize payment. Attachments and feedback will remain off-chain.

## Distribution

The app is prepared to generate an Android project through Expo Prebuild. No compiled
APK or publishing certificate is included. The configuration allows HTTP for local
development; `APP_VARIANT=production` disables cleartext traffic, but this alone does
not turn the foundation into a production-ready application.

Pending requirements include SGT, real developer authorization, payment verification,
rate limits, a privacy policy, evidence management, and testing SIWS on a real Seeker
device and controlled domain. The API rejects combining `APP_ENV=production` with local
authentication or an insecure SIWS URI.
