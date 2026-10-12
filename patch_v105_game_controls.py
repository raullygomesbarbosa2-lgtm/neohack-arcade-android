#!/usr/bin/env python3
"""Add green neon styling, editable touch/controller controls, specials, and local Pix settings."""
from pathlib import Path

MAIN = Path("app/src/main/java/br/com/raully/neohackarcade/MainActivity.java")
s = MAIN.read_text(encoding="utf-8")


def require_replace(old: str, new: str, label: str, count: int = 1) -> None:
    global s
    found = s.count(old)
    if found != count:
        raise SystemExit(f"{label}: expected {count} anchor(s), found {found}")
    s = s.replace(old, new, count)


def replace_method(start: str, end: str, body: str) -> None:
    global s
    a = s.find(start)
    b = s.find(end, a + len(start))
    if a < 0 or b < 0:
        raise SystemExit(f"Could not replace method between {start!r} and {end!r}")
    s = s[:a] + body + s[b:]

# Use a distinct mint/lime neon palette throughout the native app and CHIP-8 view.
palette = {
    "0xff00e5ff": "0xff9aff3f", "0xff00d9ff": "0xffb0ff65",
    "0xff00bfd8": "0xff8be648", "0xff00bde8": "0xff9cee55",
    "0xff00cfff": "0xffb7ff59", "0xff00dffc": "0xffc2ff66",
    "0xff58eaff": "0xffc7ff9b", "0xff71f0ff": "0xffd9ffa8",
    "0xff79faff": "0xffc9ff8a", "0xff9affff": "0xffe2ffb7",
    "0xffa9f7ff": "0xffd9ffb1", "0xffa7fbff": "0xffd4ffaa",
    "0xffc8f6ff": "0xffe5ffc9", "0xffc5eaf0": "0xffd8f3c2",
    "0xffd7fdff": "0xffe4ffc8", "0xffd7fbff": "0xffdfffc1",
    "0xffe8fbff": "0xffebffdb", "0xffedfcff": "0xfff0ffe3",
    "0xff80aeb8": "0xffa3c58b", "0xff43efff": "0xffb2ff64",
    "0x8858eaff": "0x889bff55", "0xff007f98": "0xff477c24",
    "0xff00b9d4": "0xff89dd49", "0xff14536a": "0xff2c6425",
    "0xff00cde8": "0xff8fe648", "0xff007f98": "0xff477c24",
    "0xffb2dce4": "0xffd2e9b8", "0xffa9d2dc": "0xffbcd2a5",
    "0xff91a2aa": "0xff98a88b", "0xff0b202b": "0xff13220d",
    "0xff0c1c27": "0xff10200d", "0xff10212b": "0xff19270f",
    "0xff071c28": "0xff091d0a", "0xff081018": "0xff080f07",
    "0xff03070d": "0xff030603", "0xff030a10": "0xff030803",
    "0xff0a2832": "0xff1b2a0c", "0xff0a1720": "0xff091407",
    "0xff07333f": "0xff18300c", "0xff07131c": "0xff071207",
    "0xff0b1018": "0xff0b1208", "0xff101b24": "0xff101b0a",
    "0xff0d1a23": "0xff0d1b09",
}
for file in Path("app/src/main/java").rglob("*.java"):
    text = file.read_text(encoding="utf-8")
    for old, new in palette.items():
        text = text.replace(old, new)
    file.write_text(text, encoding="utf-8")
s = MAIN.read_text(encoding="utf-8")

