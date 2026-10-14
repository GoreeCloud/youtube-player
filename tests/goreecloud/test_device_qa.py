"""Safe no-write Android device QA preflight regression tests."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "qa_android_device.py"
spec = importlib.util.spec_from_file_location("goreecloud_device_qa", MODULE_PATH)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


class DeviceQATests(unittest.TestCase):
    def test_only_arm64_debug_apks_eligible(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "app-arm64-v8a-foss-debug.apk"
            path.write_bytes(b"dummy")
            self.assertTrue(qa.eligible_apk(path))
            self.assertFalse(qa.eligible_apk(path.with_name("app-universal-foss-debug.apk")))
            self.assertFalse(qa.eligible_apk(path.with_name("app-arm64-v8a-full-release.apk")))

    def test_preflight_rejects_existing_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "app-arm64-v8a-foss-debug.apk"
            apk.write_bytes(b"dummy")
            def response(*args):
                if "ro.build.version.sdk" in args: return "36"
                if "ro.product.cpu.abilist" in args: return "arm64-v8a"
                if "pm" in args: return "package:/data/app/com.goreecloud.youtubeplayer/base.apk"
                return "DE2117"
            with patch.object(qa, "run", side_effect=response):
                with self.assertRaisesRegex(RuntimeError, "already installed"):
                    qa.inspect(apk, "test")

    def test_readonly_preflight_never_installs_or_launches(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk = Path(tmp) / "app-arm64-v8a-foss-debug.apk"
            apk.write_bytes(b"dummy")
            commands = []
            def response(*args):
                commands.append(args)
                if "ro.build.version.sdk" in args: return "36"
                if "ro.product.cpu.abilist" in args: return "arm64-v8a"
                if "pm" in args: return ""
                return "DE2117"
            with patch.object(qa, "authorized_device", return_value="test"), patch.object(qa, "run", side_effect=response):
                self.assertEqual(qa.main([str(apk)]), 0)
            self.assertFalse(any("install" in cmd or "monkey" in cmd for cmd in commands))
            self.assertEqual(len([cmd for cmd in commands if "apksigner" in cmd]), 1)


if __name__ == "__main__":
    unittest.main()
