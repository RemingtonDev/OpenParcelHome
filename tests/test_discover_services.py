import asyncio
import contextlib
import io
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import discover_services as discovery

TARGET = '00000000-0000-0000-0000-000000000001'


class ServiceDiscoveryTests(unittest.TestCase):
    def test_requires_approval_before_target_read_or_ble_import(self):
        with patch.object(discovery, 'load_target', side_effect=AssertionError('read target')), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                discovery.main(['--target-file', 'nonexistent'])
        self.assertEqual(raised.exception.code, 2)

    def test_no_connection_when_missing_or_wrong_target(self):
        async def missing(*args, **kwargs):
            return None
        async def wrong(*args, **kwargs):
            return SimpleNamespace(address='00000000-0000-0000-0000-000000000002')
        for finder in [missing, wrong]:
            with self.assertRaises(RuntimeError):
                asyncio.run(discovery.discover(TARGET, finder, lambda *a, **k: self.fail('client constructed')))

    def test_one_connection_metadata_only_and_cleanup(self):
        calls = []
        device = SimpleNamespace(address=TARGET)
        async def finder(target, timeout):
            self.assertEqual(target, TARGET)
            return device
        class Client:
            def __init__(self, found, timeout, pair):
                self_test.assertIs(found, device)
                self_test.assertFalse(pair)
                self.services = [SimpleNamespace(uuid='synthetic-service', characteristics=[
                    SimpleNamespace(uuid='synthetic-characteristic', properties=['write'], descriptors=[])])]
            async def connect(self):
                calls.append('connect')
            async def disconnect(self):
                calls.append('disconnect')
        self_test = self
        result = asyncio.run(discovery.discover(TARGET, finder, Client))
        self.assertEqual(calls, ['connect', 'disconnect'])
        self.assertEqual(result[0]['uuid'], 'synthetic-service')
        # This fake deliberately provides no read/write/notify/pair methods.
        class FailedClient(Client):
            async def connect(self):
                calls.append('failed-connect')
                raise TimeoutError('synthetic')
        with self.assertRaises(TimeoutError):
            asyncio.run(discovery.discover(TARGET, finder, FailedClient))
        self.assertEqual(calls[-2:], ['failed-connect', 'disconnect'])
