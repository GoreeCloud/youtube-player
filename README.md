# GoreeCloud YouTube Player

Fork-to-Native development of an independent GoreeCloud YouTube and YouTube Music player.

**Status: development foundation — not yet production-ready.** The source is derived from NouTube and remains in phased native modernization. The mobile application currently uses Expo/React Native and native WebView bridging. This is not a completed native conversion.

## Foundation
- Imported from https://github.com/nonbili/NouTube at pinned commit 270a3e9b94df53eee9b7b9dd6b1f757fe739961e.
- Independent GoreeCloud repository, Android application ID com.goreecloud.youtubeplayer, and iOS bundle identifier com.goreecloud.youtubeplayer.
- GoreeCloud app name, release-feed and source link foundations.
- Upstream license and contributor attribution retained in LICENSE and UPSTREAM.md.
- Internal bridge identifiers, WebView features and upstream-linked backend flows need staged replacement.

## Development
Inherited Android entrypoints are app.config.ts and android/app/build.gradle. Preliminary source integrity checks run with:

    python3 -m unittest discover -s tests/goreecloud -p 'test_*.py'

Cloud sign-in, inherited billing and upstream sync are now disabled in this development baseline; device-local player, bookmarks, history and settings remain the preservation targets. Android, iOS and desktop native builds, on-device parity tests, privacy/security acceptance, development signing and Glaze conformance are **not yet verified**.

See docs/fork-to-native.md for feature inventory, release blockers, and migration gates.

## License and independence
Derived from NouTube, copyright its original authors and contributors, under GNU Affero General Public License v3; see LICENSE and UPSTREAM.md. Distribution and network use of modified covered code must satisfy source availability and other applicable AGPL terms. Not affiliated with YouTube or Google.
