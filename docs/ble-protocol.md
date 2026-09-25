# BLE static observations

Artifact A1; see [evidence ledger](evidence-ledger.md). Service UUIDs and properties were confirmed in experiment D1 below. Response
semantics and opening operations remain untested.

| Role observed in app | UUID |
| --- | --- |
| Service | `5c640100-05f8-44de-8b2f-834e5c583db4` |
| App writes toward box (app constant TX) | `5c640101-05f8-44de-8b2f-834e5c583db4` |
| App subscribes to box notifications (app constant RX) | `5c640102-05f8-44de-8b2f-834e5c583db4` |
| Client characteristic configuration descriptor | `00002902-0000-1000-8000-00805f9b34fb` |

The app matches Eddystone URL beacons (service 0xFEAA, frame type 0x10) against the
selected box ID, connects, discovers services, enables notifications and writes
the descriptor. This is observed app intent; actual characteristic permissions
and whether a revision requires bonding must be checked separately.

The inspected command builder uses big-endian ByteBuffer fields, a payload header,
a two-byte operation identifier and framing in chunks of 18 payload bytes. Its
opening builder parses a numeric string into an integer and adds a flags integer,
then optional log-ID and timestamp integers. A final-frame flag and frame indexes
are present. Critical numeric-code encoding was cross-checked against smali.

Acknowledgment and response parsing paths exist. Complete response/error semantics,
fragmentation edge cases and retry behaviour are not yet specified or implemented.
Other code-management and reset operations exist in the APK; they are not part of
the first recovery experiment. No packet examples here contain real credentials.

## D1 — owner-approved service discovery, 2026-09-25

Verified/device: one connection completed, enumerated two services and disconnected
without an error. The selected candidate had appeared in four advertisement scans;
the owner confirmed successful keypad opening during the final scan. The owner also confirmed normal keypad access after this connection.

| Observed UUID | Advertised GATT properties |
| --- | --- |
| `5c640102-05f8-44de-8b2f-834e5c583db4` | read, notify; descriptor 0x2902 |
| `5c640101-05f8-44de-8b2f-834e5c583db4` | write, write-without-response |
| `5c640110-05f8-44de-8b2f-834e5c583db4` | write, write-without-response; purpose unknown |

The service UUID is exactly `5c640100-05f8-44de-8b2f-834e5c583db4`, matching A1.
A second service, `0000180a-0000-1000-8000-00805f9b34fb`, exposes read properties
on UUIDs 0x2a29, 0x2a27 and 0x2a26. No characteristic values were read.
No notifications were subscribed to and no control writes were sent. Properties
alone do not prove authorisation or successful command handling. Do not use the
additional write characteristic until its semantics are established.

## Offline opening codec

`openparcelhome/protocol.py` implements only the minimal single-frame opening form:
frame header 0x8000, a type-0 14-bit message identifier (restricted to the original
random range 0..8189), operation 1, code parsed as a nonnegative signed-32-bit-range
integer, then a zero flags integer. All multi-byte fields are big-endian; total
length is 14 bytes. Leading zeroes are parsed numerically, as in the inspected app.
The zero flags omit log-ID and timestamp fields; no admin/code-sync commands exist
in this implementation. Synthetic vectors are in tests/fixtures/opening-vectors.json.

The bounded reassembler uses a two-byte first frame header and a one-byte continuation
header, frame indices and the last-frame bit observed in the builder. It retains the
message's two-bit type and 14-bit ID; trailing values use the app parser's signed
16-bit interpretation. The response tests are synthetic structural tests. Message
types, success codes and response ordering have NOT been validated on the device.
The first opening experiment sends no application ACK; see its explicit limits in
opening-test.md. No real opening command has been sent.
