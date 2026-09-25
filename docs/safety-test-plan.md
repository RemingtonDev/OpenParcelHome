# First physical experiment: advertisement discovery

**Status: prepared, not run.** Owner must be beside their own box and approve the
specific scan before an agent runs it. An owner manually invoking the documented
confirmation flag expresses approval for that scan only.

- Action: collect BLE advertisements for 15 seconds on the nearby Mac.
- Expected box change: none; scanner does not connect or issue GATT operations.
- Success signal: candidate observations consistent with the target using multiple
  signals. No observation is also a valid, inconclusive result.
- Private output: up to 512 devices' latest advertisements; identifiers and payloads
  remain in ignored `.local/captures/`. Review locally and discard unrelated data.
- Stop: denied permission, unexpected pairing prompt, abnormal box behaviour or
  loss of normal access. Do not retry automatically or reset to force advertising.

macOS scanning is active, not radio-passive. CoreBluetooth supplies Mac-local
identifiers rather than physical MAC addresses. See the official
[Bleak scanner](https://bleak.readthedocs.io/en/latest/api/scanner.html) and
[macOS backend](https://bleak.readthedocs.io/en/latest/backends/macos.html) docs.

Later connection/property discovery, specific reads/subscriptions, authentication,
and opening each require an explicit experiment plan and approval. Notifications
can cause descriptor writes. Never batch reset, provisioning, PIN synchronisation
or firmware updates into a recovery test. Keep the box empty and accessible for
any later approved actuation and retain normal owner recovery access.
