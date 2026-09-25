# D3 proposal — status and fixed-code permission query

**Completed under explicit approval.** Both queries succeeded; see
[the D3 results](diagnostic-result-01.md). No opening command was included.
The diagnostic retry guard is active; the plan below records the approved scope.

## Question and deciding test

Does the box accept ordinary status requests, and does it recognise the owner's
working keypad code as a fixed code with a permission? This could distinguish a
general protocol/session issue from a credential-role restriction. It cannot prove
why D2 returned result 2, nor prove that an acknowledged opening would work.

Verified/static in A1:
- `BTCommandBuilder.buildGetStatus` encodes command 0 without credentials.
- `buildGetAuthFixedCode` encodes command 37 and a numeric code.
- `FixedCodeController.safeForNext` interprets the first response-data byte as the
  fixed-code permission; `FixedCodeAuth` maps 0/1/2/3 to none/open-if-empty/always-open/
  single-open. The permission value 2 is NOT the same field as D2's error/status 2.
- `BTService.finalizeCommand` acknowledges the response's own message ID.
- `StatusBox.Builder.decode` reads door state at data byte 2 and firmware integer
  at data offsets 15..18. Other data, including box identifiers, will not be logged.

The minimal query and ACK encodings were executed in the private synthetic Java
reference harness and match the Python implementation. These are intended query
operations according to app code, not a guarantee that unknown firmware has no
side effects. No permission is changed by the proposed command construction.

## Proposed batch for one approval

1. On the same identified box, enter `DIAGNOSE ONCE` in the local Terminal, then
   the existing working code into the hidden prompt. No PIN in chat, arguments,
   environment variables or saved files. It stays in process memory for this batch.
2. Reacquire the exact local identifier, connect once, verify known characteristics
   and subscribe to RX notifications. Subscription changes the GATT descriptor.
3. Send one GET_STATUS. Require a matching request ACK and a complete type-0 reply.
   Acknowledge that reply's own ID. If status is nonzero or framing is unexpected,
   stop without sending the code-permission query.
4. Otherwise send one GET_AUTH_FIXED_CODE for the supplied code and acknowledge its
   reply. Interpret a permission only if the status is zero and the data is exactly
   one supported byte. Do not reproduce the original app's synchronisation fallback,
   which can change codes; this runner has no such commands.
5. Unsubscribe and disconnect. Save only status codes, returned permission, door-state
   flag, firmware integer and cleanup outcome. Owner confirms normal keypad access.

Maximum four application writes: two requests and two acknowledgements. No opening,
reset, provisioning, code change, clock update or cloud operation. No automatic
retry. A separate diagnostic attempt marker prevents redispatch; the existing
opening-attempt marker is not removed or altered. Stop for an unexpected pairing
prompt, timeout, malformed reply or abnormal box behaviour.

Discovery/connection/subscribe timeouts are 12/20/5 seconds, each request write is
limited to 5 seconds, each reply-plus-ACK stage to 10 seconds, cleanup to 5 seconds
per operation. A timeout leaves results inconclusive and does not trigger retries.

## Commands

Offline default (no radio or real input):

```sh
.venv/bin/python scripts/diagnose_box.py
```

Only after explicit approval for this batch, in a local interactive Terminal:

```sh
.venv/bin/python scripts/diagnose_box.py --execute \
  --target-file .local/reports/service-discovery-target.json
```

The agent can launch the Terminal, monitor sanitised results and interpret the
batch; the owner need only enter the code privately and observe normal operation.
No ongoing unrestricted testing or repeated opening attempts are implied.

## Validation

36 offline tests pass. Eight diagnostic tests cover original-builder vectors,
permission semantics, invalid inputs, offline default, exact maximum writes,
response IDs distinct from request IDs, stop on status error, malformed replies,
wrong ACK, write failure, enablement and cleanup. Earlier opening and discovery
safety tests also remain green. D3 subsequently confirmed this query/acknowledgement sequence on the owner's box.
