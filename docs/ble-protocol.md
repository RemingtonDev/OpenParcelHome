# BLE static observations

Artifact A1; see [evidence ledger](evidence-ledger.md). No device-confirmed UUIDs,
properties, response semantics or successful operations yet.

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
