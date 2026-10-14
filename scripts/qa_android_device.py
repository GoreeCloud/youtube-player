#!/usr/bin/env python3
"""Bounded first-install Android QA. Never uninstalls, upgrades or publishes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

PACKAGE = "com.goreecloud.youtubeplayer"


def run(*args):
    return subprocess.run(args, text=True, capture_output=True, check=True).stdout.strip()


def eligible_apk(path):
    name = path.name.lower()
    return (path.is_file() and name.endswith("-debug.apk") and
            "arm64-v8a" in name and ("foss" in name or "full" in name))


def apk_package(apk):
    # Never rely on the filename alone to identify an installable APK.
    if shutil.which("aapt"):
        metadata = run("aapt", "dump", "badging", str(apk))
        match = re.search(r"^package: name='([^']+)'", metadata, re.MULTILINE)
        if match:
            return match.group(1)
    elif shutil.which("aapt2"):
        return run("aapt2", "dump", "packagename", str(apk)).strip()
    raise RuntimeError("aapt or aapt2 is required to inspect the APK package identity")


def authorized_device(requested):
    lines = run("adb", "devices", "-l").splitlines()[1:]
    devices = [line.split()[0] for line in lines if len(line.split()) > 1 and line.split()[1] == "device"]
    if requested:
        if requested not in devices:
            raise RuntimeError("Requested ADB serial is not authorized")
        return requested
    if len(devices) != 1:
        raise RuntimeError("Exactly one authorized ADB device is required, or supply --serial")
    return devices[0]


def already_installed(serial):
    try:
        return bool(run("adb", "-s", serial, "shell", "pm", "path", PACKAGE))
    except subprocess.CalledProcessError as exc:
        # Android's package manager can return exit 1 with no output when the
        # package is absent. Device-offline, permission and transport errors
        # contain diagnostic output and must remain hard failures.
        if exc.returncode == 1 and not (exc.stdout or "").strip() and not (exc.stderr or "").strip():
            return False
        raise


def inspect(apk, serial):
    if not eligible_apk(apk):
        raise RuntimeError("Only existing FOSS/Full arm64-v8a debug APKs are eligible")
    run("apksigner", "verify", "--verbose", str(apk))
    if apk_package(apk) != PACKAGE:
        raise RuntimeError("APK package identity mismatch")
    model = run("adb", "-s", serial, "shell", "getprop", "ro.product.model")
    abi = run("adb", "-s", serial, "shell", "getprop", "ro.product.cpu.abilist")
    sdk = int(run("adb", "-s", serial, "shell", "getprop", "ro.build.version.sdk"))
    if "arm64-v8a" not in abi or sdk < 23:
        raise RuntimeError("Unsupported Android target architecture or API level")
    if already_installed(serial):
        raise RuntimeError("Package already installed; no upgrades, replacement, or data changes allowed")
    digest = hashlib.sha256(apk.read_bytes()).hexdigest()
    return {"package": PACKAGE, "apk_name": apk.name, "sha256": digest,
            "device_model": model, "android_api": sdk, "installed_before": False,
            "time_utc": datetime.now(timezone.utc).isoformat()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--serial", help="Explicit authorized ADB serial (not recorded)")
    parser.add_argument("--install", action="store_true", help="Explicitly permit first install + launch")
    parser.add_argument("--expected-sha256", help="SHA-256 from the verified GitHub build evidence")
    parser.add_argument("--report", type=Path, help="Write sanitized JSON evidence; fails if already exists")
    args = parser.parse_args(argv)
    serial = authorized_device(args.serial)
    details = inspect(args.apk.resolve(), serial)
    if args.expected_sha256 and details["sha256"] != args.expected_sha256.lower():
        raise RuntimeError("APK SHA-256 does not match verified build evidence")
    if args.install and not args.expected_sha256:
        raise RuntimeError("First installation requires --expected-sha256 from CI evidence")
    details["result"] = "verified_only"
    if args.install:
        run("adb", "-s", serial, "install", str(args.apk.resolve()))
        installed = run("adb", "-s", serial, "shell", "pm", "path", PACKAGE)
        if not installed:
            raise RuntimeError("ADB install returned success but target package was not found")
        details["result"] = "installed"
        try:
            run("adb", "-s", serial, "shell", "monkey", "-p", PACKAGE,
                "-c", "android.intent.category.LAUNCHER", "1")
            details["result"] = "launch_sent"
            details["process_running"] = bool(run("adb", "-s", serial, "shell", "pidof", PACKAGE))
        except subprocess.CalledProcessError:
            details["result"] = "launch_failed"
    print(json.dumps(details, indent=2))
    if args.report:
        with args.report.open("x", encoding="utf-8") as f:
            json.dump(details, f, indent=2)
    if details["result"] == "launch_failed":
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"QA preflight stopped: {exc}", file=sys.stderr)
        sys.exit(1)
