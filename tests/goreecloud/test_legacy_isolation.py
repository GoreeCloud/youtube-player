from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]

def source(filename: str) -> str:
    return (ROOT / filename).read_text()

class LegacyServiceIsolation(unittest.TestCase):
    def test_upstream_api_cannot_send_tokens(self):
        query = source("lib/query/index.ts")
        self.assertNotIn("a.inks.page", query)
        self.assertIn("throw new Error('Legacy account, purchase and sync APIs are disabled", query)
        self.assertNotIn("fetch(", query)

    def test_clients_do_not_restore_or_refresh_upstream_tokens(self):
        for filename in (
            "lib/supabase/client.ts",
            "lib/supabase/client.native.ts",
            "extension/lib/app/supabase-client.ts",
        ):
            with self.subTest(filename=filename):
                value = source(filename)
                self.assertIn("goreecloud-sync-unconfigured.invalid", value)
                self.assertIn("persistSession: false", value)
                self.assertIn("autoRefreshToken: false", value)
                self.assertNotIn("pgukcvgypvjwtibzlvhr", value)

    def test_mobile_cloud_sync_and_billing_off(self):
        page = source("components/page/MainPage.tsx")
        settings = source("components/modal/SettingsModalTabSync.tsx")
        self.assertNotIn("listenIosTransactions()", page)
        self.assertNotIn("onAuthStateChange", page)
        self.assertNotIn("noutube.inks.page", settings)
        self.assertNotIn("NouBilling", settings)
        self.assertIn("GoreeCloud Sync is not connected", settings)
        self.assertIn("const canSync = () => false", source("lib/supabase/sync.ts"))

    def test_extension_legacy_hosts_and_identity_removed(self):
        config = source("extension/wxt.config.ts")
        for host in ("pgukcvgypvjwtibzlvhr", "a.inks.page", "noutube.inks.page"):
            self.assertNotIn(host, config)
        self.assertNotIn("'identity',", config)
        self.assertIn("GoreeCloud YouTube Player", config)
        self.assertIn("const canSync = () => false", source("extension/lib/app/background-core.ts"))
        self.assertIn("throw new Error(DISABLED_MESSAGE)", source("extension/lib/app/auth.ts"))

    def test_desktop_has_no_upstream_auto_publisher(self):
        self.assertIn("export const isUpdateSupported = false", source("desktop/src/main/lib/auto-update.ts"))
        config = source("desktop/electron-builder.yml")
        self.assertIn("appId: com.goreecloud.youtubeplayer", config)
        self.assertNotIn("owner: nonbili", config)
        self.assertNotIn("provider: github", config)
        pkg = json.loads(source("desktop/package.json"))
        self.assertEqual(pkg["name"], "goreecloud-youtube-player-desktop")
        self.assertNotIn("noutube", pkg.get("devDependencies", {}))

if __name__ == "__main__":
    unittest.main()
