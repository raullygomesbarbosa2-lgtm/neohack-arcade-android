#!/usr/bin/env python3
"""Remove touch latency, improve large-finger multitouch, and tune virtual-stick response."""
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

# Allow independent fingers to be delivered to separate overlay buttons.
replace_once(
    "        gameOverlayRoot = parent;\n        touchControlViews.clear();\n",
    "        gameOverlayRoot = parent;\n        parent.setMotionEventSplittingEnabled(true);\n        touchControlViews.clear();\n",
    "multitouch split",
)

# Larger touch targets for people using broad fingers.
s = s.replace("dp(52), dp(42)", "dp(60), dp(48)")
s = s.replace("dp(144), dp(144)", "dp(160), dp(160)")
s = s.replace("grid.addView(keyButton(text, keyCode, dp(54), dp(54)), gridParams(row, column));",
              "grid.addView(keyButton(text, keyCode, dp(66), dp(66)), gridParams(row, column));")
s = s.replace("params.width = dp(54); params.height = dp(54); params.setMargins(dp(2), dp(2), dp(2), dp(2));",
              "params.width = dp(66); params.height = dp(66); params.setMargins(dp(3), dp(3), dp(3), dp(3));")
s = s.replace("FrameLayout.LayoutParams(dp(52), dp(52), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL)",
              "FrameLayout.LayoutParams(dp(66), dp(56), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL)")
# Apply lighter direction input immediately, with per-user sensitivity stored on-device.
old_thresholds = '''            boolean nextLeft = magnitude > 0.24f && nx < -0.34f;
            boolean nextRight = magnitude > 0.24f && nx > 0.34f;
            boolean nextUp = magnitude > 0.24f && ny < -0.34f;
            boolean nextDown = magnitude > 0.24f && ny > 0.34f;'''
new_thresholds = '''            float sensitivity = Math.max(0, Math.min(100, getPreferences(0).getInt("stick_sensitivity", 78))) / 100f;
            float magnitudeGate = 0.24f - 0.12f * sensitivity;
            float axisGate = 0.34f - 0.12f * sensitivity;
            boolean nextLeft = magnitude > magnitudeGate && nx < -axisGate;
            boolean nextRight = magnitude > magnitudeGate && nx > axisGate;
            boolean nextUp = magnitude > magnitudeGate && ny < -axisGate;
            boolean nextDown = magnitude > magnitudeGate && ny > axisGate;'''
replace_once(old_thresholds, new_thresholds, "joystick sensitivity")

# Cadillacs and Dinosaurs commonly needs A+B; preserve the usual per-game defaults elsewhere.
old_default = '        return slot == 0 ? "A+C" : "B+D";'
new_default = '''        String rom = currentStateFile == null ? "" : currentStateFile.getName().toLowerCase(java.util.Locale.ROOT);
        if (rom.contains("dino") || rom.contains("cadillacs") || rom.contains("dinosaurs"))
            return slot == 0 ? "A+B" : "C+D";
        return slot == 0 ? "A+C" : "B+D";'''
replace_once(old_default, new_default, "Cadillacs special default")

# Show the active simultaneous pair on each large special pad and keep it held until finger-up.
replace_once('Button button = menuButton("ESP" + (slot + 1));',
             'Button button = menuButton("ESP " + specialTriggerForSlot(slot));', "special pad label")
replace_once('''        button.setOnTouchListener((view, event) -> {
            if (event.getActionMasked() == MotionEvent.ACTION_DOWN) triggerSpecialChord(slot);
            return true;
        });''', '''        button.setOnTouchListener((view, event) -> {
            int action = event.getActionMasked();
            if (action == MotionEvent.ACTION_DOWN) beginTouchSpecialChord(slot);
            else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) endTouchSpecialChord(slot);
            return true;
        });''', "special pad hold/release")

replace_method(
    "    private final java.util.HashMap<Integer, Runnable> specialChordReleaseTasks = new java.util.HashMap<>();\n\n    private void triggerSpecialChord(int slot) {\n",
    "    private void triggerSpecialMacro(int slot) {\n",
    '''    private final java.util.HashMap<Integer, int[]> activeTouchSpecialPairs = new java.util.HashMap<>();

    private void beginTouchSpecialChord(int slot) {
        if (retroView == null) return;
        endTouchSpecialChord(slot);
        final int[] pair;
        try { pair = parseSpecialTrigger(specialTriggerForSlot(slot)); }
        catch (IllegalArgumentException error) {
            Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
            return;
        }
        activeTouchSpecialPairs.put(slot, pair);
        retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, pair[0], 0);
        retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, pair[1], 0);
    }

    private void endTouchSpecialChord(int slot) {
        int[] pair = activeTouchSpecialPairs.remove(slot);
        if (pair != null && retroView != null) {
            retroView.sendKeyEvent(KeyEvent.ACTION_UP, pair[0], 0);
            retroView.sendKeyEvent(KeyEvent.ACTION_UP, pair[1], 0);
        }
    }

''',
)

