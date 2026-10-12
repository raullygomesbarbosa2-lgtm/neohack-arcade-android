#!/usr/bin/env python3
"""Vortix 0.9.16: optionally let one tap on C send a per-game special chord."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply C special-trigger patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)


start = text.find("    private void showSpecialConfigDialog() {")
end = text.find("    private String bluetoothPreferenceKey(int slot) {", start)
if start < 0 or end < 0 or text.find("    private void showSpecialConfigDialog() {", start + 1) >= 0:
    raise SystemExit("Could not locate the unique per-game special configuration block")
text = text[:start] + '''    private String specialCTriggerPreferenceKey() {
        String game = currentStateFile == null ? "default" : currentStateFile.getName();
        return "special_c_trigger_" + game;
    }

    private boolean isSpecialCTriggerEnabled() {
        return getPreferences(0).getBoolean(specialCTriggerPreferenceKey(), false);
    }

        private void showSpecialConfigDialog() {
        final String[] choices = {"A", "B", "C", "D"};
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        form.setPadding(dp(18), dp(8), dp(18), dp(8));
        form.setBackgroundColor(0xff08131b);
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Configure os pares deste jogo. Se ativar C como gatilho, um toque no botão C envia o Par 1 simultaneamente ao jogo enquanto C estiver pressionado; ao soltar, os dois botões também são soltos. Cada jogo guarda sua própria configuração.");
        hint.setTextColor(0xffc8f6ff);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        android.widget.Switch cSpecial = new android.widget.Switch(this);
        cSpecial.setText("Um toque em C aciona o Especial 1 neste jogo");
        cSpecial.setTextColor(0xffedfcff);
        cSpecial.setChecked(isSpecialCTriggerEnabled());
        android.widget.LinearLayout.LayoutParams switchParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
        switchParams.topMargin = dp(10);
        form.addView(cSpecial, switchParams);
        android.widget.ArrayAdapter<String> adapter = new android.widget.ArrayAdapter<>(
                this, android.R.layout.simple_spinner_item, choices);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        android.widget.Spinner[][] selectors = new android.widget.Spinner[2][2];
        for (int pair = 0; pair < 2; pair++) {
            android.widget.TextView label = new android.widget.TextView(this);
            label.setText("Par simultâneo " + (pair + 1));
            label.setTextColor(0xff00e5ff);
            android.widget.LinearLayout.LayoutParams labelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            labelParams.topMargin = dp(12);
            form.addView(label, labelParams);
            android.widget.LinearLayout row = new android.widget.LinearLayout(this);
            row.setOrientation(android.widget.LinearLayout.HORIZONTAL);
            String[] saved = specialTriggerForSlot(pair).split("\\\\+");
            for (int button = 0; button < 2; button++) {
                selectors[pair][button] = new android.widget.Spinner(this);
                selectors[pair][button].setAdapter(adapter);
                String selected = saved.length > button ? saved[button] : (button == 0 ? "A" : "C");
                selectors[pair][button].setSelection(specialChoiceIndex(selected));
                android.widget.LinearLayout.LayoutParams spinnerParams = new android.widget.LinearLayout.LayoutParams(0, -2, 1f);
                spinnerParams.setMargins(dp(4), 0, dp(4), 0);
                row.addView(selectors[pair][button], spinnerParams);
                if (button == 0) {
                    android.widget.TextView plus = new android.widget.TextView(this);
                    plus.setText("+");
                    plus.setTextColor(0xff00e5ff);
                    plus.setGravity(Gravity.CENTER);
                    row.addView(plus, new android.widget.LinearLayout.LayoutParams(dp(28), -2));
                }
            }
            form.addView(row, new android.widget.LinearLayout.LayoutParams(-1, -2));
        }
        new android.app.AlertDialog.Builder(this)
                .setTitle("Especiais deste jogo")
                .setView(form)
                .setPositiveButton("Salvar", (dialog, which) -> {
                    String[] values = new String[2];
                    try {
                        for (int pair = 0; pair < 2; pair++) {
                            String first = selectors[pair][0].getSelectedItem().toString();
                            String second = selectors[pair][1].getSelectedItem().toString();
                            values[pair] = first + "+" + second;
                            parseSpecialChord(values[pair]);
                        }
                        int[] first = parseSpecialChord(values[0]);
                        int[] second = parseSpecialChord(values[1]);
                        if ((first[0] == second[0] && first[1] == second[1])
                                || (first[0] == second[1] && first[1] == second[0]))
                            throw new IllegalArgumentException("Escolha dois pares diferentes.");
                    } catch (IllegalArgumentException error) {
                        Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
                        return;
                    }
                    android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
                    for (int pair = 0; pair < values.length; pair++)
                        editor.putString(specialTriggerPreferenceKey(pair), values[pair]);
                    editor.putBoolean(specialCTriggerPreferenceKey(), cSpecial.isChecked());
                    editor.apply();
                    rebuildTouchControls();
                    Toast.makeText(this, cSpecial.isChecked()
                            ? "C agora aciona o Par 1 neste jogo."
                            : "Pares salvos; C continua como botão normal.", Toast.LENGTH_SHORT).show();
                })
                .setNeutralButton("Padrão", (dialog, which) -> {
                    getPreferences(0).edit()
                            .putString(specialTriggerPreferenceKey(0), "A+C")
                            .putString(specialTriggerPreferenceKey(1), "B+D")
                            .putBoolean(specialCTriggerPreferenceKey(), false)
                            .apply();
                    rebuildTouchControls();
                    Toast.makeText(this, "Padrões restaurados; C continua normal.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

''' + text[end:]

# Mark the virtual C control when it is configured as a one-tap special trigger.
replace_once(
    '        addGridKey(action, "C", KeyEvent.KEYCODE_BUTTON_X, 1, 0);',
    '        addGridKey(action, isSpecialCTriggerEnabled() ? "C*" : "C", KeyEvent.KEYCODE_BUTTON_X, 1, 0);',
    "show active C special trigger on screen",
)

# Send the configured pair instead of ordinary C only when this game's C trigger is enabled.
key_button = '''            if (action == MotionEvent.ACTION_DOWN) {
                retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            }'''
replace_once(
    key_button,
    '''            if (action == MotionEvent.ACTION_DOWN) {
                sendGameplayKeyEvent(KeyEvent.ACTION_DOWN, keyCode);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                sendGameplayKeyEvent(KeyEvent.ACTION_UP, keyCode);
            }''',
    "route touch buttons through per-game C trigger",
)

replace_once(
    '''            retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, targetKeyCode, 0);
            return true;''',
    '''            sendGameplayKeyEvent(KeyEvent.ACTION_DOWN, targetKeyCode);
            return true;''',
    "route Bluetooth/key down through per-game C trigger",
)
replace_once(
    '''            retroView.sendKeyEvent(KeyEvent.ACTION_UP, targetKeyCode, 0);
            return true;''',
    '''            sendGameplayKeyEvent(KeyEvent.ACTION_UP, targetKeyCode);
            return true;''',
    "route Bluetooth/key up through per-game C trigger",
)

marker = "    private Button keyButton(String text, int keyCode, int width, int height) {\n"
if text.count(marker) != 1:
    raise SystemExit("Could not locate gameplay-key helper insertion point")
helper = '''    private void sendGameplayKeyEvent(int action, int keyCode) {
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
    }

'''
text = text.replace(marker, helper + marker, 1)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 24\n        versionName '0.9.15'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected official Vortix 0.9.15 version markers")
build.write_text(build_text.replace(old_version, "versionCode 25\n        versionName '0.9.16'", 1))
activity.write_text(text)
print("Added an optional per-game C one-tap special trigger and bumped Vortix to 0.9.16.")
