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
    '''        parent.addView(label, labelParams);

        VirtualJoystickView joystick = new VirtualJoystickView();''',
    '''        parent.addView(label, labelParams);\n\n        Button shoulderL = keyButton("L", KeyEvent.KEYCODE_BUTTON_L1, dp(52), dp(42));
        FrameLayout.LayoutParams shoulderLParams = new FrameLayout.LayoutParams(dp(52), dp(42), Gravity.TOP | Gravity.LEFT);
        shoulderLParams.leftMargin = dp(12);
        shoulderLParams.topMargin = dp(28);
        parent.addView(shoulderL, shoulderLParams);

        Button shoulderR = keyButton("R", KeyEvent.KEYCODE_BUTTON_R1, dp(52), dp(42));
        FrameLayout.LayoutParams shoulderRParams = new FrameLayout.LayoutParams(dp(52), dp(42), Gravity.TOP | Gravity.RIGHT);
        shoulderRParams.rightMargin = dp(12);
        shoulderRParams.topMargin = dp(28);
        parent.addView(shoulderR, shoulderRParams);

        VirtualJoystickView joystick = new VirtualJoystickView();''',
    "add L and R shoulder controls",
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

replace_once(
    '            } else if (requestCode == REQUEST_ARCADE) {\n                startRetroGame(copyRom(uri), "libmame2003_plus_libretro_android.so", "ARCADE CLÁSSICO • MAME 2003-Plus");\n            } else if (requestCode == REQUEST_SNES) {\n                startRetroGame(copyRom(uri), "libsnes9x_libretro_android.so", "SUPER NINTENDO • SNES9x");\n            } else if (requestCode == REQUEST_SEGA_8_16) {\n                startRetroGame(copyRom(uri), "libgenesis_plus_gx_libretro_android.so", "SEGA • Mega Drive / Master System / Game Gear");\n            } else if (requestCode >= REQUEST_NES && requestCode <= REQUEST_WSWAN) {\n                String[] system = getAdditionalSystem(requestCode);\n                startRetroGame(copyRom(uri), system[0], system[1]);\n            } else if (requestCode == REQUEST_CHIP8) {\n                byte[] rom = readChip8Rom(uri);\n                startChip8(rom, displayName(uri));\n            }',
    '            } else if (requestCode != REQUEST_PROFILE_PHOTO) {\n                openSelectedGame(uri, requestCode);\n            }',
    "route selected games through ZIP-aware loader",
)

