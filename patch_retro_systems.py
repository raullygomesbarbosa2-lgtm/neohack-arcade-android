#!/usr/bin/env python3
"""Add a curated set of lightweight Libretro systems to the generated Android app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
main = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = main.read_text()

def replace_once(old: str, new: str, description: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"Could not apply retro systems patch: {description}")
    text = text.replace(old, new, 1)

replace_once(
    '    private static final int REQUEST_SEGA_8_16 = 46;\n',
    '''    private static final int REQUEST_SEGA_8_16 = 46;
    private static final int REQUEST_NES = 47;
    private static final int REQUEST_GAMEBOY = 48;
    private static final int REQUEST_GBA = 49;
    private static final int REQUEST_ATARI2600 = 50;
    private static final int REQUEST_ATARI7800 = 51;
    private static final int REQUEST_PCE = 52;
    private static final int REQUEST_LYNX = 53;
    private static final int REQUEST_NGP = 54;
    private static final int REQUEST_WSWAN = 55;
''',
    "request codes",
)

replace_once(
    '        info.setText("CHIP-8 • Super Nintendo • Mega Drive • Master System • Game Gear • Arcade");',
    '        info.setText("CHIP-8 • SNES • Sega • Arcade • + 9 sistemas retrô");',
    "library subtitle",
)

replace_once(
    "        panel.addView(info, infoParams);\n\n        Button chip = menuButton(\"Jogar CHIP-8 — abrir arquivo .ch8 / .c8\");",
    "        panel.addView(info, infoParams);\n\n        TextView romHelp = new TextView(this);\n        romHelp.setText(\"Escolha o console e selecione a ROM do jogo; não escolha um APK.\");\n        romHelp.setTextColor(0xffb6d5dc);\n        romHelp.setTextSize(12);\n        romHelp.setGravity(Gravity.CENTER);\n        panel.addView(romHelp, new LinearLayout.LayoutParams(-1, dp(30)));\n\n        Button chip = menuButton(\"Jogar CHIP-8 — abrir arquivo .ch8 / .c8\");",
    "ROM picker guidance",
)

replace_once(
    "        intent.setType(requestCode == REQUEST_PROFILE_PHOTO ? \"image/*\" : \"*/*\");",
    "        intent.setType(requestCode == REQUEST_PROFILE_PHOTO ? \"image/*\" : \"*/*\");\n        intent.putExtra(Intent.EXTRA_TITLE, requestCode == REQUEST_PROFILE_PHOTO ? \"Escolha uma foto\" : \"Escolha a ROM do jogo (não o APK)\");",
    "file picker title",
)

replace_once(
    "            Uri uri = data.getData();",
    "            Uri uri = data.getData();\n            if (requestCode != REQUEST_PROFILE_PHOTO) rejectInstallerFile(uri);",
    "reject installer files to prevent black screen",
)

replace_once(
    "    @Override @SuppressWarnings(\"deprecation\")\n    protected void onActivityResult(int requestCode, int resultCode, Intent data) {",
    "    private void rejectInstallerFile(Uri uri) {\n        String name = displayName(uri);\n        if (name == null) return;\n        String lower = name.toLowerCase(java.util.Locale.ROOT);\n        if (lower.endsWith(\".apk\") || lower.endsWith(\".xapk\") || lower.endsWith(\".apks\")) {\n            throw new IllegalArgumentException(\"Esse arquivo é um instalador APK, não um jogo. Volte e escolha uma ROM, por exemplo .sfc, .nes, .gba ou .zip.\");\n        }\n    }\n\n    @Override @SuppressWarnings(\"deprecation\")\n    protected void onActivityResult(int requestCode, int resultCode, Intent data) {",
    "ROM versus APK guard",
)

replace_once(
    '''        panel.addView(arcade, arcadeParams);

        ScrollView scroll = new ScrollView(this);''',
    '''        panel.addView(arcade, arcadeParams);

        Button moreSystems = menuButton("Mais consoles antigos — NES, Game Boy, Atari e outros");
        moreSystems.setOnClickListener(v -> showMoreSystemsDialog());
        LinearLayout.LayoutParams moreSystemsParams = buttonParams();
        moreSystemsParams.topMargin = dp(6);
        panel.addView(moreSystems, moreSystemsParams);

        ScrollView scroll = new ScrollView(this);''',
    "additional systems button",
)

replace_once(
    '''        data.setCoreFilePath(coreLibrary);''',
    '''        File nativeCore = new File(getApplicationInfo().nativeLibraryDir, coreLibrary);
        if (!nativeCore.isFile()) {
            throw new IllegalStateException("Núcleo de emulação não encontrado no APK: " + coreLibrary);
        }
        data.setCoreFilePath(nativeCore.getAbsolutePath());''',
    "absolute native core path to prevent blank emulator screen",
)

replace_once(
    "        data.setSkipDuplicateFrames(true);",
    "        data.setSkipDuplicateFrames(false);",
    "disable duplicate-frame skipping to test black video output",
)

replace_once(
    '''    private Button menuButton(String label) {''',
    '''    private void showMoreSystemsDialog() {
        final int[] requestCodes = {
                REQUEST_NES, REQUEST_GAMEBOY, REQUEST_GBA, REQUEST_ATARI2600,
                REQUEST_ATARI7800, REQUEST_PCE, REQUEST_LYNX, REQUEST_NGP, REQUEST_WSWAN
        };
        String[] systems = {
                "NES / Famicom", "Game Boy / Game Boy Color", "Game Boy Advance",
                "Atari 2600", "Atari 7800", "PC Engine / TurboGrafx-16",
                "Atari Lynx", "Neo Geo Pocket / Color", "WonderSwan / Color"
        };
        new android.app.AlertDialog.Builder(this)
                .setTitle("Escolha um console retrô")
                .setItems(systems, (dialog, which) -> openPicker(requestCodes[which]))
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private Button menuButton(String label) {''',
    "systems chooser",
)

replace_once(
    '''            } else if (requestCode == REQUEST_SEGA_8_16) {
                startRetroGame(copyRom(uri), "libgenesis_plus_gx_libretro_android.so", "SEGA • Mega Drive / Master System / Game Gear");
            } else if (requestCode == REQUEST_CHIP8) {''',
    '''            } else if (requestCode == REQUEST_SEGA_8_16) {
                startRetroGame(copyRom(uri), "libgenesis_plus_gx_libretro_android.so", "SEGA • Mega Drive / Master System / Game Gear");
            } else if (requestCode >= REQUEST_NES && requestCode <= REQUEST_WSWAN) {
                String[] system = getAdditionalSystem(requestCode);
                startRetroGame(copyRom(uri), system[0], system[1]);
            } else if (requestCode == REQUEST_CHIP8) {''',
    "additional system dispatch",
)

replace_once(
    '''    private byte[] readChip8Rom(Uri uri) throws Exception {''',
    '''    private String[] getAdditionalSystem(int requestCode) {
        switch (requestCode) {
            case REQUEST_NES: return new String[]{"libfceumm_libretro_android.so", "NINTENDO • NES / Famicom"};
            case REQUEST_GAMEBOY: return new String[]{"libgambatte_libretro_android.so", "NINTENDO • Game Boy / Game Boy Color"};
            case REQUEST_GBA: return new String[]{"libmednafen_gba_libretro_android.so", "NINTENDO • Game Boy Advance (Beetle GBA)"};
            case REQUEST_ATARI2600: return new String[]{"libstella2014_libretro_android.so", "ATARI • 2600"};
            case REQUEST_ATARI7800: return new String[]{"libprosystem_libretro_android.so", "ATARI • 7800"};
            case REQUEST_PCE: return new String[]{"libmednafen_pce_fast_libretro_android.so", "PC ENGINE • TurboGrafx-16"};
            case REQUEST_LYNX: return new String[]{"libmednafen_lynx_libretro_android.so", "ATARI • Lynx"};
            case REQUEST_NGP: return new String[]{"libmednafen_ngp_libretro_android.so", "SNK • Neo Geo Pocket / Color"};
            case REQUEST_WSWAN: return new String[]{"libmednafen_wswan_libretro_android.so", "BANDAI • WonderSwan / Color"};
            default: throw new IllegalArgumentException("Sistema retrô desconhecido.");
        }
    }

    private byte[] readChip8Rom(Uri uri) throws Exception {''',
    "core mapping",
)

text = text.replace("NexoEmu", "Vortix")
main.write_text(text)

manifest = ROOT / "app/src/main/AndroidManifest.xml"
manifest_text = manifest.read_text().replace('android:label="NexoEmu"', 'android:label="Vortix"')
manifest.write_text(manifest_text)

# Bump the generated app version for the expanded core bundle.
gradle = ROOT / "app/build.gradle"
gradle_text = gradle.read_text()
gradle_text = gradle_text.replace("versionCode 6", "versionCode 10", 1)
gradle_text = gradle_text.replace("versionName '0.6.0-classic'", "versionName '0.9.1-frame-output'", 1)
gradle.write_text(gradle_text)
print("Added nine additional retro systems and updated app version")
