"""Single opening experiment; inject BLE and storage for offline verification."""
import asyncio
import hashlib
import os
from pathlib import Path
import uuid

from .protocol import SERVICE, TX, RX, Reassembler, opening_frame


def attempt_path(directory: Path, target: str):
    return directory / (hashlib.sha256(target.encode('ascii')).hexdigest() + '.attempt')


def reserve_attempt(directory: Path, target: str):
    """Durable guard: no second automatic/manual run until the attempt is reviewed."""
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(attempt_path(directory, target), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as out:
        out.write('Opening dispatch reserved. Outcome may be unknown. Review before any further attempt.\n')
        out.flush()
        os.fsync(out.fileno())


async def open_once(target, code, message_id, finder, client_factory, reserve,
                    *, enabled=False, observe=asyncio.sleep):
    if enabled is not True:
        raise PermissionError('Live execution not enabled')
    target = str(uuid.UUID(target)).upper()
    frame = opening_frame(code, message_id)  # Validate before radio access.
    device = await asyncio.wait_for(finder(target, timeout=10), 12)
    if device is None or str(uuid.UUID(device.address)).upper() != target:
        raise RuntimeError('Target unavailable or mismatched')
    client = client_factory(device, timeout=15, pair=False)
    parser = Reassembler()
    report = {'opening_write_attempted': False, 'opening_write_completed': False,
              'outcome': 'not-dispatched', 'notification_count': 0, 'messages': [],
              'unsupported_response': False, 'cleanup_ok': False}
    subscribed = False
    accepting = False

    def notified(sender, value):
        if not accepting:
            return
        report['notification_count'] += 1
        if report['notification_count'] > 32 or report['unsupported_response']:
            report['unsupported_response'] = True
            return
        try:
            message = parser.feed(bytes(value))
            if message is not None:
                report['messages'].append(message.summary(message_id))
        except (ValueError, TypeError):
            report['unsupported_response'] = True

    try:
        await asyncio.wait_for(client.connect(), 20)
        service = client.services.get_service(SERVICE)
        if service is None:
            raise RuntimeError('Expected service absent')
        chars = {c.uuid.lower(): c for c in service.characteristics}
        if TX not in chars or RX not in chars:
            raise RuntimeError('Expected characteristics absent')
        if 'write' not in chars[TX].properties or 'notify' not in chars[RX].properties:
            raise RuntimeError('Expected properties absent')
        await asyncio.wait_for(client.start_notify(chars[RX], notified), 5)
        subscribed = True
        reserve(target)  # Synchronous, exclusive, durable; before ANY opening write.
        report['opening_write_attempted'] = True
        report['outcome'] = 'unknown-check-physical-box'
        accepting = True
        await asyncio.wait_for(client.write_gatt_char(chars[TX], frame, response=True), 5)
        report['opening_write_completed'] = True
        await asyncio.wait_for(observe(5), 6)
        report['partial_response'] = bool(parser.buffer)
        # No ACK writes in this first experiment: response sequencing is unverified.
    except Exception as exc:
        report['error_type'] = type(exc).__name__  # Never include backend messages.
    finally:
        accepting = False
        cleanup_ok = True
        if subscribed:
            try:
                await asyncio.wait_for(client.stop_notify(chars[RX]), 5)
            except Exception:
                cleanup_ok = False
        try:
            await asyncio.wait_for(client.disconnect(), 5)
        except Exception:
            cleanup_ok = False
        report['cleanup_ok'] = cleanup_ok
    return report
