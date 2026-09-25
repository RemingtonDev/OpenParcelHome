# First physical experiment: advertisement discovery

**Status: first owner-approved 15-second scan completed on 2026-09-25.**
26 devices observed; one Eddystone URL candidate, not yet confirmed as the target.
No connection, GATT operation or opening command was issued. Raw observations
and the experiment record remain private. Owner must be beside their own box and approve the
specific scan before an agent runs it. An owner manually invoking the documented
confirmation flag expresses approval for that scan only.

- Action: collect BLE advertisements for 15 seconds on the nearby Mac.
- Expected box change: none; scanner does not connect or issue GATT operations.
- Success signal: candidate observations consistent with the target using multiple
  signals. No observation is also a valid, inconclusive result.
- Private output: up to 512 devices' latest advertisements; identifiers and payloads
  remain in ignored `.local/captures/`. Review locally and discard unrelated data.
- Stop: denied permission, unexpected pairing prompt, abnormal box behaviour or
  loss of normal access. Do not retry automatically or reset to force advertising.

macOS scanning is active, not radio-passive. CoreBluetooth supplies Mac-local
identifiers rather than physical MAC addresses. See the official
[Bleak scanner](https://bleak.readthedocs.io/en/latest/api/scanner.html) and
[macOS backend](https://bleak.readthedocs.io/en/latest/backends/macos.html) docs.

Later connection/property discovery, specific reads/subscriptions, authentication,
and opening each require an explicit experiment plan and approval. Notifications
can cause descriptor writes. Never batch reset, provisioning, PIN synchronisation
or firmware updates into a recovery test. Keep the box empty and accessible for
any later approved actuation and retain normal owner recovery access.

## Follow-up scans — 2026-09-25

Two owner-approved 30-second scans completed after the initial scan. The same
candidate appeared in both; its advertisement trailer changed. The owner reported
keypad issues during the first repeat. Successful opening during the second repeat
has not yet been confirmed. The helper retains only the latest advertisement per
device, so within-scan timing cannot establish correlation. No connections or GATT
operations were performed. Raw observations and comparisons remain private.

A third owner-approved 30-second repeat scan completed. The same candidate was
observed again; physical opening still awaits owner confirmation. No connection
or control operation was performed. See private discovery-04.json for the result.

## Prepared experiment: one service-discovery connection

Owner subsequently confirmed normal keypad opening during the final repeat scan.
The selected candidate was present in all four scans and its advertisement changed;
identity remains provisional because within-scan event timestamps were not retained.

Status: owner approved and the single connection completed successfully (D1).
Service and app RX/TX UUIDs matched; disconnection completed without error.
Owner confirmed normal keypad access after the connection.
Target: the same Mac-local candidate, stored in ignored
`.local/reports/service-discovery-target.json` (no identifier published).

Action: reacquire that exact identifier for up to 10 seconds, make one connection,
let the BLE stack enumerate services, characteristic properties and descriptor
metadata, then disconnect. Connection timeout is 20 seconds with up to 5 seconds
for disconnection. No characteristic values are read, no notification subscriptions
are made, no explicit pairing is requested and no control writes are sent.
Service discovery itself exchanges GATT protocol traffic. Expected device effect:
a temporary connection only; actual firmware behaviour is not yet verified.

Success: a private service inventory that can be compared with the app's UUIDs.
Stop on a timeout, unexpected pairing prompt, unusual box behaviour or normal-access
failure. Decline an unexpected pairing prompt; do not retry automatically. The tool
attempts disconnection on success and errors; a disconnection error remains an error.
Owner should confirm normal keypad access afterwards. Approval applies only to this
one connection experiment, not authentication or opening commands.

Offline verification: eight tests pass, including consent gate, exact target match,
one connection, metadata-only fake client and cleanup after a connection failure.

## D2 opening probe

The owner explicitly approved the prepared opening test. One command was sent and
the connection cleaned up. The owner reported no opening. The retry marker remains
active. See opening-result-01.md; no further command is authorised.
