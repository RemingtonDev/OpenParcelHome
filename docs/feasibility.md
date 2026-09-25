# Feasibility assessment — 2026-09-25

**Can an owner without the original app recover local access using an existing
keypad code? Unknown, with a specific hypothesis now supported by static evidence.**

Verified (static, archive authenticity unresolved): the inspected Android app
builds a BLE opening command containing a numeric code. The normal UI path gets
that code, a last-log identifier and a timestamp from a cloud response. The
inspected builder and GATT write path contain no extra app-layer encryption step.
This does not establish the device's permission checks or Bluetooth link security.

Hypothesis: an existing owner-held fixed/keypad code might also be accepted by the
BLE opening command. One owner-entered code was tried in an approved minimal BLE opening probe; it did
not open the box. This does not establish that all fixed-code paths are impossible.
A server-issued receive code may have different privileges, lifetime or validation.
The firmware might reject fixed codes, require other state, or differ from the APK.

Probed: GitHub repository search for `parcelhome` returned
[florisvdk/parcelhome](https://github.com/florisvdk/parcelhome), a 2016 cloud API
example using api2.parcelhome.com. Its inspected PHP files have no Bluetooth path.
This bounded search does not prove that no community replacement exists.

The supplied owner context reports a ParcelHome 3 with working keypad access and
no recoverable original iPhone app. This has not been independently hardware-tested.

## Smallest next experiment

The device service inventory now matches the app; Android v1/v2 signatures verify.
The codec matches five synthetic reference vectors and 28 offline tests pass.
The [first approved opening experiment](opening-result-01.md) has now run: one
write completed, two replies arrived, but the owner reported no opening. The
next step is to explain the nonzero response and credential/session requirements
before proposing any further live operation. The retry marker remains active.

## Completion boundary

The GitHub research project is useful now. Restored access is not achieved until
an independent implementation succeeds on the actual box. Full offline recovery
also requires onboarding from a fresh client with original cloud infrastructure
unreachable. Neither outcome is demonstrated by this assessment.

## Update after D1

Owner-approved discovery now confirms the service and communication UUIDs on the
selected nearby device. One connection and disconnection completed successfully,
without reading values, subscribing or sending control commands. This removes the
service-compatibility uncertainty for this candidate; numeric-code equivalence and
authorised command behaviour remain untested. Signature verification and offline protocol/response tests subsequently completed;
see the prepared opening experiment.
