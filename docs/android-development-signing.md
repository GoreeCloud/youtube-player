# Protected Android Development signing (pre-release)

**State:** signing pipeline prepared; no GoreeCloud Development signing key,
signed candidate, owner-delivered APK, or release acceptance is claimed here.

## Separate app identities

- Bounded disposable QA APK: `com.goreecloud.youtubeplayer`, signed with an
  ephemeral Android Debug certificate. This already exists on the OnePlus N200.
- Repeat-installable Development channel: `com.goreecloud.youtubeplayer.dev`,
  an isolated **non-debuggable, JS-bundled** variant with initial arm64
  `versionCode=204` and `versionName=0.1.0-dev`. FOSS/Full variants are
  distinct but **share that Development package name**, so install only one at
  a time. Do not uninstall or overwrite either channel as a workaround.
- Production identity `com.goreecloud.youtubeplayer` remains a separate,
  unapproved signing/release concern. Do **not** assume a protected key for
  `.dev` can update the existing Debug-signed package of the same source.

## Artifact custody and signing boundary

`.github/workflows/android-unsigned-development.yml` is **manual, main-only,
default-off**. It builds an **unsigned** arm64 FOSS Development candidate,
checks package identity/version, verifies the absence of an APK signature and
records exact Git SHA and SHA-256. The staged non-installable artifact expires
after one day. It does not use or transmit signing secrets.

The owner-controlled `scripts/sign_android_development.py` signs on a trusted
device **outside GitHub Actions** and refuses to sign unless:

1. The source revision, unsigned APK SHA-256, `.dev` package identity and versionCode match `provenance.txt`. The signer also requires an authenticated `GoreeCloud` GitHub CLI account, verifies the recorded GitHub Actions run succeeded from `main` using the approved manual workflow, and downloads the original **unexpired** artifact to compare both APK bytes and provenance before signing. A locally edited provenance file alone is not trusted evidence.
2. The keystore exists **outside Git**, is owner-only readable (0600), and the
   expected signing certificate SHA-256 is pinned.
3. Signing credentials are supplied through protected environment variables
   `GC_YOUTUBE_PLAYER_STORE_PASSWORD`, `GC_YOUTUBE_PLAYER_KEY_PASSWORD`,
   and `GC_YOUTUBE_PLAYER_KEY_ALIAS` (never in command arguments or Git).
4. Initial issue uses `--first-issue` and `versionCode 204`, or an update
   uses `--previous-version-code N` and a **strictly increasing** version.
5. Neither the signed output nor its receipt already exists. The signed
   result is reverified for certificate, package identity and version.

The signer creates a local 0600 APK and receipt with source identity, signed
and unsigned SHA-256, certificate digest and versionCode. **It does not
distribute, install, promote or publish.**

Before first key issuance, establish secure owner-held custody plus a
**separately recoverable encrypted backup**, and verify that restoring the
backup preserves the same signer certificate. Do not put raw private keys,
passwords, signing environment files or recovery material in repositories,
Actions artifacts, terminal output, issues, or public downloads.

Owner delivery of any signed installable APK requires prior authenticated
upload to the authorized `goreecloud@gmail.com` GoreeCloud Drive folder,
verified permissions and readback of the **exact bytes**. A link to a CI
unsigned or ephemeral-Debug artifact is not a Development APK delivery.

## Remaining acceptance

Verify CI prebuild and unsigned Development package generation, owner
Development key custody and tested backup recovery, local signing and
certificate pin, protected Drive upload, initial install on representative
hardware, an **upgrade with higher versionCode preserving app data**, and
network/privacy, playback, PiP, background audio, search, download, Glaze,
accessibility and crash checks. No Stable/Anchor designation is supported.
