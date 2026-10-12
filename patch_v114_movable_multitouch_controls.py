#!/usr/bin/env python3
"""Vortix 0.9.19: remove separate C* and add movable, configurable multi-touch controls."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply movable-controls patch ({label}); found {count} matches")
    text = text.replace(old, new, 1)


# Persist edit state and one active drag gesture.
replace_once(
    "    private String activeTouchSystemLabel;\n",
    "    private String activeTouchSystemLabel;\n"
    "    private boolean touchLayoutEditMode;\n"
    "    private View touchDraggingView;\n"
    "    private int touchDragPointerId = MotionEvent.INVALID_POINTER_ID;\n"
    "    private float touchDragOffsetX;\n"
    "    private float touchDragOffsetY;\n",
    "add movable layout state",
)

# Let the in-game menu enter and leave drag-edit mode.
replace_once(
    '''        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem", "Configurar especiais", "Configurar controle Bluetooth", "Controles na tela / toque leve"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else if (which == 3) showImageFilterDialog();
                    else if (which == 4) showSpecialConfigDialog();
                    else if (which == 5) showBluetoothConfigDialog();
                    else showTouchControlConfigDialog();
                })''',
    '''        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem", "Configurar especiais", "Configurar controle Bluetooth", "Controles na tela / toque leve",
                touchLayoutEditMode ? "Concluir movimentação dos botões" : "Mover botões na tela"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else if (which == 3) showImageFilterDialog();
                    else if (which == 4) showSpecialConfigDialog();
                    else if (which == 5) showBluetoothConfigDialog();
                    else if (which == 6) showTouchControlConfigDialog();
                    else toggleTouchLayoutEditMode();
                })''',
    "add move-controls menu entry",
)

# The option now exposes the multi-touch state rather than silently fixing it on.
replace_once(
    "        parent.setMotionEventSplittingEnabled(true);",
    "        parent.setMotionEventSplittingEnabled(isTouchMultitouchEnabled());",
    "make root multi-touch configurable",
)
replace_once(
    "        controls.setMotionEventSplittingEnabled(true);",
    "        controls.setMotionEventSplittingEnabled(isTouchMultitouchEnabled());",
    "make overlay multi-touch configurable",
)

# Replace the fixed 2x2 action grid with individually draggable A/B/C/D buttons.
replace_once(
    '''        GridLayout action = new GridLayout(this);
        action.setMotionEventSplittingEnabled(true);
        action.setColumnCount(2); action.setRowCount(2);
        addGridKey(action, "A", KeyEvent.KEYCODE_BUTTON_A, 0, 0);
        addGridKey(action, "B", KeyEvent.KEYCODE_BUTTON_B, 0, 1);
        addGridKey(action, "C", KeyEvent.KEYCODE_BUTTON_X, 1, 0);
        addGridKey(action, "D", KeyEvent.KEYCODE_BUTTON_Y, 1, 1);
        FrameLayout.LayoutParams actionParams = new FrameLayout.LayoutParams(-2, -2, Gravity.BOTTOM | Gravity.RIGHT);
        actionParams.rightMargin = dp(12); actionParams.bottomMargin = dp(10); controls.addView(action, actionParams);''',
    '''        addTouchActionButton(controls, "A", KeyEvent.KEYCODE_BUTTON_A, 0, 0);
        addTouchActionButton(controls, "B", KeyEvent.KEYCODE_BUTTON_B, 0, 1);
        addTouchActionButton(controls, "C", KeyEvent.KEYCODE_BUTTON_X, 1, 0);
        addTouchActionButton(controls, "D", KeyEvent.KEYCODE_BUTTON_Y, 1, 1);''',
    "replace fixed face-button grid with separate controls",
)

# Make the analog stick draggable during edit mode but leave its normal input behavior alone.
replace_once(
    '''        VirtualJoystickView joystick = new VirtualJoystickView();
        FrameLayout.LayoutParams joystickParams = new FrameLayout.LayoutParams(dp(144), dp(144), Gravity.BOTTOM | Gravity.LEFT);
        joystickParams.leftMargin = dp(18); joystickParams.bottomMargin = dp(14);
        controls.addView(joystick, joystickParams);''',
    '''        VirtualJoystickView joystick = new VirtualJoystickView();
        joystick.setTag("touch:DPAD");
        joystick.setOnTouchListener((view, event) -> touchLayoutEditMode && handleTouchControlDrag(view, event));
        FrameLayout.LayoutParams joystickParams = new FrameLayout.LayoutParams(dp(144), dp(144), Gravity.BOTTOM | Gravity.LEFT);
        joystickParams.leftMargin = dp(18); joystickParams.bottomMargin = dp(14);
        controls.addView(joystick, joystickParams);
        restoreTouchControlPosition(joystick);''',
    "allow moving the directional pad",
)

# Add move/drag and persistent normalized positions.
marker = "    private Button keyButton(String text, int keyCode, int width, int height) {\n"
if text.count(marker) != 1:
    raise SystemExit("Could not locate touch-button helper insertion point")
helpers = '''    private void addTouchActionButton(FrameLayout parent, String label, int keyCode, int row, int column) {
        int size = touchActionButtonDp();
        Button button = keyButton(label, keyCode, dp(size), dp(size));
        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(dp(size), dp(size), Gravity.BOTTOM | Gravity.RIGHT);
        params.rightMargin = dp(12 + (1 - column) * (size + 6));
        params.bottomMargin = dp(10 + (1 - row) * (size + 6));
        parent.addView(button, params);
    }

    private boolean isTouchMultitouchEnabled() {
        return getPreferences(0).getBoolean("touch_multitouch_enabled", true);
    }

    private String touchControlId(View view) {
        Object tag = view.getTag();
        if (tag instanceof String && ((String) tag).startsWith("touch:"))
            return ((String) tag).substring("touch:".length());
        return "control_" + view.getId();
    }

    private String touchPositionKey(View view, String axis) {
        return "touch_pos_" + touchControlId(view) + "_" + axis;
    }

    private void restoreTouchControlPosition(View view) {
        view.addOnLayoutChangeListener(new View.OnLayoutChangeListener() {
            private boolean applied;
            @Override public void onLayoutChange(View v, int left, int top, int right, int bottom,
                    int oldLeft, int oldTop, int oldRight, int oldBottom) {
                if (applied || !(v.getParent() instanceof FrameLayout)) return;
                FrameLayout parent = (FrameLayout) v.getParent();
                if (parent.getWidth() <= v.getWidth() || parent.getHeight() <= v.getHeight()) return;
                android.content.SharedPreferences preferences = getPreferences(0);
                float nx = preferences.getFloat(touchPositionKey(v, "x"), -1f);
                float ny = preferences.getFloat(touchPositionKey(v, "y"), -1f);
                if (nx < 0f || ny < 0f) {
                    applied = true;
                    v.removeOnLayoutChangeListener(this);
                    return;
                }
                applied = true;
                v.removeOnLayoutChangeListener(this);
                nx = Math.max(0f, Math.min(1f, nx));
                ny = Math.max(0f, Math.min(1f, ny));
                FrameLayout.LayoutParams params = (FrameLayout.LayoutParams) v.getLayoutParams();
                params.gravity = Gravity.TOP | Gravity.LEFT;
                params.leftMargin = Math.round(nx * (parent.getWidth() - v.getWidth()));
                params.topMargin = Math.round(ny * (parent.getHeight() - v.getHeight()));
                v.setTranslationX(0f);
                v.setTranslationY(0f);
                v.setLayoutParams(params);
            }
        });
    }

    private boolean handleTouchControlDrag(View view, MotionEvent event) {
        if (!touchLayoutEditMode || touchControlsContainer == null
                || !(view.getParent() instanceof FrameLayout)) return false;
        FrameLayout parent = (FrameLayout) view.getParent();
        int action = event.getActionMasked();
        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            if (touchDraggingView != null && touchDraggingView != view) return true;
            touchDraggingView = view;
            touchDragPointerId = event.getPointerId(event.getActionIndex());
            int[] location = new int[2];
            parent.getLocationOnScreen(location);
            touchDragOffsetX = event.getRawX() - location[0] - view.getX();
            touchDragOffsetY = event.getRawY() - location[1] - view.getY();
            view.bringToFront();
            return true;
        }
        if (view != touchDraggingView) return true;
        if (action == MotionEvent.ACTION_MOVE && touchDragPointerId != MotionEvent.INVALID_POINTER_ID) {
            int[] location = new int[2];
            parent.getLocationOnScreen(location);
            float maxX = Math.max(0f, parent.getWidth() - view.getWidth());
            float maxY = Math.max(0f, parent.getHeight() - view.getHeight());
            float x = event.getRawX() - location[0] - touchDragOffsetX;
            float y = event.getRawY() - location[1] - touchDragOffsetY;
            view.setX(Math.max(0f, Math.min(maxX, x)));
            view.setY(Math.max(0f, Math.min(maxY, y)));
            return true;
        }
        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL
                || action == MotionEvent.ACTION_POINTER_UP) {
            if (action == MotionEvent.ACTION_POINTER_UP
                    && event.getPointerId(event.getActionIndex()) != touchDragPointerId) return true;
            float maxX = Math.max(1f, parent.getWidth() - view.getWidth());
            float maxY = Math.max(1f, parent.getHeight() - view.getHeight());
            float x = Math.max(0f, Math.min(maxX, view.getX()));
            float y = Math.max(0f, Math.min(maxY, view.getY()));
            getPreferences(0).edit()
                    .putFloat(touchPositionKey(view, "x"), x / maxX)
                    .putFloat(touchPositionKey(view, "y"), y / maxY)
                    .apply();
            if (view.getLayoutParams() instanceof FrameLayout.LayoutParams) {
                FrameLayout.LayoutParams params = (FrameLayout.LayoutParams) view.getLayoutParams();
                params.gravity = Gravity.TOP | Gravity.LEFT;
                params.leftMargin = Math.round(x);
                params.topMargin = Math.round(y);
                view.setTranslationX(0f);
                view.setTranslationY(0f);
                view.setLayoutParams(params);
            }
            touchDraggingView = null;
            touchDragPointerId = MotionEvent.INVALID_POINTER_ID;
            return true;
        }
        return true;
    }

    private void toggleTouchLayoutEditMode() {
        touchLayoutEditMode = !touchLayoutEditMode;
        Toast.makeText(this, touchLayoutEditMode
                ? "Arraste A/B/C/D e os outros controles; abra MENU e conclua para sair."
                : "Posições dos controles salvas.", Toast.LENGTH_LONG).show();
    }

'''
text = text.replace(marker, helpers + marker, 1)

# Drag any key button only while edit mode is active; ordinary touch still sends immediate game input.
replace_once(
    '''        button.setText(text); button.setTextColor(0xffe8fbff); button.setTextSize(text.length() > 1 ? 11 : 17);
        button.setAllCaps(false); button.setPadding(0, 0, 0, 0);''',
    '''        button.setText(text); button.setTextColor(0xffe8fbff); button.setTextSize(text.length() > 1 ? 11 : 17);
        button.setTag("touch:" + text);
        button.setAllCaps(false); button.setPadding(0, 0, 0, 0);''',
    "tag on-screen controls for saved positions",
)
replace_once(
    '''        button.setOnTouchListener((view, event) -> {
            if (retroView == null) return true;
            int action = event.getActionMasked();''',
    '''        button.setOnTouchListener((view, event) -> {
            if (touchLayoutEditMode) return handleTouchControlDrag(view, event);
            if (retroView == null) return true;
            int action = event.getActionMasked();''',
    "route edit-mode touches to dragging instead of gameplay",
)
replace_once(
    '''        button.setLayoutParams(new FrameLayout.LayoutParams(width, height));
        return button;''',
    '''        button.setLayoutParams(new FrameLayout.LayoutParams(width, height));
        restoreTouchControlPosition(button);
        return button;''',
    "restore saved per-control locations",
)

# Add an on-screen indication that controls are being edited.
replace_once(
    '''    private void showTouchControlConfigDialog() {
        final int[] sizes = {54, 64, 76};
        final String[] labels = {"Compactos (54 dp)", "Médios • recomendado (64 dp)", "Grandes • dedo maior (76 dp)"};
        int current = getPreferences(0).getInt("touch_action_button_dp", 64);
        int selected = current <= 54 ? 0 : current >= 76 ? 2 : 1;
        final int[] choice = {selected};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Toque imediato • tamanho dos botões")
                .setSingleChoiceItems(labels, selected, (dialog, which) -> choice[0] = which)
                .setPositiveButton("Aplicar", (dialog, which) -> {
                    getPreferences(0).edit().putInt("touch_action_button_dp", sizes[choice[0]]).apply();
                    rebuildTouchControls();
                    Toast.makeText(this, "Aplicado: toque leve e multitoque simultâneo nos botões.", Toast.LENGTH_SHORT).show();
                })
                .setNeutralButton("Padrão", (dialog, which) -> {
                    getPreferences(0).edit().putInt("touch_action_button_dp", 64).apply();
                    rebuildTouchControls();
                    Toast.makeText(this, "Botões médios restaurados; toque continua imediato.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

''',
    '''    private void showTouchControlConfigDialog() {
        final int[] sizes = {54, 64, 76};
        final String[] labels = {"Compactos (54 dp)", "Médios • recomendado (64 dp)", "Grandes • dedo maior (76 dp)"};
        int current = getPreferences(0).getInt("touch_action_button_dp", 64);
        int selected = current <= 54 ? 0 : current >= 76 ? 2 : 1;
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        form.setPadding(dp(18), dp(8), dp(18), dp(8));
        TextView sizeHint = new TextView(this);
        sizeHint.setText("Tamanho dos botões de ação");
        sizeHint.setTextColor(0xff00e5ff);
        form.addView(sizeHint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        android.widget.RadioGroup sizesGroup = new android.widget.RadioGroup(this);
        sizesGroup.setOrientation(android.widget.RadioGroup.VERTICAL);
        for (int i = 0; i < labels.length; i++) {
            android.widget.RadioButton radio = new android.widget.RadioButton(this);
            radio.setId(i + 1);
            radio.setText(labels[i]);
            radio.setTextColor(0xffedfcff);
            radio.setChecked(i == selected);
            sizesGroup.addView(radio, new android.widget.RadioGroup.LayoutParams(-1, -2));
        }
        form.addView(sizesGroup, new android.widget.LinearLayout.LayoutParams(-1, -2));
        android.widget.Switch multitouch = new android.widget.Switch(this);
        multitouch.setText("Permitir multitoque simultâneo");
        multitouch.setTextColor(0xffedfcff);
        multitouch.setChecked(isTouchMultitouchEnabled());
        android.widget.LinearLayout.LayoutParams switchParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
        switchParams.topMargin = dp(10);
        form.addView(multitouch, switchParams);
        TextView hint = new TextView(this);
        hint.setText("Use MENU → Mover botões na tela para arrastar A/B/C/D e aproximá-los. O C normal continua; não há botão C separado.");
        hint.setTextColor(0xffc8f6ff);
        android.widget.LinearLayout.LayoutParams hintParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
        hintParams.topMargin = dp(8);
        form.addView(hint, hintParams);
        new android.app.AlertDialog.Builder(this)
                .setTitle("Controles na tela • toque e multitoque")
                .setView(form)
                .setPositiveButton("Aplicar", (dialog, which) -> {
                    int checked = sizesGroup.getCheckedRadioButtonId();
                    int sizeIndex = checked >= 1 && checked <= sizes.length ? checked - 1 : 1;
                    getPreferences(0).edit()
                            .putInt("touch_action_button_dp", sizes[sizeIndex])
                            .putBoolean("touch_multitouch_enabled", multitouch.isChecked())
                            .apply();
                    rebuildTouchControls();
                    Toast.makeText(this, multitouch.isChecked()
                            ? "Tamanho aplicado; multitoque simultâneo ativado."
                            : "Tamanho aplicado; multitoque desativado.", Toast.LENGTH_SHORT).show();
                })
                .setNeutralButton("Padrão", (dialog, which) -> {
                    getPreferences(0).edit()
                            .putInt("touch_action_button_dp", 64)
                            .putBoolean("touch_multitouch_enabled", true)
                            .apply();
                    rebuildTouchControls();
                    Toast.makeText(this, "Botões médios e multitoque restaurados.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

''',
    "add visible touch-size and multi-touch settings",
)

# Preserve Cadillacs' requested A+B default after removing the experimental C* patches.
replace_once(
    '''        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        return slot == 0 ? "A+C" : "B+D";''',
    '''        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        String gameName = currentStateFile == null ? "" : currentStateFile.getName().toLowerCase(java.util.Locale.ROOT);
        if (slot == 0 && gameName.contains("cadillacs")) return "A+B";
        return slot == 0 ? "A+C" : "B+D";''',
    "retain Cadillacs A+B default",
)

build = ROOT / "app/build.gradle"
build_text = build.read_text()
old_version = "versionCode 24\n        versionName '0.9.15'"
if build_text.count(old_version) != 1:
    raise SystemExit("Expected Vortix 0.9.15 markers from the v110 base")
build.write_text(build_text.replace(old_version, "versionCode 28\n        versionName '0.9.19'", 1))
activity.write_text(text)
print("Removed the separate C* control; added draggable button positions and a multi-touch toggle; Vortix 0.9.19.")
