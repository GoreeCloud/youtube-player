#!/usr/bin/env python3
"""Fail-closed verification of generated development Android sources."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "android"
GRADLE = ANDROID / "app" / "build.gradle"
MANIFEST = ANDROID / "app" / "src" / "main" / "AndroidManifest.xml"
PKG = "com.goreecloud.youtubeplayer"
EXPO_SCHEME = "goreecloud-youtube-player"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify() -> None:
    require(GRADLE.is_file(), "Android Gradle application file missing: prebuild not complete")
    require(MANIFEST.is_file(), "Android manifest missing: prebuild not complete")
    gradle = GRADLE.read_text(encoding="utf-8")
    require(re.search(r"applicationId\s+['\"]" + re.escape(PKG) + r"['\"]", gradle),
            f"Expected {PKG} applicationId")
    require(re.search(r"namespace\s+['\"]" + re.escape(PKG) + r"['\"]", gradle),
            f"Expected {PKG} namespace")
    require(re.search(r"flavorDimensions\s+['\"]distribution['\"]", gradle),
            "Missing distribution flavor dimension")
    require(re.search(r"\bfull\s*\{", gradle) and re.search(r"\bfoss\s*\{", gradle),
            "Missing full/foss flavors")
    release = re.search(r"\brelease\s*\{(.*?)\n\s*\}\n", gradle, re.S)
    require(release is not None, "Release buildType missing")
    require("signingConfig" not in release.group(1),
            "Release must not implicitly inherit ephemeral debug signing")
    development = re.search(r"\bdevelopment\s*\{(.*?)\n\s*\}", gradle, re.S)
    require(development is not None, "Independent Development build type missing")
    dev = development.group(1)
    require("applicationIdSuffix '.dev'" in dev,
            "Development must install under a separate .dev package")
    require("versionNameSuffix '-dev'" in dev and "debuggable false" in dev,
            "Development is not a debug-enabled or normal release build")
    require("initWith release" in dev, "Development must bundle its JS and resources")
    require("signingConfig" not in dev, "Development must NEVER inherit debug signing")
    import json
    metadata = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    require(isinstance(metadata.get("versionCode"), int) and metadata["versionCode"] >= 2,
            "Development versionCode must exceed prior QA baseline 1")

    android_ns = "{http://schemas.android.com/apk/res/android}"
    tree = ET.parse(MANIFEST)
    app = tree.find("application")
    require(app is not None, "Android application manifest element missing")
    activity = next((a for a in app.findall("activity")
                     if a.attrib.get(android_ns + "name", "").endswith("MainActivity")), None)
    require(activity is not None, "MainActivity not present")
    require(activity.attrib.get(android_ns + "supportsPictureInPicture") == "true",
            "Picture-in-picture capability lost")
    urls = [node.attrib.get(android_ns + "scheme", "")
            for node in activity.iter("data")]
    require(EXPO_SCHEME in urls, "GoreeCloud deep-link scheme not registered")
    require("noutube" not in " ".join(urls).lower(), "Legacy NouTube scheme still registered")
    print("Android source verified: identity, flavors, PiP, deep link; no release debug-signing.")


if __name__ == "__main__":
    try:
        verify()
    except (AssertionError, ET.ParseError) as error:
        print(f"Android validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
