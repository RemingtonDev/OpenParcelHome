import asyncio
import contextlib
import io
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import scan_advertisements as scan


class DiscoveryTests(unittest.TestCase):
    def test_missing_consent_never_imports_ble(self):
        with patch.dict('sys.modules', {'bleak': None}), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                scan.main([])
        self.assertEqual(raised.exception.code, 2)

    def test_duration_bounds(self):
        for value in ['0', '-1', '31', 'nan', 'inf']:
            with self.subTest(value=value), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    scan.arguments(['--confirm-owner-present', '--seconds', value])

    def test_scanner_only_and_cleanup_on_failure(self):
        calls = []
        class Scanner:
            def __init__(self, detection_callback):
                self.callback = detection_callback
            async def __aenter__(self):
                calls.append('start')
                self.callback(SimpleNamespace(address='synthetic-id'), SimpleNamespace(
                    local_name='synthetic', rssi=-40, service_uuids=['synthetic-service'],
                    manufacturer_data={1: b'\x01'}, service_data={}))
                return self
            async def __aexit__(self, *args):
                calls.append('stop')
        async def immediate(seconds):
            self.assertEqual(seconds, 15)
        records = asyncio.run(scan.collect(15, Scanner, immediate))
        self.assertEqual(calls, ['start', 'stop'])
        self.assertEqual(records[0]['manufacturer_data'], {'1': '01'})
        async def failure(seconds):
            raise RuntimeError('synthetic error')
        with self.assertRaises(RuntimeError):
            asyncio.run(scan.collect(15, Scanner, failure))
        self.assertEqual(calls, ['start', 'stop', 'start', 'stop'])
        # Fake exposes no connect/read/write/notify methods; such use would fail.

    def test_private_unique_capture(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder) / 'captures'
            path = scan.save_private([{'local_identifier': 'synthetic'}], directory)
            second = scan.save_private([], directory)
            self.assertNotEqual(path, second)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(json.loads(path.read_text())['schema_version'], 1)

    def test_invalid_duration_does_not_construct_scanner(self):
        with self.assertRaises(ValueError):
            asyncio.run(scan.collect(31, lambda **kwargs: self.fail('scanner started')))


if __name__ == '__main__':
    unittest.main()
