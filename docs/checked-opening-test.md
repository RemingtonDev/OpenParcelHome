# D4 — permission-checked, acknowledged opening

Prepared and offline-tested. No D4 radio operation has run yet.
The owner requested preparation of this revised test. Local confirmation below
approves one execution when the owner is beside the box.

Question: does one opening with the same code just confirmed as ALWAYS_OPEN work
when the complete response acknowledgement is sent? A failure still will not
establish the meaning of result 2. This does not test server-issued credentials.

1. Owner is beside the same empty, accessible box and verifies normal keypad
   access. Retain normal recovery access. Decline unexpected pairing prompts.
2. Enter `CHECK AND OPEN ONCE` in local Terminal, then enter the existing code in
   the hidden prompt. It is never saved, logged or supplied through chat, process
   arguments or environment variables. Python cannot guarantee memory erasure.
3. Reacquire the selected private target, connect once, verify service and TX/RX
   properties, and subscribe to notifications (a GATT descriptor write).
4. Reserve a durable D4 attempt marker before the permission request. Send command
   37, require its matching request ACK and valid response, then acknowledge the
   response's own ID. Proceed only on status zero and permission ALWAYS_OPEN.
5. Send at most one command 1 using the same in-memory code; optional log/time
   flags stay zero. Require the request ACK and response, acknowledge the response
   ID, then disconnect. Nonzero opening responses are also acknowledged but never
   retried. A timeout or malformed stream stops the batch.
6. Report physical opening and whether normal keypad access still works. Neither
   GATT write completion nor status zero establishes physical success.

Maximum four application writes: permission, response ACK, opening, response ACK.
No reset, provisioning, code synchronisation/change, clock update, log request,
firmware operation or cloud request. A rejected opening may affect an unknown
firmware lockout counter. This is one bounded experiment, not repeated guessing.
Discovery/connection/subscription limits: 12/20/5 seconds. Each request write:
5 seconds. Response-plus-ACK: 10 seconds. Unsubscribe/disconnect: 5 seconds each.

D4 uses `.local/checked-opening-attempts/` and saves sanitised summaries under
`.local/checked-opening-results/`. D2 and D3 guards are preserved. There is no
retry/reset switch; even an interrupted dispatch remains reserved.

Offline (no radio, no private input):

```sh
.venv/bin/python scripts/checked_open_once.py
```

In local interactive Terminal, with the above preconditions:

```sh
.venv/bin/python scripts/checked_open_once.py --execute \
  --target-file .local/reports/service-discovery-target.json
```

Verification: synthetic tests cover identical credential bytes in both commands,
ID wrap, response-ID acknowledgements, permission rejection, malformed and extra
notifications, partial frames, failed acknowledgement, exclusive reservation,
opening rejection, actual timeout cancellation, no retry, cleanup, hidden-input
failure and the offline default. No vendor app code or real credentials are used
in tests. The same encoder and diagnostic query implementation used in D2/D3 is
reused. Physical D4 behaviour remains unverified.
