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
            case REQUEST_GBA: return new String[]{"libmgba_libretro_android.so", "NINTENDO • Game Boy Advance"};
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

main.write_text(text)

# Bump the generated app version for the expanded core bundle.
gradle = ROOT / "app/build.gradle"
gradle_text = gradle.read_text()
gradle_text = gradle_text.replace("versionCode 6", "versionCode 7", 1)
gradle_text = gradle_text.replace("versionName '0.6.0-classic'", "versionName '0.7.0-retro-pack'", 1)
gradle.write_text(gradle_text)
print("Added nine additional retro systems and updated app version")
