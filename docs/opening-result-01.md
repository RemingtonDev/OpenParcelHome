# D2 — first opening probe, 2026-09-25

**Verified/device + owner report: the single authorised attempt did not open the box.**
The opening write completed, two notifications arrived, and unsubscribe/disconnect
completed without reported errors. No second command or application ACK was sent.
The exclusive attempt marker remains active. The owner confirmed normal keypad access still works afterwards.

| Reply | Parsed observation |
| --- | --- |
| First | Kind 2, request ID matches, empty body |
| Second | Kind 0, different message ID, two-byte body, signed trailing value 2 |

No raw payload, code, target identifier or exact message IDs are published.
The code was entered only in a local non-echoing Terminal prompt. The raw credential
was not logged. The private report contains only the sanitised summaries above.

## Interpretation and limits

The first reply is consistent with the app's type-2 acknowledgement format. The
second reply having its own message ID is **not by itself a protocol mismatch**:
`BTService.finalizeCommand` constructs an ACK from the ID in the second received
message, rather than from the original request. The runner exposed ID equality as
an observation, not an acceptance test, and did not discard this reply.

The inspected app reads the final two bytes as a signed error code and treats zero
as the opening-success path (`HomeActivity.java:333`). The observed nonzero value
therefore supports unsuccessful processing. A specific meaning for value 2 has
not been found in the inspected app's BLE code or opening callback. In particular,
this is **not proof that 2 means invalid PIN**. Cloud error enums are not evidence
of the BLE code meanings.

The experiment intentionally omitted optional log/timestamp fields and the final
application ACK. The app supports constructing those omitted optional fields, but
the device's exact acceptance requirements and the effect of the omitted ACK are
not fully known. We cannot yet conclude that all fixed/keypad codes are unusable
through Bluetooth, or that another code should be tried.

## Next deciding evidence

Preserve normal keypad access and the retry marker. Review the device response
semantics, code roles and original-session sequencing offline before proposing
any further physical test. A known-good configured app/session or firmware protocol
documentation could distinguish a credential-role restriction from a session
requirement. No guessing, code changes, timestamp experimentation or retries are
authorised by this result.
