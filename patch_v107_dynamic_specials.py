#!/usr/bin/env python3
"""Allow up to six per-game simultaneous specials and add one screen button per configured pair."""
from pathlib import Path

main = Path("app/src/main/java/br/com/raully/neohackarcade/MainActivity.java")
s = main.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global s
    if s.count(old) != 1:
        raise SystemExit(f"{label}: expected one anchor, found {s.count(old)}")
    s = s.replace(old, new, 1)

def replace_method(start: str, end: str, body: str) -> None:
    global s
    a = s.find(start)
    b = s.find(end, a + len(start))
    if a < 0 or b < 0:
        raise SystemExit(f"Could not find {start!r} / {end!r}")
    s = s[:a] + body + s[b:]

replace_once(
    "    private String specialTriggerPreferenceKey(int slot) {\n",
    "    private static final int MAX_SPECIAL_SLOTS = 6;\n\n    private String specialTriggerPreferenceKey(int slot) {\n",
    "special slots constant",
)

replace_method(
    "    private String specialTriggerForSlot(int slot) {\n",
    "    private int[] parseSpecialTrigger(String raw) {\n",
    '''    private String specialTriggerForSlot(int slot) {
        if (slot < 0 || slot >= MAX_SPECIAL_SLOTS) return "";
        String key = specialTriggerPreferenceKey(slot);
        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        String rom = currentStateFile == null ? "" : currentStateFile.getName().toLowerCase(java.util.Locale.ROOT);
        if (rom.contains("dino") || rom.contains("cadillacs") || rom.contains("dinosaurs")) {
            if (slot == 0) return "A+B";
            if (slot == 1) return "C+D";
            return "";
        }
        if (slot == 0) return "A+C";
        if (slot == 1) return "B+D";
        return "";
    }

''',
)

replace_once(
    '''        Button special1 = specialChordButton(0);
        FrameLayout.LayoutParams special1Params = new FrameLayout.LayoutParams(dp(66), dp(56), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        special1Params.bottomMargin = dp(112); special1Params.rightMargin = dp(46); parent.addView(special1, special1Params);
        registerTouchControl(parent, "special1", special1, 56, 66);
        Button special2 = specialChordButton(1);
        FrameLayout.LayoutParams special2Params = new FrameLayout.LayoutParams(dp(66), dp(56), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        special2Params.bottomMargin = dp(112); special2Params.leftMargin = dp(46); parent.addView(special2, special2Params);
        registerTouchControl(parent, "special2", special2, 64, 66);
''',
    '''        specialControlsRow = new android.widget.LinearLayout(this);
        specialControlsRow.setOrientation(android.widget.LinearLayout.HORIZONTAL);
        FrameLayout.LayoutParams specialRowParams = new FrameLayout.LayoutParams(-2, -2, Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        specialRowParams.bottomMargin = dp(112);
        parent.addView(specialControlsRow, specialRowParams);
        registerTouchControl(parent, "specials", specialControlsRow, 50, 66);
        rebuildSpecialButtons();
''',
    "dynamic special row",
)

replace_once(
    '    private FrameLayout gameOverlayRoot;\n',
    '    private FrameLayout gameOverlayRoot;\n    private android.widget.LinearLayout specialControlsRow;\n',
    "special row field",
)

replace_once(
    '        final String[] ids = {"joystick", "actions", "l", "r", "start", "select", "special1", "special2"};\n        final String[] labels = {"Alavanca direcional", "Grupo A/B/C/D", "Ombro L", "Ombro R", "Start", "Select", "Especial 1", "Especial 2"};',
    '        final String[] ids = {"joystick", "actions", "l", "r", "start", "select", "specials"};\n        final String[] labels = {"Alavanca direcional", "Grupo A/B/C/D", "Ombro L", "Ombro R", "Start", "Select", "Faixa de especiais"};',
    "special row in control settings",
)

replace_once(
    'Button button = menuButton("ESP " + specialTriggerForSlot(slot));',
    'Button button = menuButton("ESP" + (slot + 1) + " " + specialTriggerForSlot(slot));',
    "numbered special labels",
)
replace_once(
    '        button.setTextSize(12);\n        button.setContentDescription("Especial simultâneo " + (slot + 1));',
    '        button.setTextSize(9);\n        button.setMinWidth(dp(54));\n        button.setContentDescription("Especial simultâneo " + (slot + 1) + " " + specialTriggerForSlot(slot));',
    "special pad sizing and accessibility",
)

