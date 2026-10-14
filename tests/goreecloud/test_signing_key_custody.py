"""Private Development key-custody guards; no real owner keys or backups."""
import importlib.util
import os
from pathlib import Path
import secrets
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/provision_android_dev_signing.py"
spec = importlib.util.spec_from_file_location("dev_custody", SCRIPT)
custody = importlib.util.module_from_spec(spec)
spec.loader.exec_module(custody)


class KeyCustodyTests(unittest.TestCase):
    def test_rejects_missing_or_unrecoverable_owner_secrets(self):
        envs = [
            {},
            {custody.STORE_ENV: "short", custody.KEY_ENV: "short",
             custody.BACKUP_ENV: "backup-long-" * 3},
            {custody.STORE_ENV: "store-password-" * 3,
             custody.KEY_ENV: "different-" * 4, custody.BACKUP_ENV: "backup-password-" * 3},
            {custody.STORE_ENV: "repeated-password-" * 3,
             custody.KEY_ENV: "repeated-password-" * 3,
             custody.BACKUP_ENV: "repeated-password-" * 3},
        ]
        for env in envs:
            with self.subTest(fields=set(env)), patch.dict(os.environ, env, clear=True):
                with self.assertRaises(ValueError):
                    custody.require_env()

    def test_owner_secrets_never_echoed_by_failed_subprocess(self):
        with patch.object(custody.subprocess, "run", return_value=SimpleNamespace(
                returncode=1, stdout="SECRET", stderr="SECRET")):
            with self.assertRaisesRegex(RuntimeError, "Protected key operation failed") as x:
                custody.execute("keytool", "-list")
            self.assertNotIn("SECRET", str(x.exception))

    def test_same_filesystem_backup_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            primary = root / "development.p12"
            backup = root / "development.p12.gpg"
            with self.assertRaisesRegex(ValueError, "different mounted filesystem"):
                custody.validate_paths(primary, backup, create=True)

    def test_rejects_owner_world_readable_directory(self):
        if not Path("/dev/shm").is_dir():
            self.skipTest("Independent temporary filesystem unavailable")
        with tempfile.TemporaryDirectory() as folder:
            with tempfile.TemporaryDirectory(dir="/dev/shm") as mirror:
                root = Path(folder)
                root.chmod(0o755)
                with self.assertRaisesRegex(ValueError, "0700"):
                    custody.validate_paths(root / "development.p12",
                                           Path(mirror) / "development.p12.gpg",
                                           create=True)

    def test_validates_keytool_certificate_fingerprint(self):
        digest = "AB:" * 31 + "AB"
        with patch.object(custody, "execute", return_value="SHA256: " + digest):
            self.assertEqual(custody.certificate(Path("/fake/development.p12"),
                                                 custody.ALIAS), "ab" * 32)
        with patch.object(custody, "execute", return_value="invalid output"):
            with self.assertRaisesRegex(ValueError, "one certificate"):
                custody.certificate(Path("/fake/development.p12"), custody.ALIAS)

    def test_disallows_overwriting_primary_or_backup(self):
        if not Path("/dev/shm").is_dir():
            self.skipTest("Independent temporary filesystem unavailable")
        with tempfile.TemporaryDirectory() as folder:
            with tempfile.TemporaryDirectory(dir="/dev/shm") as mirror:
                key = Path(folder) / "development.p12"
                backup = Path(mirror) / "development.p12.gpg"
                key.write_bytes(b"not-a-real-key")
                with self.assertRaisesRegex(ValueError, "overwrite"):
                    custody.validate_paths(key, backup, create=True)
                key.unlink()
                backup.write_bytes(b"not-a-real-backup")
                with self.assertRaisesRegex(ValueError, "overwrite"):
                    custody.validate_paths(key, backup, create=True)

    def test_refuses_private_key_inside_a_git_repository(self):
        if not Path("/dev/shm").is_dir():
            self.skipTest("Independent temporary filesystem unavailable")
        with tempfile.TemporaryDirectory() as folder:
            with tempfile.TemporaryDirectory(dir="/dev/shm") as mirror:
                (Path(folder) / ".git").mkdir()
                key = Path(folder) / "development.p12"
                backup = Path(mirror) / "development.p12.gpg"
                with self.assertRaisesRegex(ValueError, "outside Git repositories"):
                    custody.validate_paths(key, backup, create=True)

    def test_refuses_symlinked_private_directory(self):
        if not Path("/dev/shm").is_dir():
            self.skipTest("Independent temporary filesystem unavailable")
        with tempfile.TemporaryDirectory() as folder:
            with tempfile.TemporaryDirectory(dir="/dev/shm") as mirror:
                actual = Path(folder) / "real"
                actual.mkdir(mode=0o700)
                alternate = Path(folder) / "alias"
                alternate.symlink_to(actual, target_is_directory=True)
                with self.assertRaisesRegex(ValueError, "symlinked"):
                    custody.validate_paths(alternate / "key.p12",
                                           Path(mirror) / "key.p12.gpg",
                                           create=True)

    @unittest.skipUnless(os.environ.get("GC_SYNTHETIC_KEY_CUSTODY_TEST") == "1",
                         "Opt-in actual test-only keystore and encrypted backup recovery")
    def test_real_temporary_key_and_cross_device_encrypted_restore(self):
        if not Path("/dev/shm").is_dir():
            self.skipTest("Separate test-only tmpfs not available")
        with tempfile.TemporaryDirectory(prefix="goreecloud-synthetic-primary-") as work:
            with tempfile.TemporaryDirectory(prefix="goreecloud-synthetic-backup-",
                                             dir="/dev/shm") as mirror:
                primary = Path(work) / "synthetic.p12"
                backup = Path(mirror) / "synthetic.p12.gpg"
                password = secrets.token_urlsafe(34)
                backup_password = secrets.token_urlsafe(34)
                with patch.dict(os.environ, {
                    custody.STORE_ENV: password,
                    custody.KEY_ENV: password,
                    custody.BACKUP_ENV: backup_password,
                }):
                    result = custody.create_custody(primary, backup,
                                                     custody.ALIAS,
                                                     custody.require_env())
                    self.assertTrue(result["backup_restore_verified"])
                    restored = custody.verify_custody(primary, backup,
                                                       custody.ALIAS,
                                                       custody.require_env())
                    self.assertEqual(result["certificate_sha256"],
                                     restored["certificate_sha256"])
                    with self.assertRaisesRegex(ValueError, "overwrit"):
                        custody.validate_paths(primary, backup, create=True)
                    backup.write_bytes(b"tampered synthetic backup")
                    with self.assertRaises(RuntimeError):
                        custody.verify_custody(primary, backup, custody.ALIAS,
                                               custody.require_env())


if __name__ == "__main__":
    unittest.main()
