#!/usr/bin/env python3
"""Owner-side Development signing key custody with tested encrypted recovery.

Creation is explicitly opt-in; nothing is committed, uploaded, installed or
distributed. Passwords come only from inherited owner-protected environment.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

ALIAS = "goreecloud-youtube-player-development"
STORE_ENV = "GC_YOUTUBE_PLAYER_STORE_PASSWORD"
KEY_ENV = "GC_YOUTUBE_PLAYER_KEY_PASSWORD"
BACKUP_ENV = "GC_YOUTUBE_PLAYER_BACKUP_PASSWORD"
SHA256 = re.compile(r"^\s*SHA256:\s*([a-fA-F0-9:]+)", re.M)


def execute(*args, stdin=None):
    proc = subprocess.run(args, input=stdin, capture_output=True, text=True,
                          check=False)
    if proc.returncode:
        # Never echo child process output: it can accidentally contain secrets.
        raise RuntimeError("Protected key operation failed: " + args[0])
    return proc.stdout


def require_env():
    password = os.getenv(STORE_ENV, "")
    key_password = os.getenv(KEY_ENV, "")
    backup_password = os.getenv(BACKUP_ENV, "")
    if len(password) < 24 or len(backup_password) < 24:
        raise ValueError("Owner store and backup passwords must each be at least 24 characters")
    if key_password != password:
        raise ValueError("PKCS12 store and key passwords must match")
    if backup_password == password:
        raise ValueError("Encrypted backup must use an independent password")
    return backup_password


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def certificate(keystore, alias):
    output = execute("keytool", "-list", "-v", "-storetype", "PKCS12",
                     "-keystore", str(keystore), "-alias", alias,
                     "-storepass:env", STORE_ENV)
    values = SHA256.findall(output)
    if len(values) != 1:
        raise ValueError("Expected one certificate SHA-256 fingerprint")
    value = values[0].replace(":", "").lower()
    if not re.fullmatch(r"[a-f0-9]{64}", value):
        raise ValueError("Invalid certificate SHA-256 fingerprint")
    return value


def validate_paths(primary, backup, create=False):
    primary = primary.expanduser().absolute()
    backup = backup.expanduser().absolute()
    if not primary.parent.is_dir() or not backup.parent.is_dir():
        raise ValueError("Create the primary and independent backup directories first")
    if any(parent.is_symlink() for parent in (*primary.parents, *backup.parents)):
        raise ValueError("Refuse symlinked custody directories")
    if any((parent / '.git').exists() for parent in primary.parents):
        raise ValueError("Private signing keys must stay outside Git repositories")
    if not primary.name.endswith(".p12") or not backup.name.endswith(".p12.gpg"):
        raise ValueError("Expected a PKCS12 primary and GPG-encrypted backup")
    if primary.parent.stat().st_dev == backup.parent.stat().st_dev:
        raise ValueError("Backup must live on a different mounted filesystem")
    mode = stat.S_IMODE(primary.parent.stat().st_mode)
    if mode & 0o077:
        raise ValueError("Owner's primary signing directory must have mode 0700")
    if create and (primary.exists() or backup.exists()
                   or primary.with_suffix(".custody.json").exists()):
        raise ValueError("Refusing to overwrite existing key, backup or custody receipt")
    if not create and (not primary.is_file() or not backup.is_file()):
        raise ValueError("Existing key and encrypted backup are required")
    if primary.is_symlink() or backup.is_symlink():
        raise ValueError("Refuse symlinked signing material")
    return primary, backup


def restore_and_compare(primary, backup, alias, backup_password, scratch):
    restored = scratch / "restored.p12"
    execute("gpg", "--batch", "--no-tty", "--pinentry-mode", "loopback",
            "--passphrase-fd", "0", "--decrypt", "--output", str(restored),
            str(backup), stdin=backup_password + "\n")
    if sha_file(restored) != sha_file(primary):
        raise ValueError("Encrypted backup restores different keystore bytes")
    fingerprint = certificate(primary, alias)
    if certificate(restored, alias) != fingerprint:
        raise ValueError("Restored signing certificate differs from primary")
    return fingerprint


def create_custody(primary, backup, alias, backup_password):
    primary, backup = validate_paths(primary, backup, create=True)
    with tempfile.TemporaryDirectory(prefix=".goreecloud-key-", dir=primary.parent) as work:
        with tempfile.TemporaryDirectory(prefix=".goreecloud-backup-", dir=backup.parent) as backup_work:
            workdir = Path(work)
            staged_key = workdir / "development.p12"
            staged_backup = Path(backup_work) / "development.p12.gpg"
            execute(
                "keytool", "-genkeypair", "-noprompt",
                "-alias", alias, "-keyalg", "RSA", "-keysize", "3072",
                "-sigalg", "SHA256withRSA", "-validity", "3650",
                "-storetype", "PKCS12", "-keystore", str(staged_key),
                "-storepass:env", STORE_ENV, "-keypass:env", KEY_ENV,
                "-dname", "CN=GoreeCloud YouTube Player Development, O=GoreeCloud",
            )
            os.chmod(staged_key, 0o600)
            original_cert = certificate(staged_key, alias)
            execute("gpg", "--batch", "--no-tty", "--pinentry-mode", "loopback",
                    "--passphrase-fd", "0", "--symmetric", "--cipher-algo", "AES256",
                    "--s2k-digest-algo", "SHA512", "--output", str(staged_backup),
                    str(staged_key), stdin=backup_password + "\n")
            verified = restore_and_compare(staged_key, staged_backup, alias,
                                           backup_password, workdir)
            if verified != original_cert:
                raise ValueError("Backup recovery certificate mismatch")
            custody = {
                "package": "com.goreecloud.youtubeplayer.dev",
                "key_alias": alias,
                "key_algorithm": "RSA-3072",
                "store_type": "PKCS12",
                "certificate_sha256": original_cert,
                "backup_encryption": "OpenPGP AES256 symmetric",
                "backup_separate_filesystem": True,
                "backup_restore_verified": True,
                "release_state": "owner_private_no_distribution",
            }
            staged_receipt = workdir / "custody.json"
            staged_receipt.write_text(json.dumps(custody, indent=2) + "\n",
                                      encoding="utf-8")
            os.chmod(staged_receipt, 0o600)
            # Exclusive hard links are atomic and do not replace existing files.
            # Publish encrypted backup before the only persistent primary key.
            os.link(staged_backup, backup)
            os.link(staged_key, primary)
            os.link(staged_receipt, primary.with_suffix(".custody.json"))
            return custody


def verify_custody(primary, backup, alias, backup_password):
    primary, backup = validate_paths(primary, backup)
    if stat.S_IMODE(primary.stat().st_mode) & 0o077:
        raise ValueError("Private signing key must be owner-only (0600)")
    with tempfile.TemporaryDirectory(prefix=".goreecloud-restore-",
                                     dir=primary.parent) as work:
        fingerprint = restore_and_compare(primary, backup, alias,
                                          backup_password, Path(work))
    evidence = primary.with_suffix(".custody.json")
    if not evidence.is_file() or evidence.is_symlink():
        raise ValueError("Original protected custody receipt missing")
    receipt = json.loads(evidence.read_text(encoding="utf-8"))
    if (receipt.get("certificate_sha256") != fingerprint
            or receipt.get("key_alias") != alias
            or receipt.get("backup_restore_verified") is not True):
        raise ValueError("Custody receipt does not match recovered key")
    return {"package": "com.goreecloud.youtubeplayer.dev",
            "key_alias": alias, "certificate_sha256": fingerprint,
            "backup_separate_filesystem": True,
            "backup_restore_verified": True,
            "release_state": "owner_private_no_distribution"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--create", action="store_true")
    mode.add_argument("--verify-recovery", action="store_true")
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--encrypted-backup", type=Path, required=True)
    parser.add_argument("--alias", default=ALIAS)
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[a-z][a-z0-9-]{3,64}", args.alias):
        raise ValueError("Invalid signing key alias")
    backup_password = require_env()
    if args.create:
        result = create_custody(args.primary, args.encrypted_backup,
                                args.alias, backup_password)
    else:
        result = verify_custody(args.primary, args.encrypted_backup,
                                args.alias, backup_password)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, RuntimeError, json.JSONDecodeError) as exc:
        print("Protected key custody refused: " + str(exc), file=sys.stderr)
        sys.exit(1)
