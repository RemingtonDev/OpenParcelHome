# Draft enquiry to RENZ — not sent

To: info@renzgroup.dk

Subject: Existing ParcelHome 3 compatibility with myRENZbox Homebox

Hello,

I own a ParcelHome 3 in Belgium. Its existing keypad access works, but I would
like to restore app access. Your MEFA Homebox product page describes ParcelHome
Technology, and the hardware appears identical to my box.

Can you confirm:

1. Can an existing ParcelHome 3 be registered with your current Homebox service
   for an owner in Belgium, while preserving its existing keypad codes? What
   information, fees or hardware/firmware requirements would apply?
2. Does Bluetooth OPEN_BOX (command 1) accept an existing fixed keypad code, or
   does it require a server-generated receive code? What does result code 2 mean?
3. Is there documentation or an owner-supported route for local opening without
   dependence on the original ParcelHome cloud?

For context, owner-authorised diagnostics succeeded: GET_STATUS returned success,
and GET_AUTH_FIXED_CODE (command 37) returned ALWAYS_OPEN for an existing code.
A single Bluetooth opening attempt returned result 2 and did not open the box.
Normal keypad access still works. No reset or configuration changes were made.

I am documenting an independent open-source preservation project:
https://github.com/RemingtonDev/OpenParcelHome

Thank you,
Julien

---

Source for contact and product relationship:
[MEFA Homebox product page](https://me-fa.dk/produkt/myrenzbox-homebox-paa-fod-sort/).
This initial enquiry contains no PIN, device identifier or account credentials.
