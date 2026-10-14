#!/usr/bin/env python3
"""Read-only check for GoreeCloud removable-drive backup containment.

A USB mount name can change. Require its actual filesystem UUID before relying
on a path, and never create folders or write any key material here.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

EXPECTED_SUBDIR = ("GoreeCloud", "Backups", "Signing", "youtube-player")


def command(*args):
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode:
        raise ValueError("USB verification command failed: " + args[0])
    return result.stdout.strip()


def verify_usb_backup_dir(folder, uuid):
    if not re.fullmatch(r"[A-Za-z0-9-]{8,64}", uuid):
        raise ValueError("Expected removable filesystem UUID required")
    folder = folder.expanduser().absolute()
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("Backup directory must exist without symlinks")
    if any(item.is_symlink() for item in folder.parents):
        raise ValueError("Backup path traverses a symlink")
    mounted = json.loads(command(
        "findmnt", "--json", "-T", str(folder),
        "-o", "SOURCE,TARGET,FSTYPE,OPTIONS"))
    matches = mounted.get("filesystems", [])
    if len(matches) != 1:
        raise ValueError("Expected one mounted backup filesystem")
    data = matches[0]
    source = data.get("source", "")
    root = Path(data.get("target", "/"))
    if not source.startswith("/dev/") or root == Path("/"):
        raise ValueError("Removable storage is not mounted")
    if command("blkid", "-s", "UUID", "-o", "value", source).lower() != uuid.lower():
        raise ValueError("Wrong USB volume identity")
    if "rw" not in data.get("options", "").split(","):
        raise ValueError("USB storage is not mounted read-write")
    expected = root.joinpath(*EXPECTED_SUBDIR)
    if folder != expected or root.is_symlink():
        raise ValueError("Backup destination must be under the GoreeCloud USB root")
    return {"status": "verified_read_only", "filesystem": data.get("fstype"),
            "backup_directory": str(folder), "volume_uuid": uuid.upper()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup-directory", required=True, type=Path)
    parser.add_argument("--expected-uuid", required=True)
    args = parser.parse_args(argv)
    print(json.dumps(verify_usb_backup_dir(args.backup_directory,
                                            args.expected_uuid), indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print("GoreeCloud USB backup destination refused: " + str(error),
              file=sys.stderr)
        sys.exit(1)