# Pix is configured locally by the owner; no private key is placed in source or CI artifacts.
replace_method(
    "    private String readPixKey() {\n",
    "    private void showCoreCatalog() {\n",
    '''    private String readPixKey() {
        String local = getPreferences(0).getString("pix_key_local", "").trim();
        if (!local.isEmpty()) return local;
        // Optional private-build asset fallback. Public builds intentionally omit this asset.
        try (InputStream input = getAssets().open("pix_key.txt");
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[128];
            int count;
            while ((count = input.read(buffer)) != -1) output.write(buffer, 0, count);
            return new String(output.toByteArray(), java.nio.charset.StandardCharsets.UTF_8).trim();
        } catch (Exception ignored) {
            return "";
        }
    }

    private void copyPixKey() {
        String pixKey = readPixKey();
        if (pixKey.isEmpty()) {
            showPixKeySetupDialog();
            return;
        }
        copyPixValue(pixKey);
    }

    private void copyPixValue(String pixKey) {
        ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (clipboard != null) {
            clipboard.setPrimaryClip(ClipData.newPlainText("Chave Pix Vortix Pro", pixKey));
            Toast.makeText(this, "Chave Pix copiada.", Toast.LENGTH_LONG).show();
        } else {
            Toast.makeText(this, "Não consegui copiar a chave Pix.", Toast.LENGTH_SHORT).show();
        }
    }

    private void showPixKeySetupDialog() {
        final EditText input = new EditText(this);
        input.setSingleLine(true);
        input.setHint("Digite ou cole sua chave Pix");
        input.setText(readPixKey());
        input.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        android.app.AlertDialog dialog = new android.app.AlertDialog.Builder(this)
                .setTitle("Configurar chave Pix")
                .setMessage("A chave fica salva somente neste aparelho; ela não é enviada nem incluída no APK público.")
                .setView(input)
                .setPositiveButton("Salvar e copiar", null)
                .setNeutralButton("Apagar chave", null)
                .setNegativeButton("Cancelar", null)
                .create();
        dialog.setOnShowListener(ignored -> {
            dialog.getButton(android.app.AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
                String value = input.getText().toString().trim();
                if (value.isEmpty()) {
                    Toast.makeText(this, "Digite uma chave Pix primeiro.", Toast.LENGTH_SHORT).show();
                    return;
                }
                getPreferences(0).edit().putString("pix_key_local", value).apply();
                copyPixValue(value);
                dialog.dismiss();
            });
            dialog.getButton(android.app.AlertDialog.BUTTON_NEUTRAL).setOnClickListener(v -> {
                getPreferences(0).edit().remove("pix_key_local").apply();
                Toast.makeText(this, "Chave Pix removida deste aparelho.", Toast.LENGTH_SHORT).show();
                dialog.dismiss();
            });
        });
        dialog.show();
    }

''',
)

