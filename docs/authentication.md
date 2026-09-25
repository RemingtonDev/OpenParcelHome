# Authentication observations

Evidence references below use [the ledger](evidence-ledger.md). All code findings
are static observations of artifact A1, not confirmed device behaviour.

- **Verified/static:** SessionController registers a phone number and exchanges a
  confirmation value for an API token (E5). Session data includes a token, selected
  box ID and owner/delegate account information; it is serialised to SharedPreferences.
- **Verified/static:** requests attach a nonempty token in the `PhAuth` header (E4).
- **Verified/static:** the open UI consumes a ReceiveCode API result and passes its
  numeric code, log ID and timestamp to the BLE builder (E2/E3).
- **Unknown:** whether a fixed keypad code can substitute for the API receive code;
  firmware role checks, lockout behaviour, link pairing requirements and revocation.
- **Unknown:** a complete legitimate migration/export path from a configured phone.
  Android manifest declares `allowBackup=false`; do not assume generic backup export.

| Starting state | Current evidence and limitation |
| --- | --- |
| Fresh original-app installation | Registration/token and account-selection dependencies exist; no independent local onboarding demonstrated. |
| Previously authenticated installation | Session persistence exists; cached API token is not proof of a usable offline opening credential. |
| No internet | Inspected opening UI asks API for a receive code; no proven offline fallback in that path. |
| Expired/missing credentials | Failure events and login error cases exist; recovery/refresh lifecycle is not fully mapped. |
| New replacement phone | No validated credential import or code-only onboarding yet. |

A cloud token, BLE bond and delivery/fixed code are different concepts. No server
signing key or per-box cryptographic secret requirement has been established in
this inspected path; absence in this path is not evidence of universal absence.
