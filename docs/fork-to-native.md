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
