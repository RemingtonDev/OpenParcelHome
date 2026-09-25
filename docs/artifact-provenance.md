# Android artifact — 2026-09-25

**Verified locally:** an archive was downloaded successfully; publisher authenticity
is not established. It was parsed, not installed or executed.

| Field | Observation |
| --- | --- |
| Listing | https://apkpure.net/myparcelhome/com.parcelhome.myparcelhome/download |
| Download link present in listing | https://d.apkpure.net/b/APK/com.parcelhome.myparcelhome?version=latest |
| HTTP result | 200 |
| Size | 15,975,854 bytes |
| SHA-256 | `e4ba0a6822bbff48e6aab18d8c4ec2ab14618c34839c731ffecb382f34eedfdc` |
| Local saved filename | `myparcelhome-download.bin` (assigned by researcher) |
| Container | Single APK/ZIP, 2,164 entries, classes.dex and classes2.dex |
| Package | `com.parcelhome.myparcelhome` |
| Version | 3.0.2 / 30020 |
| Minimum / target SDK | 18 / 33 |
| Native ABIs | arm64-v8a, armeabi-v7a, x86, x86_64 |
| Native library observed | librealm-jni.so in each ABI |
| Signing certificate SHA-256 | `1711e99916ddf1c15ca2a6db1a52d412e0ad427689fd1a8b65543da89e6e4853` |
| Signing certificate SHA-1 | `55a24011387f7605a32229d54adbe116ae5d6c07` |

JDK 27 jarsigner reports `jar verified` but also warns about a self-signed chain,
a 1024-bit RSA key, absent timestamp and JarFile/JarInputStream inconsistencies.
Therefore this is **partial JAR-signature evidence**, not verified Android install
validity. The SHA-1 matches the mirror listing; this is not independent confirmation
of publisher identity. Android apksigner verification, signing lineage and comparison
with a known-good owner installation remain open.

The local manifest records the file modification time as retrieval completion UTC.
Raw APK, decoded resources, decompiled source and logs are private in `.local/` and
excluded from this repository. The initial APKCombo download page returned an error;
APKPure provided the retrievable candidate. No downloader application was installed.
