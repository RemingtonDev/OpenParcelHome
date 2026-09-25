import json
from pathlib import Path
import struct
import unittest
from openparcelhome.protocol import opening_frame, Reassembler


class ProtocolTests(unittest.TestCase):
    def test_matches_original_builder_reference_vectors(self):
        fixture = json.loads((Path(__file__).parent / 'fixtures/opening-vectors.json').read_text())
        self.assertEqual(len(fixture['vectors']), 5)
        for v in fixture['vectors']:
            with self.subTest(code=v['synthetic_code']):
                self.assertEqual(opening_frame(v['synthetic_code'], v['message_id']).hex(), v['frame_hex'])

    def test_reject_invalid_credentials_without_echo(self):
        for code in ['', ' 123', '-1', '1.2', '１２３', '2147483648', '0'*11, None]:
            with self.subTest(code=code), self.assertRaises(ValueError):
                opening_frame(code, 1)

    def test_message_id_range(self):
        for value in [-1,8190,16383,True,1.2]:
            with self.assertRaises(ValueError): opening_frame('123',value)
        self.assertEqual(opening_frame('123',8189)[2:4], b'\x1f\xfd')

    def test_message_header_and_signed_trailer(self):
        for status in [-32768,-1,0,1,32767]:
            message=Reassembler().feed(b'\x80\x00'+struct.pack('>Hh',0x407b,status))
            self.assertEqual(message.kind,1)
            self.assertEqual(message.summary(123)['trailing_signed_value'], status)
            self.assertTrue(message.summary(123)['matches_request'])
            self.assertFalse(message.summary(124)['matches_request'])

    def test_fragmentation_and_reset(self):
        parser=Reassembler()
        self.assertIsNone(parser.feed(b'\x00\x00\x40\x7b\x01'))
        message=parser.feed(b'\x81\x02\x00\x00')
        self.assertEqual(message.body,b'\x01\x02\x00\x00')
        self.assertIsNotNone(parser.feed(b'\x80\x00\x80\x7b'))

    def test_reject_malformed_frames(self):
        for raw in [b'',b'\x80',b'\x80\x00',b'\x80\x00\x01',b'\x81\x00\x00',b'\x80\x01\x00\x00',b'\x00'*21]:
            with self.subTest(raw=raw),self.assertRaises(ValueError): Reassembler().feed(raw)
        parser=Reassembler(); parser.feed(b'\x00\x00\x40\x01')
        with self.assertRaises(ValueError): parser.feed(b'\x82\x00\x00')

    def test_reply_bound_and_repr_redaction(self):
        parser=Reassembler()
        for i in range(14):
            parser.feed(bytes([i])+(b'\x00' if i==0 else b'')+b'x'*18)
        with self.assertRaises(ValueError): parser.feed(b'\x0e'+b'x'*18)
        message=Reassembler().feed(b'\x80\x00\x40\x01SECRET')
        self.assertNotIn('SECRET',repr(message))
        self.assertNotIn('SECRET',str(message.summary(1)))
