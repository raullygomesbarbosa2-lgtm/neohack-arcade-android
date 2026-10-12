#!/usr/bin/env python3
"""Vortix 0.9.14: keep the Arcade core choices visible in Android AlertDialog."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()

old_message = '                .setMessage("MAME 2010 requer ROMset 0.139 em ZIP. Se o jogo veio de outro ROMset, escolha o MAME/FBNeo compatível; um conjunto de outra versão pode não abrir.")\n'
if text.count(old_message) != 1:
    raise SystemExit(f"Expected one MAME 2010 chooser message; found {text.count(old_message)}")
text = text.replace(old_message, "", 1)
old_title = '                .setTitle("Escolha o núcleo que combina com o ROMset")\n'
if text.count(old_title) != 1:
    raise SystemExit(f"Expected one Arcade core chooser title; found {text.count(old_title)}")
text = text.replace(old_title, '                .setTitle("Escolha o núcleo (MAME 2010: ROMset 0.139)")\n', 1)
activity.write_text(text)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 22\n        versionName '0.9.13'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected official Vortix 0.9.13 version markers")
build.write_text(build_text.replace(old_version, "versionCode 23\n        versionName '0.9.14'", 1))
print("Fixed the Arcade chooser list and bumped Vortix to 0.9.14.")
