#!/usr/bin/env python3
"""Vortix 0.9.12: specials are direct simultaneous ordinary action-button inputs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply simultaneous-chord patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)


# Remove the previous macro timer/state; button events below are forwarded as ordinary inputs.
replace_once('''    private final android.os.Handler specialMacroHandler = new android.os.Handler(android.os.Looper.getMainLooper());
    private boolean specialMacroRunning;
''', "", "remove macro runner state")

start = text.find("    private String specialMovePreferenceKey(int slot) {")
end = text.find("    private void showImageFilterDialog() {", start)
if start < 0 or end < 0 or text.find("    private String specialMovePreferenceKey(int slot) {", start + 1) >= 0:
    raise SystemExit("Could not locate the unique special-move configuration block")
text = text[:start] + '''    private String specialTriggerPreferenceKey(int slot) {
        String game = currentStateFile == null ? "default" : currentStateFile.getName();
        return "special_trigger_" + game + "_" + slot;
    }

    private String specialTriggerForSlot(int slot) {
        if (slot < 0 || slot > 1) return "";
        String key = specialTriggerPreferenceKey(slot);
        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        return slot == 0 ? "A+C" : "B+D";
    }

    private int specialActionKeyCode(String token) {
        switch (token.trim().toUpperCase(java.util.Locale.ROOT)) {
            case "A": return KeyEvent.KEYCODE_BUTTON_A;
            case "B": return KeyEvent.KEYCODE_BUTTON_B;
            case "C": return KeyEvent.KEYCODE_BUTTON_X;
            case "D": return KeyEvent.KEYCODE_BUTTON_Y;
            default: return -1;
        }
    }

    private int[] parseSpecialChord(String raw) {
        String[] parts = raw == null ? new String[0] : raw.trim().toUpperCase(java.util.Locale.ROOT).split("\\\\+");
        if (parts.length != 2) throw new IllegalArgumentException("Informe exatamente dois botões, por exemplo A+C ou B+D.");
        int first = specialActionKeyCode(parts[0]);
        int second = specialActionKeyCode(parts[1]);
        if (first < 0 || second < 0 || first == second)
            throw new IllegalArgumentException("Use dois botões diferentes entre A, B, C e D.");
        return new int[]{first, second};
    }

    private void showSpecialConfigDialog() {
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        int padding = dp(18);
        form.setPadding(padding, dp(8), padding, dp(8));
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Configure os dois pares reconhecidos por este jogo. Padrões: A+C e B+D. Estes são os botões normais do jogo: pressione dois juntos na tela ou no controle Bluetooth; os dois comandos são enviados diretamente e permanecem pressionados enquanto cada botão estiver pressionado. Botões isolados continuam funcionando normalmente. Não há sequência automática.");
        hint.setTextColor(0xffc8f6ff);
        form.setBackgroundColor(0xff08131b);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        EditText[] fields = new EditText[2];
        for (int i = 0; i < fields.length; i++) {
            android.widget.TextView label = new android.widget.TextView(this);
            label.setText("Par simultâneo " + (i + 1));
            label.setTextColor(0xff00e5ff);
            android.widget.LinearLayout.LayoutParams labelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            labelParams.topMargin = dp(10);
            form.addView(label, labelParams);
            fields[i] = new EditText(this);
            fields[i].setSingleLine(true);
            fields[i].setHint(i == 0 ? "A+C" : "B+D");
            fields[i].setHintTextColor(0xff80aeb8);
            fields[i].setTextColor(0xffedfcff);
            fields[i].setText(specialTriggerForSlot(i));
            GradientDrawable background = new GradientDrawable();
            background.setColor(0xff10212b);
            background.setCornerRadius(dp(8));
            background.setStroke(dp(1), 0xff00bfd8);
            fields[i].setBackground(background);
            form.addView(fields[i], new android.widget.LinearLayout.LayoutParams(-1, -2));
        }
        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.addView(form);
        new android.app.AlertDialog.Builder(this)
                .setTitle("Combinações deste jogo")
                .setView(scroll)
                .setPositiveButton("Salvar", (dialog, which) -> {
                    String[] values = new String[2];
                    try {
                        for (int i = 0; i < fields.length; i++) {
                            values[i] = fields[i].getText().toString().trim().toUpperCase(java.util.Locale.ROOT);
                            parseSpecialChord(values[i]);
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
                    for (int i = 0; i < values.length; i++)
                        editor.putString(specialTriggerPreferenceKey(i), values[i]);
                    editor.apply();
                    Toast.makeText(this, "Pares simultâneos salvos para este jogo.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

''' + text[end:]

# Make all touch face buttons ordinary, immediate press/release inputs.
replace_once('''        int specialSlot = specialSlotForKey(keyCode);
        GradientDrawable background = new GradientDrawable();
        if (specialSlot >= 0) {
            int[] neon = {0xff00e5ff, 0xff00e5ff, 0xff00e5ff, 0xff00e5ff};
            background.setShape(GradientDrawable.OVAL);
            background.setColor(0xdd101820);
            background.setStroke(dp(2), neon[specialSlot]);
            button.setTextColor(neon[specialSlot]);
            button.setShadowLayer(dp(8), 0, 0, neon[specialSlot]);
        } else {
            background.setColor(0x990b1018);
            background.setCornerRadius(dp(24));
            background.setStroke(dp(1), 0xff00bfd8);
        }
''', '''        GradientDrawable background = new GradientDrawable();
        background.setColor(0x990b1018);
        background.setCornerRadius(dp(24));
        background.setStroke(dp(1), 0xff00bfd8);
''', "remove macro-specific touch-button treatment")
replace_once('''            if (action == MotionEvent.ACTION_DOWN) {
                if (specialSlot < 0 || !handleConfiguredChordKey(keyCode, true))
                    retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                if (specialSlot < 0 || !handleConfiguredChordKey(keyCode, false))
                    retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
                // Cancellation is treated as a proper release by the chord handler.
            }
''', '''            if (action == MotionEvent.ACTION_DOWN) {
                retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            }
''', "forward touch-button states directly")
replace_once('''            if (!handleConfiguredChordKey(keyCode, true)) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            return true;''', '''            retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            return true;''', "forward gamepad key-down directly")
replace_once('''            if (!handleConfiguredChordKey(keyCode, false)) retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            return true;''', '''            retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            return true;''', "forward gamepad key-up directly")

activity.write_text(text)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 20\n        versionName '0.9.11'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected official Vortix 0.9.11 version markers from patch_v101_chord_macros.py")
build.write_text(build_text.replace(old_version, "versionCode 21\n        versionName '0.9.12'", 1))
print("Replaced macro specials with direct per-game simultaneous ordinary-button pairs (A+C, B+D).")