# Add the touch-layout editor and Bluetooth mapper to the in-game menu.
replace_method(
    "    private void showGameOptions() {\n",
    "    private void saveCurrentState() {\n",
    '''    private void showGameOptions() {
        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem",
                "Configurar controles da tela", "Mapear controle Bluetooth", "Configurar especiais"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else if (which == 3) showImageFilterDialog();
                    else if (which == 4) showTouchControlSettings();
                    else if (which == 5) showBluetoothMappingDialog();
                    else showSpecialConfigDialog();
                })
                .setNegativeButton("Fechar", null)
                .show();
    }

    private String controlsScope() {
        return currentStateFile == null ? "default" : currentStateFile.getName();
    }

    private String touchKey(String id, String field) {
        return "touch_" + controlsScope() + "_" + id + "_" + field;
    }

    private String bluetoothKey(int action) {
        return "bluetooth_" + controlsScope() + "_" + action;
    }

    private final java.util.HashMap<String, View> touchControlViews = new java.util.HashMap<>();
    private final java.util.HashMap<String, int[]> touchControlDefaults = new java.util.HashMap<>();
    private final java.util.HashMap<Integer, Integer> controllerDownMap = new java.util.HashMap<>();
    private FrameLayout gameOverlayRoot;

    private void registerTouchControl(FrameLayout parent, String id, View view, int defaultX, int defaultY) {
        touchControlViews.put(id, view);
        touchControlDefaults.put(id, new int[]{defaultX, defaultY});
        android.content.SharedPreferences prefs = getPreferences(0);
        int size = prefs.getInt(touchKey(id, "size"), 100);
        int angle = prefs.getInt(touchKey(id, "angle"), 0);
        int opacity = prefs.getInt(touchKey(id, "opacity"), 90);
        view.setScaleX(size / 100f);
        view.setScaleY(size / 100f);
        view.setRotation(angle);
        view.setAlpha(opacity / 100f);
        if (prefs.contains(touchKey(id, "x")) || prefs.contains(touchKey(id, "y"))) {
            int x = prefs.getInt(touchKey(id, "x"), defaultX);
            int y = prefs.getInt(touchKey(id, "y"), defaultY);
            parent.post(() -> setTouchPosition(parent, view, x, y));
        }
    }

    private void setTouchPosition(FrameLayout parent, View view, int x, int y) {
        if (parent.getWidth() <= 0 || parent.getHeight() <= 0 || view.getWidth() <= 0 || view.getHeight() <= 0) {
            parent.postDelayed(() -> setTouchPosition(parent, view, x, y), 40);
            return;
        }
        FrameLayout.LayoutParams params = (FrameLayout.LayoutParams) view.getLayoutParams();
        params.gravity = Gravity.TOP | Gravity.LEFT;
        params.leftMargin = Math.round(Math.max(0, parent.getWidth() - view.getWidth()) * Math.max(0, Math.min(100, x)) / 100f);
        params.topMargin = Math.round(Math.max(0, parent.getHeight() - view.getHeight()) * Math.max(0, Math.min(100, y)) / 100f);
        params.rightMargin = 0;
        params.bottomMargin = 0;
        view.setLayoutParams(params);
    }

    private void saveTouchControl(String id, int x, int y, int size, int angle, int opacity) {
        getPreferences(0).edit()
                .putInt(touchKey(id, "x"), x).putInt(touchKey(id, "y"), y)
                .putInt(touchKey(id, "size"), size).putInt(touchKey(id, "angle"), angle)
                .putInt(touchKey(id, "opacity"), opacity).apply();
        View view = touchControlViews.get(id);
        if (view == null) return;
        view.setScaleX(size / 100f);
        view.setScaleY(size / 100f);
        view.setRotation(angle);
        view.setAlpha(opacity / 100f);
        if (gameOverlayRoot != null) setTouchPosition(gameOverlayRoot, view, x, y);
    }

    private void showTouchControlSettings() {
        if (gameOverlayRoot == null || touchControlViews.isEmpty()) {
            Toast.makeText(this, "Abra um jogo para editar os controles da tela.", Toast.LENGTH_SHORT).show();
            return;
        }
        final String[] ids = {"joystick", "actions", "l", "r", "start", "select", "special1", "special2"};
        final String[] labels = {"Alavanca direcional", "Grupo A/B/C/D", "Ombro L", "Ombro R", "Start", "Select", "Especial 1", "Especial 2"};
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        int pad = dp(16);
        form.setPadding(pad, dp(8), pad, dp(8));
        android.widget.Spinner selector = new android.widget.Spinner(this);
        selector.setAdapter(new android.widget.ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, labels));
        form.addView(selector, new android.widget.LinearLayout.LayoutParams(-1, dp(48)));
        android.widget.TextView xLabel = new android.widget.TextView(this);
        android.widget.TextView yLabel = new android.widget.TextView(this);
        android.widget.TextView sizeLabel = new android.widget.TextView(this);
        android.widget.TextView angleLabel = new android.widget.TextView(this);
        android.widget.TextView opacityLabel = new android.widget.TextView(this);
        android.widget.SeekBar xSeek = new android.widget.SeekBar(this); xSeek.setMax(100);
        android.widget.SeekBar ySeek = new android.widget.SeekBar(this); ySeek.setMax(100);
        android.widget.SeekBar sizeSeek = new android.widget.SeekBar(this); sizeSeek.setMax(150);
        android.widget.SeekBar angleSeek = new android.widget.SeekBar(this); angleSeek.setMax(360);
        android.widget.SeekBar opacitySeek = new android.widget.SeekBar(this); opacitySeek.setMax(70);
        form.addView(xLabel); form.addView(xSeek);
        form.addView(yLabel); form.addView(ySeek);
        form.addView(sizeLabel); form.addView(sizeSeek);
        form.addView(angleLabel); form.addView(angleSeek);
        form.addView(opacityLabel); form.addView(opacitySeek);
        Button reset = menuButton("RESTAURAR ESTE CONTROLE");
        form.addView(reset, new android.widget.LinearLayout.LayoutParams(-1, dp(44)));
        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.addView(form);
        final boolean[] loading = {true};
        final int[] selected = {0};
        Runnable updateLabels = () -> {
            xLabel.setText("Posição horizontal: " + xSeek.getProgress() + "%");
            yLabel.setText("Posição vertical: " + ySeek.getProgress() + "%");
            sizeLabel.setText("Tamanho: " + (50 + sizeSeek.getProgress()) + "%");
            angleLabel.setText("Ângulo: " + angleSeek.getProgress() + "°");
            opacityLabel.setText("Opacidade: " + (30 + opacitySeek.getProgress()) + "%");
        };
        Runnable loadSelected = () -> {
            selected[0] = selector.getSelectedItemPosition();
            String id = ids[Math.max(0, Math.min(ids.length - 1, selected[0]))];
            int[] defaults = touchControlDefaults.get(id);
            int dx = defaults == null ? 50 : defaults[0];
            int dy = defaults == null ? 50 : defaults[1];
            android.content.SharedPreferences prefs = getPreferences(0);
            loading[0] = true;
            xSeek.setProgress(prefs.getInt(touchKey(id, "x"), dx));
            ySeek.setProgress(prefs.getInt(touchKey(id, "y"), dy));
            sizeSeek.setProgress(prefs.getInt(touchKey(id, "size"), 100) - 50);
            angleSeek.setProgress(prefs.getInt(touchKey(id, "angle"), 0));
            opacitySeek.setProgress(prefs.getInt(touchKey(id, "opacity"), 90) - 30);
            loading[0] = false;
            updateLabels.run();
        };
        Runnable persist = () -> {
            if (loading[0]) return;
            int index = Math.max(0, Math.min(ids.length - 1, selector.getSelectedItemPosition()));
            saveTouchControl(ids[index], xSeek.getProgress(), ySeek.getProgress(),
                    50 + sizeSeek.getProgress(), angleSeek.getProgress(), 30 + opacitySeek.getProgress());
            updateLabels.run();
        };
        android.widget.SeekBar.OnSeekBarChangeListener listener = new android.widget.SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(android.widget.SeekBar bar, int value, boolean fromUser) { persist.run(); }
            @Override public void onStartTrackingTouch(android.widget.SeekBar bar) { }
            @Override public void onStopTrackingTouch(android.widget.SeekBar bar) { }
        };
        xSeek.setOnSeekBarChangeListener(listener); ySeek.setOnSeekBarChangeListener(listener);
        sizeSeek.setOnSeekBarChangeListener(listener); angleSeek.setOnSeekBarChangeListener(listener);
        opacitySeek.setOnSeekBarChangeListener(listener);
        selector.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(android.widget.AdapterView<?> parent, View view, int position, long id) { loadSelected.run(); }
            @Override public void onNothingSelected(android.widget.AdapterView<?> parent) { }
        });
        reset.setOnClickListener(v -> {
            String id = ids[Math.max(0, Math.min(ids.length - 1, selector.getSelectedItemPosition()))];
            int[] defaults = touchControlDefaults.get(id);
            int dx = defaults == null ? 50 : defaults[0]; int dy = defaults == null ? 50 : defaults[1];
            loading[0] = true;
            xSeek.setProgress(dx); ySeek.setProgress(dy); sizeSeek.setProgress(50); angleSeek.setProgress(0); opacitySeek.setProgress(60);
            loading[0] = false;
            persist.run();
        });
        selector.setSelection(0);
        loadSelected.run();
        new android.app.AlertDialog.Builder(this)
                .setTitle("Controles da tela • posição, tamanho e ângulo")
                .setMessage("Escolha um controle e ajuste os sliders. As alterações ficam salvas para este jogo.")
                .setView(scroll)
                .setPositiveButton("Concluir", null)
                .setNegativeButton("Fechar", null)
                .show();
    }

    private static final int[] CONTROLLER_ACTIONS = {
            KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_DPAD_DOWN, KeyEvent.KEYCODE_DPAD_LEFT, KeyEvent.KEYCODE_DPAD_RIGHT,
            KeyEvent.KEYCODE_BUTTON_A, KeyEvent.KEYCODE_BUTTON_B, KeyEvent.KEYCODE_BUTTON_X, KeyEvent.KEYCODE_BUTTON_Y,
            KeyEvent.KEYCODE_BUTTON_L1, KeyEvent.KEYCODE_BUTTON_R1, KeyEvent.KEYCODE_BUTTON_START, KeyEvent.KEYCODE_BUTTON_SELECT
    };
    private static final String[] CONTROLLER_ACTION_LABELS = {
            "Cima", "Baixo", "Esquerda", "Direita", "A", "B", "C / X", "D / Y", "L", "R", "Start", "Select"
    };
    private static final int[] CONTROLLER_PHYSICAL_KEYS = {
            KeyEvent.KEYCODE_BUTTON_A, KeyEvent.KEYCODE_BUTTON_B, KeyEvent.KEYCODE_BUTTON_X, KeyEvent.KEYCODE_BUTTON_Y,
            KeyEvent.KEYCODE_BUTTON_L1, KeyEvent.KEYCODE_BUTTON_R1, KeyEvent.KEYCODE_BUTTON_L2, KeyEvent.KEYCODE_BUTTON_R2,
            KeyEvent.KEYCODE_BUTTON_START, KeyEvent.KEYCODE_BUTTON_SELECT,
            KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_DPAD_DOWN, KeyEvent.KEYCODE_DPAD_LEFT, KeyEvent.KEYCODE_DPAD_RIGHT
    };
    private static final String[] CONTROLLER_PHYSICAL_LABELS = {
            "Botão A", "Botão B", "Botão X", "Botão Y", "L1", "R1", "L2", "R2", "Start", "Select",
            "Direcional cima", "Direcional baixo", "Direcional esquerda", "Direcional direita"
    };

    private int mappedPhysicalForAction(int action) {
        return getPreferences(0).getInt(bluetoothKey(action), action);
    }

    private int mapControllerDown(int physical) {
        int logical = physical;
        for (int action : CONTROLLER_ACTIONS) if (mappedPhysicalForAction(action) == physical) { logical = action; break; }
        controllerDownMap.put(physical, logical);
        return logical;
    }

    private int mapControllerUp(int physical) {
        Integer mapped = controllerDownMap.remove(physical);
        if (mapped != null) return mapped;
        for (int action : CONTROLLER_ACTIONS) if (mappedPhysicalForAction(action) == physical) return action;
        return physical;
    }

    private void saveControllerMapping(int action, int physical) {
        for (int other : CONTROLLER_ACTIONS) {
            if (other != action && mappedPhysicalForAction(other) == physical) {
                Toast.makeText(this, "Esse botão físico já está mapeado para " + controllerActionName(other) + ".", Toast.LENGTH_LONG).show();
                return;
            }
        }
        android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
        if (physical == action) editor.remove(bluetoothKey(action));
        else editor.putInt(bluetoothKey(action), physical);
        editor.apply();
        Toast.makeText(this, controllerActionName(action) + " mapeado para " + KeyEvent.keyCodeToString(physical) + ".", Toast.LENGTH_SHORT).show();
    }

    private String controllerActionName(int key) {
        for (int i = 0; i < CONTROLLER_ACTIONS.length; i++) if (CONTROLLER_ACTIONS[i] == key) return CONTROLLER_ACTION_LABELS[i];
        return KeyEvent.keyCodeToString(key);
    }

    private void showBluetoothMappingDialog() {
        String[] rows = new String[CONTROLLER_ACTIONS.length];
        for (int i = 0; i < rows.length; i++) {
            int physical = mappedPhysicalForAction(CONTROLLER_ACTIONS[i]);
            rows[i] = CONTROLLER_ACTION_LABELS[i] + "  ←  " + KeyEvent.keyCodeToString(physical);
        }
        new android.app.AlertDialog.Builder(this)
                .setTitle("Mapeamento manual • Bluetooth")
                .setMessage("Toque numa ação e escolha qual botão físico do controle vai acioná-la.")
                .setItems(rows, (dialog, which) -> showBluetoothActionOptions(CONTROLLER_ACTIONS[which]))
                .setNeutralButton("Restaurar padrão", (dialog, which) -> {
                    android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
                    for (int action : CONTROLLER_ACTIONS) editor.remove(bluetoothKey(action));
                    editor.apply();
                    Toast.makeText(this, "Mapeamento Bluetooth restaurado.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Fechar", null)
                .show();
    }

    private void showBluetoothActionOptions(int action) {
        String[] options = new String[CONTROLLER_PHYSICAL_KEYS.length];
        for (int i = 0; i < options.length; i++) options[i] = CONTROLLER_PHYSICAL_LABELS[i];
        final android.app.AlertDialog[] holder = new android.app.AlertDialog[1];
        android.app.AlertDialog dialog = new android.app.AlertDialog.Builder(this)
                .setTitle("Mapear " + controllerActionName(action))
                .setItems(options, (d, which) -> saveControllerMapping(action, CONTROLLER_PHYSICAL_KEYS[which]))
                .setNeutralButton("Capturar botão agora", null)
                .setNegativeButton("Cancelar", null)
                .create();
        dialog.setOnShowListener(ignored -> dialog.getButton(android.app.AlertDialog.BUTTON_NEUTRAL).setOnClickListener(v -> {
            dialog.dismiss();
            captureBluetoothButton(action);
        }));
        holder[0] = dialog;
        dialog.show();
    }

    private void captureBluetoothButton(int action) {
        final android.widget.TextView prompt = new android.widget.TextView(this);
        prompt.setText("Pressione agora o botão do controle Bluetooth que deve acionar " + controllerActionName(action) + ".");
        prompt.setTextColor(0xffe5ffc9);
        prompt.setPadding(dp(24), dp(24), dp(24), dp(24));
        prompt.setFocusable(true); prompt.setFocusableInTouchMode(true);
        final android.app.AlertDialog dialog = new android.app.AlertDialog.Builder(this)
                .setTitle("Capturar botão físico")
                .setView(prompt)
                .setNegativeButton("Cancelar", null)
                .create();
        android.view.View.OnKeyListener listener = (view, keyCode, event) -> {
            if (event.getAction() == KeyEvent.ACTION_DOWN && event.getRepeatCount() == 0
                    && keyCode != KeyEvent.KEYCODE_BACK && keyCode != KeyEvent.KEYCODE_VOLUME_UP && keyCode != KeyEvent.KEYCODE_VOLUME_DOWN) {
                saveControllerMapping(action, keyCode);
                dialog.dismiss();
                return true;
            }
            return true;
        };
        prompt.setOnKeyListener(listener);
        dialog.setOnKeyListener((d, keyCode, event) -> listener.onKey(prompt, keyCode, event));
        dialog.setOnShowListener(ignored -> { prompt.requestFocus(); });
        dialog.show();
        prompt.requestFocus();
    }

''',
)

