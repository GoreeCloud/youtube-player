"""Tests for removable USB directory and mount identity safeguards."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / "scripts/verify_usb_backup_destination.py"
spec = importlib.util.spec_from_file_location("usb_backup_guard", SOURCE)
usb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usb)
UUID = "22BF4F1E38A27405"


class USBBackupDestinationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.mount = Path(self.temp.name) / "Media Drive"
        self.target = self.mount.joinpath(*usb.EXPECTED_SUBDIR)
        self.target.mkdir(parents=True)

    def fake_command(self, options="rw,nodev", source="/dev/sdb"):
        def simulate(*args):
            if args[0] == "findmnt":
                return json.dumps({"filesystems": [{"source": source, "target": str(self.mount),
                    "fstype": "ntfs3", "options": options}]})
            if args[0] == "blkid":
                return UUID
            raise AssertionError("Unexpected command")
        return simulate

    def test_matching_uuid_and_goreecloud_tree(self):
        with patch.object(usb, "command", side_effect=self.fake_command()):
            result = usb.verify_usb_backup_dir(self.target, UUID.lower())
        self.assertEqual(result["status"], "verified_read_only")
        self.assertEqual(result["backup_directory"], str(self.target))

    def test_refuses_wrong_volume_uuid(self):
        with patch.object(usb, "command", side_effect=self.fake_command()):
            with self.assertRaisesRegex(ValueError, "Wrong USB volume"):
                usb.verify_usb_backup_dir(self.target, "0" * 16)

    def test_refuses_storage_outside_goreecloud(self):
        other = self.mount / "backups"
        other.mkdir()
        with patch.object(usb, "command", side_effect=self.fake_command()):
            with self.assertRaisesRegex(ValueError, "GoreeCloud USB root"):
                usb.verify_usb_backup_dir(other, UUID)

    def test_refuses_unmounted_laptop_storage(self):
        with patch.object(usb, "command", side_effect=self.fake_command(source="/dev/root")):
            with self.assertRaisesRegex(ValueError, "Wrong USB volume"):
                usb.verify_usb_backup_dir(self.target, "0" * 16)
        with patch.object(usb, "command", side_effect=self.fake_command(source="overlay")):
            with self.assertRaisesRegex(ValueError, "not mounted"):
                usb.verify_usb_backup_dir(self.target, UUID)

    def test_refuses_read_only_removable_storage(self):
        with patch.object(usb, "command", side_effect=self.fake_command(options="ro,nodev")):
            with self.assertRaisesRegex(ValueError, "read-write"):
                usb.verify_usb_backup_dir(self.target, UUID)

    def test_refuses_symlinked_backup_directory(self):
        link = self.mount / "backups-link"
        link.symlink_to(self.target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            usb.verify_usb_backup_dir(link, UUID)


    def test_key_custody_cli_checks_usb_before_credentials(self):
        key_script = SOURCE.with_name("provision_android_dev_signing.py")
        spec = importlib.util.spec_from_file_location("dev_key_custody", key_script)
        custody = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custody)
        with patch.object(custody, "execute", side_effect=RuntimeError("unexpected USB")):
            with patch.object(custody, "require_env") as credentials:
                with self.assertRaisesRegex(RuntimeError, "unexpected USB"):
                    custody.main([
                        "--verify-recovery",
                        "--primary", "/missing/key.p12",
                        "--encrypted-backup", str(self.target / "key.p12.gpg"),
                        "--expected-usb-uuid", UUID,
                    ])
                credentials.assert_not_called()


if __name__ == "__main__":
    unittest.main()