replace_once(
    '    private String[] getAdditionalSystem(int requestCode) {',
    '    private void openSelectedGame(Uri uri, int requestCode) throws Exception {\n        File selected = copyRom(uri);\n        if (!selected.getName().toLowerCase(java.util.Locale.ROOT).endsWith(".zip")) {\n            launchSelectedGame(selected, requestCode);\n            return;\n        }\n        java.util.ArrayList<String> matches = listMatchingZipEntries(selected, requestCode);\n        if (requestCode == REQUEST_ARCADE && matches.isEmpty()) {\n            // A MAME game is commonly itself a ZIP set; pass it through unchanged.\n            launchSelectedGame(selected, requestCode);\n            return;\n        }\n        if (matches.isEmpty()) {\n            throw new IllegalArgumentException("Esse ZIP não contém uma ROM compatível com o console selecionado. Abra o ZIP e escolha o arquivo do jogo correto.");\n        }\n        if (matches.size() == 1) {\n            launchSelectedGame(extractZipEntry(selected, matches.get(0)), requestCode);\n            return;\n        }\n        final File archive = selected;\n        new android.app.AlertDialog.Builder(this)\n                .setTitle("Escolha a ROM dentro do ZIP")\n                .setItems(matches.toArray(new String[matches.size()]), (dialog, which) -> {\n                    try {\n                        launchSelectedGame(extractZipEntry(archive, matches.get(which)), requestCode);\n                    } catch (Exception error) {\n                        showGameOpenError(error);\n                    }\n                })\n                .setNegativeButton("Cancelar", null)\n                .show();\n    }\n\n    private java.util.ArrayList<String> listMatchingZipEntries(File archive, int requestCode) throws Exception {\n        String[] extensions = getRomExtensions(requestCode);\n        java.util.ArrayList<String> matches = new java.util.ArrayList<>();\n        try (java.util.zip.ZipFile zip = new java.util.zip.ZipFile(archive)) {\n            java.util.Enumeration<? extends java.util.zip.ZipEntry> entries = zip.entries();\n            while (entries.hasMoreElements()) {\n                java.util.zip.ZipEntry entry = entries.nextElement();\n                if (entry.isDirectory()) continue;\n                String lower = entry.getName().toLowerCase(java.util.Locale.ROOT);\n                for (String extension : extensions) {\n                    if (lower.endsWith(extension)) {\n                        matches.add(entry.getName());\n                        break;\n                    }\n                }\n            }\n        }\n        return matches;\n    }\n\n    private String[] getRomExtensions(int requestCode) {\n        if (requestCode == REQUEST_CHIP8) return new String[]{".ch8", ".c8", ".chip8"};\n        if (requestCode == REQUEST_SNES) return new String[]{".sfc", ".smc", ".fig", ".swc", ".bin"};\n        if (requestCode == REQUEST_SEGA_8_16) return new String[]{".md", ".gen", ".bin", ".sms", ".gg", ".sg"};\n        if (requestCode == REQUEST_ARCADE) return new String[]{".zip"};\n        switch (requestCode) {\n            case REQUEST_NES: return new String[]{".nes", ".unf", ".unif"};\n            case REQUEST_GAMEBOY: return new String[]{".gb", ".gbc"};\n            case REQUEST_GBA: return new String[]{".gba"};\n            case REQUEST_ATARI2600: return new String[]{".a26", ".bin"};\n            case REQUEST_ATARI7800: return new String[]{".a78", ".bin"};\n            case REQUEST_PCE: return new String[]{".pce"};\n            case REQUEST_LYNX: return new String[]{".lnx"};\n            case REQUEST_NGP: return new String[]{".ngp", ".ngc"};\n            case REQUEST_WSWAN: return new String[]{".ws", ".wsc"};\n            default: return new String[0];\n        }\n    }\n\n    private File extractZipEntry(File archive, String entryName) throws Exception {\n        File romDir = new File(getFilesDir(), "roms");\n        if (!romDir.exists() && !romDir.mkdirs()) throw new IllegalStateException("Não foi possível preparar o armazenamento do app.");\n        String baseName = new java.io.File(entryName).getName().replaceAll("[^A-Za-z0-9._ -]", "_");\n        File destination = new File(romDir, "zip_" + System.currentTimeMillis() + "_" + baseName);\n        try (java.util.zip.ZipFile zip = new java.util.zip.ZipFile(archive)) {\n            java.util.zip.ZipEntry entry = zip.getEntry(entryName);\n            if (entry == null || entry.isDirectory()) throw new IllegalArgumentException("A ROM selecionada não foi encontrada dentro do ZIP.");\n            try (InputStream input = zip.getInputStream(entry);\n                 FileOutputStream output = new FileOutputStream(destination)) {\n                byte[] buffer = new byte[64 * 1024];\n                int count;\n                long total = 0;\n                while ((count = input.read(buffer)) != -1) {\n                    total += count;\n                    if (total > 64L * 1024L * 1024L) throw new IllegalArgumentException("A ROM dentro do ZIP excede 64 MB.");\n                    output.write(buffer, 0, count);\n                }\n            }\n        }\n        return destination;\n    }\n\n    private void launchSelectedGame(File file, int requestCode) {\n        try {\n            if (requestCode == REQUEST_CHIP8) {\n                startChip8(readChip8RomFile(file), file.getName());\n            } else if (requestCode == REQUEST_ARCADE) {\n                startRetroGame(file, "libmame2003_plus_libretro_android.so", "ARCADE CLÁSSICO • MAME 2003-Plus");\n            } else if (requestCode == REQUEST_SNES) {\n                startRetroGame(file, "libsnes9x_libretro_android.so", "SUPER NINTENDO • SNES9x");\n            } else if (requestCode == REQUEST_SEGA_8_16) {\n                startRetroGame(file, "libgenesis_plus_gx_libretro_android.so", "SEGA • Mega Drive / Master System / Game Gear");\n            } else if (requestCode >= REQUEST_NES && requestCode <= REQUEST_WSWAN) {\n                String[] system = getAdditionalSystem(requestCode);\n                startRetroGame(file, system[0], system[1]);\n            } else {\n                throw new IllegalArgumentException("Console não reconhecido.");\n            }\n        } catch (Exception error) {\n            showGameOpenError(error);\n        }\n    }\n\n    private byte[] readChip8RomFile(File file) throws Exception {\n        try (InputStream input = new java.io.FileInputStream(file);\n             java.io.ByteArrayOutputStream output = new java.io.ByteArrayOutputStream()) {\n            byte[] buffer = new byte[4096];\n            int count;\n            while ((count = input.read(buffer)) != -1) {\n                output.write(buffer, 0, count);\n                if (output.size() > 3584) throw new IllegalArgumentException("A ROM CHIP-8 precisa ter no máximo 3584 bytes. Selecione o arquivo .ch8 ou .c8 extraído do ZIP.");\n            }\n            byte[] bytes = output.toByteArray();\n            if (bytes.length == 0) throw new IllegalArgumentException("O arquivo CHIP-8 está vazio.");\n            return bytes;\n        }\n    }\n\n    private void showGameOpenError(Exception error) {\n        showLibrary();\n        new android.app.AlertDialog.Builder(this)\n                .setTitle("Não consegui abrir o jogo")\n                .setMessage(error.getMessage() == null ? "Confira o arquivo selecionado e tente de novo." : error.getMessage())\n                .setPositiveButton("OK", null)\n                .show();\n    }\n\n    private String[] getAdditionalSystem(int requestCode) {',
    "extract console-matched ROM files from ZIP archives",
)

