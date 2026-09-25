import asyncio
import contextlib
import io
import struct
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from openparcelhome.checked_opening import checked_open_once
from openparcelhome.diagnostics import acknowledgement_frame
from openparcelhome.protocol import SERVICE, TX, RX
from scripts import checked_open_once as cli

TARGET='00000000-0000-0000-0000-000000000001'

class CheckedOpeningTests(unittest.IsolatedAsyncioTestCase):
    async def batch(self, scenario='ok', permission=2, enabled=True):
        writes=[]; calls=[]
        async def finder(*args, **kwargs):
            calls.append('scan')
            return SimpleNamespace(address=TARGET)
        class Client:
            def __init__(self, device, timeout, pair):
                assert not pair
                self.services=SimpleNamespace(get_service=lambda u: SimpleNamespace(characteristics=[SimpleNamespace(uuid=TX,properties=['write']),SimpleNamespace(uuid=RX,properties=['notify'])]) if u==SERVICE else None)
            async def connect(self): calls.append('connect')
            async def disconnect(self): calls.append('disconnect')
            async def start_notify(self,char,callback): self.callback=callback
            async def stop_notify(self,char): calls.append('unsubscribe')
            async def write_gatt_char(self,char,frame,response):
                assert response and char.uuid==TX
                writes.append(frame)
                ident=int.from_bytes(frame[2:4],'big')
                if ident>>14==2:
                    if len(writes)==2:
                        if scenario=='ack-fail': raise TimeoutError('secret')
                        if scenario=='partial': self.callback(None,b'\x00\x00\x01')
                        if scenario=='extra': self.callback(None,b'\x80\x00\x80\x01')
                    return
                opcode=int.from_bytes(frame[4:6],'big')
                assert opcode in (37,1)
                if scenario=='hang' and opcode==1: await asyncio.Future()
                if scenario=='open-fail' and opcode==1: raise TimeoutError('secret')
                if scenario=='malformed': self.callback(None,b'\x80'); return
                self.callback(None,b'\x80\x00'+struct.pack('>H',0x8000 | (ident if scenario!='wrong-ack' else ident+1)))
                data=bytes([permission]) if opcode==37 else b''
                status=2 if (scenario=='open-rejected' and opcode==1) or (scenario=='permission-error' and opcode==37) else 0
                self.callback(None,b'\x80\x00'+struct.pack('>H',999)+data+struct.pack('>h',status))
        def reserve(target):
            calls.append('reserve')
            if scenario=='reserved': raise FileExistsError()
        result=await checked_open_once(TARGET,'123456',8189,finder,Client,reserve,enabled=enabled)
        return result,writes,calls

    async def test_same_code_one_open_and_own_response_acks(self):
        result,writes,calls=await self.batch()
        self.assertEqual(len(writes),4)
        self.assertEqual([int.from_bytes(writes[i][4:6],'big') for i in (0,2)],[37,1])
        self.assertEqual(writes[0][6:10],writes[2][6:10])
        self.assertEqual(writes[2][2:4],b'\x00\x00') # ID wrap
        self.assertEqual(writes[2][10:],b'\x00'*4) # no optional state changes
        self.assertEqual(writes[1],acknowledgement_frame(999))
        self.assertEqual(writes[3],acknowledgement_frame(999))
        self.assertTrue(result['opening_write_attempted'])
        self.assertEqual(result['outcome'],'unknown-check-physical-box')
        self.assertTrue(result['cleanup_ok'])
        self.assertNotIn('123456',str(result))
        self.assertEqual(calls[-2:],['unsubscribe','disconnect'])

    async def test_non_always_open_never_opens(self):
        for permission in (0,1,3,4):
            result,writes,_=await self.batch(permission=permission)
            self.assertFalse(result['opening_write_attempted'])
            self.assertLessEqual(len(writes),2)

    async def test_errors_before_open_fail_closed(self):
        for scenario in ('ack-fail','partial','extra','malformed','wrong-ack','permission-error','reserved'):
            result,writes,calls=await self.batch(scenario)
            self.assertFalse(result['opening_write_attempted'],scenario)
            self.assertLessEqual(len(writes),2)
            self.assertTrue(result['cleanup_ok'])
            self.assertNotIn('secret',str(result))

    async def test_rejected_open_acknowledged_without_retry(self):
        result,writes,_=await self.batch('open-rejected')
        self.assertEqual(len(writes),4)
        self.assertEqual(result['queries'][-1]['status'],2)
        self.assertEqual(result['outcome'],'unknown-check-physical-box')

    async def test_open_write_failure_unknown_no_retry(self):
        result,writes,_=await self.batch('open-fail')
        self.assertEqual(len(writes),3)
        self.assertTrue(result['opening_write_attempted'])
        self.assertEqual(result['outcome'],'unknown-check-physical-box')
        self.assertTrue(result['cleanup_ok'])

    async def test_enablement(self):
        with self.assertRaises(PermissionError): await self.batch(enabled=False)

    def test_offline_default(self):
        with patch.dict('sys.modules',{'bleak':None}),patch.object(cli.getpass,'getpass',side_effect=AssertionError()),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main([]),0)

    async def test_real_timeout_cancels_open_without_retry(self):
        real_wait=asyncio.wait_for
        async def bounded(awaitable,timeout):
            return await real_wait(awaitable,min(timeout,0.01))
        with patch('openparcelhome.checked_opening.asyncio.wait_for',side_effect=bounded):
            result,writes,calls=await self.batch('hang')
        self.assertEqual(len(writes),3)
        self.assertEqual(result['error_type'],'TimeoutError')
        self.assertEqual(calls[-2:],['unsubscribe','disconnect'])

    def test_existing_guard_blocks_before_private_prompt(self):
        with patch.object(cli.sys.stdin,'isatty',return_value=True),patch.object(cli,'load_target',return_value=TARGET),patch.object(cli,'attempt_path') as marker,patch('builtins.input',side_effect=AssertionError()),contextlib.redirect_stdout(io.StringIO()):
            marker.return_value.exists.return_value=True
            self.assertEqual(cli.main(['--execute','--target-file','unused']),1)

    def test_no_echo_failure_stops_before_ble(self):
        import getpass
        with patch.object(cli.sys.stdin,'isatty',return_value=True),patch.object(cli,'load_target',return_value=TARGET),patch.object(cli,'attempt_path') as marker,patch('builtins.input',return_value='CHECK AND OPEN ONCE'),patch.object(cli.getpass,'getpass',side_effect=getpass.GetPassWarning()),patch.dict('sys.modules',{'bleak':None}),contextlib.redirect_stdout(io.StringIO()):
            marker.return_value.exists.return_value=False
            self.assertEqual(cli.main(['--execute','--target-file','unused']),1)
