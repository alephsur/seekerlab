# Initial increments

## 1. Verifiable identity

- Create an SIWS challenge with a unique nonce, domain, URI, and expiration.
- Verify the Ed25519 signature on the server and consume the nonce atomically.
- Issue sessions and support renewal and revocation.
- Use the session instead of static tokens in the client.
- Test reused and expired nonces, invalid signatures, and wallet changes.

Acceptance: connecting a wallet and authenticating a session are explicit steps;
no one can impersonate another address through a field sent to the backend.

## 2. Seeker eligibility

- Implement `SeekerVerifier` with a read-only mainnet RPC endpoint.
- Validate the SGT, current nonzero balance, authority, and group.
- Associate participation with its mint and retain it even if the primary account changes.
- Distinguish provider failures from the genuine absence of an SGT.

Acceptance: the same SGT cannot participate twice in a campaign by switching wallets.

## 3. Campaigns and review

- Add real developer identities.
- Add acceptance and rejection with a reason, rules, and explicit states.
- Implement deadlines, cancellation, and editing before submissions are received.
- Test PostgreSQL concurrency with many requests for a single slot.
- Add a dedicated developer dashboard once the flows have been validated.

## 4. Evidence and AI

- Attach screenshots and voice notes with size limits and private access.
- Transcribe and summarize only the evidence provided.
- Show the link between each report claim and its supporting evidence.
- Group similar issues without discarding the original feedback.
- Add a file retention and deletion policy.

## 5. Non-custodial payment

- Configure mints per network and verify their decimals.
- Build transfers on mobile and obtain MWA approval.
- Verify success, network, token, payer, recipient, and amount in the backend.
- Prevent a signature from being reused for two submissions.
- Reconcile state after retries or a lost connection.

Acceptance: “paid” requires evidence of a valid transfer; client-supplied text or an
unverified signature does not change the status.

## 6. Pilot and hackathon delivery

- Test on at least one Seeker and one other Android device.
- Recruit real campaigns and participants.
- Measure useful submissions, returning developers, and resolution times.
- Create the final icon, domain, Digital Asset Links, and release signature.
- Prepare the APK, repository, video, presentation, and publication.