# Screen buttons bypass the delayed 130 ms chord recognizer: simultaneous fingers arrive immediately.
old_touch = '''            if (action == MotionEvent.ACTION_DOWN) {
                if (specialSlot < 0 || !handleConfiguredChordKey(keyCode, true))
                    retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                if (specialSlot < 0 || !handleConfiguredChordKey(keyCode, false))
                    retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
                // Cancellation is treated as a proper release by the chord handler.
            }'''
new_touch = '''            if (action == MotionEvent.ACTION_DOWN) {
                retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            }'''
replace_once(old_touch, new_touch, "immediate touchscreen key events")

# Bluetooth key presses also go straight through. A+B naturally overlap in the emulator with no timer.
old_keydown = '''            int mapped = mapControllerDown(keyCode);
            if (!handleConfiguredChordKey(mapped, true)) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, mapped, 0);
            return true;'''
new_keydown = '''            int mapped = mapControllerDown(keyCode);
            if (event.getRepeatCount() == 0) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, mapped, 0);
            return true;'''
replace_once(old_keydown, new_keydown, "immediate Bluetooth key-down")
old_keyup = '''            int mapped = mapControllerUp(keyCode);
            if (!handleConfiguredChordKey(mapped, false)) retroView.sendKeyEvent(KeyEvent.ACTION_UP, mapped, 0);
            return true;'''
new_keyup = '''            int mapped = mapControllerUp(keyCode);
            retroView.sendKeyEvent(KeyEvent.ACTION_UP, mapped, 0);
            return true;'''
replace_once(old_keyup, new_keyup, "immediate Bluetooth key-up")

# Remove the old delayed chord recognizer; physical and touch buttons now emit
# normal simultaneous key-down/key-up events directly.
replace_method(
    "    private static final long SPECIAL_CHORD_WINDOW_MS = 130L;\n",
    "    private void playSpecialMacroStep(java.util.ArrayList<java.util.ArrayList<Integer>> sequence, int index) {\n",
    "",
)

# Add a simple, live sensitivity slider to the on-screen controls settings.
replace_once(
    '        android.widget.TextView opacityLabel = new android.widget.TextView(this);\n',
    '        android.widget.TextView opacityLabel = new android.widget.TextView(this);\n        android.widget.TextView sensitivityLabel = new android.widget.TextView(this);\n',
    "sensitivity label",
)
replace_once(
    '        android.widget.SeekBar opacitySeek = new android.widget.SeekBar(this); opacitySeek.setMax(70);\n',
    '        android.widget.SeekBar opacitySeek = new android.widget.SeekBar(this); opacitySeek.setMax(70);\n        android.widget.SeekBar sensitivitySeek = new android.widget.SeekBar(this); sensitivitySeek.setMax(100);\n',
    "sensitivity slider",
)
replace_once(
    '        form.addView(opacityLabel); form.addView(opacitySeek);\n',
    '        form.addView(opacityLabel); form.addView(opacitySeek);\n        form.addView(sensitivityLabel); form.addView(sensitivitySeek);\n',
    "sensitivity slider layout",
)
replace_once(
    '            opacityLabel.setText("Opacidade: " + (30 + opacitySeek.getProgress()) + "%");\n',
    '            opacityLabel.setText("Opacidade: " + (30 + opacitySeek.getProgress()) + "%");\n            sensitivityLabel.setText("Sensibilidade do direcional: " + sensitivitySeek.getProgress() + "% (toque leve)");\n',
    "sensitivity label update",
)
replace_once(
    '            opacitySeek.setProgress(prefs.getInt(touchKey(id, "opacity"), 90) - 30);\n',
    '            opacitySeek.setProgress(prefs.getInt(touchKey(id, "opacity"), 90) - 30);\n            sensitivitySeek.setProgress(prefs.getInt("stick_sensitivity", 78));\n',
    "sensitivity load",
)
replace_once(
    '        opacitySeek.setOnSeekBarChangeListener(listener);\n',
    '''        opacitySeek.setOnSeekBarChangeListener(listener);
        sensitivitySeek.setOnSeekBarChangeListener(new android.widget.SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(android.widget.SeekBar bar, int value, boolean fromUser) {
                if (!loading[0]) getPreferences(0).edit().putInt("stick_sensitivity", value).apply();
                updateLabels.run();
            }
            @Override public void onStartTrackingTouch(android.widget.SeekBar bar) { }
            @Override public void onStopTrackingTouch(android.widget.SeekBar bar) { }
        });
''',
    "sensitivity listener",
)
replace_once(
    '            loading[0] = false;\n            persist.run();\n        });\n        selector.setSelection(0);',
    '            loading[0] = false;\n            getPreferences(0).edit().putInt("stick_sensitivity", 78).apply();\n            sensitivitySeek.setProgress(78);\n            persist.run();\n        });\n        selector.setSelection(0);',
    "sensitivity reset",
)

if "handleConfiguredChordKey(" in s or "triggerSpecialChord(" in s:
    raise SystemExit("A delayed chord-handler reference remains in generated MainActivity.java")

main.write_text(s, encoding="utf-8")
print("Applied immediate multitouch input, larger targets, lighter stick, per-game A+B default, and hold-to-release specials")
