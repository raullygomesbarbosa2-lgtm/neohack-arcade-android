#!/usr/bin/env python3
"""Vortix 0.9.21: add a best-effort shortcut to Android's TV casting settings."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply TV-cast shortcut patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)


replace_once(
    '''        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem", "Configurar especiais", "Configurar controle Bluetooth", "Controles na tela / toque leve",
                touchLayoutEditMode ? "Concluir movimentação dos botões" : "Mover botões na tela"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else if (which == 3) showImageFilterDialog();
                    else if (which == 4) showSpecialConfigDialog();
                    else if (which == 5) showBluetoothConfigDialog();
                    else if (which == 6) showTouchControlConfigDialog();
                    else toggleTouchLayoutEditMode();
                })''',
    '''        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem", "Configurar especiais", "Configurar controle Bluetooth", "Controles na tela / toque leve",
                touchLayoutEditMode ? "Concluir movimentação dos botões" : "Mover botões na tela", "Transmitir para TV"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else if (which == 3) showImageFilterDialog();
                    else if (which == 4) showSpecialConfigDialog();
                    else if (which == 5) showBluetoothConfigDialog();
                    else if (which == 6) showTouchControlConfigDialog();
                    else if (which == 7) toggleTouchLayoutEditMode();
                    else openTvCastingSettings();
                })''',
    "add TV transmission option to the game menu",
)

marker = "    private void showImageFilterDialog() {\n"
if text.count(marker) != 1:
    raise SystemExit("Could not locate TV-casting helper insertion point")
helper = '''    private void openTvCastingSettings() {
        String[] actions = {"android.settings.WIFI_DISPLAY_SETTINGS", "android.settings.CAST_SETTINGS"};
        for (String action : actions) {
            try {
                startActivity(new android.content.Intent(action));
                return;
            } catch (android.content.ActivityNotFoundException | SecurityException ignored) {
                // This Android build has no matching system casting screen; try the next action.
            }
        }
        new android.app.AlertDialog.Builder(this)
                .setTitle("Transmitir para TV")
                .setMessage("Não há um menu universal disponível neste celular. Abra o painel rápido e toque em Smart View ou Transmitir. O celular e a TV precisam estar na mesma rede Wi-Fi, e a TV precisa oferecer um método compatível.")
                .setPositiveButton("Entendi", null)
                .show();
    }

'''
text = text.replace(marker, helper + marker, 1)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 29\n        versionName '0.9.20'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected Vortix 0.9.20 version markers")
build.write_text(build_text.replace(old_version, "versionCode 30\n        versionName '0.9.21'", 1))
activity.write_text(text)
print("Added an in-game shortcut to Android TV-casting settings with a compatibility fallback; Vortix 0.9.21.")
