# Android artifact — 2026-09-25

**Verified locally:** an archive was downloaded successfully; publisher authenticity
is not established. The APK was not installed or run as an Android app. Selected
decompiled builder methods were later executed in a local synthetic reference harness.

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
of publisher identity. Google apksig verification now supersedes the partial JAR-only check, as below.
Comparison with a known-good owner installation remains open.

The local manifest records the file modification time as retrieval completion UTC.
Raw APK, decoded resources, decompiled source and logs are private in `.local/` and
excluded from this repository. The initial APKCombo download page returned an error;
APKPure provided the retrievable candidate. No downloader application was installed.

## Android signature verification completed

Google's official `com.android.tools.build:apksig:9.4.1` library was downloaded
from Google Maven. Original wrapper `scripts/VerifyApk.java` invokes ApkVerifier;
no Android SDK installation, licence acceptance or APK execution was needed.

- Verification: **true**. v1: true; v2: true; v3/v3.1/v4: false.
- Signing certificate SHA-256 matches the table above. No signing lineage present.
- 53 warnings concern signature protection of META-INF entries in the JAR view;
  warnings were retained privately. Overall Android verification passes including v2.
- Negative control: a private copy with one classes.dex compressed-data byte changed
  is rejected with exit 1 and a CHUNKED_SHA256 integrity mismatch.
- Original APK SHA-256 was rechecked and remains unchanged.

Library SHA-256: `7ae2e5980c77d853e3513074ee7c822bbdcdcde1668889d17faa7fe8bc8aa821`.
Source: [Google Maven artifact](https://dl.google.com/dl/android/maven2/com/android/tools/build/apksig/9.4.1/apksig-9.4.1.jar).
[Upstream ApkVerifier](https://android.googlesource.com/platform/tools/apksig/+/refs/heads/main/src/main/java/com/android/apksig/ApkVerifier.java)
documents the verifier implementation. This is the apksig library API, not a claim
that the SDK's apksigner executable was installed or run.

Reproduction after obtaining the same library and APK privately:

```sh
java --class-path .local/tools/apksig/apksig-9.4.1.jar \
  scripts/VerifyApk.java .local/artifacts/myparcelhome-download.bin
```

Valid signatures establish integrity under the embedded signing identity, not an
independent identification of the original publisher. The source remains a mirror.
