# First-install Android QA harness

`scripts/qa_android_device.py` is a **read-only preflight by default** for an
ephemeral FOSS or Full `arm64-v8a` debug APK from a verified GoreeCloud CI run.

It requires one authorized ADB device (or an explicitly selected `--serial`),
verifies the APK signature with `apksigner`, checks the actual APK package
name with `aapt` or `aapt2`, verifies the phone's CPU architecture and Android
API, calculates SHA-256 and **refuses an existing installation**.

Example preflight:

```sh
python3 scripts/qa_android_device.py /path/to/app-arm64-v8a-foss-debug.apk
```

For a bounded, owner-authorized QA first installation only, pass `--install`
**and** `--expected-sha256 HASH` from the validated CI evidence. A missing or
mismatched digest stops installation. This sends one launcher intent and records
whether the app process stays alive.
It does not uninstall, replace, reset data, publish, sign or deliver the APK.
`--report /path/to/new-report.json` writes sanitized evidence exclusively to
a new file without an ADB serial. The user must separately verify playback,
privacy, background audio, PiP, visual quality and accessibility.

**Prerequisites:** a CI artifact matching its source SHA and checksums,
`adb`, `apksigner`, and `aapt` or `aapt2`, sufficient device storage, and no preexisting
`com.goreecloud.youtubeplayer` package. CI debug signing is ephemeral; it is
not an update-compatible Development identity or approval for release.
