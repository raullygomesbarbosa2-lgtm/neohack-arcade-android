#!/usr/bin/env python3
"""Vortix 0.9.20: add a movable rectangular Especial A e B touch button."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply Especial A+B button patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)


replace_once(
    "    private boolean touchLayoutEditMode;\n",
    "    private boolean touchLayoutEditMode;\n    private boolean specialABButtonHeld;\n",
    "track simultaneous A+B button state",
)

replace_once(
    '''        addTouchActionButton(controls, "A", KeyEvent.KEYCODE_BUTTON_A, 0, 0);
        addTouchActionButton(controls, "B", KeyEvent.KEYCODE_BUTTON_B, 0, 1);
        addTouchActionButton(controls, "C", KeyEvent.KEYCODE_BUTTON_X, 1, 0);
        addTouchActionButton(controls, "D", KeyEvent.KEYCODE_BUTTON_Y, 1, 1);''',
    '''        addTouchActionButton(controls, "A", KeyEvent.KEYCODE_BUTTON_A, 0, 0);
        addTouchActionButton(controls, "B", KeyEvent.KEYCODE_BUTTON_B, 0, 1);
        addTouchActionButton(controls, "C", KeyEvent.KEYCODE_BUTTON_X, 1, 0);
        addTouchActionButton(controls, "D", KeyEvent.KEYCODE_BUTTON_Y, 1, 1);
        addSpecialABTouchButton(controls);''',
    "add a distinct rectangular A+B action",
)

marker = "    private boolean isTouchMultitouchEnabled() {\n"
if text.count(marker) != 1:
    raise SystemExit("Could not locate special-button helper insertion point")
helper = '''    private void addSpecialABTouchButton(FrameLayout parent) {
        int size = touchActionButtonDp();
        int width = dp(size * 2 + 6);
        int height = dp(48);
        Button button = keyButton("Especial A e B", KeyEvent.KEYCODE_UNKNOWN, width, height);
        button.setTag("touch:SPECIAL_AB");
        button.setTextSize(12f);
        button.setTextColor(0xffb9ff66);
        button.setContentDescription("Especial A e B: pressiona A e B simultaneamente");
        button.setOnTouchListener((view, event) -> {
            if (touchLayoutEditMode) return handleTouchControlDrag(view, event);
            if (retroView == null) return true;
            int action = event.getActionMasked();
            if ((action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN)
                    && !specialABButtonHeld) {
                retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_BUTTON_A, 0);
                retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_BUTTON_B, 0);
                specialABButtonHeld = true;
            } else if ((action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP
                    || action == MotionEvent.ACTION_CANCEL) && specialABButtonHeld) {
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_BUTTON_B, 0);
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_BUTTON_A, 0);
                specialABButtonHeld = false;
            }
            return true;
        });
        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(width, height, Gravity.BOTTOM | Gravity.RIGHT);
        params.rightMargin = dp(12);
        params.bottomMargin = dp(10 + 2 * (size + 6));
        parent.addView(button, params);
    }

'''
text = text.replace(marker, helper + marker, 1)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 28\n        versionName '0.9.19'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected Vortix 0.9.19 version markers")
build.write_text(build_text.replace(old_version, "versionCode 29\n        versionName '0.9.20'", 1))
activity.write_text(text)
print("Added a movable rectangular Especial A e B button; normal C remains unchanged; Vortix 0.9.20.")
