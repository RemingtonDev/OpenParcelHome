# Research environment — 2026-09-25

Verified locally: macOS 27.0 (26A428), native arm64, 18 GiB memory;
Python 3.14.7; Git 2.54.0; Homebrew 7.0.2; Apple Command Line Tools available.
No supplied starter files were present in the workspace; helpers were written here.

Installed JADX 1.5.6 and Apktool 3.0.3 through existing Homebrew. Homebrew added
OpenJDK 27 and upgraded dependency formulae glib to 2.90.0 and harfbuzz to 14.5.0.
No global Python, shell profile or JAVA_HOME changes. A project `.venv` contains
Bleak 3.0.2 and PyObjC 12.2.2 components; exact resolved versions are kept privately
in `.local/reports/python-resolved.txt`.

Apktool decoding exited 0. JADX exited 3 with 84 reported decompilation errors;
its output is partial, and critical encoding was cross-checked in smali. No claim
of complete decompilation. Android SDK/apksigner are not installed. Android signature verification was later
completed using Google apksig 9.4.1 stored privately in `.local/tools/apksig/`, with
the existing JDK. No further system installation was needed.

Five offline tests passed locally and on GitHub Actions with Python 3.12 and 3.14
([run 36175438164](https://github.com/RemingtonDev/OpenParcelHome/actions/runs/36175438164)). No scan, connection, notification subscription,
cloud authentication or physical operation was performed in the initial research.

Current preparation: 28 offline tests pass, including the opening runner. The APK
signatures pass and a tampered copy fails. No new Bluetooth operation was performed
during preparation, and no opening command has been sent.
