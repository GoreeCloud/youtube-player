# Android Development upgrade preflight (read-only)

Use `scripts/qa_android_dev_upgrade.py` to check whether a previously
installed `com.goreecloud.youtubeplayer.dev` build can be updated **without
uninstalling or resetting application data**.

Before running, independently authenticate the GitHub unsigned CI artifact
and owner signing receipt, including source revision, package identity,
signed/unsigned hashes, certificate fingerprint and protected key custody.
The receipt alone is not proof that a candidate originated from CI.

Example:

```sh
python3 scripts/qa_android_dev_upgrade.py \
  --candidate /secure/path/goreecloud-player-development.apk \
  --receipt /secure/path/goreecloud-player-development.apk.receipt.json
```

The script verifies the candidate's signed APK certificate, .dev package,
source receipt and digest; requires one authorized arm64 ADB device; queries
the existing .dev package; retrieves **only its base APK** into an automatically
deleted temporary directory; compares signer certificates and requires the
new versionCode to exceed the installed versionCode.

A missing Development installation is a **hard stop**, not evidence for a
successful update. It does not install, uninstall, downgrade, change package
data, modify the existing `com.goreecloud.youtubeplayer` QA app, or distribute
anything. Initial Development installation and subsequent real update tests
have separate owner-approval and recovery gates; this check alone does not
establish playback, UI, background audio, privacy, or Stable readiness.
