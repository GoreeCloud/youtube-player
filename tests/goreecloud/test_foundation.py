from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]

class GoreeCloudFoundationTests(unittest.TestCase):
    def test_application_identity(self):
        config = (ROOT / "app.config.ts").read_text()
        gradle = (ROOT / "android/app/build.gradle").read_text()
        self.assertIn("name: 'GoreeCloud YouTube Player'", config)
        self.assertIn("package: 'com.goreecloud.youtubeplayer'", config)
        self.assertIn("bundleIdentifier: 'com.goreecloud.youtubeplayer'", config)
        self.assertIn("applicationId 'com.goreecloud.youtubeplayer'", gradle)
        self.assertNotIn("appleTeamId:", config)

    def test_provenance(self):
        self.assertIn(
            "270a3e9b94df53eee9b7b9dd6b1f757fe739961e",
            (ROOT / "UPSTREAM.md").read_text()
        )
        license_text = (ROOT / "LICENSE").read_text()
        self.assertIn("GNU AFFERO GENERAL PUBLIC LICENSE", license_text)
        self.assertIn("Version 3", license_text)

    def test_package_identity(self):
        data = json.loads((ROOT / "package.json").read_text())
        self.assertEqual(data["name"], "goreecloud-youtube-player")
        self.assertEqual(data["version"], "0.1.0")
        self.assertGreaterEqual(data["versionCode"], 2)
        self.assertTrue(data["private"])

    def test_no_inherited_ci_release_jobs(self):
        filenames = {p.name for p in (ROOT / ".github/workflows").glob("*")}
        self.assertIn("foundation.yml", filenames)
        self.assertFalse(filenames & {
            "build.yml", "release-desktop.yml", "release-extension.yml", "flatpak-assets.yml"
        })

if __name__ == "__main__":
    unittest.main()
