#!/usr/bin/env python3
"""Explicitly enabled advertisement discovery; no client or control operations."""
import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]


def duration(value):
    seconds = int(value)
    if not 1 <= seconds <= 30:
        raise argparse.ArgumentTypeError('seconds must be between 1 and 30')
    return seconds


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--confirm-owner-present', action='store_true',
                        help='approve this scan beside your own box')
    parser.add_argument('--seconds', type=duration, default=15)
    args = parser.parse_args(argv)
    if not args.confirm_owner_present:
        parser.error('scan requires --confirm-owner-present; Bluetooth was not started')
    return args


async def collect(seconds, scanner_factory, sleep=asyncio.sleep):
    if not isinstance(seconds, int) or not 1 <= seconds <= 30:
        raise ValueError('seconds must be between 1 and 30')
    observations = {}

    def observed(device, advertisement):
        # Bound memory; keep the latest advertisement for each local identifier.
        if device.address not in observations and len(observations) >= 512:
            return
        observations[device.address] = {
            'local_identifier': device.address,
            'local_name': advertisement.local_name,
            'rssi': advertisement.rssi,
            'service_uuids': list(advertisement.service_uuids),
            'manufacturer_data': {str(k): v.hex() for k, v in advertisement.manufacturer_data.items()},
            'service_data': {k: v.hex() for k, v in advertisement.service_data.items()},
        }

    async with scanner_factory(detection_callback=observed):
        await sleep(seconds)
    return list(observations.values())


def save_private(records, directory=None):
    directory = directory or ROOT / '.local' / 'captures'
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = directory / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
                        + '-' + uuid.uuid4().hex + '.json')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as handle:
        json.dump({'schema_version': 1, 'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
                   'observations': records}, handle, indent=2)
        handle.write('\n')
    return path


def main(argv=None):
    args = arguments(argv)  # Validate consent and duration before importing BLE.
    try:
        from bleak import BleakScanner
    except ImportError:
        print('Install requirements-research.txt in the project virtual environment.')
        return 1
    try:
        records = asyncio.run(collect(args.seconds, BleakScanner))
        path = save_private(records)
    except KeyboardInterrupt:
        print('Scan interrupted; no capture saved.')
        return 130
    except Exception as exc:
        # Backend error messages can contain device identifiers; do not print them.
        print(f'Scan failed ({type(exc).__name__}); check Bluetooth permission and radio state. No automatic retry.')
        return 1
    print(f'Saved {len(records)} device observations privately to {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
