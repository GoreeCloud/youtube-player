#!/usr/bin/env python3
"""Sign an isolated GoreeCloud Development candidate on an authorized owner device.

No secrets in the repository, argv, logs, GitHub artifacts or signed receipts.
This script does not upload, install or publish anything.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile

PKG = "com.goreecloud.youtubeplayer.dev"


def command(*args, check=True):
    return subprocess.run(args, text=True, capture_output=True, check=check)


def inspect_unsigned(apk, expected_digest):
    if (not apk.is_file() or not apk.name.endswith("-development-unsigned.apk") or
            "arm64-v8a" not in apk.name or "foss" not in apk.name):
        raise ValueError("Expected a verified arm64 FOSS Development unsigned APK")
    digest = hashlib.sha256(apk.read_bytes()).hexdigest()
    if digest != expected_digest.lower():
        raise ValueError("Unsigned artifact SHA-256 mismatch")
    result = command("aapt", "dump", "badging", str(apk)).stdout
    match = re.search(r"^package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", result, re.M)
    if not match or match.group(1) != PKG or not match.group(3).endswith("-dev"):
        raise ValueError("Wrong Android Development package or version")
    version_code = int(match.group(2))
    if version_code < 204:
        raise ValueError("Development versionCode below initial baseline")
    if command("apksigner", "verify", str(apk), check=False).returncode == 0:
        raise ValueError("Refusing already-signed input; expected unsigned source")
    return digest, version_code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--keystore", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--unsigned-sha256", required=True)
    parser.add_argument("--expected-cert-sha256", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--first-issue", action="store_true")
    mode.add_argument("--previous-version-code", type=int)
    args = parser.parse_args(argv)

    if not re.fullmatch(r"[0-9a-fA-F]{40}", args.source_sha):
        raise ValueError("Expected exact Git source revision SHA")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", args.unsigned_sha256):
        raise ValueError("Expected full unsigned SHA-256 digest")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", args.expected_cert_sha256):
        raise ValueError("Expected pinned signing certificate SHA-256 digest")
    keystore = args.keystore.expanduser().resolve(strict=True)
    if not keystore.is_file() or keystore == args.input.resolve():
        raise ValueError("Invalid protected keystore")
    if stat.S_IMODE(keystore.stat().st_mode) & 0o077:
        raise ValueError("Signing keystore must be owner-only readable (mode 0600)")
    for name in ("GC_YOUTUBE_PLAYER_STORE_PASSWORD",
                 "GC_YOUTUBE_PLAYER_KEY_PASSWORD", "GC_YOUTUBE_PLAYER_KEY_ALIAS"):
        if not os.getenv(name):
            raise ValueError(f"Protected signing environment variable missing: {name}")
    output = args.output.expanduser().absolute()
    if output.exists() or output == args.input.resolve():
        raise ValueError("Output already exists; never overwrite signed APKs")
    for executable in ("aapt", "zipalign", "apksigner"):
        if not shutil.which(executable):
            raise RuntimeError(f"Missing local Android build tool: {executable}")
    digest, version_code = inspect_unsigned(args.input.resolve(), args.unsigned_sha256)
    if args.previous_version_code is not None and version_code <= args.previous_version_code:
        raise ValueError("Android versionCode must increase for signed Development updates")
    if args.first_issue and version_code != 204:
        raise ValueError("First Development issue must start at ABI-specific versionCode 204")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".goreecloud-sign-", dir=output.parent) as work:
        aligned = Path(work) / "aligned.apk"
        staged = Path(work) / "signed.apk"
        command("zipalign", "-p", "-f", "4", str(args.input.resolve()), str(aligned))
        command(
            "apksigner", "sign",
            "--ks", str(keystore),
            "--ks-key-alias", os.environ["GC_YOUTUBE_PLAYER_KEY_ALIAS"],
            "--ks-pass", "env:GC_YOUTUBE_PLAYER_STORE_PASSWORD",
            "--key-pass", "env:GC_YOUTUBE_PLAYER_KEY_PASSWORD",
            "--out", str(staged), str(aligned),
        )
        verification = command("apksigner", "verify", "--print-certs", "--verbose", str(staged)).stdout
        match = re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]{64})", verification)
        if not match or match.group(1).lower() != args.expected_cert_sha256.lower():
            raise ValueError("Signed APK certificate differs from owner-pinned Development identity")
        # Readback after signing, since signature processing can change metadata.
        metadata = command("aapt", "dump", "badging", str(staged)).stdout
        if not re.search(r"^package: name='" + re.escape(PKG) + r"' versionCode='" + str(version_code) + r"'", metadata, re.M):
            raise ValueError("Signed APK package/version changed")
        staged.replace(output)
    os.chmod(output, 0o600)
    receipt = {
        "channel": "Development (not released)",
        "package": PKG,
        "source_sha": args.source_sha.lower(),
        "unsigned_sha256": digest,
        "signed_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "certificate_sha256": args.expected_cert_sha256.lower(),
        "version_code": version_code,
        "first_issue": bool(args.first_issue),
        "status": "locally_signed_not_distributed",
    }
    receipt_path = output.with_suffix(output.suffix + ".receipt.json")
    with receipt_path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
    os.chmod(receipt_path, 0o600)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Development signing stopped: {exc}", file=sys.stderr)
        sys.exit(1)
