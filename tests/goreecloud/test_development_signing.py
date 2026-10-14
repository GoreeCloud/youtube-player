"""Signing lane must remain independent, non-distributing, and fail closed."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("dev_signing", ROOT / "scripts/sign_android_development.py")
signer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(signer)


class DevelopmentSigningGate(unittest.TestCase):
    def test_independent_package_and_non_decreasing_version_floor(self):
        package = json.loads((ROOT / "package.json").read_text())
        plugin = (ROOT / "plugins/withAndroidPlugin.ts").read_text()
        self.assertGreaterEqual(package["versionCode"], 2)
        self.assertIn("applicationIdSuffix '.dev'", plugin)
        self.assertIn("initWith release", plugin)
        self.assertIn("debuggable false", plugin)
        self.assertNotIn("signingConfig signingConfigs.debug\n        }\n        debug {", plugin)

    def test_ci_never_uses_signing_keys_or_exposes_signed_apks(self):
        workflow = (ROOT / ".github/workflows/android-unsigned-development.yml").read_text()
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("default: false", workflow)
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertIn("retention-days: 1", workflow)
        self.assertIn("development-unsigned.apk", workflow)
        self.assertIn("signing=NONE", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("pull_request:", workflow)
        self.assertNotIn("push:", workflow)
        self.assertNotIn("apksigner sign", workflow)
        standard = (ROOT / ".github/workflows/android-development.yml").read_text()
        self.assertIn("assembleFossDevelopment", standard)
        self.assertIn("Development APK unexpectedly signed", standard)
        self.assertIn("name '*debug.apk'", standard)

    def test_unsigned_apk_checks_origin_and_checksum(self):
        with tempfile.TemporaryDirectory() as temp:
            apk = Path(temp) / "app-foss-arm64-v8a-development-unsigned.apk"
            apk.write_bytes(b"test")
            import hashlib
            expected = hashlib.sha256(b"test").hexdigest()
            package_line = "package: name='com.goreecloud.youtubeplayer.dev' versionCode='204' versionName='0.1.0-dev'"
            def fake_run(*args, **kwargs):
                if args[0] == "aapt":
                    return SimpleNamespace(stdout=package_line, returncode=0)
                return SimpleNamespace(stdout="", returncode=1)
            with patch.object(signer, "command", side_effect=fake_run):
                self.assertEqual(signer.inspect_unsigned(apk, expected), (expected, 204))
                with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                    signer.inspect_unsigned(apk, "0" * 64)
                with patch.object(signer, "command", return_value=SimpleNamespace(stdout=package_line.replace(".dev", ".other"), returncode=0)):
                    with self.assertRaisesRegex(ValueError, "Wrong Android"):
                        signer.inspect_unsigned(apk, expected)

    def test_no_key_no_sign_and_output_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            apk = Path(temp) / "app-foss-arm64-v8a-development-unsigned.apk"
            apk.write_bytes(b"test")
            output = Path(temp) / "signed.apk"
            keystore = Path(temp) / "owner.p12"
            keystore.write_bytes(b"test")
            keystore.chmod(0o600)
            import hashlib
            digest = hashlib.sha256(b"test").hexdigest()
            args = ["--input", str(apk), "--output", str(output),
                    "--keystore", str(keystore), "--source-sha", "a" * 40,
                    "--unsigned-sha256", digest, "--expected-cert-sha256", "b" * 64,
                    "--first-issue"]
            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaisesRegex(ValueError, "variable missing"):
                    signer.main(args)
            keystore.chmod(0o644)
            with self.assertRaisesRegex(ValueError, "owner-only"):
                signer.main(args)


if __name__ == "__main__":
    unittest.main()
