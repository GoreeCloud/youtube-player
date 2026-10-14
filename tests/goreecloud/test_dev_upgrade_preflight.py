"""Non-destructive Development upgrade preflight regression tests."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("dev_upgrade", ROOT / "scripts/qa_android_dev_upgrade.py")
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
CERT = "c" * 64


class DevelopmentUpgradeTests(unittest.TestCase):
    def test_accepts_correct_package_and_signer(self):
        def response(*args, **kwargs):
            if args[:2] == ("adb", "devices"):
                return "List of devices attached\nmockdevice device product:test"
            if "ro.product.cpu.abilist" in args:
                return "arm64-v8a,armeabi-v7a"
            if "pm" in args:
                return "package:/data/app/sample/base.apk"
            return ""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "candidate.apk"
            p.write_bytes(b"APK")
            receipt = Path(tmp) / "candidate.receipt.json"
            receipt.write_text(json.dumps({
                "package": qa.PACKAGE, "signed_sha256": hashlib.sha256(b"APK").hexdigest(),
                "certificate_sha256": CERT, "version_code": 205,
                "source_sha": "a" * 40, "status": "locally_signed_not_distributed"}))
            with patch.object(qa, "command", side_effect=response) as cmd:
                with patch.object(qa, "apk_identity", side_effect=[(205, CERT), (204, CERT)]):
                    result = qa.verify_upgrade(p, receipt)
            self.assertEqual(result["status"], "read_only_compatible")
            self.assertEqual(result["old_version_code"], 204)
            self.assertFalse(any("install" in args or "uninstall" in args for args, _ in [(x.args, x.kwargs) for x in cmd.call_args_list]))

    def test_wrong_cert_and_downgrade_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "candidate.apk"
            p.write_bytes(b"APK")
            receipt = Path(tmp) / "receipt.json"
            receipt.write_text(json.dumps({
                "package": qa.PACKAGE, "signed_sha256": hashlib.sha256(b"APK").hexdigest(),
                "certificate_sha256": CERT, "version_code": 205,
                "source_sha": "a" * 40, "status": "locally_signed_not_distributed"}))
            def response(*args, **kwargs):
                if args[:2] == ("adb", "devices"):
                    return "List of devices attached\nmockdevice device"
                if "ro.product.cpu.abilist" in args:
                    return "arm64-v8a"
                if "pm" in args:
                    return "package:/data/app/sample/base.apk"
                return ""
            for old_version, old_cert, error in [(204, "d" * 64, "signer"), (205, CERT, "versionCode")]:
                with self.subTest(error=error), patch.object(qa, "command", side_effect=response):
                    with patch.object(qa, "apk_identity", side_effect=[(205, CERT), (old_version, old_cert)]):
                        with self.assertRaisesRegex(ValueError, error):
                            qa.verify_upgrade(p, receipt)

    def test_absent_baseline_is_not_approved_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "candidate.apk"
            p.write_bytes(b"APK")
            receipt = Path(tmp) / "receipt.json"
            receipt.write_text(json.dumps({
                "package": qa.PACKAGE, "signed_sha256": hashlib.sha256(b"APK").hexdigest(),
                "certificate_sha256": CERT, "version_code": 205,
                "source_sha": "a" * 40, "status": "locally_signed_not_distributed"}))
            def response(*args, **kwargs):
                if args[:2] == ("adb", "devices"):
                    return "List of devices attached\nmockdevice device"
                if "ro.product.cpu.abilist" in args:
                    return "arm64-v8a"
                return ""
            with patch.object(qa, "command", side_effect=response):
                with patch.object(qa, "apk_identity", return_value=(205, CERT)):
                    with self.assertRaisesRegex(RuntimeError, "missing"):
                        qa.verify_upgrade(p, receipt)

    def test_receipt_mismatch_stops_before_adb(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "candidate.apk"
            p.write_bytes(b"APK")
            receipt = Path(tmp) / "receipt.json"
            receipt.write_text(json.dumps({"package": qa.PACKAGE, "signed_sha256": "0" * 64}))
            with patch.object(qa, "command") as cmd:
                with patch.object(qa, "apk_identity", return_value=(205, CERT)):
                    with self.assertRaisesRegex(ValueError, "receipt"):
                        qa.verify_upgrade(p, receipt)
                cmd.assert_not_called()


if __name__ == "__main__":
    unittest.main()
