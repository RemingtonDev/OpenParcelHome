# Cryptography and credential boundary

**Verified/static, bounded:** the inspected `buildOpenBox` method encodes the
numeric input directly into a big-endian integer. `BTService.writeToGatt` assigns
the resulting frame bytes to the characteristic before writing. No AES, HMAC or
signature step occurs in those inspected methods (E2, E6).

**Unknown:** firmware-side code verification; whether codes are derived from a
secret elsewhere; required BLE link security; whether other operations/revisions
use a different protocol. No conclusion about the security of deployed boxes can
be drawn from these methods alone. No cryptographic key has been recovered.

Owner-held keypad codes are a candidate credential to investigate, not proven BLE
credentials. Keep live codes outside the repository and agent-readable reports.
Future protocol tests must use explicit synthetic values.
