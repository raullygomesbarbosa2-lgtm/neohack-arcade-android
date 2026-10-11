#!/usr/bin/env python3
"""Vortix 0.9.9 Test 3: per-game default macros and cyan-on-black neon UI."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()

def replace_once(old: str, new: str, description: str) -> None:
    global text
    if text.count(old) != 1:
        raise SystemExit(f"Could not apply Vortix 0.9.9 patch ({description}); found {text.count(old)} matches")
    text = text.replace(old, new, 1)

# Per-ROM preference values override the default preset, including an explicit empty value to disable it.
replace_once('''    private boolean hasSpecialMacro(int slot) {
        return slot >= 0 && !getPreferences(0).getString(specialMovePreferenceKey(slot), "").trim().isEmpty();
    }''', '''    private String specialMacroForSlot(int slot) {
        if (slot < 0 || slot > 3) return "";
        String key = specialMovePreferenceKey(slot);
        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        if (slot == 0) return "A+B";
        if (slot == 1) return "C+D";
        return "";
    }

    private boolean hasSpecialMacro(int slot) {
        return !specialMacroForSlot(slot).isEmpty();
    }''', "per-game defaults and explicit override support")

replace_once('''        hint.setText("Configure cada especial: vírgula separa etapas e + aperta botões juntos. Ex.: BAIXO, BAIXO+DIREITA, DIREITA, A+B. Toque duplo no botão correspondente executa a sequência.");
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));''', '''        hint.setText("Padrões por jogo: toque duplo em A executa A+B juntos; toque duplo em B executa C+D juntos. Você pode editar cada sequência só para esta ROM. Use vírgula para etapas e + para apertar botões juntos (ex.: BAIXO, DIREITA, A+B). Deixe um campo vazio para desativar esse especial neste jogo.");
        hint.setTextColor(0xffc8f6ff);
        form.setBackgroundColor(0xff08131b);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));''', "explain default presets in settings")

replace_once('''            label.setText(labels[i]);
            android.widget.LinearLayout.LayoutParams labelParams''', '''            label.setText(labels[i]);
            label.setTextColor(0xff00e5ff);
            android.widget.LinearLayout.LayoutParams labelParams''', "cyan macro field labels")
replace_once('''            fields[i].setHint("BAIXO, DIREITA, A+B");
            fields[i].setText(getPreferences(0).getString(specialMovePreferenceKey(i), ""));
            form.addView(fields[i], new android.widget.LinearLayout.LayoutParams(-1, -2));''', '''            fields[i].setHint("BAIXO, DIREITA, A+B");
            fields[i].setHintTextColor(0xff80aeb8);
            fields[i].setTextColor(0xffedfcff);
            fields[i].setText(specialMacroForSlot(i));
            GradientDrawable macroInput = new GradientDrawable();
            macroInput.setColor(0xff10212b); macroInput.setCornerRadius(dp(8)); macroInput.setStroke(dp(1), 0xff00bfd8);
            fields[i].setBackground(macroInput);
            form.addView(fields[i], new android.widget.LinearLayout.LayoutParams(-1, -2));''', "dark readable macro editor")
replace_once('''        String raw = getPreferences(0).getString(specialMovePreferenceKey(slot), "");''', '''        String raw = specialMacroForSlot(slot);''', "run default or per-game override")

# Cyan neon dark interface, including the library and profile screens.
replacements = [
    ('new int[]{0xfff5fcff, 0xffe7f7fb, 0xffffffff}', 'new int[]{0xff03070d, 0xff07131c, 0xff030810}'),
    ('shape.setColor(filled ? 0xffe4fbff : 0xffffffff);', 'shape.setColor(filled ? 0xff07333f : 0xff101b24);'),
    ('button.setTextColor(0xff123542);', 'button.setTextColor(0xffe8fbff);\n        button.setShadowLayer(dp(4), 0, 0, 0xff00bde8);'),
    ('title.setTextColor(0xff007f9b);', 'title.setTextColor(0xffa9f7ff);'),
    ('info.setTextColor(0xff286477);', 'info.setTextColor(0xffc5eaf0);'),
    ('romHelp.setTextColor(0xff335966);', 'romHelp.setTextColor(0xffa9d2dc);'),
    ('box.setColor(0xeeffffff);', 'box.setColor(0xee0a1720);'),
    ('name.setTextColor(0xff12323f);', 'name.setTextColor(0xffe8fbff);'),
    ('edit.setText("EDITAR PERFIL"); edit.setTextColor(0xff007f9e);', 'edit.setText("EDITAR PERFIL"); edit.setTextColor(0xff00e5ff);'),
    ('circle.setShape(GradientDrawable.OVAL); circle.setColor(0xffdef9ff);', 'circle.setShape(GradientDrawable.OVAL); circle.setColor(0xff0a2832);'),
    ('glyph.setTextSize(sizeDp * .43f); glyph.setGravity(Gravity.CENTER); glyph.setTextColor(0xff12414d);', 'glyph.setTextSize(sizeDp * .43f); glyph.setGravity(Gravity.CENTER); glyph.setTextColor(0xffd7fbff);'),
    ('hint.setTextColor(0xff335966);', 'hint.setTextColor(0xffb2dce4);'),
    ('profileNameInput.setSingleLine(true); profileNameInput.setTextSize(17); profileNameInput.setTextColor(0xff12323f);', 'profileNameInput.setSingleLine(true); profileNameInput.setTextSize(17); profileNameInput.setTextColor(0xffedfcff);'),
    ('profileNameInput.setHintTextColor(0xff7faab2);', 'profileNameInput.setHintTextColor(0xff80aeb8);'),
    ('inputBg.setColor(0xfff8fdff);', 'inputBg.setColor(0xff0d1a23);'),
    ('choose.setTextColor(0xff007f9e);', 'choose.setTextColor(0xff00e5ff);'),
    ('button.setText(text); button.setTextColor(Color.WHITE);', 'button.setText(text); button.setTextColor(0xffe8fbff);'),
    ('int[] neon = {0xffff5470, 0xff42d7ff, 0xff9cff57, 0xffffcb4b};', 'int[] neon = {0xff00e5ff, 0xff00e5ff, 0xff00e5ff, 0xff00e5ff};'),
    ('background.setStroke(dp(1), 0x99ffffff);', 'background.setStroke(dp(1), 0xff00bfd8);'),
]
for old, new in replacements:
    if old not in text:
        raise SystemExit(f"Could not apply Vortix 0.9.9 theme replacement: {old}")
    text = text.replace(old, new)
activity.write_text(text)

# Dark system dialogs as well as custom native views.
styles = ROOT / "app/src/main/res/values/styles.xml"
style_text = styles.read_text()
old = 'parent="android:style/Theme.Material.Light.NoActionBar"'
if style_text.count(old) != 1:
    raise SystemExit("Expected exactly one light AppTheme parent")
styles.write_text(style_text.replace(old, 'parent="android:style/Theme.Material.NoActionBar"', 1))

# Keep both downloadable APKs genuinely single-ABI for smaller, diagnosable installs.
build = ROOT / "app/build.gradle"
build_text = build.read_text()
if "applicationId 'br.com.raully.neohackarcade.test098'" not in build_text:
    raise SystemExit("Expected Test 2 application ID before creating side-by-side Test 3")
build_text = build_text.replace("applicationId 'br.com.raully.neohackarcade.test098'", "applicationId 'br.com.raully.neohackarcade.test099'", 1)
old_version = "versionCode 17\n        versionName '0.9.8-first-run-fix'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected Vortix 0.9.8 version markers before bump")
build_text = build_text.replace(old_version, "versionCode 18\n        versionName '0.9.9-cyan-macros'", 1)
abi_filters = "        ndk { abiFilters 'armeabi-v7a', 'arm64-v8a' }\n"
if build_text.count(abi_filters) != 1:
    raise SystemExit("Expected the generated two-ABI ndk filter block before configuring split APKs")
build_text = build_text.replace(abi_filters, "", 1)
marker = "    packaging {\n"
if build_text.count(marker) != 1:
    raise SystemExit("Expected exactly one Android packaging block")
build_text = build_text.replace(marker, "    splits {\n        abi {\n            enable true\n            reset()\n            include 'armeabi-v7a', 'arm64-v8a'\n            universalApk false\n        }\n    }\n\n" + marker, 1)
build.write_text(build_text)

manifest = ROOT / "app/src/main/AndroidManifest.xml"
manifest_text = manifest.read_text()
if manifest_text.count('android:label="Vortix Test 2"') != 1:
    raise SystemExit("Expected Vortix Test 2 launcher label")
manifest.write_text(manifest_text.replace('android:label="Vortix Test 2"', 'android:label="Vortix Test 3"', 1))
print("Applied Vortix 0.9.9 Test 3 defaults, editable per-game overrides, cyan neon dark theme and ABI splits")
