"""Enforce development-safe defaults on inherited iOS store publication paths."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
GATE = "GOREECLOUD_IOS_STORE_PUBLISH_AUTHORIZED"


class StorePublicationGuards(unittest.TestCase):
    def test_bun_entrypoint_refuses_implicit_publishing(self):
        source = (ROOT / "scripts/upload-app-store.ts").read_text()
        self.assertIn(f"process.env.{GATE} !== '1'", source)
        self.assertLess(source.index(GATE), source.index("await packageInfo()"))
        self.assertLess(source.index(GATE), source.index("requireEnv('APP_STORE_KEY_ID')"))
        for flag in ("IOS_SUBMIT_FOR_REVIEW", "IOS_REJECT_IF_POSSIBLE", "IOS_AUTOMATIC_RELEASE"):
            self.assertIn(f"envFlag('{flag}', false)", source)

    def test_fastlane_lanes_are_independently_guarded(self):
        source = (ROOT / "fastlane-config/ios/Fastfile").read_text()
        for lane in ("upload_ipa do |options|", "upload_screenshots do"):
            section = source.split(lane, 1)[1]
            self.assertIn(f'ENV["{GATE}"] == "1"', section.split("upload_to_app_store(", 1)[0])
        self.assertEqual(source.count(f'ENV["{GATE}"] == "1"'), 2)


if __name__ == "__main__":
    unittest.main()
