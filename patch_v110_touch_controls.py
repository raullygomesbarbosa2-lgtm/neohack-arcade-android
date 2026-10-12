#!/usr/bin/env python3
"""Vortix 0.9.15: larger touch targets and explicit simultaneous touchscreen input."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply touchscreen-control patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)


replace_once(
    "    private boolean onboardingProfile;\n",
    "    private boolean onboardingProfile;\n    private FrameLayout touchControlsContainer;\n    private String activeTouchSystemLabel;\n",
    "add live touch-control container state",
)

replace_once(
    '''        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem", "Configurar especiais", "Configurar controle Bluetooth"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else if (which == 3) showImageFilterDialog();
                    else if (which == 4) showSpecialConfigDialog();
                    else showBluetoothConfigDialog();
                })''',
    '''        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem", "Configurar especiais", "Configurar controle Bluetooth", "Controles na tela / toque leve"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else if (which == 3) showImageFilterDialog();
                    else if (which == 4) showSpecialConfigDialog();
                    else if (which == 5) showBluetoothConfigDialog();
                    else showTouchControlConfigDialog();
                })''',
    "add touch-control settings to game menu",
)

start = text.find("    private void addTouchControls(FrameLayout parent, String systemLabel) {")
end = text.find("    private Button overlayMenuButton(String text) {", start)
if start < 0 or end < 0 or text.find("    private void addTouchControls(FrameLayout parent, String systemLabel) {", start + 1) >= 0:
    raise SystemExit("Could not locate the unique touchscreen overlay method")
block = text[start:end]
header = "    private void addTouchControls(FrameLayout parent, String systemLabel) {\n"
if block.count(header) != 1:
    raise SystemExit("Could not locate touchscreen method header")
init = '''        activeTouchSystemLabel = systemLabel;
        parent.setMotionEventSplittingEnabled(true);
        FrameLayout controls = new FrameLayout(this);
        controls.setMotionEventSplittingEnabled(true);
        touchControlsContainer = controls;
        parent.addView(controls, new FrameLayout.LayoutParams(-1, -1));
'''
block = block.replace(header, header + init, 1)
anchor = "        parent.addView(controls, new FrameLayout.LayoutParams(-1, -1));\n"
anchor_end = block.find(anchor) + len(anchor)
if anchor_end < len(anchor):
    raise SystemExit("Could not locate touch overlay container insertion")
block = block[:anchor_end] + block[anchor_end:].replace("parent.addView(", "controls.addView(")
text = text[:start] + block + text[end:]

replace_once(
    '''    private void addGridKey(GridLayout grid, String text, int keyCode, int row, int column) {
        grid.addView(keyButton(text, keyCode, dp(54), dp(54)), gridParams(row, column));
    }

    private GridLayout.LayoutParams gridParams(int row, int column) {
        GridLayout.LayoutParams params = new GridLayout.LayoutParams(GridLayout.spec(row), GridLayout.spec(column));
        params.width = dp(54); params.height = dp(54); params.setMargins(dp(2), dp(2), dp(2), dp(2));
        return params;
    }''',
    '''    private int touchActionButtonDp() {
        int size = getPreferences(0).getInt("touch_action_button_dp", 64);
        return Math.max(54, Math.min(76, size));
    }

    private void addGridKey(GridLayout grid, String text, int keyCode, int row, int column) {
        int size = touchActionButtonDp();
        grid.addView(keyButton(text, keyCode, dp(size), dp(size)), gridParams(row, column, size));
    }

    private GridLayout.LayoutParams gridParams(int row, int column, int size) {
        GridLayout.LayoutParams params = new GridLayout.LayoutParams(GridLayout.spec(row), GridLayout.spec(column));
        params.width = dp(size); params.height = dp(size); params.setMargins(dp(3), dp(3), dp(3), dp(3));
        return params;
    }''',
    "make action-button hit areas larger and configurable",
)

needle = "    private void showImageFilterDialog() {\n"
if text.count(needle) != 1:
    raise SystemExit("Could not locate image-filter settings insertion point")
touch_settings = '''    private void rebuildTouchControls() {
        if (root == null || touchControlsContainer == null || activeTouchSystemLabel == null) return;
        root.removeView(touchControlsContainer);
        addTouchControls(root, activeTouchSystemLabel);
    }

    private void showTouchControlConfigDialog() {
        final int[] sizes = {54, 64, 76};
        final String[] labels = {"Compactos (54 dp)", "Médios • recomendado (64 dp)", "Grandes • dedo maior (76 dp)"};
        int current = getPreferences(0).getInt("touch_action_button_dp", 64);
        int selected = current <= 54 ? 0 : current >= 76 ? 2 : 1;
        final int[] choice = {selected};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Toque imediato • tamanho dos botões")
                .setSingleChoiceItems(labels, selected, (dialog, which) -> choice[0] = which)
                .setPositiveButton("Aplicar", (dialog, which) -> {
                    getPreferences(0).edit().putInt("touch_action_button_dp", sizes[choice[0]]).apply();
                    rebuildTouchControls();
                    Toast.makeText(this, "Aplicado: toque leve e multitoque simultâneo nos botões.", Toast.LENGTH_SHORT).show();
                })
                .setNeutralButton("Padrão", (dialog, which) -> {
                    getPreferences(0).edit().putInt("touch_action_button_dp", 64).apply();
                    rebuildTouchControls();
                    Toast.makeText(this, "Botões médios restaurados; toque continua imediato.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

'''
text = text.replace(needle, touch_settings + needle, 1)

# Explicitly allow independent fingers to hit different action buttons at once.
replace_once(
    '''        GridLayout action = new GridLayout(this);
        action.setColumnCount(2); action.setRowCount(2);''',
    '''        GridLayout action = new GridLayout(this);
        action.setMotionEventSplittingEnabled(true);
        action.setColumnCount(2); action.setRowCount(2);''',
    "enable multi-touch splitting on action pad",
)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 23\n        versionName '0.9.14'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected official Vortix 0.9.14 version markers")
build.write_text(build_text.replace(old_version, "versionCode 24\n        versionName '0.9.15'", 1))
activity.write_text(text)
print("Added live touch sizing, explicit multi-touch splitting, and Vortix 0.9.15 version markers.")
