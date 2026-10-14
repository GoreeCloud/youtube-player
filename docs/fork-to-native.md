# Fork-to-Native — baseline, parity, and release gates

**Current milestone:** 0.1.0 development source import. Not Stable or production-ready.

## Feature and UI inventory

| Capability | Source baseline | Required acceptance work |
|---|---|---|
| YouTube and YouTube Music | Imported WebView and JavaScript bridges | Device playback and native architecture verification |
| Background play, PiP, media controls | Imported Android module | Permission, media session and lifecycle tests |
| Local lists, settings and history | Imported | Data safety, migrations and recovery tests |
| Video download, RSS, shorts hiding, captions and live chat | Imported | Regression and offline behavior tests |
| Navigation, appearance and gestures | Imported React Native UI | Glaze Stable implementation and accessibility audit |
| Account sync and subscriptions | Inherited upstream integrations | Isolate and replace with authorized GoreeCloud contracts before distribution |
| Android and iOS identities | New app identifiers configured | Deep links, signing, upgrade compatibility, on-device tests |
| Desktop and browser extension code | Retained for capability parity | Separate identity and platform review before distribution |

Present in source is NOT verified runtime functionality or policy approval.

## Release and security blockers

1. Isolate or remove upstream-operated sign-in endpoints, payment identifiers, subscriptions, donation and promotional surfaces. Do not imply these are GoreeCloud services or collect user credentials without an authorized integration and informed consent.
2. Inventory all external URLs, JavaScript injections and WebView navigation, permission use, download handling, credentials, storage and third-party dependencies; threat-model and test fixes.
3. Implement verified GoreeCloud visual identity and official Stable Glaze components across screens; update onboarding.
4. Rebuild product-specific flows behind native GoreeCloud interfaces while retaining valuable functionality and legacy-data portability.
5. Evaluate and implement applicable contracts for GoreeCloud Manager, Privacy Shield, Wardveil, Everkeep, Glaze, Mesh, Identity, Policy and Observability.
6. Set up protected Development signing, monotonic Android versions, real build/install/device testing, backups, rollback and eligible delivery through GoreeCloud Drive.
7. Comply with AGPL licensing and any separate dependencies. No production release until source availability, security, privacy, parity, compatibility and CI gates are verified.

## Migration discipline

Preserve imported behavior as a reference; replace one subsystem at a time, add reproducible tests, verify data migration and rollback, then retire old code. The Android library namespace and NouTube JavaScript bridge/API names remain unchanged initially to avoid breaking compatibility; application ID and UI display name are independent already.

## Phase 2 — account-service isolation and build hygiene

**Implemented in source (not release certified):**
- Mobile account/sync settings now clearly state that GoreeCloud cloud sync is not connected. Existing local data stores are retained.
- Legacy NouTube authentication token redemption, account API requests, purchase UI and on-start iOS purchase reconciliation are disabled; upstream Supabase URLs/keys have been removed from mobile and shared clients.
- Browser-extension login and remote sync are disabled, upstream host/identity permissions removed, and the extension's locally available features remain wired.
- Desktop automatic updates are disabled pending an independently verified signed GoreeCloud release channel; inherited publisher configuration, donation prompts and update links are removed or replaced.
- Root/desktop/extension workspace identities and dependency lockfile have been aligned; inherited root package-link build errors removed.
- Missing nativewind type declarations and legacy desktop package imports were corrected.

**Local verification on October 12, 2026:**
- Nine Python source/identity isolation tests passed.
- Root Bun test suite: 332 passed / 0 failed.
- TypeScript shared/mobile source, desktop Node and renderer, and extension (after WXT prepare) passed.
- Bun locked dependency restoration completed using ignore-scripts.

**Still pending (not claimed as complete):**
- Build and install on Android/iOS physical devices, native feature parity and background media verification.
- Official GoreeCloud Glaze implementation and approved visual assets, accessibility review and first-run onboarding refresh.
- GoreeCloud Identity/Sync/Privacy Shield/Wardveil interfaces, encrypted data/credential migration and external security review.
- Approved Development key management, signed APK in GoreeCloud Drive, release channel, licensed-source disclosures and actual deployment.
- Desktop native package builds and browser extension signing/distribution.

## Desktop Flatpak metadata identity

The legacy local Flatpak manifest and AppStream/desktop entry names have been
replaced with the independent development identity
\`com.goreecloud.youtubeplayer.Dev\`. Previously inherited NouTube release
history and screenshot URLs have deliberately been excluded: neither describes
a verified GoreeCloud build. The wrapper points at the GoreeCloud executable,
with the original NouTube provenance retained in \`UPSTREAM.md\`.

This is source-metadata validation only; the pinned Flatpak runtime, Electron
archives, packaging, installation and desktop runtime have not been certified.
No Flatpak production release or distribution is authorized by this change.
