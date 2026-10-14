#!/usr/bin/env python3
"""Check Dev APK upgrade compatibility without installing or changing app data."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

PACKAGE = "com.goreecloud.youtubeplayer.dev"
APK_INFO = re.compile(r"^package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", re.M)
CERT_INFO = re.compile(r"Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]{64})")


def command(*args, missing_ok=False):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        if missing_ok and result.returncode == 1 and not result.stdout.strip() and not result.stderr.strip():
            return ""
        raise RuntimeError(f"{args[0]} failed (exit {result.returncode})")
    return result.stdout.strip()


def apk_identity(path):
    match = APK_INFO.search(command("aapt", "dump", "badging", str(path)))
    if not match or match.group(1) != PACKAGE or not match.group(3).endswith("-dev"):
        raise ValueError("Expected GoreeCloud .dev APK identity")
    matchcert = CERT_INFO.findall(command("apksigner", "verify", "--print-certs", str(path)))
    if len(matchcert) != 1:
        raise ValueError("Expected exactly one valid signing certificate")
    return int(match.group(2)), matchcert[0].lower()


def authorized_serial(requested):
    lines = command("adb", "devices", "-l").splitlines()[1:]
    devices = [x.split()[0] for x in lines if len(x.split()) > 1 and x.split()[1] == "device"]
    if requested:
        if requested not in devices:
            raise RuntimeError("Requested device unavailable")
        return requested
    if len(devices) != 1:
        raise RuntimeError("Exactly one authorized device required")
    return devices[0]


def verify_upgrade(candidate, receipt, serial=None):
    if not candidate.is_file() or not receipt.is_file():
        raise ValueError("Signed candidate and signing receipt required")
    evidence = json.loads(receipt.read_text(encoding="utf-8"))
    if not isinstance(evidence, dict):
        raise ValueError("Malformed signing receipt")
    candidate_sha = hashlib.sha256(candidate.read_bytes()).hexdigest()
    new_version, new_cert = apk_identity(candidate)
    if (evidence.get("package") != PACKAGE
            or evidence.get("signed_sha256") != candidate_sha
            or evidence.get("certificate_sha256", "").lower() != new_cert
            or evidence.get("version_code") != new_version
            or evidence.get("status") != "locally_signed_not_distributed"
            or not re.fullmatch(r"[0-9a-f]{40}", evidence.get("source_sha", ""))):
        raise ValueError("Candidate fails protected signing-receipt checks")

    selected = authorized_serial(serial)
    abis = command("adb", "-s", selected, "shell", "getprop", "ro.product.cpu.abilist")
    if "arm64-v8a" not in abis.split(","):
        raise RuntimeError("Device ABI does not support arm64 Development APK")
    listing = command("adb", "-s", selected, "shell", "pm", "path", PACKAGE, missing_ok=True)
    base_apks = [line.removeprefix("package:") for line in listing.splitlines()
                 if line.startswith("package:") and line.endswith("/base.apk")]
    if len(base_apks) != 1:
        raise RuntimeError("Development app missing or base APK ambiguous")
    with tempfile.TemporaryDirectory(prefix="goreecloud-upgrade-preflight-") as folder:
        installed_apk = Path(folder) / "installed.apk"
        command("adb", "-s", selected, "pull", base_apks[0], str(installed_apk))
        old_version, old_cert = apk_identity(installed_apk)
    if new_cert != old_cert:
        raise ValueError("Update signer differs from installed Development signer")
    if new_version <= old_version:
        raise ValueError("Update must increase versionCode")
    return {"status": "read_only_compatible", "package": PACKAGE,
            "old_version_code": old_version, "new_version_code": new_version,
            "candidate_sha256": candidate_sha, "certificate_sha256": new_cert,
            "source_sha": evidence["source_sha"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--serial")
    opts = parser.parse_args(argv)
    print(json.dumps(verify_upgrade(opts.candidate, opts.receipt, opts.serial), indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        print(f"Upgrade preflight refused: {exc}", file=sys.stderr)
        sys.exit(1)
