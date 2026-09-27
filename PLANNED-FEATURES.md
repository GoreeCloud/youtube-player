# GoreeCloud YouTube Player — Planned Features

> **Authority:** Repository-native planned-feature record  
> **Migration:** Replaces the retired `FEATURE-ROADMAP.md` / Google Drive roadmap controls. GitHub is the sole feature-state authority.

**Lifecycle:** Active Development  
**Roadmap authority:** docx`  
**Canonical product scope:** GoreeCloud Drive → Projects → `Project Specification — YouTube Player.docx`

This roadmap orders work. It does not upgrade planned capabilities into implemented features.

## Milestone 0 — Repository recovery and governed native foundation

Current objective: establish a recoverable, reviewable native repository baseline.

- [x] Restore canonical repository identity and source-control continuity.
- [x] Re-establish exact-head/default-branch Android CI.
- [ ] Integrate the documentation-complete native Android foundation through current exact-head CI and review.
- [x] Reconcile the canonical project specification from recovery-blocked wording to the verified restored repository state.
- [ ] Close recovery tracking only after repository, canonical documentation, and task records agree.

## Milestone 1 — Local-first durable state

- [ ] Bind schema-v1 to a runtime persistence adapter.
- [ ] Persist watch history and resume positions.
- [ ] Provide versioned portable export/import with fail-closed validation.
- [ ] Add migration boundaries and tests.
- [ ] Define Privacy Shield authorization for durable user state.
- [ ] Define Everkeep backup/restore coverage before recovery claims.

The first portion is under stacked Development PR #2 and remains unintegrated until its dependency, review, and exact-head validation gates pass.

## Milestone 2 — Search, library, and subscriptions

- [ ] Build provider-neutral local library/search interfaces.
- [ ] Add RSS feed provider contracts and safe parsing.
- [ ] Implement channel following and chronological Subscription Inbox.
- [ ] Add folders, tags, unread state, import, and export with explicit local ownership.

## Milestone 3 — Media and provider contracts

- [ ] Define media-source and playback-session contracts before remote provider implementation.
- [ ] Add a capability-aware playback-engine boundary and provider failure taxonomy.
- [ ] Implement a YouTube provider only behind approved networking, privacy, security, and provider-capability boundaries.
- [ ] Keep unsupported, restricted, degraded, and unknown capabilities truthful and fail closed.

## Milestone 4 — Current Glaze UI and accessibility acceptance

- [ ] Integrate the current approved Glaze UI contract; current published Stable target is 1.3.0.
- [ ] Verify compact/expanded layout, text scaling, reduced motion/transparency, contrast, keyboard/focus, TalkBack, and switch-access behavior as applicable.
- [ ] Establish Android rendered and representative-device evidence.
- [ ] Revalidate whenever the approved Glaze baseline changes.

## Milestone 5 — Ordered platform expansion

- [ ] Treat any additional platform beyond Android, Linux, and Android TV / Google TV as a separate product decision requiring its own justification and authorization.
- [ ] Expand to a supported native Linux Desktop client after the Android foundation is established.
- [ ] After Linux expansion, add the Android TV / Google TV client with purpose-built input, focus, layout, and remote-control behavior.
- [ ] Add Docker/Podman only if a server-hosted or otherwise container-appropriate component is introduced.

## Milestone 6 — GoreeCloud Platform Systems

Evaluate and implement the current applicable contracts for:

- [ ] GoreeCloud Manager
- [ ] Privacy Shield
- [ ] Wardveil Security
- [ ] Everkeep
- [ ] Glaze UI
- [ ] GoreeCloud Mesh
- [ ] GoreeCloud Identity

Documentation/metadata alone cannot satisfy these gates.

## Milestone 7 — Product capability expansion

- [ ] Native Home/discovery controls and user-configurable surfaces.
- [ ] Custom playlists, collections, Watch Later, favorites, notes, tags, and queue management.
- [ ] Continue Watching, Shorts controls, live/premiere awareness, and granular notifications.
- [ ] URL/share integration, privacy-bounded clipboard handling, capability-aware casting, and authorized offline/local media.

## Milestone 8 — Release qualification

- [ ] Exact release-candidate build/test evidence on every supported target.
- [ ] Security, privacy, recovery, rollback, signing/distribution, accessibility, and current Glaze UI acceptance.
- [ ] Production/runtime acceptance for every claimed capability.
- [ ] Documentation and roadmap reconciliation before lifecycle promotion.

Stable is prohibited until all applicable governing requirements are implemented, current, validated, and accepted.
