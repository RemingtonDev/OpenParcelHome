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

No confirmed-device claims or live capture IDs exist yet.
