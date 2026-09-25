# Contributing

Useful contributions include original documentation links, app version information,
redacted hardware revision information, protocol observations with reproducible
provenance, and offline tests. A consenting owner with a still-configured app could
help establish what onboarding requires; a spare controller could support later work.

Start an issue describing the question and non-sensitive evidence. Do not upload
APKs, firmware, decompiled source, full phone backups, PINs, tokens, keys, device
identifiers or raw BLE captures. Keep access-bearing data private. Do not reset a
working box to help this project.

Contribute original code under the MIT licence and describe your sources. This
project does not claim an independently staffed clean-room process. Evidence from
static analysis must name the artifact hash and method; device claims must identify
a sanitised experiment record and its limitations.

Run `python3 -m unittest discover -s tests -v`. Tests must remain offline. Protocol
and physical experiments require separate evidence and review.