replace_once(
    'import com.swordfish.libretrodroid.GLRetroViewData;\n',
    'import com.swordfish.libretrodroid.GLRetroViewData;\nimport com.swordfish.libretrodroid.ShaderConfig;\n',
    "import shader choices",
)

replace_once(
    '    private String selectedPhotoUri;\n',
    '    private String selectedPhotoUri;\n    private File currentStateFile;\n    private String activeCheatCode = "";\n',
    "save-state and cheat state",
)

replace_once(
    '        savesDir.mkdirs();\n        GLRetroViewData data = new GLRetroViewData(this);',
    '        savesDir.mkdirs();\n        String stateBase = (coreLibrary + "_" + rom.getName()).replaceAll("[^A-Za-z0-9._-]", "_");\n        if (stateBase.length() > 120) stateBase = stateBase.substring(0, 120);\n        currentStateFile = new File(savesDir, stateBase + ".state");\n        activeCheatCode = "";\n        GLRetroViewData data = new GLRetroViewData(this);',
    "per-ROM save-state filename",
)

replace_once(
    '        if (chip8View != null) { showLibrary(); return; }\n        if (profileScreenActive) {',
    '        if (chip8View != null) { showLibrary(); return; }\n        if (retroView != null) { returnToRomSelection(); return; }\n        if (profileScreenActive) {',
    "hardware back returns to ROM selection",
)

replace_once(
    '        parent.addView(shoulderR, shoulderRParams);\n\n        VirtualJoystickView joystick = new VirtualJoystickView();',
    '''        parent.addView(shoulderR, shoulderRParams);

        Button changeRom = overlayMenuButton("ROM");
        changeRom.setOnClickListener(v -> returnToRomSelection());
        FrameLayout.LayoutParams changeRomParams = new FrameLayout.LayoutParams(dp(72), dp(36), Gravity.TOP | Gravity.LEFT);
        changeRomParams.leftMargin = dp(12);
        changeRomParams.topMargin = dp(76);
        parent.addView(changeRom, changeRomParams);

        Button options = overlayMenuButton("MENU");
        options.setOnClickListener(v -> showGameOptions());
        FrameLayout.LayoutParams optionsParams = new FrameLayout.LayoutParams(dp(72), dp(36), Gravity.TOP | Gravity.RIGHT);
        optionsParams.rightMargin = dp(12);
        optionsParams.topMargin = dp(76);
        parent.addView(options, optionsParams);

        VirtualJoystickView joystick = new VirtualJoystickView();''',
    "ROM and options overlay buttons",
)

