#!/usr/bin/env python3
"""Vortix 0.9.13: visual per-game special pairs and manual Bluetooth key mapping."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply manual-controls patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)


replace_once(
    "    private boolean onboardingProfile;\n",
    """    private boolean onboardingProfile;
    private static final String[] BLUETOOTH_CONTROL_LABELS = {
            "Cima", "Baixo", "Esquerda", "Direita", "A", "B", "C", "D", "L", "R", "START", "SELECT"
    };
    private static final String[] BLUETOOTH_CONTROL_KEYS = {
            "up", "down", "left", "right", "a", "b", "c", "d", "l", "r", "start", "select"
    };
    private static final int[] BLUETOOTH_TARGET_KEY_CODES = {
            KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_DPAD_DOWN,
            KeyEvent.KEYCODE_DPAD_LEFT, KeyEvent.KEYCODE_DPAD_RIGHT,
            KeyEvent.KEYCODE_BUTTON_A, KeyEvent.KEYCODE_BUTTON_B,
            KeyEvent.KEYCODE_BUTTON_X, KeyEvent.KEYCODE_BUTTON_Y,
            KeyEvent.KEYCODE_BUTTON_L1, KeyEvent.KEYCODE_BUTTON_R1,
            KeyEvent.KEYCODE_BUTTON_START, KeyEvent.KEYCODE_BUTTON_SELECT
    };
    private final android.util.SparseIntArray pressedBluetoothKeys = new android.util.SparseIntArray();
    private int pendingBluetoothCaptureSlot = -1;
    private int pendingBluetoothCaptureReleaseKey = -1;
    private Button pendingBluetoothCaptureButton;
    private TextView pendingBluetoothCaptureStatus;
    private boolean bluetoothConfigDialogOpen;
