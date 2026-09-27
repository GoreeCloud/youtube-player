# GoreeCloud YouTube Player — Implemented Features

> **Authority:** Repository-native implemented-feature record  
> **Migration:** Seeded from the existing repository `FEATURES.md`; verified implementation evidence and source remain controlling.

## GoreeCloud YouTube Player — Features

This file separates **integrated capability**, **current Development validation work**, and **planned product scope**.

## Integrated Android source

- Native Android application shell using Kotlin and Jetpack Compose.
- Development package identity using `com.goreecloud.youtubeplayer.dev`.
- Provider-neutral `Video` domain model.
- Explicit provider capability states and fail-to-`UNKNOWN` resolution.
- `ContentProvider` abstraction.
- Deterministic, network-free `LocalDemoProvider`.
- Versioned schema-v1 contract for local library-oriented state.
- Runtime SQLite binding through `SQLiteLocalLibraryStore`.
- Durable watch-history persistence operations.
- Durable resume-position persistence operations.
- Atomic replacement of validated imported progress state.
- Deterministic `GCYTP-LIBRARY` v1 UTF-8 export/import.
- SHA-256 integrity verification plus count, range, identity, and duplicate validation.
- Development UI visibility of schema version and local progress counts.
- Machine-readable provider and Platform-System contracts.
- Exact-source Android validation workflow with unit tests, lint, APK identity checks, and a no-`INTERNET` guard.
- Android automatic backup disabled pending accepted recovery authority.

## Current Development validation candidate

The current runtime-acceptance branch adds Android instrumentation and CI coverage for the integrated local-data boundary:

- schema-v1 initialization on an Android 16 emulator;
- persisted watch-history and resume-position state surviving database close/reopen;
- replacement state surviving reopen while displaced state is removed;
- tampered/rejected imports leaving existing persisted progress unchanged.

These checks are Development validation evidence only until their exact pull-request head passes and the validated source is intentionally integrated and post-merge verified.

## Planned product features

Planned scope includes Home/discovery, provider-neutral search, native channel pages, RSS subscriptions and chronological inbox, production playback, PiP/background playback where allowed, queues, playlists/collections, Watch Later/favorites/history/Continue Watching, Shorts controls, live/premiere awareness, notifications, notes/tags, authorized offline/local media, URL/share handling, casting, accessibility/input adaptation, Linux expansion, Android TV / Google TV expansion, provider failure isolation, caching/diagnostics, and evidence-backed GoreeCloud Platform-System integration.

## Current non-features

The application must not currently be represented as providing YouTube authentication, remote YouTube retrieval, production playback, downloads, casting, cloud synchronization, telemetry, accepted Privacy Shield/Wardveil/Everkeep integration, Glaze UI conformance, Linux support, television support, release readiness, production acceptance, or Stable status.