# Add control settings references and two actual simultaneous special buttons to gameplay overlay.
require_replace(
    "    private void addTouchControls(FrameLayout parent, String systemLabel) {\n",
    "    private void addTouchControls(FrameLayout parent, String systemLabel) {\n        gameOverlayRoot = parent;\n        touchControlViews.clear();\n        touchControlDefaults.clear();\n",
    "touch-control registry",
)
require_replace("        parent.addView(shoulderL, shoulderLParams);\n", "        parent.addView(shoulderL, shoulderLParams);\n        registerTouchControl(parent, \"l\", shoulderL, 2, 5);\n", "left shoulder registration")
require_replace("        parent.addView(shoulderR, shoulderRParams);\n", "        parent.addView(shoulderR, shoulderRParams);\n        registerTouchControl(parent, \"r\", shoulderR, 92, 5);\n", "right shoulder registration")
require_replace("        parent.addView(joystick, joystickParams);\n", "        parent.addView(joystick, joystickParams);\n        registerTouchControl(parent, \"joystick\", joystick, 4, 72);\n", "joystick registration")
require_replace("        actionParams.rightMargin = dp(12); actionParams.bottomMargin = dp(10); parent.addView(action, actionParams);\n", "        actionParams.rightMargin = dp(12); actionParams.bottomMargin = dp(10); parent.addView(action, actionParams);\n        registerTouchControl(parent, \"actions\", action, 75, 68);\n\n        Button special1 = specialChordButton(0);\n        FrameLayout.LayoutParams special1Params = new FrameLayout.LayoutParams(dp(52), dp(52), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);\n        special1Params.bottomMargin = dp(112); special1Params.rightMargin = dp(46); parent.addView(special1, special1Params);\n        registerTouchControl(parent, \"special1\", special1, 56, 66);\n        Button special2 = specialChordButton(1);\n        FrameLayout.LayoutParams special2Params = new FrameLayout.LayoutParams(dp(52), dp(52), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);\n        special2Params.bottomMargin = dp(112); special2Params.leftMargin = dp(46); parent.addView(special2, special2Params);\n        registerTouchControl(parent, \"special2\", special2, 64, 66);\n", "special touchscreen buttons")
require_replace("        coinParams.bottomMargin = dp(12); coinParams.leftMargin = dp(40); parent.addView(coin, coinParams);\n", "        coinParams.bottomMargin = dp(12); coinParams.leftMargin = dp(40); parent.addView(coin, coinParams);\n        registerTouchControl(parent, \"start\", start, 55, 88);\n        registerTouchControl(parent, \"select\", coin, 36, 88);\n", "start/select registration")

