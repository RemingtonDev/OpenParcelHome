# D3 — status and code-permission results, 2026-09-25

**Verified/device: both approved queries succeeded and the connection cleaned up.**
The owner confirmed normal keypad access still works afterwards. No opening or
configuration command was sent. Opening and diagnostic retry guards remain active.

| Query | Result |
| --- | --- |
| GET_STATUS | Status 0; 47 data bytes; reported door closed |
| Firmware field | Integer 196865; no semantic version inferred |
| GET_AUTH_FIXED_CODE | Status 0; one data byte; permission decoded as `ALWAYS_OPEN` |
| Session completion | Each response acknowledged using its own ID; unsubscribe/disconnect succeeded |

The PIN was supplied through the local hidden prompt, never chat or a command-line
argument. Raw packets, box identifiers and the code are not published or retained
in the diagnostic report. These results do not prove the PIN entered in D3 was
identical to D2: the scripts intentionally do not store or fingerprint credentials.

## What this establishes

The independently implemented BLE request/acknowledgement/response path works for
two non-opening queries on this box. The code supplied during D3 is recognised in
the fixed-code permission query with the app's `ALWAYS_OPEN` permission value.
This is a tested local diagnostic capability, not a successful opening recovery.

It rules out an unknown fixed code for the D3 input. It does not establish that
OPEN_BOX accepts that credential type, explain error 2 from D2, or prove that an
application acknowledgement would turn a nonzero opening response into success.
The permission value 2 and D2's error/status value 2 are separate fields.

## Remaining question

The inspected original opening UI obtains a receive code from the cloud, whereas
D3 queried the fixed-code store. Whether the opening command uses distinct code
validation, optional fields or session requirements remains unresolved. Compare
these requirements with a configured original app or additional firmware/protocol
evidence before another opening proposal. No retry, optional clock/log update,
code change or firmware intervention is authorised by the successful diagnostics.