""",
    "add Bluetooth mapping state",
)

replace_once(
    '''        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem", "Configurar especiais"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else if (which == 3) showImageFilterDialog();
                    else showSpecialConfigDialog();
                })''',
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
    "add Bluetooth configuration menu",
)

start = text.find("    private void showSpecialConfigDialog() {")
end = text.find("    private void showImageFilterDialog() {", start)
if start < 0 or end < 0 or text.find("    private void showSpecialConfigDialog() {", start + 1) >= 0:
    raise SystemExit("Could not locate the unique special/Bluetooth settings block")
text = text[:start] + '''    private int specialChoiceIndex(String token) {
        String value = token == null ? "" : token.trim().toUpperCase(java.util.Locale.ROOT);
        if ("B".equals(value)) return 1;
        if ("C".equals(value)) return 2;
        if ("D".equals(value)) return 3;
        return 0;
    }

    private void showSpecialConfigDialog() {
        final String[] choices = {"A", "B", "C", "D"};
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        form.setPadding(dp(18), dp(8), dp(18), dp(8));
        form.setBackgroundColor(0xff08131b);
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Escolha manualmente os dois botões que você quer pressionar juntos para cada especial deste jogo. Os botões são enviados normalmente ao jogo; não há macro nem sequência automática. Essa configuração vale só para o jogo aberto.");
        hint.setTextColor(0xffc8f6ff);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        android.widget.ArrayAdapter<String> adapter = new android.widget.ArrayAdapter<>(
                this, android.R.layout.simple_spinner_item, choices);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        android.widget.Spinner[][] selectors = new android.widget.Spinner[2][2];
        for (int pair = 0; pair < 2; pair++) {
            android.widget.TextView label = new android.widget.TextView(this);
            label.setText("Especial " + (pair + 1));
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
                .setTitle("Configurar especiais")
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
                        if (values[0].equals(values[1]) || values[0].equals(values[1].substring(2) + "+" + values[1].substring(0, 1)))
                            throw new IllegalArgumentException("Escolha dois pares diferentes.");
                    } catch (IllegalArgumentException error) {
                        Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
                        return;
                    }
                    android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
                    for (int pair = 0; pair < values.length; pair++)
                        editor.putString(specialTriggerPreferenceKey(pair), values[pair]);
                    editor.apply();
                    Toast.makeText(this, "Especiais salvos para este jogo.", Toast.LENGTH_SHORT).show();
                })
                .setNeutralButton("Padrão", (dialog, which) -> {
                    getPreferences(0).edit()
                            .putString(specialTriggerPreferenceKey(0), "A+C")
                            .putString(specialTriggerPreferenceKey(1), "B+D")
                            .apply();
                    Toast.makeText(this, "Pares padrão restaurados para este jogo.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private String bluetoothPreferenceKey(int slot) {
        return "bluetooth_control_" + BLUETOOTH_CONTROL_KEYS[slot];
    }

    private int bluetoothPhysicalKey(int slot) {
        return getPreferences(0).getInt(bluetoothPreferenceKey(slot), BLUETOOTH_TARGET_KEY_CODES[slot]);
    }

    private String bluetoothKeyLabel(int keyCode) {
        String label = KeyEvent.keyCodeToString(keyCode);
        return label.startsWith("KEYCODE_") ? label.substring(8) : label;
    }

    private int mappedBluetoothTarget(int physicalKeyCode) {
        for (int slot = 0; slot < BLUETOOTH_TARGET_KEY_CODES.length; slot++) {
            if (bluetoothPhysicalKey(slot) == physicalKeyCode) return BLUETOOTH_TARGET_KEY_CODES[slot];
        }
        return physicalKeyCode;
    }

    private boolean isBluetoothKeyEvent(KeyEvent event) {
        return event.isFromSource(android.view.InputDevice.SOURCE_GAMEPAD)
                || event.isFromSource(android.view.InputDevice.SOURCE_JOYSTICK)
                || event.isFromSource(android.view.InputDevice.SOURCE_DPAD);
    }

    private void captureBluetoothBinding(int physicalKeyCode) {
        int slot = pendingBluetoothCaptureSlot;
        if (slot < 0 || slot >= BLUETOOTH_TARGET_KEY_CODES.length) return;
        if (physicalKeyCode == KeyEvent.KEYCODE_UNKNOWN
                || physicalKeyCode == KeyEvent.KEYCODE_BACK
                || physicalKeyCode == KeyEvent.KEYCODE_VOLUME_UP
                || physicalKeyCode == KeyEvent.KEYCODE_VOLUME_DOWN) {
            if (pendingBluetoothCaptureStatus != null)
                pendingBluetoothCaptureStatus.setText("Esse botão do sistema não pode ser vinculado. Tente outro.");
            return;
        }
        int oldPhysicalKeyCode = bluetoothPhysicalKey(slot);
        android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
        for (int other = 0; other < BLUETOOTH_TARGET_KEY_CODES.length; other++) {
            if (other != slot && bluetoothPhysicalKey(other) == physicalKeyCode)
                editor.putInt(bluetoothPreferenceKey(other), oldPhysicalKeyCode);
        }
        editor.putInt(bluetoothPreferenceKey(slot), physicalKeyCode).apply();
        pendingBluetoothCaptureSlot = -1;
        pendingBluetoothCaptureReleaseKey = physicalKeyCode;
        if (pendingBluetoothCaptureButton != null)
            pendingBluetoothCaptureButton.setText(bluetoothKeyLabel(physicalKeyCode));
        if (pendingBluetoothCaptureStatus != null)
            pendingBluetoothCaptureStatus.setText(BLUETOOTH_CONTROL_LABELS[slot] + " vinculado a " + bluetoothKeyLabel(physicalKeyCode) + ".");
        pendingBluetoothCaptureButton = null;
        Toast.makeText(this, "Botão Bluetooth configurado.", Toast.LENGTH_SHORT).show();
    }

    private void resetBluetoothBindings() {
        android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
        for (String key : BLUETOOTH_CONTROL_KEYS) editor.remove("bluetooth_control_" + key);
        editor.apply();
    }

    private void showBluetoothConfigDialog() {
        bluetoothConfigDialogOpen = true;
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        form.setPadding(dp(18), dp(8), dp(18), dp(8));
        form.setBackgroundColor(0xff08131b);
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Toque em Capturar ao lado de cada ação e pressione o botão correspondente no controle Bluetooth. Se um botão já estiver ligado a outra ação, os vínculos são trocados. O mapeamento vale para todos os jogos; analógicos continuam no padrão e o direcional pode ser remapeado.");
        hint.setTextColor(0xffc8f6ff);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        TextView status = new TextView(this);
        status.setText("Conecte o controle Bluetooth antes de capturar.");
        status.setTextColor(0xff00e5ff);
        android.widget.LinearLayout.LayoutParams statusParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
        statusParams.topMargin = dp(8);
        form.addView(status, statusParams);
        Button[] captureButtons = new Button[BLUETOOTH_CONTROL_LABELS.length];
        for (int slot = 0; slot < BLUETOOTH_CONTROL_LABELS.length; slot++) {
            final int captureSlot = slot;
            android.widget.LinearLayout row = new android.widget.LinearLayout(this);
            row.setOrientation(android.widget.LinearLayout.HORIZONTAL);
            row.setGravity(Gravity.CENTER_VERTICAL);
            TextView label = new TextView(this);
            label.setText(BLUETOOTH_CONTROL_LABELS[slot]);
            label.setTextColor(0xffedfcff);
            row.addView(label, new android.widget.LinearLayout.LayoutParams(0, -2, 1f));
            Button capture = menuButton(bluetoothKeyLabel(bluetoothPhysicalKey(slot)));
            capture.setOnClickListener(view -> {
                pendingBluetoothCaptureSlot = captureSlot;
                pendingBluetoothCaptureButton = captureButtons[captureSlot];
                pendingBluetoothCaptureStatus = status;
                status.setText("Pressione agora o botão do controle para " + BLUETOOTH_CONTROL_LABELS[captureSlot] + ".");
            });
            captureButtons[slot] = capture;
            row.addView(capture, new android.widget.LinearLayout.LayoutParams(dp(142), dp(42)));
            android.widget.LinearLayout.LayoutParams rowParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            rowParams.topMargin = dp(4);
            form.addView(row, rowParams);
        }
        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.addView(form);
        android.app.AlertDialog dialog = new android.app.AlertDialog.Builder(this)
                .setTitle("Controles Bluetooth")
                .setView(scroll)
                .setPositiveButton("Fechar", null)
                .setNeutralButton("Padrão", (ignored, which) -> {
                    resetBluetoothBindings();
                    Toast.makeText(this, "Mapeamento Bluetooth padrão restaurado.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .create();
        pendingBluetoothCaptureStatus = status;
        dialog.setOnKeyListener((ignored, keyCode, event) -> {
            if (pendingBluetoothCaptureReleaseKey == keyCode) {
                if (event.getAction() == KeyEvent.ACTION_UP) pendingBluetoothCaptureReleaseKey = -1;
                return true;
            }
            if (pendingBluetoothCaptureSlot >= 0 && event.getAction() == KeyEvent.ACTION_DOWN && event.getRepeatCount() == 0) {
                captureBluetoothBinding(keyCode);
                return true;
            }
            return isBluetoothKeyEvent(event);
        });
        dialog.setOnDismissListener(ignored -> {
            bluetoothConfigDialogOpen = false;
            pendingBluetoothCaptureSlot = -1;
            pendingBluetoothCaptureReleaseKey = -1;
            pendingBluetoothCaptureButton = null;
            pendingBluetoothCaptureStatus = null;
        });
        dialog.show();
    }

''' + text[end:]

replace_once(
    '''    @Override public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (retroView != null && keyCode != KeyEvent.KEYCODE_VOLUME_UP && keyCode != KeyEvent.KEYCODE_VOLUME_DOWN) {
            retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
    @Override public boolean onKeyUp(int keyCode, KeyEvent event) {
        if (retroView != null && keyCode != KeyEvent.KEYCODE_VOLUME_UP && keyCode != KeyEvent.KEYCODE_VOLUME_DOWN) {
            retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            return true;
        }
        return super.onKeyUp(keyCode, event);
    }
    @Override public boolean onGenericMotionEvent(MotionEvent event) {
        if (retroView != null) {''',
    '''    @Override public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (pendingBluetoothCaptureSlot >= 0 && keyCode != KeyEvent.KEYCODE_VOLUME_UP
                && keyCode != KeyEvent.KEYCODE_VOLUME_DOWN && keyCode != KeyEvent.KEYCODE_BACK) {
            captureBluetoothBinding(keyCode);
            return true;
        }
        if (retroView != null && keyCode != KeyEvent.KEYCODE_VOLUME_UP && keyCode != KeyEvent.KEYCODE_VOLUME_DOWN) {
            int targetKeyCode = isBluetoothKeyEvent(event) ? mappedBluetoothTarget(keyCode) : keyCode;
            if (isBluetoothKeyEvent(event)) pressedBluetoothKeys.put(keyCode, targetKeyCode);
            retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, targetKeyCode, 0);
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
    @Override public boolean onKeyUp(int keyCode, KeyEvent event) {
        if (pendingBluetoothCaptureReleaseKey == keyCode) {
            pendingBluetoothCaptureReleaseKey = -1;
            return true;
        }
        if (retroView != null && keyCode != KeyEvent.KEYCODE_VOLUME_UP && keyCode != KeyEvent.KEYCODE_VOLUME_DOWN) {
            int index = pressedBluetoothKeys.indexOfKey(keyCode);
            int targetKeyCode;
            if (index >= 0) {
                targetKeyCode = pressedBluetoothKeys.valueAt(index);
                pressedBluetoothKeys.removeAt(index);
            } else {
                targetKeyCode = isBluetoothKeyEvent(event) ? mappedBluetoothTarget(keyCode) : keyCode;
            }
            retroView.sendKeyEvent(KeyEvent.ACTION_UP, targetKeyCode, 0);
            return true;
        }
        return super.onKeyUp(keyCode, event);
    }
    @Override public boolean onGenericMotionEvent(MotionEvent event) {
        if (bluetoothConfigDialogOpen) return true;
        if (retroView != null) {''',
    "route Bluetooth controls through manual mapping",
)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 21\n        versionName '0.9.12'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected official Vortix 0.9.12 version markers")
build.write_text(build_text.replace(old_version, "versionCode 22\n        versionName '0.9.13'", 1))
activity.write_text(text)
print("Added manual special-pair selectors and Bluetooth controller remapping for Vortix 0.9.13.")
