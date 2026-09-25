# Evidence ledger — 2026-09-25

A1: APK SHA-256 `e4ba0a6822bbff48e6aab18d8c4ec2ab14618c34839c731ffecb382f34eedfdc`. All references below concern this artifact only.
JADX 1.5.6 output is partial (84 errors, exit 3); Apktool 3.0.3 exited 0.
Paths are local investigation indexes, not distributed vendor files or original source lines.

| ID | Observation | Local JADX reference | Confidence |
| --- | --- | --- | --- |
| E1 | BLE UUID declarations | `.local/analysis/jadx/sources/com/parcelhome/android/owner/service/ble/BTService.java:29` | Verified/static in A1; not device tested |
| E2 | Numeric opening-code builder | `.local/analysis/jadx/sources/com/parcelhome/android/owner/service/ble/BTCommandBuilder.java:46` | Verified/static in A1; not device tested |
| E3 | Cloud response passed into opening builder | `.local/analysis/jadx/sources/com/parcelhome/android/owner/view/fragment/OpenBoxFragment.java:111` | Verified/static in A1; not device tested |
| E4 | Cloud token header and base URL | `.local/analysis/jadx/sources/com/parcelhome/android/owner/webservice/builder/WebServiceBuilder.java:140` | Verified/static in A1; not device tested |
| E5 | Session persistence and registration/token exchange | `.local/analysis/jadx/sources/com/parcelhome/android/owner/controller/SessionController.java:34` | Verified/static in A1; not device tested |
| E6 | Raw frame assigned to GATT characteristic | `.local/analysis/jadx/sources/com/parcelhome/android/owner/service/ble/BTService.java:118` | Verified/static in A1; not device tested |
| E7 | BLE connection and subscription | `.local/analysis/jadx/sources/com/parcelhome/android/owner/ParcelHomeApplication.java:251` | Verified/static in A1; not device tested |
| E8 | Receive-code API route | `.local/analysis/jadx/sources/com/parcelhome/android/owner/webservice/service/ParcelHomeService.java:55` | Verified/static in A1; not device tested |

Cross-checks in `.local/analysis/apktool/smali/com/parcelhome/android/owner/`:
- `service/ble/BTCommandBuilder.smali:367` through the end of `buildOpenBox`: numeric parse, big-endian encoding, flags and optional fields.
- `service/ble/BTService$Params.smali:37`: service UUID, with characteristic constants at lines 55 and 64.
- `service/ble/BTService.smali:666` and `:685`: characteristic assignment and write.

**Owner-report:** initial model, existing keypad access and missing iPhone app come from the supplied private handover; no hardware check performed.
**Probed:** GitHub search and PHP inspection of florisvdk/parcelhome show a historical cloud API lead only.
**Hypothesis:** an existing keypad code may work in the numeric BLE opening field.
**Unknown:** credential equivalence, target revision, link permissions, full Android signing validity, offline onboarding.

D1 — verified/device: owner-approved service enumeration completed at
2026-09-25T18:59:03Z. Two services were returned; ParcelHome service and app RX/TX
UUIDs match E1/E7. Properties are recorded in ble-protocol.md. The tool disconnected
without error. Private capture: `.local/service-discovery/20260925T185903Z-88811a63d351498590d6a47ecbb9601a.json`.
No characteristic values, subscriptions or control commands were used. No claim
of successful app-level authentication or unlocking follows from this connection.


A2 — verified/local: Google apksig 9.4.1 accepts A1 under v1/v2; certificate matches
A1's recorded digest. A one-byte-mutated private copy fails with CHUNKED_SHA256 digest
mismatch. Logs: `.local/reports/apksig-verification.txt` and `apksig-tampered.txt`.
This is integrity evidence, not independent publisher identification.

E9 — verified/static: `BTCommandBuilder.smali:61` and `:86` use shift 0x0e for
payload type; `:367` starts buildOpenBox, including optional-field branches.
The `OPEN_BOX` enum value is 1. Zero optional inputs omit both fields.

E10 — verified/local synthetic reference: the inspected builder, ByteParser and
enum were compiled in `.local/reference/`. Explicit short casts repaired a JADX
compile issue in enum constants; BSON.SYMBOL=14 and an unused TagAuthorization
class were stubbed. Only buildOpenBox(code,0,0) and signed trailer parsing ran.
Five synthetic inputs were used, with random message ID bytes replaced with 123.
Output: `.local/reports/reference-vectors.txt`; public synthetic equivalents are
`tests/fixtures/opening-vectors.json`. This is not execution of the Android app.

E11 — verified/offline: 28 tests cover reference matching, parser bounds, malformed
and mismatched responses, consent, explicit target, exclusive attempt marker,
timeout/cancellation cleanup, and no repeat opening writes. No response capture
or successful opening result is claimed.


D2 — verified/device + owner report: explicitly approved opening write completed at
2026-09-25T19:14:26Z. Owner confirmed no opening. Two complete parsed replies, then
clean unsubscribe/disconnect. Private sanitised capture:
`.local/opening-results/20260925T191426Z-2332d8ab0ceb43fa9b7e2386be317913.json`.
No control retries or final application ACK sent; marker remains active.

E12 — verified/static: BTService.java:93 (`finalizeCommand`) builds its ACK using
the second received message's ID. HomeActivity.java:333 checks zero error status
for its opening-success path. This supports interpreting the observed nonzero
trailer as unsuccessful; the exact meaning of 2 is unknown. See opening-result-01.md.


E13 — verified/static: `BTCommandBuilder.buildGetAuthFixedCode` and smali method at
`BTCommandBuilder.smali:197` construct command 37 with the numeric code.
`FixedCodeAuth` enum values and `FixedCodeController.safeForNext` identify the
successful one-byte permission response. Permission 2 and D2 status 2 are different
fields and must not be conflated. `StatusBox.Builder.decode` provides the selected
status-field offsets. These findings support docs/diagnostic-plan.md.

E14 — verified/local synthetic reference: `.local/reference/ReferenceDiagnostics.java`
executed the inspected builder's GET_STATUS, GET_AUTH_FIXED_CODE("123456") and ACK
methods. Request IDs were replaced with 123/124; ACK used 16383. Results are private
in `.local/reports/diagnostic-reference-vectors.txt` and encoded as synthetic test
expectations in tests/test_diagnostics.py. No live diagnostic query was sent.
