#!/usr/bin/env python3
"""One explicitly approved connection for service metadata only."""
import argparse
import asyncio
import json
from pathlib import Path
import uuid

try:
    from .scan_advertisements import save_private
except ImportError:
    from scan_advertisements import save_private

ROOT = Path(__file__).resolve().parents[1]


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-file', required=True, type=Path,
                        help='private JSON file containing local_identifier')
    parser.add_argument('--confirm-service-discovery', action='store_true')
    args = parser.parse_args(argv)
    if not args.confirm_service_discovery:
        parser.error('explicit approval required; Bluetooth was not started')
    return args


def load_target(path):
    data = json.loads(path.read_text())
    identifier = data['local_identifier']
    # This initial utility deliberately supports only Mac-local UUID targets.
    return str(uuid.UUID(identifier)).upper()


async def discover(target, finder, client_factory):
    device = await asyncio.wait_for(finder(target, timeout=10), timeout=12)
    if device is None:
        raise RuntimeError('Target not found; no connection attempted')
    if str(uuid.UUID(device.address)).upper() != target:
        raise RuntimeError('Discovered target mismatch; no connection attempted')
    client = client_factory(device, timeout=15, pair=False)
    try:
        await asyncio.wait_for(client.connect(), timeout=20)
        services = []
        for service in client.services:
            services.append({
                'uuid': service.uuid,
                'characteristics': [
                    {'uuid': characteristic.uuid,
                     'properties': list(characteristic.properties),
                     'descriptors': [{'uuid': d.uuid, 'handle': d.handle}
                                     for d in characteristic.descriptors]}
                    for characteristic in service.characteristics],
            })
        return services
    finally:
        # One attempt only. Also clean up a partially completed connection.
        await asyncio.wait_for(client.disconnect(), timeout=5)


def main(argv=None):
    args = arguments(argv)
    try:
        target = load_target(args.target_file)
        from bleak import BleakClient, BleakScanner
        services = asyncio.run(discover(target, BleakScanner.find_device_by_address, BleakClient))
        path = save_private(services, ROOT / '.local' / 'service-discovery')
    except KeyboardInterrupt:
        print('Service discovery interrupted. No automatic retry.')
        return 130
    except Exception as exc:
        print(f'Service discovery failed ({type(exc).__name__}). No automatic retry; check normal keypad access.')
        return 1
    print(f'Saved {len(services)} service definitions privately to {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
