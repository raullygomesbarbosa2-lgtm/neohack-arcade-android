#!/usr/bin/env python3
"""Vortix 0.9.7: make per-game double-tap macros easier to trigger and diagnose."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
main = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = main.read_text()

def replace_once(old: str, new: str, description: str) -> None:
    global text
    if old not in text:
        raise SystemExit(f"Could not apply Vortix 0.9.7 patch: {description}")
    text = text.replace(old, new, 1)

replace_once(
    "now - lastTap[0] <= android.view.ViewConfiguration.getDoubleTapTimeout();",
    "now - lastTap[0] <= Math.max(500, android.view.ViewConfiguration.getDoubleTapTimeout());",
    "more forgiving double-tap window",
)

replace_once(
    '''                isSecondTap[0] = specialSlot >= 0 && hasSpecialMacro(specialSlot)
                        && lastTap[0] > 0
                        && now - lastTap[0] <= Math.max(500, android.view.ViewConfiguration.getDoubleTapTimeout());
                lastTap[0] = isSecondTap[0] ? 0L : now;
                if (!isSecondTap[0]) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                if (!isSecondTap[0]) retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
                if (action == MotionEvent.ACTION_UP && isSecondTap[0]) triggerSpecialMacro(specialSlot);''',
    '''                isSecondTap[0] = specialSlot >= 0
                        && lastTap[0] > 0
                        && now - lastTap[0] <= Math.max(500, android.view.ViewConfiguration.getDoubleTapTimeout());
                lastTap[0] = isSecondTap[0] ? 0L : now;
                if (!isSecondTap[0] || !hasSpecialMacro(specialSlot))
                    retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                if (!isSecondTap[0] || !hasSpecialMacro(specialSlot))
                    retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
                if (action == MotionEvent.ACTION_UP && isSecondTap[0]) {
                    if (hasSpecialMacro(specialSlot)) triggerSpecialMacro(specialSlot);
                    else Toast.makeText(MainActivity.this,
                            "Sem especial salvo para este jogo. Abra MENU > Configurar especiais.",
                            Toast.LENGTH_LONG).show();
                }''',
    "keep normal presses while explaining missing per-game macro configuration",
)

replace_once(
    '''            specialMacroHandler.postDelayed(() -> playSpecialMacroStep(sequence, index + 1), 35);
        }, 70);''',
    '''            specialMacroHandler.postDelayed(() -> playSpecialMacroStep(sequence, index + 1), 70);
        }, 120);''',
    "hold each macro input longer for arcade cores to sample it",
)

main.write_text(text)

gradle = ROOT / "app/build.gradle"
gradle_text = gradle.read_text()
if "versionCode 15" not in gradle_text or "versionName '0.9.6-white-neon'" not in gradle_text:
    raise SystemExit("Expected Vortix 0.9.6 version markers before bumping to 0.9.7")
gradle_text = gradle_text.replace("versionCode 15", "versionCode 16", 1)
gradle_text = gradle_text.replace("versionName '0.9.6-white-neon'", "versionName '0.9.7-special-macros'", 1)
gradle.write_text(gradle_text)
print("Applied Vortix 0.9.7 double-tap, feedback, and macro timing improvements")
