# Historical Drive Feature Roadmap Migration Source — GoreeCloud YouTube Player

> **Status:** Historical, non-authoritative migration evidence.  
> **Source:** Former Google Drive roadmap, captured during repository migration on 2026-09-27.  
> **Rule:** Do not synchronize this file with Google Drive and do not use historical authority statements below as current governance. Current feature truth is in `IMPLEMENTED-FEATURES.md`, `PLANNED-FEATURES.md`, and `CHANGELOGS.md`.

GoreeCloud YouTube Player
FEATURE-ROADMAP — Active Development
Canonical repository: GoreeCloud/goreecloud-youtube-player
Canonical product specification: GoreeCloud/Projects/Project Specification — YouTube Player.docx
Design-system target: Current published Stable Glaze UI 1.3.0; application conformance pending
Roadmap status: Active Development; planned items are not implementation claims
Purpose
This roadmap orders development work for GoreeCloud YouTube Player. It is synchronized with the repository FEATURE-ROADMAP.md and must remain subordinate to verified implementation state, current GoreeCloud governance, and the canonical product specification.
Milestone 0 — Repository recovery and governed native foundation
Restore canonical repository identity and source-control continuity. [Verified]
Re-establish exact-head/default-branch Android CI. [Verified]
Integrate the documentation-complete native Android foundation through current exact-head CI and review. [Verified]
Reconcile the canonical project specification from recovery-blocked wording to the verified restored and foundation-integrated repository state. [Verified]
Close recovery tracking only after repository, canonical documentation, Linear, and GoreeCloud task-management records agree. [Verified]
Milestone 1 — Local-first durable state
Bind schema-v1 to a runtime persistence adapter. [Verified]
Persist watch history and resume positions. [Verified]
Provide versioned portable export/import with fail-closed validation. [Verified]
Add Android emulator/runtime acceptance for schema initialization, persistence across reopen, replacement semantics, and rejected-import state preservation.
Define and implement approved schema migration behavior before increasing the database schema version.
Define Privacy Shield authorization and Everkeep backup/restore coverage before protected-state or recovery-ready claims.
Milestone 2 — Search, library, and subscriptions
Build provider-neutral local library and search interfaces.
Add RSS feed provider contracts and safe parsing.
Implement channel following and chronological Subscription Inbox.
Add folders, tags, unread state, import, and export with local ownership.
Milestone 3 — Media and provider contracts
Define media-source and playback-session contracts before remote provider implementation.
Add a capability-aware playback-engine boundary and failure taxonomy.
Implement a YouTube provider only behind approved networking, privacy, security, and provider-capability boundaries.
Keep unsupported, restricted, degraded, and unknown capabilities truthful and fail closed.
Milestone 4 — Glaze UI and accessibility acceptance
Integrate the current approved Glaze UI contract; current published Stable target is 1.3.0.
Verify compact/expanded layout, text scaling, reduced motion/transparency, contrast, keyboard/focus, TalkBack and switch-access behavior as applicable.
Establish Android rendered and representative-device evidence.
Revalidate whenever the approved Glaze baseline changes.
Milestone 5 — Ordered platform expansion
Reconcile the separate GoreeCloud-wide web-application delivery preference with this product-specific rollout direction before release planning.
Expand to a supported native Linux Desktop client after the Android foundation is established.
After Linux expansion, add the Android TV / Google TV client with purpose-built input, focus, layout, and remote-control behavior.
Add Docker/Podman only if a server-hosted or otherwise container-appropriate component is introduced.
Milestone 6 — GoreeCloud Platform Systems
Implement and validate current applicable GoreeCloud Manager contracts.
Implement and validate Privacy Shield.
Implement and validate Wardveil Security.
Implement and validate Everkeep.
Implement and validate current Glaze UI.
Implement and validate GoreeCloud Mesh where applicable.
Implement and validate GoreeCloud Identity where applicable.
Milestone 7 — Product capability expansion
Native Home/discovery controls and user-configurable surfaces.
Custom playlists, collections, Watch Later, favorites, notes, tags, and queue management.
Continue Watching, Shorts controls, live/premiere awareness, and granular notifications.
URL/share integration, privacy-bounded clipboard handling, capability-aware casting, and authorized offline/local media.
Milestone 8 — Release qualification
Exact release-candidate build/test evidence on every supported target.
Security, privacy, recovery, rollback, signing/distribution, accessibility, and current Glaze UI acceptance.
Production/runtime acceptance for every claimed capability.
Documentation and roadmap reconciliation before lifecycle promotion.
Stable remains prohibited until all applicable requirements are implemented, current, validated, and accepted.
Current boundary
The native Android foundation and first durable local-data source slice are integrated and post-merge validated on authoritative `main` at `cc4ced31bf1e98fbba495976e72f0c5fd9b2c857`. Android emulator runtime acceptance is the current separate Development gate under PR #4; physical-device acceptance, approved migrations, Privacy Shield authorization, Everkeep recovery, broader library persistence, provider support, Linux expansion, and Android TV / Google TV expansion remain unaccepted. Planned roadmap items must not be described as shipped functionality.