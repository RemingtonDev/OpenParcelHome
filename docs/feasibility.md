# Feasibility assessment — 2026-09-25

**Can an owner without the original app recover local access using an existing
keypad code? Unknown, with a specific hypothesis now supported by static evidence.**

Verified (static, archive authenticity unresolved): the inspected Android app
builds a BLE opening command containing a numeric code. The normal UI path gets
that code, a last-log identifier and a timestamp from a cloud response. The
inspected builder and GATT write path contain no extra app-layer encryption step.
This does not establish the device's permission checks or Bluetooth link security.

Hypothesis: an existing owner-held fixed/keypad code might also be accepted by the
BLE opening command. No code has been tested and no replacement client exists.
A server-issued receive code may have different privileges, lifetime or validation.
The firmware might reject fixed codes, require other state, or differ from the APK.

Probed: GitHub repository search for `parcelhome` returned
[florisvdk/parcelhome](https://github.com/florisvdk/parcelhome), a 2016 cloud API
example using api2.parcelhome.com. Its inspected PHP files have no Bluetooth path.
This bounded search does not prove that no community replacement exists.

The supplied owner context reports a ParcelHome 3 with working keypad access and
no recoverable original iPhone app. This has not been independently hardware-tested.

## Smallest next experiment

Approve a 15-second advertisement scan beside the box, then inspect only relevant
observations locally. The scan does not connect or open anything. Use proximity,
normal owner wake behaviour and the extracted Eddystone/service evidence together;
strong signal or a matching name alone is insufficient identification.

After target identification, separately approve one connection for service and
property enumeration. Review the result before subscriptions or any command. Before
an unlock experiment, finish signature checks, offline encoding/response tests and
review credential input, side effects, error handling and normal recovery access.
Never enter the owner's real code in chat or a command-line argument.

## Completion boundary

The GitHub research project is useful now. Restored access is not achieved until
an independent implementation succeeds on the actual box. Full offline recovery
also requires onboarding from a fresh client with original cloud infrastructure
unreachable. Neither outcome is demonstrated by this assessment.
