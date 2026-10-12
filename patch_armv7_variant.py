#!/usr/bin/env python3
"""Convert the generated ARM64 catalog app to a single-ABI ARMv7 build."""
from pathlib import Path

main = Path("app/src/main/java/br/com/raully/neohackarcade/MainActivity.java")
s = main.read_text(encoding="utf-8")
replacements = [
    ('NÚCLEOS • CATÁLOGO ARM64 • POC 190', 'NÚCLEOS • CATÁLOGO ARMv7 • POC 178'),
    ('Este catálogo local contém apenas núcleos ARM64. Use a versão arm64-v8a do app.', 'Este catálogo local contém núcleos ARMv7. Use a versão armeabi-v7a do app.'),
    ('Este núcleo exige uma versão ARM64 do app.', 'Este núcleo exige a versão ARMv7 do app.'),
    ('O pacote não contém a biblioteca ARM64 esperada:', 'O pacote não contém a biblioteca ARMv7 esperada:'),
    ('A biblioteca do pacote não é um arquivo ELF ARM64 válido:', 'A biblioteca do pacote não é um arquivo ELF ARMv7 válido:'),
    ('Não foi possível concluir a instalação do núcleo.', 'Não foi possível concluir a instalação do núcleo.'),
    ('"arm64-v8a"', '"armeabi-v7a"'),
    ('isArm64AppProcess', 'isArmV7AppProcess'),
    ('isArm64Elf', 'isArmV7Elf'),
    ('return architecture.contains("aarch64") || architecture.contains("arm64");', 'return architecture.contains("arm") && !architecture.contains("64");'),
    ('header[4] == 2 && header[5] == 1 && (header[18] & 0xff) == 0xb7', 'header[4] == 1 && header[5] == 1 && (header[18] & 0xff) == 40'),
]
for old, new in replacements:
    if old not in s:
        raise SystemExit(f"Expected ARMv7 patch anchor missing: {old!r}")
    s = s.replace(old, new)
if "arm64-v8a" in s or "ARM64" in s:
    raise SystemExit("ARM64-only runtime reference remains in MainActivity.java")
main.write_text(s, encoding="utf-8")

build = Path("app/build.gradle")
g = build.read_text(encoding="utf-8")
old = "include 'arm64-v8a'"
if old not in g:
    raise SystemExit(f"Expected Gradle split anchor missing: {old!r}")
g = g.replace(old, "include 'armeabi-v7a'")
if "arm64-v8a" in g:
    raise SystemExit("ARM64 ABI remains in the ARMv7 Gradle configuration")
g = g.replace("versionCode 21", "versionCode 22").replace("versionName '1.0.0'", "versionName '1.0.1-trial'")
build.write_text(g, encoding="utf-8")
print("Configured a single-ABI ARMv7 catalog build with 178 entries")
