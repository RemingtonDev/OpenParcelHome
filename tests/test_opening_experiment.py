import asyncio
import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from openparcelhome.experiment import open_once,reserve_attempt
from openparcelhome.protocol import SERVICE,TX,RX
from scripts import open_once as cli

TARGET='00000000-0000-0000-0000-000000000001'


class OpeningTests(unittest.IsolatedAsyncioTestCase):
    def harness(self, failure=None):
        calls=[]
        chars=[SimpleNamespace(uuid=TX,properties=['write']),SimpleNamespace(uuid=RX,properties=['notify'])]
        async def finder(target,timeout):
            calls.append('find')
            return SimpleNamespace(address=TARGET)
        async def observe(seconds):
            calls.append('observe')
            if failure=='observe': raise TimeoutError('sensitive backend detail')
        class Client:
            def __init__(self,device,timeout,pair):
                if pair: raise AssertionError('pairing requested')
                self.services=SimpleNamespace(get_service=lambda uuid: SimpleNamespace(characteristics=chars) if uuid==SERVICE and failure!='services' else None)
            async def connect(self):
                calls.append('connect')
                if failure=='connect': raise TimeoutError('sensitive backend detail')
            async def start_notify(self,char,callback):
                calls.append('subscribe'); self.callback=callback
                if failure=='subscribe': raise RuntimeError('sensitive backend detail')
            async def write_gatt_char(self,char,data,response):
                calls.append('write')
                if char.uuid!=TX or not response: raise AssertionError('incorrect characteristic or mode')
                if failure=='write': raise TimeoutError('sensitive backend detail')
                if failure=='hang-write': await asyncio.Future()
                if failure=='malformed':
                    self.callback(None, bytearray(b'\x80'))
                    return
                if failure=='mismatched':
                    self.callback(None, bytearray(b'\x80\x00\x40\x7c\x00\x00'))
                    return
                self.callback(None, bytearray(b'\x80\x00\x40\x7b\x00\x00'))
            async def stop_notify(self,char):
                calls.append('unsubscribe')
                if failure=='unsubscribe': raise RuntimeError('sensitive backend detail')
            async def disconnect(self):
                calls.append('disconnect')
                if failure=='disconnect': raise RuntimeError('sensitive backend detail')
        def reserve(target):
            calls.append('reserve')
            if failure=='reserve': raise FileExistsError('prior attempt')
        return calls,finder,Client,reserve,observe

    async def test_disabled_never_touches_radio(self):
        h=self.harness()
        with self.assertRaises(PermissionError):
            await open_once(TARGET,'123456',123,*h[1:4])
        self.assertEqual(h[0],[])

    async def test_one_write_and_never_claim_physical_success(self):
        calls,finder,client,reserve,observe=self.harness()
        result=await open_once(TARGET,'123456',123,finder,client,reserve,enabled=True,observe=observe)
        self.assertEqual(calls,['find','connect','subscribe','reserve','write','observe','unsubscribe','disconnect'])
        self.assertEqual(result['outcome'],'unknown-check-physical-box')
        self.assertEqual(len(result['messages']),1)
        self.assertNotIn('123456',json.dumps(result))
        self.assertTrue(result['cleanup_ok'])

    async def test_failures_never_repeat_write_and_always_disconnect(self):
        for failure in ['connect','services','subscribe','reserve','write','observe','unsubscribe','disconnect']:
            with self.subTest(failure=failure):
                calls,finder,client,reserve,observe=self.harness(failure)
                result=await open_once(TARGET,'123456',123,finder,client,reserve,enabled=True,observe=observe)
                self.assertEqual(calls.count('write'),0 if failure in ['connect','services','subscribe','reserve'] else 1)
                self.assertEqual(calls[-1],'disconnect')
                self.assertNotIn('sensitive',json.dumps(result))
                if failure in ['unsubscribe','disconnect']: self.assertFalse(result['cleanup_ok'])
                if failure=='write': self.assertTrue(result['opening_write_attempted'])

    async def test_invalid_code_and_wrong_target_prevent_write(self):
        calls,finder,client,reserve,observe=self.harness()
        with self.assertRaises(ValueError):
            await open_once(TARGET,'bad',123,finder,client,reserve,enabled=True)
        self.assertEqual(calls,[])
        async def wrong(*args,**kwargs): return SimpleNamespace(address='00000000-0000-0000-0000-000000000002')
        with self.assertRaises(RuntimeError):
            await open_once(TARGET,'123456',123,wrong,client,reserve,enabled=True)
        self.assertEqual(calls,[])

    async def test_actual_timeout_cancels_write_without_retry(self):
        calls,finder,client,reserve,observe=self.harness('hang-write')
        real_wait_for=asyncio.wait_for
        async def short_wait(awaitable,timeout):
            return await real_wait_for(awaitable,min(timeout,0.01))
        with patch('openparcelhome.experiment.asyncio.wait_for',side_effect=short_wait):
            result=await open_once(TARGET,'123456',123,finder,client,reserve,enabled=True,observe=observe)
        self.assertEqual(calls.count('write'),1)
        self.assertEqual(calls[-2:],['unsubscribe','disconnect'])
        self.assertEqual(result['error_type'],'TimeoutError')
        self.assertEqual(result['outcome'],'unknown-check-physical-box')

    async def test_malformed_and_mismatched_responses_do_not_trigger_writes(self):
        for failure in ['malformed','mismatched']:
            calls,finder,client,reserve,observe=self.harness(failure)
            result=await open_once(TARGET,'123456',123,finder,client,reserve,enabled=True,observe=observe)
            self.assertEqual(calls.count('write'),1)
            self.assertEqual(result['outcome'],'unknown-check-physical-box')
            if failure=='malformed': self.assertTrue(result['unsupported_response'])
            else: self.assertFalse(result['messages'][0]['matches_request'])

    async def test_cancellation_cleanup(self):
        calls,finder,client,reserve,observe=self.harness()
        async def cancel(seconds): raise asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await open_once(TARGET,'123456',123,finder,client,reserve,enabled=True,observe=cancel)
        self.assertEqual(calls.count('write'),1)
        self.assertEqual(calls[-2:],['unsubscribe','disconnect'])