replace_once(
    '    private final class VirtualJoystickView extends View {',
    '''    private Button overlayMenuButton(String text) {
        Button button = menuButton(text);
        button.setTextSize(10);
        button.setMinHeight(dp(32));
        button.setMinWidth(0);
        button.setPadding(0, 0, 0, 0);
        return button;
    }

    private void returnToRomSelection() {
        recreate();
    }

    private void showGameOptions() {
        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else showImageFilterDialog();
                })
                .setNegativeButton("Fechar", null)
                .show();
    }

    private void saveCurrentState() {
        final GLRetroView view = retroView;
        final File target = currentStateFile;
        if (view == null || target == null) return;
        new Thread(() -> {
            try {
                byte[] state = view.serializeState(true);
                if (state == null || state.length == 0 || state.length > 128 * 1024 * 1024) {
                    throw new IllegalStateException("Estado vazio ou grande demais.");
                }
                File temporary = new File(target.getParentFile(), target.getName() + ".tmp");
                try (FileOutputStream output = new FileOutputStream(temporary)) {
                    output.write(state);
                    output.getFD().sync();
                }
                if (target.exists() && !target.delete()) throw new IllegalStateException("Não consegui substituir o save anterior.");
                if (!temporary.renameTo(target)) throw new IllegalStateException("Não consegui gravar o save.");
                runOnUiThread(() -> Toast.makeText(this, "Jogo salvo.", Toast.LENGTH_SHORT).show());
            } catch (Exception error) {
                runOnUiThread(() -> Toast.makeText(this, "Não foi possível salvar o estado.", Toast.LENGTH_LONG).show());
            }
        }, "vortix-save-state").start();
    }

    private void loadCurrentState() {
        final GLRetroView view = retroView;
        final File source = currentStateFile;
        if (view == null || source == null) return;
        if (!source.isFile()) {
            Toast.makeText(this, "Ainda não existe um save para este jogo.", Toast.LENGTH_SHORT).show();
            return;
        }
        new Thread(() -> {
            try (InputStream input = new java.io.FileInputStream(source);
                 ByteArrayOutputStream output = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[64 * 1024];
                int count;
                long total = 0;
                while ((count = input.read(buffer)) != -1) {
                    total += count;
                    if (total > 128L * 1024L * 1024L) throw new IllegalStateException("Save grande demais.");
                    output.write(buffer, 0, count);
                }
                if (!view.unserializeState(output.toByteArray(), true)) {
                    throw new IllegalStateException("O núcleo recusou o save.");
                }
                runOnUiThread(() -> Toast.makeText(this, "Save carregado.", Toast.LENGTH_SHORT).show());
            } catch (Exception error) {
                runOnUiThread(() -> Toast.makeText(this, "Não foi possível carregar o save deste jogo.", Toast.LENGTH_LONG).show());
            }
        }, "vortix-load-state").start();
    }

    private void showCheatDialog() {
        final EditText input = new EditText(this);
        input.setSingleLine(true);
        input.setHint("Código compatível com este console");
        if (!activeCheatCode.isEmpty()) input.setText(activeCheatCode);
        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this)
                .setTitle("Cheat")
                .setMessage("O formato do código depende do núcleo e do jogo.")
                .setView(input)
                .setPositiveButton("Ativar", (dialog, which) -> {
                    String code = input.getText().toString().trim();
                    if (code.isEmpty() || retroView == null) return;
                    try {
                        retroView.setCheat(0, true, code, true);
                        activeCheatCode = code;
                        Toast.makeText(this, "Cheat ativado.", Toast.LENGTH_SHORT).show();
                    } catch (Exception error) {
                        Toast.makeText(this, "Esse código não foi aceito pelo núcleo.", Toast.LENGTH_LONG).show();
                    }
                })
                .setNegativeButton("Cancelar", null);
        if (!activeCheatCode.isEmpty()) {
            builder.setNeutralButton("Desativar", (dialog, which) -> {
                try {
                    if (retroView != null) retroView.setCheat(0, false, activeCheatCode, true);
                    activeCheatCode = "";
                    Toast.makeText(this, "Cheat desativado.", Toast.LENGTH_SHORT).show();
                } catch (Exception error) {
                    Toast.makeText(this, "Não foi possível desativar o cheat.", Toast.LENGTH_LONG).show();
                }
            });
        }
        builder.show();
    }

    private void showImageFilterDialog() {
        String[] filters = {"Padrão", "Nítido", "CRT", "LCD"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Filtro de imagem")
                .setItems(filters, (dialog, which) -> {
                    if (retroView == null) return;
                    if (which == 0) retroView.setShader(ShaderConfig.Default.INSTANCE);
                    else if (which == 1) retroView.setShader(ShaderConfig.Sharp.INSTANCE);
                    else if (which == 2) retroView.setShader(ShaderConfig.CRT.INSTANCE);
                    else retroView.setShader(ShaderConfig.LCD.INSTANCE);
                    Toast.makeText(this, "Filtro aplicado.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private final class VirtualJoystickView extends View {''',
    "save/load, cheat and image filter options",
)

