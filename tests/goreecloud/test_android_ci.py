from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class AndroidCIGates(unittest.TestCase):
    def test_workflow_is_read_only_and_does_not_distribute(self):
        workflow = (ROOT / ".github/workflows/android-development.yml").read_text()
        self.assertIn("contents: read", workflow)
        self.assertIn("--frozen-lockfile --ignore-scripts", workflow)
        self.assertIn("expo prebuild --platform android --clean --no-install", workflow)
        self.assertIn("assembleFossDebug", workflow)
        self.assertIn("assembleFullDebug", workflow)
        self.assertIn("verify-android-prebuild.py", workflow)
        self.assertNotIn("upload-artifact@", workflow)
        self.assertNotIn("release-action@", workflow)
        self.assertNotIn("secrets.", workflow)

    def test_identity_verifier_is_explicit(self):
        validator = (ROOT / "scripts/verify-android-prebuild.py").read_text()
        self.assertIn("com.goreecloud.youtubeplayer", validator)
        self.assertIn("goreecloud-youtube-player", validator)
        self.assertIn("supportsPictureInPicture", validator)
        self.assertIn('Missing full/foss flavors', validator)


if __name__ == "__main__":
    unittest.main()
