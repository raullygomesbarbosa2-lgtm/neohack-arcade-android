#!/usr/bin/env python3
"""Vortix 0.9.17: show a dedicated per-game on-screen special button."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply separate special-button patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)


# The regular C remains an ordinary game button; the special is a separate control.
replace_once(
    '''    private void sendGameplayKeyEvent(int action, int keyCode) {
        if (retroView == null) return;
        if (keyCode == KeyEvent.KEYCODE_BUTTON_X && isSpecialCTriggerEnabled()) {
            try {
                int[] pair = parseSpecialChord(specialTriggerForSlot(0));
                retroView.sendKeyEvent(action, pair[0], 0);
                retroView.sendKeyEvent(action, pair[1], 0);
                return;
            } catch (IllegalArgumentException error) {
                Toast.makeText(this, "Configure o Par 1 antes de ativar C como especial.", Toast.LENGTH_SHORT).show();
            }
        }
        retroView.sendKeyEvent(action, keyCode, 0);
    }''',
    '''    private void sendGameplayKeyEvent(int action, int keyCode) {
        if (retroView != null) retroView.sendKeyEvent(action, keyCode, 0);
    }''',
    "keep regular C input unchanged",
)

# Update the per-game dialog to make the new behavior clear.
replace_once(
    'hint.setText("Configure os pares deste jogo. Se ativar C como gatilho, um toque no botão C envia o Par 1 simultaneamente ao jogo enquanto C estiver pressionado; ao soltar, os dois botões também são soltos. Cada jogo guarda sua própria configuração.");',
    'hint.setText("Configure os pares deste jogo. Ao ativar o botão especial, um controle C* separado aparece automaticamente na tela; o C normal continua funcionando. Um toque em C* envia o Par 1 simultaneamente enquanto estiver pressionado. Cada jogo guarda sua própria configuração.");',
    "explain separate special button",
)
replace_once(
    'cSpecial.setText("Um toque em C aciona o Especial 1 neste jogo");',
    'cSpecial.setText("Mostrar um botão C* separado para o Especial 1");',
    "label the separate on-screen control",
)
replace_once(
    '''                    Toast.makeText(this, cSpecial.isChecked()
                            ? "C agora aciona o Par 1 neste jogo."
                            : "Pares salvos; C continua como botão normal.", Toast.LENGTH_SHORT).show();''',
    '''                    Toast.makeText(this, cSpecial.isChecked()
                            ? "Botão C* especial adicionado à tela deste jogo."
                            : "Botão C* oculto; C normal continua disponível.", Toast.LENGTH_SHORT).show();''',
    "confirm separate button visibility",
)
replace_once(
    'Toast.makeText(this, "Padrões restaurados; C continua normal.", Toast.LENGTH_SHORT).show();',
    'Toast.makeText(this, "Padrões restaurados; botão especial C* oculto.", Toast.LENGTH_SHORT).show();',
    "describe reset state",
)

# Give Cadillacs and Dinosaurs its requested A+B default; other games keep A+C.
replace_once(
    '''        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        return slot == 0 ? "A+C" : "B+D";''',
    '''        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        String gameName = currentStateFile == null ? "" : currentStateFile.getName().toLowerCase(java.util.Locale.ROOT);
        if (slot == 0 && gameName.contains("cadillacs")) return "A+B";
        return slot == 0 ? "A+C" : "B+D";''',
    "default Cadillacs to A+B",
)

# Add a separate touch control as a fifth action button when the per-game toggle is on.
replace_once(
    '''        action.setColumnCount(2); action.setRowCount(2);
        addGridKey(action, "A", KeyEvent.KEYCODE_BUTTON_A, 0, 0);
        addGridKey(action, "B", KeyEvent.KEYCODE_BUTTON_B, 0, 1);
        addGridKey(action, isSpecialCTriggerEnabled() ? "C*" : "C", KeyEvent.KEYCODE_BUTTON_X, 1, 0);
        addGridKey(action, "D", KeyEvent.KEYCODE_BUTTON_Y, 1, 1);''',
    '''        action.setColumnCount(2); action.setRowCount(isSpecialCTriggerEnabled() ? 3 : 2);
        addGridKey(action, "A", KeyEvent.KEYCODE_BUTTON_A, 0, 0);
        addGridKey(action, "B", KeyEvent.KEYCODE_BUTTON_B, 0, 1);
        addGridKey(action, "C", KeyEvent.KEYCODE_BUTTON_X, 1, 0);
        addGridKey(action, "D", KeyEvent.KEYCODE_BUTTON_Y, 1, 1);
        if (isSpecialCTriggerEnabled()) addSpecialTouchKey(action, 2, 0);''',
    "show the extra special button beside normal actions",
)

# Add the special-button helpers before keyButton so the button inherits the standard touch styling.
marker = "    private Button keyButton(String text, int keyCode, int width, int height) {\n"
if text.count(marker) != 1:
    raise SystemExit("Could not locate keyButton insertion point")
helpers = '''    private void addSpecialTouchKey(GridLayout grid, int row, int column) {
        int size = touchActionButtonDp();
        grid.addView(specialTouchKeyButton(size), gridParams(row, column, size));
    }

    private Button specialTouchKeyButton(int size) {
        Button button = keyButton("C*", KeyEvent.KEYCODE_UNKNOWN, dp(size), dp(size));
        button.setTextColor(0xffb9ff66);
        button.setContentDescription("Botão especial C; envia " + specialTriggerForSlot(0));
        button.setOnTouchListener((view, event) -> {
            int action = event.getActionMasked();
            if (action == MotionEvent.ACTION_DOWN) {
                sendConfiguredSpecialPair(KeyEvent.ACTION_DOWN);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                sendConfiguredSpecialPair(KeyEvent.ACTION_UP);
            }
            return true;
        });
        return button;
    }

    private void sendConfiguredSpecialPair(int action) {
        if (retroView == null) return;
        try {
            int[] pair = parseSpecialChord(specialTriggerForSlot(0));
            retroView.sendKeyEvent(action, pair[0], 0);
            retroView.sendKeyEvent(action, pair[1], 0);
        } catch (IllegalArgumentException error) {
            Toast.makeText(this, "Escolha dois botões no Par 1 primeiro.", Toast.LENGTH_SHORT).show();
        }
    }

'''
text = text.replace(marker, helpers + marker, 1)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 25\n        versionName '0.9.16'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected official Vortix 0.9.16 version markers")
build.write_text(build_text.replace(old_version, "versionCode 26\n        versionName '0.9.17'", 1))
activity.write_text(text)
print("Added a dedicated optional C* special button per game; regular C remains unchanged; Vortix 0.9.17.")
