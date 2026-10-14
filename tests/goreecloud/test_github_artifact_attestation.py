"""CI artifact provenance must be authenticated before owner-side signing."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/sign_android_development.py"
spec = importlib.util.spec_from_file_location("ci_attestation", SCRIPT)
signer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(signer)
SHA = "a" * 40
APK = "app-foss-arm64-v8a-development-unsigned.apk"


def sample(folder):
    apk = Path(folder) / APK
    apk.write_bytes(b"test APK")
    receipt = Path(folder) / "provenance.txt"
    receipt.write_text(
        f"source_sha={SHA}\nrun_id=456\nsigning=NONE\n"
        f"application_id={signer.PKG}\nversion_code=204\n"
        f"{hashlib.sha256(apk.read_bytes()).hexdigest()}  {APK}\n")
    return apk, receipt


def fake_actions(apk, provenance, login="GoreeCloud", outcome="success",
                 expired=False, tampered=False):
    def command(*args, **kwargs):
        if args[:3] == ("gh", "api", "user"):
            return SimpleNamespace(stdout=login)
        if args[:2] == ("gh", "api") and "/artifacts?" in args[-1]:
            return SimpleNamespace(stdout=json.dumps({"artifacts": [{
                "name": "unsigned-development-" + SHA,
                "id": 123, "expired": expired}]}))
        if args[:2] == ("gh", "api"):
            return SimpleNamespace(stdout=json.dumps({
                "name": "Android unsigned Development candidate",
                "head_branch": "main", "event": "workflow_dispatch",
                "head_sha": SHA, "status": "completed",
                "conclusion": outcome,
                "repository": {"full_name": "GoreeCloud/youtube-player"}}))
        if args[:3] == ("gh", "run", "download"):
            folder = Path(args[-1])
            (folder / APK).write_bytes(b"altered" if tampered else apk.read_bytes())
            (folder / "provenance.txt").write_bytes(provenance.read_bytes())
            return SimpleNamespace(stdout="")
        raise AssertionError("Unexpected command")
    return command


class GithubOriginalArtifactTests(unittest.TestCase):
    def test_original_artifact_matches(self):
        with tempfile.TemporaryDirectory() as folder:
            apk, provenance = sample(folder)
            with patch.object(signer, "command", side_effect=fake_actions(apk, provenance)):
                self.assertIsNone(signer.verify_original_ci_artifact(apk, provenance, SHA))

    def test_wrong_account_or_failed_ci_are_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            apk, provenance = sample(folder)
            for options, label in (({"login": "Other"}, "identity"),
                                   ({"outcome": "failure"}, "approved")):
                with self.subTest(options=options):
                    with patch.object(signer, "command", side_effect=fake_actions(apk, provenance, **options)):
                        with self.assertRaisesRegex(ValueError, label):
                            signer.verify_original_ci_artifact(apk, provenance, SHA)

    def test_expired_or_modified_ci_artifact_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            apk, provenance = sample(folder)
            for options, label in (({"expired": True}, "expired"),
                                   ({"tampered": True}, "differs")):
                with self.subTest(options=options):
                    with patch.object(signer, "command", side_effect=fake_actions(apk, provenance, **options)):
                        with self.assertRaisesRegex(ValueError, label):
                            signer.verify_original_ci_artifact(apk, provenance, SHA)

    def test_attestation_before_signing(self):
        source = SCRIPT.read_text()
        main_index = source.index("def main(")
        self.assertLess(source.index("verify_original_ci_artifact(", main_index),
                        source.index('command("zipalign"', main_index))


if __name__ == "__main__":
    unittest.main()
