#!/usr/bin/env python3
"""Vortix 0.9.18: map a physical Bluetooth control to the per-game C* special."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply Bluetooth C* patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)


replace_once(
    '''    private static final String[] BLUETOOTH_CONTROL_LABELS = {
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
    };''',
    '''    private static final String[] BLUETOOTH_CONTROL_LABELS = {
            "Cima", "Baixo", "Esquerda", "Direita", "A", "B", "C", "D", "L", "R", "START", "SELECT", "C* Especial"
    };
    private static final String[] BLUETOOTH_CONTROL_KEYS = {
            "up", "down", "left", "right", "a", "b", "c", "d", "l", "r", "start", "select", "special"
    };
    private static final int[] BLUETOOTH_TARGET_KEY_CODES = {
            KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_DPAD_DOWN,
            KeyEvent.KEYCODE_DPAD_LEFT, KeyEvent.KEYCODE_DPAD_RIGHT,
            KeyEvent.KEYCODE_BUTTON_A, KeyEvent.KEYCODE_BUTTON_B,
            KeyEvent.KEYCODE_BUTTON_X, KeyEvent.KEYCODE_BUTTON_Y,
            KeyEvent.KEYCODE_BUTTON_L1, KeyEvent.KEYCODE_BUTTON_R1,
            KeyEvent.KEYCODE_BUTTON_START, KeyEvent.KEYCODE_BUTTON_SELECT,
            KeyEvent.KEYCODE_BUTTON_MODE
    };
    private static final int BLUETOOTH_SPECIAL_SLOT = 12;''',
    "add C* as a Bluetooth target",
)

replace_once(
    '''    private int bluetoothPhysicalKey(int slot) {
        return getPreferences(0).getInt(bluetoothPreferenceKey(slot), BLUETOOTH_TARGET_KEY_CODES[slot]);
    }''',
    '''    private int bluetoothPhysicalKey(int slot) {
        if (slot == BLUETOOTH_SPECIAL_SLOT && !getPreferences(0).contains(bluetoothPreferenceKey(slot)))
            return KeyEvent.KEYCODE_UNKNOWN;
        return getPreferences(0).getInt(bluetoothPreferenceKey(slot), BLUETOOTH_TARGET_KEY_CODES[slot]);
    }''',
    "leave C* unbound until user captures a key",
)

replace_once(
    '''        editor.putInt(bluetoothPreferenceKey(slot), physicalKeyCode).apply();
        pendingBluetoothCaptureSlot = -1;
        pendingBluetoothCaptureReleaseKey = physicalKeyCode;
        if (pendingBluetoothCaptureButton != null)
            pendingBluetoothCaptureButton.setText(bluetoothKeyLabel(physicalKeyCode));
        if (pendingBluetoothCaptureStatus != null)
            pendingBluetoothCaptureStatus.setText(BLUETOOTH_CONTROL_LABELS[slot] + " vinculado a " + bluetoothKeyLabel(physicalKeyCode) + ".");
        pendingBluetoothCaptureButton = null;
        Toast.makeText(this, "Botão Bluetooth configurado.", Toast.LENGTH_SHORT).show();''',
    '''        editor.putInt(bluetoothPreferenceKey(slot), physicalKeyCode);
        boolean specialSlot = slot == BLUETOOTH_SPECIAL_SLOT;
        if (specialSlot) editor.putBoolean(specialCTriggerPreferenceKey(), true);
        editor.apply();
        if (specialSlot) rebuildTouchControls();
        pendingBluetoothCaptureSlot = -1;
        pendingBluetoothCaptureReleaseKey = physicalKeyCode;
        if (pendingBluetoothCaptureButton != null)
            pendingBluetoothCaptureButton.setText(bluetoothKeyLabel(physicalKeyCode));
        if (pendingBluetoothCaptureStatus != null)
            pendingBluetoothCaptureStatus.setText(specialSlot
                    ? "C* do Bluetooth vinculado a " + bluetoothKeyLabel(physicalKeyCode) + "; botão C* da tela ativado neste jogo."
                    : BLUETOOTH_CONTROL_LABELS[slot] + " vinculado a " + bluetoothKeyLabel(physicalKeyCode) + ".");
        pendingBluetoothCaptureButton = null;
        Toast.makeText(this, specialSlot
                ? "C* Bluetooth configurado e botão especial ativado neste jogo."
                : "Botão Bluetooth configurado.", Toast.LENGTH_SHORT).show();''',
    "activate the per-game C* touch button after capture",
)

replace_once(
    'hint.setText("Toque em Capturar ao lado de cada ação e pressione o botão correspondente no controle Bluetooth. Se um botão já estiver ligado a outra ação, os vínculos são trocados. O mapeamento vale para todos os jogos; analógicos continuam no padrão e o direcional pode ser remapeado.");',
    'hint.setText("Conecte qualquer controle Bluetooth compatível com Android. Toque em Capturar e pressione o botão desejado. É possível mapear o direcional, A/B/C/D, L/R, START/SELECT e C* Especial. Ao mapear C*, o botão especial da tela é ativado automaticamente neste jogo; o par especial continua personalizado por jogo. Analógicos seguem no padrão.");',
    "explain generic Bluetooth capture and C* activation",
)

replace_once(
    '''    private void sendGameplayKeyEvent(int action, int keyCode) {
        if (retroView != null) retroView.sendKeyEvent(action, keyCode, 0);
    }''',
    '''    private void sendGameplayKeyEvent(int action, int keyCode) {
        if (retroView == null) return;
        if (keyCode == KeyEvent.KEYCODE_BUTTON_MODE
                && getPreferences(0).contains(bluetoothPreferenceKey(BLUETOOTH_SPECIAL_SLOT))) {
            sendConfiguredSpecialPair(action);
            return;
        }
        retroView.sendKeyEvent(action, keyCode, 0);
    }''',
    "route captured Bluetooth C* key to the selected special pair",
)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 26\n        versionName '0.9.17'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected official Vortix 0.9.17 version markers")
build.write_text(build_text.replace(old_version, "versionCode 27\n        versionName '0.9.18'", 1))
activity.write_text(text)
print("Added Bluetooth C* capture, automatic per-game screen activation, and Vortix 0.9.18.")
