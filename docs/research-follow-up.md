# Public research and related APK comparison — 2026-09-25

## Assessment

We have working Bluetooth transport and a recognised fixed code, but no verified
opening credential/sequence. The original opening probe failed with trailer 2.
The successful permission query does not establish that OPEN_BOX accepts fixed
codes. No additional hardware experiment was performed for this assessment.

## Verified: related Android implementation

The [myRENZbox Homebox Google Play listing](https://play.google.com/store/apps/details?id=com.dao.homebox)
names Renz A/S and describes Bluetooth operation. A separately acquired
[APKPure archive](https://apkpure.net/homebox/com.dao.homebox/download) identifies
package `com.dao.homebox`, version 1.0.66, version code 190.

The downloaded base APK passes Android v2/v3 signature verification. This verifies
archive integrity under its included signer, not independent publisher authenticity.
The app was neither installed nor executed; no account or vendor API was used.

Static inspection of its native Android Bluetooth plugin establishes:

- Service, RX and TX UUIDs exactly match the original ParcelHome APK and D1 inventory.
- OPEN_BOX remains opcode 1, with the same big-endian numeric code, flags and
  optional last-log identifier and timestamp. No alternative fixed-code opening
  command was found in this inspected plugin.
- The Flutter-to-Android bridge passes code, last-log identifier and timestamp
  to that builder. Compiled Flutter strings include ParcelHome package names and
  receive-code network/model names; these strings alone do not establish the full
  Dart control flow or offline behaviour.
- The service acknowledges a completed response using that response's own message
  ID, as in the original app. D2 omitted this acknowledgement; D3 implemented it
  successfully for diagnostics. This is a protocol difference, not proof of why
  opening failed. The nonzero reply arrived before any such acknowledgement.
- No definition of opening result 2 was found in the inspected plugin. Its
  opening callback emits a success-named event even on its nonzero-error branch;
  a UI event from this archive therefore would not prove physical opening.

JADX reported 102 errors across the archive. The opening builder, acknowledgement
routine and opening callback above were crosschecked in Apktool smali. The Dart
application is compiled Flutter code and has not been fully reconstructed.

Reproducibility metadata:

| Item | SHA-256 |
| --- | --- |
| XAPK | `9dcce892abbaa08e1876a7bca2f6160d5fc597d31c3127c52089c1944b06e37f` |
| Base APK | `df43847a77388e975f5cace05266175339acf508973937dfb792a07c34409a39` |
| Base signer certificate | `f315b5d4efebe84cec5f02ec084da41623220e826208ff251990fd2a4df0c5b6` |

Evidence locations inside the inspected archive: plugin package
`com.embrace.dao.home.ble.homebox_ble.homebox_ble`, classes
`ble.BTCommandBuilder`, `ble.BTService`, `HomeboxBlePlugin` and `BLEUtils`.
Raw archives, extracted material and tool logs remain private under `.local/`.

## Probed: community and manufacturer material

- [florisvdk/parcelhome](https://github.com/florisvdk/parcelhome) contains an old
  cloud API example. Its inspected PHP files do not implement local BLE opening.
  Bounded GitHub repository/code searches found no verified local replacement
  beyond this project's work; this is not an exhaustive absence claim.
- [Circuits Online owner discussion](https://www.circuitsonline.net/forum/view/168323)
  includes a report that charging restored keypad operation. An earlier purported
  solution is no longer present in its posts, so it provides no reproducible
  Bluetooth recovery procedure. Our reference box already has working keypad access.
- The [manufacturer's Homebox datasheet](https://me-fa.dk/wp-content/uploads/2023/06/myRENZbox_Homebox_datasheet.pdf)
  distinguishes six-digit delivery codes lasting two minutes from fixed codes for
  keypad use. This is related-product documentation, not a specification of the
  reference ParcelHome 3 firmware.
- [ParcelHome's published lock design](https://patents.google.com/patent/US20150199857A1/en)
  describes time-dependent access codes using a per-box seed and corresponding
  server generation. It supplies architectural context, not the reference box's
  seed, a confirmed deployed algorithm, or an explanation of status 2.

## Hypotheses and next deciding evidence

1. **Credential distinction:** OPEN_BOX may require a time-dependent receive code
   rather than the fixed keypad code. The original app's cloud receive-code path
   and related-product documentation support investigating this. Fixed-code
   permission alone cannot settle it.
2. **Exchange completion:** acknowledging an opening response would match both
   inspected clients more closely. There is no evidence yet that acknowledging
   an already nonzero result would cause opening.
3. **Request context:** optional timestamp/log fields or preceding app activity may
   matter. Their presence in the builder does not establish that they are mandatory;
   guessed values or state-changing synchronisation are not warranted.

Best next step: trace the related client's compiled receive-code path and seek a
documented firmware result-code mapping or an owner-authorised successful app
exchange. These can distinguish credential rejection from missing context.
RENZ's shared protocol also makes its official support a relevant potential source
for compatibility/error-code documentation; compatibility is not established and
no contact has been made.

A further fixed-code opening experiment could remove two uncertainties by querying
permission and opening with the same in-memory input and completing the bounded
response acknowledgement. That would be a diagnostic experiment with uncertain
success, not a demonstrated fix. It requires a separate reviewed plan and owner
approval under the existing hardware-test rules. Existing retry guards remain.
No additional secret or hardware purchase is needed for the static investigation.