class GuardTests(unittest.TestCase):
    def test_durable_attempt_excludes_second_dispatch(self):
        with tempfile.TemporaryDirectory() as folder:
            reserve_attempt(Path(folder),TARGET)
            with self.assertRaises(FileExistsError): reserve_attempt(Path(folder),TARGET)
            data=next(Path(folder).iterdir()).read_text()
            self.assertNotIn(TARGET,data)

    def test_default_is_offline_and_never_prompts(self):
        with patch.dict('sys.modules',{'bleak':None}),patch.object(cli.getpass,'getpass',side_effect=AssertionError('prompted')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main([]),0)

    def test_missing_target_or_noninteractive_blocks_before_prompt(self):
        for args in [['--execute'],['--execute','--target-file','missing']]:
            with patch.object(cli.sys.stdin,'isatty',return_value=False),contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit): cli.main(args)

    def test_confirmation_cancel_does_not_request_code(self):
        with patch.object(cli.sys.stdin,'isatty',return_value=True),patch.object(cli,'load_target',return_value=TARGET),patch('builtins.input',return_value='no'),patch.object(cli.getpass,'getpass',side_effect=AssertionError('prompted')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(['--execute','--target-file','synthetic']),1)

    def test_existing_attempt_blocks_before_prompt(self):
        with patch.object(cli.sys.stdin,'isatty',return_value=True),patch.object(cli,'load_target',return_value=TARGET),patch.object(cli,'attempt_path',return_value=SimpleNamespace(exists=lambda:True)),patch('builtins.input',side_effect=AssertionError('prompted')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(['--execute','--target-file','synthetic']),1)

    def test_non_echo_input_unavailable_aborts_before_ble(self):
        import warnings
        def unsafe_prompt(*args):
            warnings.warn('synthetic no-echo failure',cli.getpass.GetPassWarning)
            raise AssertionError('warning should have aborted input')
        with patch.object(cli.sys.stdin,'isatty',return_value=True),patch.object(cli,'load_target',return_value=TARGET),patch('builtins.input',return_value='OPEN ONCE'),patch.object(cli.getpass,'getpass',side_effect=unsafe_prompt),patch.dict('sys.modules',{'bleak':None}),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(['--execute','--target-file','synthetic']),1)