# Moveable/rotatable special pads trigger only simultaneous pairs (not a scripted sequence).
marker = "    private Button overlayMenuButton(String text) {\n"
special_button = '''    private Button specialChordButton(int slot) {
        Button button = menuButton("ESP" + (slot + 1));
        button.setTextSize(12);
        button.setContentDescription("Especial simultâneo " + (slot + 1));
        button.setOnTouchListener((view, event) -> {
            if (event.getActionMasked() == MotionEvent.ACTION_DOWN) triggerSpecialChord(slot);
            return true;
        });
        return button;
    }

'''
if s.count(marker) != 1:
    raise SystemExit("Could not find overlay button insertion point")
s = s.replace(marker, special_button + marker, 1)

# Default specials are A+C and B+D, and the menu only configures simultaneous pairs.
s = s.replace('return slot == 0 ? "A+B" : "C+D";', 'return slot == 0 ? "A+C" : "B+D";')
require_replace("                triggerSpecialMacro(matchedSlot);\n", "                triggerSpecialChord(matchedSlot);\n", "simultaneous special dispatch")
replace_method(
    "    private void showSpecialConfigDialog() {\n",
    "    private void triggerSpecialMacro(int slot) {\n",
    '''    private void showSpecialConfigDialog() {
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        int padding = dp(18);
        form.setPadding(padding, dp(8), padding, dp(8));
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Configure dois botões que serão pressionados juntos. Os especiais não executam sequências automáticas.");
        hint.setTextColor(0xffe5ffc9);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        EditText[] triggers = new EditText[2];
        for (int i = 0; i < 2; i++) {
            android.widget.TextView label = new android.widget.TextView(this);
            label.setText("Especial " + (i + 1) + " • par simultâneo");
            label.setTextColor(0xffb2ff64);
            android.widget.LinearLayout.LayoutParams labelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            labelParams.topMargin = dp(12);
            form.addView(label, labelParams);
            triggers[i] = new EditText(this);
            triggers[i].setSingleLine(true);
            triggers[i].setHint(i == 0 ? "A+C" : "B+D");
            triggers[i].setText(specialTriggerForSlot(i));
            form.addView(triggers[i], new android.widget.LinearLayout.LayoutParams(-1, -2));
        }
        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.addView(form);
        new android.app.AlertDialog.Builder(this)
                .setTitle("Configurar especiais deste jogo")
                .setView(scroll)
                .setPositiveButton("Salvar", (dialog, which) -> {
                    String[] values = new String[2];
                    try {
                        for (int i = 0; i < 2; i++) {
                            values[i] = triggers[i].getText().toString().trim().toUpperCase(java.util.Locale.ROOT);
                            parseSpecialTrigger(values[i]);
                        }
                        int[] first = parseSpecialTrigger(values[0]);
                        int[] second = parseSpecialTrigger(values[1]);
                        if ((first[0] == second[0] && first[1] == second[1]) || (first[0] == second[1] && first[1] == second[0]))
                            throw new IllegalArgumentException("Escolha dois pares diferentes.");
                    } catch (IllegalArgumentException error) {
                        Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
                        return;
                    }
                    android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
                    for (int i = 0; i < 2; i++) editor.putString(specialTriggerPreferenceKey(i), values[i]);
                    editor.apply();
                    Toast.makeText(this, "Especiais simultâneos salvos para este jogo.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private final java.util.HashMap<Integer, Runnable> specialChordReleaseTasks = new java.util.HashMap<>();

    private void triggerSpecialChord(int slot) {
        if (retroView == null) return;
        final int[] pair;
        try { pair = parseSpecialTrigger(specialTriggerForSlot(slot)); }
        catch (IllegalArgumentException error) {
            Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
            return;
        }
        Runnable old = specialChordReleaseTasks.remove(slot);
        if (old != null) specialMacroHandler.removeCallbacks(old);
        retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, pair[0], 0);
        retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, pair[1], 0);
        Runnable release = () -> {
            if (retroView != null) {
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, pair[0], 0);
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, pair[1], 0);
            }
            specialChordReleaseTasks.remove(slot);
        };
        specialChordReleaseTasks.put(slot, release);
        specialMacroHandler.postDelayed(release, 120L);
    }

''',
)

