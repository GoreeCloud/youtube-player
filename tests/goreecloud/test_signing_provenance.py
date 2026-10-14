"""Fail-closed CI provenance checks for GoreeCloud unsigned Android candidates."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "sign_android_development.py"
spec = importlib.util.spec_from_file_location("goreecloud_sign_provenance", SCRIPT)
signer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(signer)

APK = "app-foss-arm64-v8a-development-unsigned.apk"
SHA = "a" * 40
DIGEST = "b" * 64


def evidence(sha=SHA, digest=DIGEST, package=signer.PKG, version="204", run="12345"):
    return (f"source_sha={sha}\nrun_id={run}\nsigning=NONE\n"
            f"application_id={package}\nversion_code={version}\n"
            f"{digest}  {APK}\n")


class ProvenanceTests(unittest.TestCase):
    def test_exact_evidence_matches_candidate(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "provenance.txt"
            path.write_text(evidence())
            self.assertIsNone(signer.inspect_provenance(path, SHA, DIGEST, APK, 204))

    def test_mismatched_critical_fields_fail_closed(self):
        changes = (
            evidence(sha="0" * 40), evidence(digest="0" * 64),
            evidence(package="com.invalid.app"), evidence(version="205"),
            evidence(run="not-a-ci-run"),
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "provenance.txt"
            for data in changes:
                with self.subTest(data=data.splitlines()[0]):
                    path.write_text(data)
                    with self.assertRaises(ValueError):
                        signer.inspect_provenance(path, SHA, DIGEST, APK, 204)

    def test_duplicated_ci_field_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "provenance.txt"
            path.write_text(evidence() + "source_sha=" + SHA + "\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                signer.inspect_provenance(path, SHA, DIGEST, APK, 204)

    def test_cli_checks_ci_provenance_before_signing(self):
        content = SCRIPT.read_text()
        start = content.index("def main(")
        self.assertLess(content.index("inspect_unsigned(", start),
                        content.index("inspect_provenance(", start))
        self.assertLess(content.index("inspect_provenance(", start),
                        content.index('command("zipalign"', start))
        self.assertIn('"--provenance", type=Path, required=True', content)


if __name__ == "__main__":
    unittest.main()
