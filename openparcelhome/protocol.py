"""Narrow codec derived from A1; response semantics remain device-unverified."""
import struct
from dataclasses import dataclass, field

SERVICE = '5c640100-05f8-44de-8b2f-834e5c583db4'
TX = '5c640101-05f8-44de-8b2f-834e5c583db4'
RX = '5c640102-05f8-44de-8b2f-834e5c583db4'


def opening_frame(code: str, message_id: int) -> bytes:
    """One frame, no log-ID/time fields. Never log this return value."""
    if not isinstance(code, str) or not code or len(code) > 10 or not code.isascii() or not code.isdecimal():
        raise ValueError('Code must contain 1–10 ASCII digits')
    value = int(code)
    if value > 0x7fffffff:
        raise ValueError('Code is outside the app integer range')
    if type(message_id) is not int or not 0 <= message_id < 8190:
        raise ValueError('Message ID outside the app-generated range')
    # Frame header; type-0 payload/message ID; OPEN_BOX=1; code; flags=0.
    return struct.pack('>HHHII', 0x8000, message_id, 1, value, 0)


@dataclass(frozen=True)
class Message:
    kind: int
    message_id: int
    body: bytes = field(repr=False)

    def summary(self, expected_id):
        # Last two bytes are what the original parser treats as signed status.
        # Do not label status=0 as physical success; message kind is not proven.
        return {'kind': self.kind, 'matches_request': self.message_id == expected_id,
                'body_length': len(self.body),
                'trailing_signed_value': int.from_bytes(self.body[-2:], 'big', signed=True)
                if len(self.body) >= 2 else None}


class Reassembler:
    """Bounded frame parser. Reject malformed/out-of-order frames, never guess."""
    def __init__(self):
        self.next_index = 0
        self.buffer = bytearray()

    def feed(self, frame: bytes):
        if not 1 <= len(frame) <= 20:
            raise ValueError('Invalid notification length')
        final, index = bool(frame[0] & 0x80), frame[0] & 0x7f
        if index != self.next_index:
            raise ValueError('Out-of-order frame')
        offset = 2 if index == 0 else 1
        if len(frame) <= offset or (index == 0 and frame[1] != 0):
            raise ValueError('Unsupported frame header')
        self.buffer.extend(frame[offset:])
        if len(self.buffer) > 256 or index >= 15:
            raise ValueError('Response exceeds experiment bounds')
        self.next_index += 1
        if not final:
            return None
        if len(self.buffer) < 2:
            raise ValueError('Missing message header')
        header = int.from_bytes(self.buffer[:2], 'big')
        result = Message(header >> 14, header & 0x3fff, bytes(self.buffer[2:]))
        self.buffer.clear()
        self.next_index = 0
        return result
