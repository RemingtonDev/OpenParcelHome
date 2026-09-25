import asyncio
import contextlib
import io
import struct
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from openparcelhome import diagnostics as d
from openparcelhome.protocol import Message,SERVICE,TX,RX
from scripts import diagnose_box

TARGET='00000000-0000-0000-0000-000000000001'

class CodecTests(unittest.TestCase):
    def test_original_builder_vectors(self):
        # Synthetic original-builder outputs; see local reference provenance.
        self.assertEqual(d.status_frame(123).hex(),'8000007b0000')
        self.assertEqual(d.permission_frame('123456',124).hex(),'8000007c00250001e240')
        self.assertEqual(d.acknowledgement_frame(16383).hex(),'8000bfff')

    def test_bad_inputs(self):
        for code in ['','-1',' 123','１２３','2147483648',None]:
            with self.assertRaises(ValueError): d.permission_frame(code,1)
        for ident in [-1,8190,True]:
            with self.assertRaises(ValueError): d.status_frame(ident)
        for ident in [-1,16384,True]:
            with self.assertRaises(ValueError): d.acknowledgement_frame(ident)

    def test_response_meanings_only_on_success(self):
        for n,label in enumerate(['none','open-if-empty','always-open','single-open']):
            self.assertEqual(d.summarise('permissions',Message(0,1,bytes([n,0,0])))['permission'],label)
        self.assertNotIn('permission',d.summarise('permissions',Message(0,1,b'\x00\x02')))
        with self.assertRaises(ValueError): d.summarise('permissions',Message(0,1,b'\x04\x00\x00'))
        with self.assertRaises(ValueError): d.summarise('status',Message(0,1,b'\x00\x00'))

    def test_default_has_no_radio_or_secret_prompt(self):
        with patch.dict('sys.modules',{'bleak':None}),patch.object(diagnose_box.getpass,'getpass',side_effect=AssertionError('prompted')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(diagnose_box.main([]),0)


class BatchTests(unittest.IsolatedAsyncioTestCase):
    async def run_batch(self,scenario='ok',enabled=True):
        calls=[]; writes=[]
        async def finder(*args,**kwargs):
            calls.append('scan'); return SimpleNamespace(address=TARGET)
        class Client:
            def __init__(self,device,timeout,pair):
                if pair: raise AssertionError()
                self.services=SimpleNamespace(get_service=lambda u:SimpleNamespace(characteristics=[SimpleNamespace(uuid=TX,properties=['write']),SimpleNamespace(uuid=RX,properties=['notify'])]) if u==SERVICE else None)
            async def connect(self): calls.append('connect')
            async def disconnect(self): calls.append('disconnect')
            async def start_notify(self,char,callback): self.callback=callback; calls.append('subscribe')
            async def stop_notify(self,char): calls.append('unsubscribe')
            async def write_gatt_char(self,char,frame,response):
                writes.append(frame)
                if not response or char.uuid!=TX: raise AssertionError()
                ident=int.from_bytes(frame[2:4],'big')
                if ident>>14==2: return  # App ACK requires no additional reply.
                operation=int.from_bytes(frame[4:6],'big')
                if operation not in [0,37]: raise AssertionError('unsafe opcode')
                if scenario=='write-failure': raise TimeoutError('private detail')
                if scenario=='malformed': self.callback(None,b'\x80'); return
                ackid=ident if scenario!='wrong-ack' else (ident+1)%8190
                self.callback(None,b'\x80\x00'+struct.pack('>H',0x8000|ackid))
                payload=(b'\x00\x00\x01' if operation==0 else b'\x02')+b'\x00\x00'
                if scenario=='status-error': payload=b'\x00\x02'
                # Separate response ID as observed in D2.
                self.callback(None,b'\x80\x00'+struct.pack('>H',999)+payload)
        def reserve(target): calls.append('reserve')
        result=await d.diagnose(TARGET,'123456',123,finder,Client,reserve,enabled=enabled)
        return result,calls,writes

    async def test_only_two_queries_and_two_acks(self):
        result,calls,writes=await self.run_batch()
        self.assertEqual(len(writes),4)
        self.assertEqual([int.from_bytes(writes[i][4:6],'big') for i in [0,2]],[0,37])
        self.assertEqual(writes[1],d.acknowledgement_frame(999))
        self.assertEqual(writes[3],d.acknowledgement_frame(999))
        self.assertTrue(result['cleanup_ok'])
        self.assertEqual(result['queries'][1]['permission'],'always-open')
        self.assertNotIn('123456',str(result))
        self.assertEqual(calls[-2:],['unsubscribe','disconnect'])

    async def test_status_error_stops_before_permission_query(self):
        result,calls,writes=await self.run_batch('status-error')
        self.assertEqual(len(writes),2)
        self.assertEqual(len(result['queries']),1)
        self.assertEqual(result['queries'][0]['status'],2)

    async def test_malformed_wrong_ack_write_error_stop_without_retry(self):
        for scenario in ['malformed','wrong-ack','write-failure']:
            result,calls,writes=await self.run_batch(scenario)
            self.assertEqual(len(writes),1)
            self.assertIn('error_type',result)
            self.assertNotIn('private detail',str(result))
            self.assertEqual(calls[-2:],['unsubscribe','disconnect'])

    async def test_enable_gate(self):
        with self.assertRaises(PermissionError): await self.run_batch(enabled=False)
