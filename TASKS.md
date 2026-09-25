# OpenParcelHome work

## First research milestone
- [x] Inspect the empty workspace, supplied context and available Mac tools.
- [x] Check upstream projects and retrieve an Android archive candidate.
- [x] Record package identity, partial JAR-signature evidence and provenance limitations.
- [x] Complete Android signature verification with Google apksig; tampered negative control rejected.
- [ ] Compare publisher identity with a known-good owner installation (external evidence still unavailable).
- [x] Trace the opening-code path and identify unresolved owner credential equivalence.
- [x] Add discovery tooling and run offline safety tests.
- [x] Publish reviewed original material to GitHub and verify CI (run 36175438164).

## Recovery milestone (not yet achieved)
- [ ] Establish an owner-authorised credential recovery/onboarding path.
- [x] Run one owner-approved 15-second advertisement scan (2026-09-25); no connection.
- [x] Run three owner-approved 30-second repeat scans; candidate reappeared, with changing advertisement state.
- [x] Owner confirmed successful normal keypad opening during the final repeat scan.
- [x] Prepare metadata-only service discovery and verify eight offline tests.
- [x] Owner approved one connection; service and app RX/TX UUIDs match; disconnection completed.
- [x] Owner confirmed normal keypad access after service discovery.
- [x] Implement opening encoder and bounded response framing with synthetic/reference tests.
- [x] Prepare private-input single-attempt runner and reviewable opening experiment (28 offline tests).
- [x] Obtain explicit approval and send one opening probe (D2); two replies received, disconnection clean.
- [x] Record D2 outcome: owner reports no opening; delivery and disconnect succeeded; reply trailer was 2.
- [x] Owner confirmed normal keypad access after D2; retry guard remains active.
- [ ] Explain nonzero BLE result and code/session requirements before proposing another test.
- [x] Verify authorised local diagnostic operations on the actual box (D3 status and code permission).
- [ ] Verify a successful opening operation on the actual box.
- [ ] Verify fresh-client offline onboarding and document limitations.
- [ ] Build the iPhone client after the protocol/credential gate passes.

## Follow-up diagnostics
- [x] Trace fixed-code permission query, status parsing and response ACKs in the app.
- [x] Prepare bounded status/permission diagnostic batch; 36 offline tests pass.
- [x] Obtain approval and run D3: status and fixed-code permission succeeded; supplied code is ALWAYS_OPEN.
- [x] Owner confirmed normal keypad access after D3; no further opening attempt authorised.
