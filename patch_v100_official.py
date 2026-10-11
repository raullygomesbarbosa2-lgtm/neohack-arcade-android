#!/usr/bin/env python3
"""Promote Vortix Test 3's UI and macros to official Vortix 0.9.10."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
build = ROOT / "app/build.gradle"
text = build.read_text()
old_package = "applicationId 'br.com.raully.neohackarcade.test099'"
if text.count(old_package) != 1:
    raise SystemExit(f"Expected Test 3 application ID exactly once; found {text.count(old_package)}")
text = text.replace(old_package, "applicationId 'br.com.raully.neohackarcade'", 1)
old_version = "versionCode 18\n        versionName '0.9.9-cyan-macros'"
if text.count(old_version) != 1:
    raise SystemExit("Expected Vortix Test 3 version markers before official release bump")
text = text.replace(old_version, "versionCode 19\n        versionName '0.9.10'", 1)
build.write_text(text)

manifest = ROOT / "app/src/main/AndroidManifest.xml"
manifest_text = manifest.read_text()
old_label = 'android:label="Vortix Test 3"'
if manifest_text.count(old_label) != 1:
    raise SystemExit("Expected exactly one Vortix Test 3 launcher label")
manifest.write_text(manifest_text.replace(old_label, 'android:label="Vortix"', 1))
print("Promoted Test 3 cyan theme and editable per-game A+B/C+D defaults into official Vortix 0.9.10")