# Route Bluetooth key presses through the manual per-game mapping while preserving key-up pairing.
require_replace(
    '            if (!handleConfiguredChordKey(keyCode, true)) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);\n',
    '            int mapped = mapControllerDown(keyCode);\n            if (!handleConfiguredChordKey(mapped, true)) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, mapped, 0);\n',
    "Bluetooth key-down mapping",
)
require_replace(
    '            if (!handleConfiguredChordKey(keyCode, false)) retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);\n',
    '            int mapped = mapControllerUp(keyCode);\n            if (!handleConfiguredChordKey(mapped, false)) retroView.sendKeyEvent(KeyEvent.ACTION_UP, mapped, 0);\n',
    "Bluetooth key-up mapping",
)

# Update the Pix button with a shortcut to configure the local-only key.
require_replace(
    '        copyPix.setOnClickListener(v -> copyPixKey());\n',
    '        copyPix.setOnClickListener(v -> copyPixKey());\n        copyPix.setOnLongClickListener(v -> { showPixKeySetupDialog(); return true; });\n',
    "Pix local settings shortcut",
)

MAIN.write_text(s, encoding="utf-8")

# Match the Android theme resource to the same green-neon palette.
styles = Path("app/src/main/res/values/styles.xml")
if styles.exists():
    text = styles.read_text(encoding="utf-8").replace("#00E5FF", "#9AFF3F").replace("#030A10", "#030803")
    styles.write_text(text, encoding="utf-8")

print("Applied green neon theme, editable touch layout, simultaneous on-screen specials, Bluetooth mapping, and local Pix configuration")
