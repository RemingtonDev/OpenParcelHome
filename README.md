# OpenParcelHome

Independent, community-led preservation of ParcelHome delivery boxes.
The goal is to let owners keep using their own hardware with a documented local
protocol and, eventually, an iPhone app. Not affiliated with or endorsed by ParcelHome.

**Research stage: this project cannot open a box yet.** No hardware compatibility
or cloud-independent recovery has been demonstrated. Existing keypad access
should be preserved throughout testing.

## What we have found

Static inspection of a myParcelHome 3.0.2 Android archive identified BLE service
and characteristic UUIDs and a command that carries a numeric opening code.
The original app obtains that code from a cloud API. Whether an existing keypad
code is accepted over BLE is **an untested hypothesis**, not a recovery procedure.
The archive's publisher authenticity and full Android signature verification are
still unresolved. See [feasibility](docs/feasibility.md) and
[artifact provenance](docs/artifact-provenance.md).

## Start here

- [Findings and next experiment](docs/feasibility.md)
- [Bluetooth observations](docs/ble-protocol.md)
- [Authentication and credentials](docs/authentication.md)
- [Evidence ledger](docs/evidence-ledger.md)
- [Tasks and recovery milestones](TASKS.md)
- [Contributing](CONTRIBUTING.md)

## Offline checks

Python 3.12 or newer; the offline tests need no third-party dependencies and do
not touch Bluetooth.

```sh
python3 -m unittest discover -s tests -v
# Optional, on a Mac: writes a private local environment report.
bash scripts/mac_preflight.sh
```

## Advertisement discovery (optional, owner enabled)

Read the [experiment plan](docs/safety-test-plan.md) first. Beside your own box:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-research.txt
.venv/bin/python scripts/scan_advertisements.py --confirm-owner-present --seconds 15
```

This collects advertisements, without a GATT connection, reads, subscriptions or
unlock commands. macOS uses active scanning and local peripheral UUIDs, so this
is not radio-passive capture and the identifiers are not portable to your phone.
The script reports only a count and file path. Raw captures may identify nearby
devices: they stay in ignored `.local/captures/` files with mode `0600`.
Do not post them publicly. Grant Bluetooth permission only to the actual host app.
A scan with no observations does not prove the box is faulty.

Bleak is pinned for the research helper; transitive dependencies remain platform
resolved. This is not yet a reproducibly locked end-user release.

## Roadmap

1. Establish artifact provenance and document protocol/credential requirements.
2. Identify the owner's box through approved discovery.
3. Implement and test offline protocol code, then one explicitly approved operation.
4. Demonstrate onboarding on a fresh client without the original cloud.
5. Build an iPhone client; consider Android, Home Assistant and Homey afterwards.

## Licence and privacy

Original project code and documentation are MIT licensed. The licence does not
cover vendor apps, firmware, decompiled source, trademarks or contributed third-party
materials. No vendor binaries or decompiled source are distributed here.
Never submit PINs, account tokens, device keys, phone backups or reusable unlock captures.