replace_once(
    '    private String activeCheatCode = "";\n',
    '''    private String activeCheatCode = "";
    private final android.os.Handler specialMacroHandler = new android.os.Handler(android.os.Looper.getMainLooper());
    private boolean specialMacroRunning;
''',
    "special-move macro state",
)

replace_once(
    '        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem"};\n',
    '        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem", "Configurar especiais"};\n',
    "special-move configuration menu item",
)

replace_once(
    '                    else showImageFilterDialog();\n',
    '                    else if (which == 3) showImageFilterDialog();\n                    else showSpecialConfigDialog();\n',
    "special-move configuration menu action",
)

replace_once(
    '    private void showImageFilterDialog() {',
    '''    private String specialMovePreferenceKey(int slot) {
        String game = currentStateFile == null ? "default" : currentStateFile.getName();
        return "special_move_" + game + "_" + slot;
    }

    private int specialSlotForKey(int keyCode) {
        if (keyCode == KeyEvent.KEYCODE_BUTTON_A) return 0;
        if (keyCode == KeyEvent.KEYCODE_BUTTON_B) return 1;
        if (keyCode == KeyEvent.KEYCODE_BUTTON_X) return 2;
        if (keyCode == KeyEvent.KEYCODE_BUTTON_Y) return 3;
        return -1;
    }

    private boolean hasSpecialMacro(int slot) {
        return slot >= 0 && !getPreferences(0).getString(specialMovePreferenceKey(slot), "").trim().isEmpty();
    }

    private int specialKeyCode(String token) {
        switch (token.trim().toUpperCase(java.util.Locale.ROOT)) {
            case "UP": case "CIMA": return KeyEvent.KEYCODE_DPAD_UP;
            case "DOWN": case "BAIXO": return KeyEvent.KEYCODE_DPAD_DOWN;
            case "LEFT": case "ESQUERDA": return KeyEvent.KEYCODE_DPAD_LEFT;
            case "RIGHT": case "DIREITA": return KeyEvent.KEYCODE_DPAD_RIGHT;
            case "A": return KeyEvent.KEYCODE_BUTTON_A;
            case "B": return KeyEvent.KEYCODE_BUTTON_B;
            case "C": case "X": return KeyEvent.KEYCODE_BUTTON_X;
            case "D": case "Y": return KeyEvent.KEYCODE_BUTTON_Y;
            case "L": return KeyEvent.KEYCODE_BUTTON_L1;
            case "R": return KeyEvent.KEYCODE_BUTTON_R1;
            case "START": return KeyEvent.KEYCODE_BUTTON_START;
            case "SELECT": return KeyEvent.KEYCODE_BUTTON_SELECT;
            default: return -1;
        }
    }

    private java.util.ArrayList<Integer> parseSpecialSequence(String sequence) {
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
    }

    private void showSpecialConfigDialog() {
        String[] labels = {"Especial do botão A", "Especial do botão B", "Especial do botão C", "Especial do botão D"};
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        int padding = dp(18);
        form.setPadding(padding, dp(8), padding, dp(8));
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Configure uma sequência por botão, separada por vírgulas. Exemplo: BAIXO, DIREITA, A. O toque duplo no botão correspondente executa o especial.");
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        EditText[] fields = new EditText[4];
        for (int i = 0; i < fields.length; i++) {
            android.widget.TextView label = new android.widget.TextView(this);
            label.setText(labels[i]);
            android.widget.LinearLayout.LayoutParams labelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            labelParams.topMargin = dp(8);
            form.addView(label, labelParams);
            fields[i] = new EditText(this);
            fields[i].setSingleLine(true);
            fields[i].setHint("BAIXO, DIREITA, A");
            fields[i].setText(getPreferences(0).getString(specialMovePreferenceKey(i), ""));
            form.addView(fields[i], new android.widget.LinearLayout.LayoutParams(-1, -2));
        }
        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.addView(form);
        android.app.AlertDialog dialog = new android.app.AlertDialog.Builder(this)
                .setTitle("Configurar especiais")
                .setView(scroll)
                .setPositiveButton("Salvar", (d, which) -> {
                    String[] values = new String[fields.length];
                    try {
                        for (int i = 0; i < fields.length; i++) {
                            values[i] = fields[i].getText().toString().trim();
                            parseSpecialSequence(values[i]);
                        }
                    } catch (IllegalArgumentException error) {
                        Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
                        return;
                    }
                    android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
                    for (int i = 0; i < values.length; i++) editor.putString(specialMovePreferenceKey(i), values[i]);
                    editor.apply();
                    Toast.makeText(this, "Especiais salvos para este jogo.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .create();
        dialog.show();
    }

    private void triggerSpecialMacro(int slot) {
        if (specialMacroRunning || retroView == null) return;
        String raw = getPreferences(0).getString(specialMovePreferenceKey(slot), "");
        if (raw.trim().isEmpty()) {
            Toast.makeText(this, "Configure o especial deste botão no MENU.", Toast.LENGTH_SHORT).show();
            return;
        }
        final java.util.ArrayList<Integer> sequence;
        try {
            sequence = parseSpecialSequence(raw);
        } catch (IllegalArgumentException error) {
            Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
            return;
        }
        if (sequence.isEmpty()) return;
        specialMacroRunning = true;
        playSpecialMacroStep(sequence, 0);
    }

    private void playSpecialMacroStep(java.util.ArrayList<Integer> sequence, int index) {
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
    }

    private void showImageFilterDialog() {''',
    "configurable double-tap special macros",
)

