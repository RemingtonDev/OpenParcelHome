# First opening experiment — completed; no opening

The owner approved this plan and the single attempt completed without opening the
box. See [D2 results](opening-result-01.md). Do not rerun it; the attempt marker remains
active. The following records the original reviewed plan.

## Reviewed preconditions

The Android archive passes Google's apksig 9.4.1 verifier (v1 and v2), and a
one-byte-tampered copy is rejected. Publisher identity has not been independently
confirmed against an owner's original installed app. The physical candidate's
service and communication UUIDs match the app, and the owner confirmed normal
keypad access after service discovery.

The proposed test asks one specific question: **does this box accept the owner's
existing keypad code in the app's BLE opening-code field?** That remains unproven.
A rejection might affect an unknown firmware lockout counter, so do not guess codes
or retry. A successful write alone does not mean that the door opened.

## Exact proposed actions

1. Owner is beside the same empty, accessible box with normal recovery access.
   Confirm that the existing code works; no need to share it with the agent.
2. In local Terminal, enter `OPEN ONCE`, then the code into a hidden prompt.
   The code is not an argument, environment variable, file or log. No credential
   is requested for the default offline check. Python does not guarantee memory
   erasure; close the process after the attempt.
3. Reacquire the explicitly selected Mac-local identifier for up to 10 seconds.
   Connect once and check the exact known service, write and notify properties.
4. Subscribe to the known RX notifications. This writes its subscription descriptor.
5. Persist an exclusive attempt marker, then issue exactly one 14-byte opening
   frame to the known TX characteristic, using a GATT write with response.
   The frame contains the supplied code; optional log and timestamp flags are zero.
6. Listen for five seconds; unsubscribe and disconnect. The original app has an
   acknowledgement path, but response ordering has not been device-verified here.
   This first experiment sends **no application-level ACK or follow-up packet**.
   This could leave a response unacknowledged before disconnect; it is a bounded
   opening probe, not a complete implementation of the original session protocol.
7. Owner reports actual door movement and confirms normal keypad access afterwards.
   A matching response, a zero trailer or a successful GATT write is insufficient
   proof of physical opening.

Timeout limits: discovery 12 seconds overall, connection 20, subscription 5,
write 5, observation 6, unsubscribe 5 and disconnect 5. No automatic retry.
Decline any unexpected pairing prompt. Interrupt for unusual behaviour or loss of
normal access; a timeout/interruption after dispatch has an **unknown outcome**.

No reset, provisioning, PIN synchronisation, firmware update, clock update, log
request, cloud request or extra write characteristic is included.

## Launch only after explicit approval

From the repository, this command is always offline:

```sh
.venv/bin/python scripts/open_once.py
```

After approval for the above experiment, the owner can run this in a local Terminal:

```sh
.venv/bin/python scripts/open_once.py --execute \
  --target-file .local/reports/service-discovery-target.json
```

Do not enter the real code in chat or through an agent tool. The target file was
selected from the private discovery captures and is not distributed on GitHub.
The process has exited. No radio operation is started by merely opening this document.

A private attempt marker blocks subsequent dispatch. The CLI also checks it before
asking for credentials or scanning. There is deliberately no retry/reset flag.
Review physical outcome and the sanitised result before any later authorised test;
never delete a marker just to make an uncertain attempt run again.

## Evidence and remaining limitations

28 offline tests pass: reference encoder vectors, malformed frames, signed trailer
handling, frame order/limits, wrong target, missing service, consent, no-echo input
policy, exclusive attempts, one-write dispatch, actual async timeout cancellation,
cleanup, malformed/mismatched notifications and no physical-success inference.

Five synthetic encoder vectors were produced by compiling the inspected Java
builder locally. Its enum required explicit short casts to compile; two unrelated
imports were stubbed, and only the generated message ID was replaced with 123.
No Android app process or BLE transport was run. The Python encoder independently
matches the resulting bytes. The real APK/Java output stays private.

Response frames in tests are synthetic structural cases, not vendor captures.
Type values and a signed trailing field are exposed only as observations; error-code
meaning and request/response sequencing remain unverified. Unsupported frames stop
parsing, never trigger writes, and never cause an opening retry. Only summaries
are retained; raw notifications and the supplied credential are not logged.

An accepted fixed code would establish a useful local route for this box and code
role, not general owner administration or universal compatibility. Fresh-client
no-cloud recovery and a maintained iPhone app remain later milestones.
