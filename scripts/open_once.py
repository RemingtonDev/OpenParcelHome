#!/usr/bin/env python3
"""Prepared experiment only. Default is offline; no real code in arguments/files."""
import argparse
import asyncio
import getpass
import json
from pathlib import Path
import secrets
import sys
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from openparcelhome.experiment import open_once, reserve_attempt, attempt_path
from openparcelhome.protocol import opening_frame
from scripts.discover_services import load_target
from scripts.scan_advertisements import save_private


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--target-file', type=Path)
    args = parser.parse_args(argv)
    if not args.execute:
        opening_frame('123456', 123)  # Explicitly synthetic; not an owner credential.
        print('Offline check passed. No Bluetooth access or real code requested.')
        return 0
    if args.target_file is None:
        parser.error('--execute requires an explicit --target-file')
    if not sys.stdin.isatty():
        parser.error('Use a local interactive Terminal; do not pipe credentials')
    print('This may OPEN your box once. Keep it empty and accessible. No automatic retries.')
    print('This tests whether your existing keypad code also works over Bluetooth; that is unproven.')
    print('Decline unexpected pairing prompts. Do not proceed without owner approval for this experiment.')
    try:
        target = load_target(args.target_file)
        if attempt_path(ROOT / '.local' / 'opening-attempts', target).exists():
            print('A previous attempt requires review. Bluetooth was not started.')
            return 1
        if input('Type OPEN ONCE to confirm this attempt: ') != 'OPEN ONCE':
            print('Cancelled; Bluetooth was not started.')
            return 1
        # Refuse getpass fallback to echoed input.
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            code = getpass.getpass('Existing keypad code (hidden; never saved): ')
        opening_frame(code, 0)
        from bleak import BleakClient, BleakScanner
        report = asyncio.run(open_once(target, code, secrets.randbelow(8190),
            BleakScanner.find_device_by_address, BleakClient,
            lambda selected: reserve_attempt(ROOT / '.local' / 'opening-attempts', selected),
            enabled=True))
        del code
        path = save_private([report], ROOT / '.local' / 'opening-results')
        print(json.dumps(report, indent=2))
        print(f'Sanitised result saved to {path}')
        print('Check the physical door and normal keypad access. Do not repeat an uncertain attempt.')
        return 0 if report['opening_write_completed'] and report['cleanup_ok'] else 1
    except KeyboardInterrupt:
        print('Interrupted; outcome may be unknown. Check the box. Do not retry.')
        return 130
    except Exception as exc:
        print(f'Experiment stopped ({type(exc).__name__}); no automatic retry. No code is logged.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
