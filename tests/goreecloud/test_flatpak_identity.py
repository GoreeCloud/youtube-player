from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
FLATPAK_ID = "com.goreecloud.youtubeplayer.Dev"


class FlatpakIdentityTests(unittest.TestCase):
    def test_appstream_identity_and_provenance(self):
        root = ET.parse(ROOT / "metadata/flatpak" / (FLATPAK_ID + ".metainfo.xml")).getroot()
        self.assertEqual(root.findtext("id"), FLATPAK_ID)
        self.assertIn("GoreeCloud", root.findtext("name", ""))
        self.assertEqual(root.findtext("launchable"), FLATPAK_ID + ".desktop")
        self.assertIn("AGPL-3.0", root.findtext("project_license", ""))
        self.assertIsNone(root.find("screenshots"))
        self.assertNotIn("nonbili", ET.tostring(root, encoding="unicode"))

    def test_no_inherited_launcher_identity(self):
        desktop = (ROOT / "metadata/flatpak" / (FLATPAK_ID + ".desktop")).read_text()
        manifest = (ROOT / "flatpak" / (FLATPAK_ID + ".yml")).read_text()
        self.assertIn("Icon=" + FLATPAK_ID, desktop)
        self.assertIn("x-scheme-handler/goreecloud-youtube-player", desktop)
        self.assertIn("app-id: " + FLATPAK_ID, manifest)
        self.assertIn("/app/main/goreecloud-youtube-player", manifest)
        self.assertNotIn("jp.nonbili", manifest)
        self.assertNotIn("noutube-dev", manifest)


if __name__ == "__main__":
    unittest.main()
