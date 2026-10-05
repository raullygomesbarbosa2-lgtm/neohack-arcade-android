#!/usr/bin/env python3
"""Vortix 0.9.6: white-neon library, ROM autodetection, and combo macros."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
main = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = main.read_text()

def replace_once(old: str, new: str, description: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"Could not apply Vortix 0.9.6 patch: {description}")
    text = text.replace(old, new, 1)

replace_once(
    '    private static final int REQUEST_WSWAN = 55;\n',
    '    private static final int REQUEST_WSWAN = 55;\n    private static final int REQUEST_AUTO_DETECT = 56;\n',
    "automatic ROM detection request",
)

replace_once(
    '        romHelp.setText("Escolha o console e selecione a ROM do jogo; não escolha um APK.");',
    '        romHelp.setText("ROM original ou hack já aplicado: escolha o console ou use detecção automática. Não escolha um APK.");',
    "ROM and hack guidance",
)

replace_once(
    '        Button chip = menuButton("Jogar CHIP-8 — abrir arquivo .ch8 / .c8");',
    '''        Button autoRom = menuButton("ABRIR ROM • DETECTAR SISTEMA");
        autoRom.setOnClickListener(v -> openPicker(REQUEST_AUTO_DETECT));
        panel.addView(autoRom, buttonParams());

        Button chip = menuButton("Jogar CHIP-8 — abrir arquivo .ch8 / .c8");''',
    "automatic ROM picker button",
)

replace_once(
    'Button snes = menuButton("Super Nintendo (SNES) — abrir ROM");',
    'Button snes = menuButton("SUPER NINTENDO • SNES9x — abrir ROM");',
    "show the SNES core in its library entry",
)
replace_once(
    'Button sega = menuButton("Mega Drive / Master System / Game Gear");',
    'Button sega = menuButton("SEGA • Genesis Plus GX — Mega Drive / Master System / Game Gear");',
    "show the Sega core in its library entry",
)
replace_once(
    'Button arcade = menuButton("Arcade clássico — abrir jogo");',
    'Button arcade = menuButton("ARCADE • FBNeo / MAME 2000, 2003, 2003+, 2010");',
    "show all arcade core generations in the library entry",
)
replace_once(
    'Button moreSystems = menuButton("Mais consoles antigos — NES, Game Boy, Atari e outros");',
    'Button moreSystems = menuButton("BIBLIOTECA DE NÚCLEOS • NES, GAME BOY, ATARI...");',
    "make the installed core library visible",
)
replace_once(
    '.setTitle("Escolha um console retrô")',
    '.setTitle("Biblioteca de consoles e núcleos")',
    "core library dialog title",
)
replace_once(
    '''        String[] systems = {
                "NES / Famicom", "Game Boy / Game Boy Color", "Game Boy Advance",
                "Atari 2600", "Atari 7800", "PC Engine / TurboGrafx-16",
                "Atari Lynx", "Neo Geo Pocket / Color", "WonderSwan / Color"
        };''',
    '''        String[] systems = {
                "NES / Famicom • FCEUmm", "Game Boy / Color • Gambatte", "Game Boy Advance • Beetle GBA",
                "Atari 2600 • Stella 2014", "Atari 7800 • ProSystem", "PC Engine • Beetle PCE Fast",
                "Atari Lynx • Beetle Lynx", "Neo Geo Pocket • Beetle NGP", "WonderSwan • Beetle WonderSwan"
        };''',
    "list installed console cores",
)

replace_once(
    '''    private void openSelectedGame(Uri uri, int requestCode) throws Exception {
        File selected = copyRom(uri);
        if (!selected.getName().toLowerCase(java.util.Locale.ROOT).endsWith(".zip")) {''',
    '''    private void openSelectedGame(Uri uri, int requestCode) throws Exception {
        enterImmersiveMode();
        File selected = copyRom(uri);
        if (requestCode == REQUEST_AUTO_DETECT) {
            openAutoDetectedGame(selected);
            return;
        }
        if (!selected.getName().toLowerCase(java.util.Locale.ROOT).endsWith(".zip")) {''',
    "route ROMs through automatic detection when requested",
)

replace_once(
    '    private java.util.ArrayList<String> listMatchingZipEntries(File archive, int requestCode) throws Exception {',
    '''    private int detectRomSystem(String filename) {
        String name = filename.toLowerCase(java.util.Locale.ROOT);
        if (name.endsWith(".ch8") || name.endsWith(".c8") || name.endsWith(".chip8")) return REQUEST_CHIP8;
        if (name.endsWith(".sfc") || name.endsWith(".smc") || name.endsWith(".fig") || name.endsWith(".swc")) return REQUEST_SNES;
        if (name.endsWith(".md") || name.endsWith(".gen") || name.endsWith(".sms") || name.endsWith(".gg") || name.endsWith(".sg")) return REQUEST_SEGA_8_16;
        if (name.endsWith(".nes") || name.endsWith(".unf") || name.endsWith(".unif")) return REQUEST_NES;
        if (name.endsWith(".gb") || name.endsWith(".gbc")) return REQUEST_GAMEBOY;
        if (name.endsWith(".gba")) return REQUEST_GBA;
        if (name.endsWith(".a26")) return REQUEST_ATARI2600;
        if (name.endsWith(".a78")) return REQUEST_ATARI7800;
        if (name.endsWith(".pce")) return REQUEST_PCE;
        if (name.endsWith(".lnx")) return REQUEST_LYNX;
        if (name.endsWith(".ngp") || name.endsWith(".ngc")) return REQUEST_NGP;
        if (name.endsWith(".ws") || name.endsWith(".wsc")) return REQUEST_WSWAN;
        if (name.endsWith(".bin")) return -2;
        return -1;
    }

    private String coreLabelForSystem(int requestCode) {
        switch (requestCode) {
            case REQUEST_CHIP8: return "CHIP-8 interno";
            case REQUEST_SNES: return "SNES9x";
            case REQUEST_SEGA_8_16: return "Genesis Plus GX";
            case REQUEST_ARCADE: return "FBNeo / MAME 2000, 2003, 2003-Plus, 2010";
            case REQUEST_NES: return "FCEUmm";
            case REQUEST_GAMEBOY: return "Gambatte";
            case REQUEST_GBA: return "Beetle GBA";
            case REQUEST_ATARI2600: return "Stella 2014";
            case REQUEST_ATARI7800: return "ProSystem";
            case REQUEST_PCE: return "Beetle PCE Fast";
            case REQUEST_LYNX: return "Beetle Lynx";
            case REQUEST_NGP: return "Beetle NGP";
            case REQUEST_WSWAN: return "Beetle WonderSwan";
            default: return "núcleo não identificado";
        }
    }

    private void openAutoDetectedGame(File selected) throws Exception {
        String name = selected.getName().toLowerCase(java.util.Locale.ROOT);
        if (name.endsWith(".zip")) {
            java.util.ArrayList<String> entries = new java.util.ArrayList<>();
            java.util.ArrayList<Integer> systems = new java.util.ArrayList<>();
            try (java.util.zip.ZipFile zip = new java.util.zip.ZipFile(selected)) {
                java.util.Enumeration<? extends java.util.zip.ZipEntry> it = zip.entries();
                while (it.hasMoreElements()) {
                    java.util.zip.ZipEntry entry = it.nextElement();
                    if (entry.isDirectory()) continue;
                    int system = detectRomSystem(entry.getName());
                    if (system >= 0) {
                        entries.add(entry.getName());
                        systems.add(system);
                    }
                }
            }
            if (entries.size() == 1) {
                launchSelectedGame(extractZipEntry(selected, entries.get(0)), systems.get(0));
                return;
            }
            if (!entries.isEmpty()) {
                String[] labels = new String[entries.size()];
                for (int i = 0; i < labels.length; i++) labels[i] = entries.get(i) + " • " + coreLabelForSystem(systems.get(i));
                new android.app.AlertDialog.Builder(this)
                        .setTitle("Escolha a ROM e o núcleo compatível")
                        .setItems(labels, (dialog, which) -> {
                            try {
                                launchSelectedGame(extractZipEntry(selected, entries.get(which)), systems.get(which));
                            } catch (Exception error) {
                                showGameOpenError(error);
                            }
                        })
                        .setNegativeButton("Cancelar", null)
                        .show();
                return;
            }
            showAutoCoreChooser(selected, true);
            return;
        }
        int system = detectRomSystem(selected.getName());
        if (system == -2) {
            showAutoCoreChooser(selected, false);
        } else if (system >= 0) {
            launchSelectedGame(selected, system);
        } else {
            throw new IllegalArgumentException("Não reconheci o formato desta ROM. Abra a biblioteca e escolha o console/núcleo correspondente.");
        }
    }

    private void showAutoCoreChooser(File selected, boolean isZip) {
        final int[] systems = {REQUEST_ARCADE, REQUEST_SNES, REQUEST_SEGA_8_16, REQUEST_NES,
                REQUEST_GAMEBOY, REQUEST_GBA, REQUEST_ATARI2600, REQUEST_ATARI7800, REQUEST_PCE,
                REQUEST_LYNX, REQUEST_NGP, REQUEST_WSWAN};
        String[] labels = new String[systems.length];
        for (int i = 0; i < systems.length; i++) {
            String platform = systems[i] == REQUEST_ARCADE ? "Arcade" : systems[i] == REQUEST_SNES ? "Super Nintendo" :
                    systems[i] == REQUEST_SEGA_8_16 ? "Mega Drive / Master System / Game Gear" :
                    systems[i] == REQUEST_NES ? "NES / Famicom" : systems[i] == REQUEST_GAMEBOY ? "Game Boy / Color" :
                    systems[i] == REQUEST_GBA ? "Game Boy Advance" : systems[i] == REQUEST_ATARI2600 ? "Atari 2600" :
                    systems[i] == REQUEST_ATARI7800 ? "Atari 7800" : systems[i] == REQUEST_PCE ? "PC Engine" :
                    systems[i] == REQUEST_LYNX ? "Atari Lynx" : systems[i] == REQUEST_NGP ? "Neo Geo Pocket" : "WonderSwan";
            labels[i] = platform + " • " + coreLabelForSystem(systems[i]);
        }
        new android.app.AlertDialog.Builder(this)
                .setTitle(isZip ? "Escolha o sistema/núcleo para este ZIP" : "Formato .bin: escolha o sistema")
                .setItems(labels, (dialog, which) -> {
                    try {
                        openDetectedFile(selected, systems[which]);
                    } catch (Exception error) {
                        showGameOpenError(error);
                    }
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private void openDetectedFile(File selected, int requestCode) throws Exception {
        if (!selected.getName().toLowerCase(java.util.Locale.ROOT).endsWith(".zip") || requestCode == REQUEST_ARCADE) {
            launchSelectedGame(selected, requestCode);
            return;
        }
        java.util.ArrayList<String> matches = listMatchingZipEntries(selected, requestCode);
        if (matches.isEmpty()) {
            throw new IllegalArgumentException("Esse ZIP não contém um arquivo ROM compatível com " + coreLabelForSystem(requestCode) + ".");
        }
        if (matches.size() == 1) {
            launchSelectedGame(extractZipEntry(selected, matches.get(0)), requestCode);
            return;
        }
        String[] labels = new String[matches.size()];
        for (int i = 0; i < labels.length; i++) labels[i] = matches.get(i) + " • " + coreLabelForSystem(requestCode);
        new android.app.AlertDialog.Builder(this)
                .setTitle("Escolha a ROM e o núcleo")
                .setItems(labels, (dialog, which) -> {
                    try {
                        launchSelectedGame(extractZipEntry(selected, matches.get(which)), requestCode);
                    } catch (Exception error) {
                        showGameOpenError(error);
                    }
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private java.util.ArrayList<String> listMatchingZipEntries(File archive, int requestCode) throws Exception {''',
    "automatic system/core detection for ROM files and ZIPs",
)

replace_once(
    '        hint.setText("Configure uma sequência por botão, separada por vírgulas. Exemplo: BAIXO, DIREITA, A. O toque duplo no botão correspondente executa o especial.");',
    '        hint.setText("Configure cada especial: vírgula separa etapas e + aperta botões juntos. Ex.: BAIXO, BAIXO+DIREITA, DIREITA, A+B. Toque duplo no botão correspondente executa a sequência.");',
    "explain simultaneous arcade button combinations",
)
replace_once(
    '            fields[i].setHint("BAIXO, DIREITA, A");',
    '            fields[i].setHint("BAIXO, DIREITA, A+B");',
    "show the simultaneous-button syntax in the form",
)
replace_once(
    '''    private java.util.ArrayList<Integer> parseSpecialSequence(String sequence) {
        java.util.ArrayList<Integer> keys = new java.util.ArrayList<>();
        if (sequence == null || sequence.trim().isEmpty()) return keys;
        String[] tokens = sequence.split(",");
        if (tokens.length > 16) throw new IllegalArgumentException("Use até 16 comandos por especial.");
        for (String token : tokens) {
            int key = specialKeyCode(token);
            if (key < 0) throw new IllegalArgumentException("Comando inválido: " + token.trim());
            keys.add(key);
        }
        return keys;
    }''',
    '''    private java.util.ArrayList<java.util.ArrayList<Integer>> parseSpecialSequence(String sequence) {
        java.util.ArrayList<java.util.ArrayList<Integer>> steps = new java.util.ArrayList<>();
        if (sequence == null || sequence.trim().isEmpty()) return steps;
        String[] tokens = sequence.split(",");
        if (tokens.length > 16) throw new IllegalArgumentException("Use até 16 etapas por especial.");
        for (String token : tokens) {
            String[] simultaneous = token.trim().split("\\\\+");
            if (simultaneous.length > 4) throw new IllegalArgumentException("Use no máximo quatro botões simultâneos por etapa.");
            java.util.ArrayList<Integer> keys = new java.util.ArrayList<>();
            for (String part : simultaneous) {
                int key = specialKeyCode(part);
                if (key < 0) throw new IllegalArgumentException("Comando inválido: " + part.trim());
                keys.add(key);
            }
            steps.add(keys);
        }
        return steps;
    }''',
    "parse sequential and simultaneous button commands",
)
replace_once(
    '        final java.util.ArrayList<Integer> sequence;\n',
    '        final java.util.ArrayList<java.util.ArrayList<Integer>> sequence;\n',
    "use grouped simultaneous button steps",
)
replace_once(
    '''    private void playSpecialMacroStep(java.util.ArrayList<Integer> sequence, int index) {
        if (retroView == null || index >= sequence.size()) {
            specialMacroRunning = false;
            return;
        }
        int key = sequence.get(index);
        retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, key, 0);
        specialMacroHandler.postDelayed(() -> {
            if (retroView != null) retroView.sendKeyEvent(KeyEvent.ACTION_UP, key, 0);
            specialMacroHandler.postDelayed(() -> playSpecialMacroStep(sequence, index + 1), 35);
        }, 70);
    }''',
    '''    private void playSpecialMacroStep(java.util.ArrayList<java.util.ArrayList<Integer>> sequence, int index) {
        if (retroView == null || index >= sequence.size()) {
            specialMacroRunning = false;
            return;
        }
        java.util.ArrayList<Integer> keys = sequence.get(index);
        for (Integer key : keys) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, key, 0);
        specialMacroHandler.postDelayed(() -> {
            if (retroView != null) {
                for (Integer key : keys) retroView.sendKeyEvent(KeyEvent.ACTION_UP, key, 0);
            }
            specialMacroHandler.postDelayed(() -> playSpecialMacroStep(sequence, index + 1), 35);
        }, 70);
    }''',
    "send simultaneous keys together during each macro step",
)

replace_once(
    '    private void launchSelectedGame(File file, int requestCode) {',
    '''    private void showArcadeCoreChooser(File rom) {
        String[] labels = {
                "FBNeo — arcade e Neo Geo",
                "MAME 2000 — ROMset 0.37b5",
                "MAME 2003 — ROMset 0.78",
                "MAME 2003-Plus — ROMset 0.78+",
                "MAME 2010 — ROMset 0.139"
        };
        String[] cores = {
                "libfbneo_libretro_android.so",
                "libmame2000_libretro_android.so",
                "libmame2003_libretro_android.so",
                "libmame2003_plus_libretro_android.so",
                "libmame2010_libretro_android.so"
        };
        new android.app.AlertDialog.Builder(this)
                .setTitle("Escolha o núcleo que combina com o ROMset")
                .setItems(labels, (dialog, which) -> {
                    try {
                        startRetroGame(rom, cores[which], "ARCADE • " + labels[which]);
                    } catch (Exception error) {
                        showGameOpenError(error);
                    }
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private void launchSelectedGame(File file, int requestCode) {''',
    "select the arcade core/ROMset version",
)

replace_once(
    '''            } else if (requestCode == REQUEST_ARCADE) {
                startRetroGame(file, "libmame2003_plus_libretro_android.so", "ARCADE CLÁSSICO • MAME 2003-Plus");''',
    '''            } else if (requestCode == REQUEST_ARCADE) {
                showArcadeCoreChooser(file);''',
    "route arcade ROMs through the core chooser",
)

# White-neon theme for the library/profile screens; gameplay remains full-screen.
text = text.replace('new int[]{0xff071c28, 0xff081018, 0xff03070d}', 'new int[]{0xfff5fcff, 0xffe7f7fb, 0xffffffff}')
text = text.replace('shape.setColor(filled ? 0xff064452 : 0xff0b1b25);', 'shape.setColor(filled ? 0xffe4fbff : 0xffffffff);')
text = text.replace('button.setTextColor(0xffbafaff);', 'button.setTextColor(0xff123542);')
text = text.replace('box.setColor(0xcc09232d);', 'box.setColor(0xeeffffff);')
text = text.replace('name.setTextColor(0xffe4fdff);', 'name.setTextColor(0xff12323f);')
text = text.replace('edit.setText("EDITAR PERFIL"); edit.setTextColor(0xff39e9ff);', 'edit.setText("EDITAR PERFIL"); edit.setTextColor(0xff007f9e);')
text = text.replace('circle.setShape(GradientDrawable.OVAL); circle.setColor(0xff062c38);', 'circle.setShape(GradientDrawable.OVAL); circle.setColor(0xffdef9ff);')
text = text.replace('glyph.setTextSize(sizeDp * .43f); glyph.setGravity(Gravity.CENTER); glyph.setTextColor(0xffbafaff);', 'glyph.setTextSize(sizeDp * .43f); glyph.setGravity(Gravity.CENTER); glyph.setTextColor(0xff12414d);')
text = text.replace('info.setTextColor(0xff9edfe5);', 'info.setTextColor(0xff286477);')
text = text.replace('romHelp.setTextColor(0xffb6d5dc);', 'romHelp.setTextColor(0xff335966);')
text = text.replace('title.setTextColor(0xffa7fbff);', 'title.setTextColor(0xff007f9b);')
text = text.replace('hint.setTextColor(0xff9edfe5);', 'hint.setTextColor(0xff335966);')
text = text.replace('inputBg.setColor(0xff09151d);', 'inputBg.setColor(0xfff8fdff);')
text = text.replace('choose.setTextColor(0xff39e9ff);', 'choose.setTextColor(0xff007f9e);')

# Round, color-coded neon face buttons; L/R/START/SELECT retain their current shape.
replace_once(
    '''        GradientDrawable background = new GradientDrawable();
        background.setColor(0x990b1018); background.setCornerRadius(dp(24)); background.setStroke(dp(1), 0x99ffffff);
        button.setBackground(background);
        int specialSlot = specialSlotForKey(keyCode);''',
    '''        int specialSlot = specialSlotForKey(keyCode);
        GradientDrawable background = new GradientDrawable();
        if (specialSlot >= 0) {
            int[] neon = {0xffff5470, 0xff42d7ff, 0xff9cff57, 0xffffcb4b};
            background.setShape(GradientDrawable.OVAL);
            background.setColor(0xdd101820);
            background.setStroke(dp(2), neon[specialSlot]);
            button.setTextColor(neon[specialSlot]);
            button.setShadowLayer(dp(8), 0, 0, neon[specialSlot]);
        } else {
            background.setColor(0x990b1018);
            background.setCornerRadius(dp(24));
            background.setStroke(dp(1), 0x99ffffff);
        }
        button.setBackground(background);''',
    "round neon face buttons",
)

# Reapply immersive mode whenever the system file picker returns to Vortix.
replace_once(
    '        startActivityForResult(intent, requestCode);',
    '        enterImmersiveMode();\n        startActivityForResult(intent, requestCode);',
    "immersive mode around ROM selection",
)
replace_once(
    '    private void enterImmersiveMode() {',
    '''    @Override public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) enterImmersiveMode();
    }

    private void enterImmersiveMode() {''',
    "restore immersive fullscreen after returning from the system file picker",
)

main.write_text(text)

# Bump the installable app version.
gradle = ROOT / "app/build.gradle"
gradle_text = gradle.read_text()
if "versionCode 14" not in gradle_text or "versionName '0.9.5-special-macros'" not in gradle_text:
    raise SystemExit("Expected Vortix 0.9.5 version markers before bumping to 0.9.6")
gradle_text = gradle_text.replace("versionCode 14", "versionCode 15", 1)
gradle_text = gradle_text.replace("versionName '0.9.5-special-macros'", "versionName '0.9.6-white-neon'", 1)
gradle.write_text(gradle_text)
print("Applied Vortix 0.9.6 white-neon, ROM detection, core catalog and combo controls")