replace_once(
    '''        return button;
    }

    private Button overlayMenuButton(String text) {''',
    '''        return button;
    }

    private void rebuildSpecialButtons() {
        if (specialControlsRow == null) return;
        for (int slot = 0; slot < MAX_SPECIAL_SLOTS; slot++) endTouchSpecialChord(slot);
        specialControlsRow.removeAllViews();
        int visible = 0;
        for (int slot = 0; slot < MAX_SPECIAL_SLOTS; slot++) {
            if (specialTriggerForSlot(slot).isEmpty()) continue;
            Button button = specialChordButton(slot);
            android.widget.LinearLayout.LayoutParams params = new android.widget.LinearLayout.LayoutParams(dp(54), dp(54));
            params.setMargins(dp(2), dp(2), dp(2), dp(2));
            specialControlsRow.addView(button, params);
            visible++;
        }
        specialControlsRow.setVisibility(visible > 0 ? View.VISIBLE : View.GONE);
    }

    private Button overlayMenuButton(String text) {''',
    "special button rebuild method",
)

replace_once(
    '        for (int slot = 0; slot < 2; slot++) {\n            int[] pair;\n            try { pair = parseSpecialTrigger(specialTriggerForSlot(slot)); }',
    '        for (int slot = 0; slot < MAX_SPECIAL_SLOTS; slot++) {\n            int[] pair;\n            try { pair = parseSpecialTrigger(specialTriggerForSlot(slot)); }',
    "pair lookup across configured specials",
)

replace_method(
    "    private void showSpecialConfigDialog() {\n",
    "    private final java.util.HashMap<Integer, int[]> activeTouchSpecialPairs = new java.util.HashMap<>();\n",
    '''    private void showSpecialConfigDialog() {
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        int padding = dp(18);
        form.setPadding(padding, dp(8), padding, dp(8));
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Configure até seis pares simultâneos. Deixe vazio para ocultar o botão. Os mesmos botões funcionam na tela e no Bluetooth quando pressionados juntos; não há sequência automática.");
        hint.setTextColor(0xffe5ffc9);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        EditText[] triggers = new EditText[MAX_SPECIAL_SLOTS];
        for (int i = 0; i < MAX_SPECIAL_SLOTS; i++) {
            android.widget.TextView label = new android.widget.TextView(this);
            label.setText("Especial " + (i + 1) + " • par simultâneo");
            label.setTextColor(0xffb2ff64);
            android.widget.LinearLayout.LayoutParams labelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            labelParams.topMargin = dp(12);
            form.addView(label, labelParams);
            triggers[i] = new EditText(this);
            triggers[i].setSingleLine(true);
            triggers[i].setHint(i == 0 ? "A+C (Cadillacs: A+B)" : (i == 1 ? "B+D (Cadillacs: C+D)" : "A+B — vazio oculta"));
            triggers[i].setText(specialTriggerForSlot(i));
            form.addView(triggers[i], new android.widget.LinearLayout.LayoutParams(-1, -2));
        }
        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.addView(form);
        new android.app.AlertDialog.Builder(this)
                .setTitle("Configurar especiais deste jogo")
                .setView(scroll)
                .setPositiveButton("Salvar", (dialog, which) -> {
                    String[] values = new String[MAX_SPECIAL_SLOTS];
                    java.util.HashSet<String> uniquePairs = new java.util.HashSet<>();
                    try {
                        for (int i = 0; i < MAX_SPECIAL_SLOTS; i++) {
                            values[i] = triggers[i].getText().toString().trim().toUpperCase(java.util.Locale.ROOT);
                            if (values[i].isEmpty()) continue;
                            int[] pair = parseSpecialTrigger(values[i]);
                            String canonical = Math.min(pair[0], pair[1]) + ":" + Math.max(pair[0], pair[1]);
                            if (!uniquePairs.add(canonical)) throw new IllegalArgumentException("Cada especial precisa de um par diferente.");
                        }
                    } catch (IllegalArgumentException error) {
                        Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
                        return;
                    }
                    android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
                    for (int i = 0; i < MAX_SPECIAL_SLOTS; i++) editor.putString(specialTriggerPreferenceKey(i), values[i]);
                    editor.apply();
                    rebuildSpecialButtons();
                    int configured = 0;
                    for (String value : values) if (!value.isEmpty()) configured++;
                    Toast.makeText(this, configured + " botões especiais atualizados na tela.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

''',
)

if 'new EditText[2]' in s or 'new String[2]' in s or 'specialChordButton(0)' in s:
    raise SystemExit("A fixed two-special configuration remains in MainActivity.java")

main.write_text(s, encoding="utf-8")
print("Applied six configurable simultaneous specials with automatic on-screen buttons and shared Bluetooth mapping behavior")
