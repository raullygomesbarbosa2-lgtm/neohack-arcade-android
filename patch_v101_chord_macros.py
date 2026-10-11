#!/usr/bin/env python3
"""Vortix 0.9.11: simultaneous configurable per-game button chords."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()

def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply chord macro patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)

replace_once('''    private String specialMacroForSlot(int slot) {
        if (slot < 0 || slot > 3) return "";''', '''    private String specialTriggerPreferenceKey(int slot) {
        String game = currentStateFile == null ? "default" : currentStateFile.getName();
        return "special_trigger_" + game + "_" + slot;
    }

    private String specialTriggerForSlot(int slot) {
        if (slot < 0 || slot > 1) return "";
        String key = specialTriggerPreferenceKey(slot);
        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        return slot == 0 ? "A+B" : "C+D";
    }

    private int[] parseSpecialTrigger(String raw) {
        String[] parts = raw == null ? new String[0] : raw.trim().toUpperCase(java.util.Locale.ROOT).split("\\\\+");
        if (parts.length != 2) throw new IllegalArgumentException("O gatilho deve conter exatamente dois botões, por exemplo A+B ou C+D.");
        int first = specialKeyCode(parts[0]);
        int second = specialKeyCode(parts[1]);
        if (!isFaceButton(first) || !isFaceButton(second) || first == second)
            throw new IllegalArgumentException("Use dois botões diferentes entre A, B, C e D.");
        return new int[]{first, second};
    }

    private boolean isFaceButton(int key) {
        return key == KeyEvent.KEYCODE_BUTTON_A || key == KeyEvent.KEYCODE_BUTTON_B
                || key == KeyEvent.KEYCODE_BUTTON_X || key == KeyEvent.KEYCODE_BUTTON_Y;
    }

    private int specialMacroSlotForPair(int first, int second) {
        for (int slot = 0; slot < 2; slot++) {
            int[] pair;
            try { pair = parseSpecialTrigger(specialTriggerForSlot(slot)); }
            catch (IllegalArgumentException ignored) { continue; }
            if ((pair[0] == first && pair[1] == second) || (pair[0] == second && pair[1] == first)) return slot;
        }
        return -1;
    }

    private String specialMacroForSlot(int slot) {
        if (slot < 0 || slot > 3) return "";''', "per-game trigger preferences and validation")

replace_once('''    private void showSpecialConfigDialog() {
        String[] labels = {"Especial do botão A", "Especial do botão B", "Especial do botão C", "Especial do botão D"};
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        int padding = dp(18);
        form.setPadding(padding, dp(8), padding, dp(8));
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Padrões por jogo: toque duplo em A executa A+B juntos; toque duplo em B executa C+D juntos. Você pode editar cada sequência só para esta ROM. Use vírgula para etapas e + para apertar botões juntos (ex.: BAIXO, DIREITA, A+B). Deixe um campo vazio para desativar esse especial neste jogo.");
        hint.setTextColor(0xffc8f6ff);
        form.setBackgroundColor(0xff08131b);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        EditText[] fields = new EditText[4];
        for (int i = 0; i < fields.length; i++) {
            android.widget.TextView label = new android.widget.TextView(this);
            label.setText(labels[i]);
            label.setTextColor(0xff00e5ff);
            android.widget.LinearLayout.LayoutParams labelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            labelParams.topMargin = dp(8);
            form.addView(label, labelParams);
            fields[i] = new EditText(this);
            fields[i].setSingleLine(true);
            fields[i].setHint("BAIXO, DIREITA, A+B");
            fields[i].setHintTextColor(0xff80aeb8);
            fields[i].setTextColor(0xffedfcff);
            fields[i].setText(specialMacroForSlot(i));
            GradientDrawable macroInput = new GradientDrawable();
            macroInput.setColor(0xff10212b); macroInput.setCornerRadius(dp(8)); macroInput.setStroke(dp(1), 0xff00bfd8);
            fields[i].setBackground(macroInput);
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
    }''', '''    private void showSpecialConfigDialog() {
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        int padding = dp(18);
        form.setPadding(padding, dp(8), padding, dp(8));
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Gatilhos simultâneos configuráveis só para este jogo: pressione os dois botões do gatilho juntos (ex.: A+B) na tela ou no controle Bluetooth. Janela de reconhecimento: 130 ms; toques/pressionamentos individuais continuam funcionando normalmente. Configure a sequência de saída abaixo: vírgula separa etapas e + aperta botões juntos (ex.: BAIXO, BAIXO+DIREITA, DIREITA, A). Deixe a sequência vazia para desativar o gatilho neste jogo.");
        hint.setTextColor(0xffc8f6ff);
        form.setBackgroundColor(0xff08131b);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        EditText[] triggers = new EditText[2];
        EditText[] sequences = new EditText[2];
        for (int i = 0; i < 2; i++) {
            android.widget.TextView triggerLabel = new android.widget.TextView(this);
            triggerLabel.setText("Gatilho simultâneo " + (i + 1) + " (dois botões)");
            triggerLabel.setTextColor(0xff00e5ff);
            android.widget.LinearLayout.LayoutParams labelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            labelParams.topMargin = dp(10);
            form.addView(triggerLabel, labelParams);
            triggers[i] = new EditText(this);
            triggers[i].setSingleLine(true);
            triggers[i].setHint(i == 0 ? "A+B" : "C+D");
            triggers[i].setHintTextColor(0xff80aeb8);
            triggers[i].setTextColor(0xffedfcff);
            triggers[i].setText(specialTriggerForSlot(i));
            GradientDrawable triggerBg = new GradientDrawable();
            triggerBg.setColor(0xff10212b); triggerBg.setCornerRadius(dp(8)); triggerBg.setStroke(dp(1), 0xff00bfd8);
            triggers[i].setBackground(triggerBg);
            form.addView(triggers[i], new android.widget.LinearLayout.LayoutParams(-1, -2));

            android.widget.TextView sequenceLabel = new android.widget.TextView(this);
            sequenceLabel.setText("Sequência de saída para " + specialTriggerForSlot(i));
            sequenceLabel.setTextColor(0xff00e5ff);
            android.widget.LinearLayout.LayoutParams sequenceLabelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            sequenceLabelParams.topMargin = dp(6);
            form.addView(sequenceLabel, sequenceLabelParams);
            triggers[i].addTextChangedListener(new android.text.TextWatcher() {
                @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) { }
                @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                    sequenceLabel.setText("Sequência de saída para " + s.toString().trim());
                }
                @Override public void afterTextChanged(android.text.Editable editable) { }
            });
            sequences[i] = new EditText(this);
            sequences[i].setSingleLine(true);
            sequences[i].setHint("BAIXO, BAIXO+DIREITA, DIREITA, A");
            sequences[i].setHintTextColor(0xff80aeb8);
            sequences[i].setTextColor(0xffedfcff);
            sequences[i].setText(specialMacroForSlot(i));
            GradientDrawable sequenceBg = new GradientDrawable();
            sequenceBg.setColor(0xff10212b); sequenceBg.setCornerRadius(dp(8)); sequenceBg.setStroke(dp(1), 0xff00bfd8);
            sequences[i].setBackground(sequenceBg);
            form.addView(sequences[i], new android.widget.LinearLayout.LayoutParams(-1, -2));
        }
        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.addView(form);
        android.app.AlertDialog dialog = new android.app.AlertDialog.Builder(this)
                .setTitle("Configurar especiais deste jogo")
                .setView(scroll)
                .setPositiveButton("Salvar", (d, which) -> {
                    String[] triggerValues = new String[2];
                    String[] sequenceValues = new String[2];
                    try {
                        for (int i = 0; i < 2; i++) {
                            triggerValues[i] = triggers[i].getText().toString().trim().toUpperCase(java.util.Locale.ROOT);
                            parseSpecialTrigger(triggerValues[i]);
                            sequenceValues[i] = sequences[i].getText().toString().trim();
                            parseSpecialSequence(sequenceValues[i]);
                        }
                        int[] firstTrigger = parseSpecialTrigger(triggerValues[0]);
                        int[] secondTrigger = parseSpecialTrigger(triggerValues[1]);
                        if ((firstTrigger[0] == secondTrigger[0] && firstTrigger[1] == secondTrigger[1])
                                || (firstTrigger[0] == secondTrigger[1] && firstTrigger[1] == secondTrigger[0]))
                            throw new IllegalArgumentException("Escolha dois gatilhos diferentes.");
                    } catch (IllegalArgumentException error) {
                        Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
                        return;
                    }
                    android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
                    for (int i = 0; i < 2; i++) {
                        editor.putString(specialTriggerPreferenceKey(i), triggerValues[i]);
                        editor.putString(specialMovePreferenceKey(i), sequenceValues[i]);
                    }
                    editor.apply();
                    Toast.makeText(this, "Gatilhos e sequências salvos para este jogo.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .create();
        dialog.show();
    }''', "explicit per-game trigger/output editor")

replace_once('''    private void playSpecialMacroStep(java.util.ArrayList<java.util.ArrayList<Integer>> sequence, int index) {''', '''    private static final long SPECIAL_CHORD_WINDOW_MS = 130L;
    private final java.util.HashSet<Integer> specialKeysPressed = new java.util.HashSet<>();
    private final java.util.HashSet<Integer> specialKeysConsumed = new java.util.HashSet<>();
    private final java.util.HashMap<Integer, Long> specialKeyDownTimes = new java.util.HashMap<>();
    private final java.util.HashMap<Integer, Runnable> pendingSpecialKeyDowns = new java.util.HashMap<>();
    private final java.util.HashSet<Integer> forwardedSpecialKeys = new java.util.HashSet<>();

    private boolean handleConfiguredChordKey(int keyCode, boolean down) {
        if (!isFaceButton(keyCode)) return false;
        boolean participates = false;
        for (int slot = 0; slot < 2; slot++) {
            try {
                int[] pair = parseSpecialTrigger(specialTriggerForSlot(slot));
                if (pair[0] == keyCode || pair[1] == keyCode) { participates = true; break; }
            } catch (IllegalArgumentException ignored) { }
        }
        if (!participates) return false;
        if (down) {
            if (!specialKeysPressed.add(keyCode)) return true; // Ignore hardware key-repeat events.
            long now = android.os.SystemClock.uptimeMillis();
            specialKeyDownTimes.put(keyCode, now);
            int matchedPartner = -1;
            int matchedSlot = -1;
            for (int slot = 0; slot < 2; slot++) {
                try {
                    int[] pair = parseSpecialTrigger(specialTriggerForSlot(slot));
                    int partner = pair[0] == keyCode ? pair[1] : pair[1] == keyCode ? pair[0] : -1;
                    if (partner >= 0 && specialKeysPressed.contains(partner)) {
                        Long partnerTime = specialKeyDownTimes.get(partner);
                        if (partnerTime != null && Math.abs(now - partnerTime) <= SPECIAL_CHORD_WINDOW_MS) {
                            matchedPartner = partner;
                            matchedSlot = slot;
                            break;
                        }
                    }
                } catch (IllegalArgumentException ignored) { }
            }
            if (matchedPartner >= 0) {
                for (int key : new int[]{keyCode, matchedPartner}) {
                    Runnable pending = pendingSpecialKeyDowns.remove(key);
                    if (pending != null) specialMacroHandler.removeCallbacks(pending);
                    if (forwardedSpecialKeys.remove(key) && retroView != null)
                        retroView.sendKeyEvent(KeyEvent.ACTION_UP, key, 0);
                    specialKeysConsumed.add(key);
                }
                triggerSpecialMacro(matchedSlot);
                return true;
            }
            final int pendingKey = keyCode;
            Runnable pending = () -> {
                pendingSpecialKeyDowns.remove(pendingKey);
                if (specialKeysPressed.contains(pendingKey) && !specialKeysConsumed.contains(pendingKey)
                        && retroView != null) {
                    retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, pendingKey, 0);
                    forwardedSpecialKeys.add(pendingKey);
                }
            };
            pendingSpecialKeyDowns.put(keyCode, pending);
            specialMacroHandler.postDelayed(pending, SPECIAL_CHORD_WINDOW_MS);
            return true;
        }
        specialKeysPressed.remove(keyCode);
        specialKeyDownTimes.remove(keyCode);
        if (specialKeysConsumed.remove(keyCode)) return true;
        Runnable pending = pendingSpecialKeyDowns.remove(keyCode);
        if (pending != null) specialMacroHandler.removeCallbacks(pending);
        if (retroView != null) {
            if (forwardedSpecialKeys.remove(keyCode)) {
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            } else {
                // Preserve short taps that end before the chord-recognition window.
                retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            }
        }
        return true;
    }

    private void playSpecialMacroStep(java.util.ArrayList<java.util.ArrayList<Integer>> sequence, int index) {''', "shared touch and controller chord recognizer")

replace_once('''                if (!isSecondTap[0] || !hasSpecialMacro(specialSlot))
                    retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);''', '''                if (specialSlot < 0 || !handleConfiguredChordKey(keyCode, true))
                    retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);''', "touch down through chord handler")
# Replace the touch up block as an exact multiline region.
replace_once('''                if (!isSecondTap[0] || !hasSpecialMacro(specialSlot))
                    retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
                if (action == MotionEvent.ACTION_UP && isSecondTap[0]) {
                    if (hasSpecialMacro(specialSlot)) triggerSpecialMacro(specialSlot);
                    else Toast.makeText(MainActivity.this,
                            "Sem especial salvo para este jogo. Abra MENU > Configurar especiais.",
                            Toast.LENGTH_LONG).show();
                }
                if (action == MotionEvent.ACTION_CANCEL) lastTap[0] = 0L;
                isSecondTap[0] = false;''', '''                if (specialSlot < 0 || !handleConfiguredChordKey(keyCode, false))
                    retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
                if (action == MotionEvent.ACTION_CANCEL) lastTap[0] = 0L;
                isSecondTap[0] = false;''', "touch up through chord handler")
replace_once('''        final long[] lastTap = {0L};
        final boolean[] isSecondTap = {false};
''', "", "remove legacy double-tap state")
replace_once('''                long now = android.os.SystemClock.uptimeMillis();
                isSecondTap[0] = specialSlot >= 0
                        && lastTap[0] > 0
                        && now - lastTap[0] <= Math.max(500, android.view.ViewConfiguration.getDoubleTapTimeout());
                lastTap[0] = isSecondTap[0] ? 0L : now;
''', "", "remove legacy double-tap recognition")
replace_once('''                if (action == MotionEvent.ACTION_CANCEL) lastTap[0] = 0L;
                isSecondTap[0] = false;''', '''                // Cancellation is treated as a proper release by the chord handler.''', "remove obsolete tap state")

replace_once('''            retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0); return true;''', '''            if (!handleConfiguredChordKey(keyCode, true)) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            return true;''', "Bluetooth key down through chord handler")
replace_once('''            retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0); return true;''', '''            if (!handleConfiguredChordKey(keyCode, false)) retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            return true;''', "Bluetooth key up through chord handler")

activity.write_text(text)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 19\n        versionName '0.9.10'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected official Vortix 0.9.10 version markers")
build.write_text(build_text.replace(old_version, "versionCode 20\n        versionName '0.9.11'", 1))
print("Added configurable per-game simultaneous chord triggers with shared touch/controller input handling.")