replace_once(
    '''    private Button keyButton(String text, int keyCode, int width, int height) {
        Button button = new Button(this);
        button.setText(text); button.setTextColor(Color.WHITE); button.setTextSize(text.length() > 1 ? 11 : 17);
        button.setAllCaps(false); button.setPadding(0, 0, 0, 0);
        GradientDrawable background = new GradientDrawable();
        background.setColor(0x990b1018); background.setCornerRadius(dp(24)); background.setStroke(dp(1), 0x99ffffff);
        button.setBackground(background);
        button.setOnTouchListener((view, event) -> {
            if (retroView == null) return true;
            int action = event.getActionMasked();
            if (action == MotionEvent.ACTION_DOWN) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            return true;
        });
        button.setLayoutParams(new FrameLayout.LayoutParams(width, height));
        return button;
    }''',
    '''    private Button keyButton(String text, int keyCode, int width, int height) {
        Button button = new Button(this);
        button.setText(text); button.setTextColor(Color.WHITE); button.setTextSize(text.length() > 1 ? 11 : 17);
        button.setAllCaps(false); button.setPadding(0, 0, 0, 0);
        GradientDrawable background = new GradientDrawable();
        background.setColor(0x990b1018); background.setCornerRadius(dp(24)); background.setStroke(dp(1), 0x99ffffff);
        button.setBackground(background);
        int specialSlot = specialSlotForKey(keyCode);
        final long[] lastTap = {0L};
        final boolean[] isSecondTap = {false};
        button.setOnTouchListener((view, event) -> {
            if (retroView == null) return true;
            int action = event.getActionMasked();
            if (action == MotionEvent.ACTION_DOWN) {
                long now = android.os.SystemClock.uptimeMillis();
                isSecondTap[0] = specialSlot >= 0 && hasSpecialMacro(specialSlot)
                        && lastTap[0] > 0
                        && now - lastTap[0] <= android.view.ViewConfiguration.getDoubleTapTimeout();
                lastTap[0] = isSecondTap[0] ? 0L : now;
                if (!isSecondTap[0]) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                if (!isSecondTap[0]) retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
                if (action == MotionEvent.ACTION_UP && isSecondTap[0]) triggerSpecialMacro(specialSlot);
                if (action == MotionEvent.ACTION_CANCEL) lastTap[0] = 0L;
                isSecondTap[0] = false;
            }
            return true;
        });
        button.setLayoutParams(new FrameLayout.LayoutParams(width, height));
        return button;
    }''',
    "double-tap triggers configured special on action buttons",
)

text = text.replace("NexoEmu", "Vortix")
main.write_text(text)

manifest = ROOT / "app/src/main/AndroidManifest.xml"
manifest_text = manifest.read_text().replace('android:label="NexoEmu"', 'android:label="Vortix"')
manifest.write_text(manifest_text)

# Bump the generated app version for the expanded core bundle.
gradle = ROOT / "app/build.gradle"
gradle_text = gradle.read_text()
gradle_text = gradle_text.replace("versionCode 6", "versionCode 14", 1)
gradle_text = gradle_text.replace("versionName '0.6.0-classic'", "versionName '0.9.5-special-macros'", 1)
gradle.write_text(gradle_text)
print("Added nine additional retro systems and updated app version")
