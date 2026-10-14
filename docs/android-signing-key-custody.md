# Development signing identity custody and recovery

This repository contains **no private signing identity**. Android Development
uses `com.goreecloud.youtubeplayer.dev`, separate from the existing
ephemeral Debug QA installation and any future production signing key.

The owner-side `scripts/provision_android_dev_signing.py` explicitly supports
`--create` or `--verify-recovery`. It is never called by GitHub Actions.

## Prerequisites

Provide two locations on **different mounted filesystems**: an existing
owner-only local directory (0700) outside any Git repository for the PKCS12
private key, and a separate removable/offline backup directory. The encrypted
backup uses AES256 OpenPGP symmetric encryption and an **independent** password.

The owner must first secure three environment variables using an authorized
password manager or protected terminal session, never chat, a repository,
shell-history command text, logs, or Drive plaintext. The store and key
passwords must be the same for PKCS12; the backup password must differ. Store
both owner-held passwords and their recovery instructions independently of
the laptop. The script enforces minimum 24-character passwords but cannot
verify that the owner will retain or recover them.

- `GC_YOUTUBE_PLAYER_STORE_PASSWORD`
- `GC_YOUTUBE_PLAYER_KEY_PASSWORD`
- `GC_YOUTUBE_PLAYER_BACKUP_PASSWORD`

Example after the owner has mounted and **approved** a backup drive and supplied
the environment values securely (paths below are placeholders):

```sh
python3 scripts/provision_android_dev_signing.py --create \
  --primary /home/OWNER/.local/share/goreecloud/secure-signing/development.p12 \
  --encrypted-backup /media/OWNER/BACKUP-DRIVE/GoreeCloud/Backups/Signing/youtube-player/development.p12.gpg \
  --expected-usb-uuid EXPECTED_VOLUME_UUID

python3 scripts/provision_android_dev_signing.py --verify-recovery \
  --primary /home/OWNER/.local/share/goreecloud/secure-signing/development.p12 \
  --encrypted-backup /media/OWNER/BACKUP-DRIVE/GoreeCloud/Backups/Signing/youtube-player/development.p12.gpg \
  --expected-usb-uuid EXPECTED_VOLUME_UUID
```

Before either command can access the credentials, the read-only USB preflight verifies that the mounted filesystem UUID is the expected one and that the backup directory is exactly `<USB mount>/GoreeCloud/Backups/Signing/youtube-player/`. Discover the UUID locally with `lsblk -o NAME,UUID,LABEL,MOUNTPOINTS`, and recheck it after any remount. An unmounted path, wrong disk, symlink, wrong directory, or read-only filesystem fails closed. The UUID is an identifier, not a password; never hardcode a particular owner's device UUID in the public repository.

The create operation generates a fresh RSA-3072 PKCS12 key with `keytool`,
encrypts the backup with `gpg`, then independently **decrypts the backup in
a temporary directory** and compares exact keystore bytes and signer
certificate SHA-256. It publishes the encrypted backup before the local
primary key and a nonsecret, 0600 custody receipt, refusing existing outputs.
A failed/partial transaction requires investigating the remaining backup or
primary files, never replacing them blindly. The verification mode reads the
existing materials without replacing or publishing them.

The displayed certificate digest is the fingerprint to pin in the local
Development APK signer with `--expected-cert-sha256`. The signing tool still
requires its original authenticated GitHub Actions unsigned APK and
`provenance.txt`, and uses `GC_YOUTUBE_PLAYER_KEY_ALIAS` and matching signing
passwords. Do **not** send the keystore, backup password, or restoration
passwords through a GitHub issue, commit, public artifact, or chat.

## Acceptance

Key generation is *not* a release. Before signing a real APK, prove separately
that encrypted backup storage is under owner control, its password and key
password are independently recoverable, offline restoration works, the cert
fingerprint is pinned, and the owner has accepted custody. Repeat recovery
verification after material changes or backups. Do not confuse a successful
synthetic test with a permanent owner's signing identity.

Any owner-delivered signed APK must pass provenance, signature, installation,
upgrade-with-data-preservation, and exact-byte GoreeCloud Drive checks.
Stable/Anchor remains blocked by remaining product runtime acceptance.
