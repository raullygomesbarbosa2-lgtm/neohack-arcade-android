#!/usr/bin/env python3
"""Add an in-game drag editor for independently repositionable touch controls."""
from pathlib import Path

main = Path("app/src/main/java/br/com/raully/neohackarcade/MainActivity.java")
s = main.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    s = s.replace(old, new, 1)


# Add a direct, easy-to-find entry while keeping the existing fine sliders.
replace_once(
    '"Configurar controles da tela", "Mapear controle Bluetooth", "Configurar especiais"};',
    '"Configurar controles da tela", "Mapear controle Bluetooth", "Configurar especiais", "Mover botões com o dedo"};',
    "move-controls menu item",
)
replace_once(
    '                    else if (which == 5) showBluetoothMappingDialog();\n                    else showSpecialConfigDialog();',
    '                    else if (which == 5) showBluetoothMappingDialog();\n                    else if (which == 6) showSpecialConfigDialog();\n                    else startTouchLayoutEditor();',
    "move-controls menu action",
)

# Mark each face key and special pad so the editor can move them separately.
replace_once(
    '        Button button = menuButton("ESP" + (slot + 1) + " " + specialTriggerForSlot(slot));\n',
    '        Button button = menuButton("ESP" + (slot + 1) + " " + specialTriggerForSlot(slot));\n        button.setTag("special_" + slot);\n        restoreNestedControlPosition(button);\n',
    "special-button move tag",
)
replace_once(
    '            specialControlsRow.addView(button, params);\n            visible++;',
    '            specialControlsRow.addView(button, params);\n            restoreNestedControlPosition(button);\n            visible++;',
    "restore special-button position",
)
replace_once(
    '''    private void addGridKey(GridLayout grid, String text, int keyCode, int row, int column) {
        grid.addView(keyButton(text, keyCode, dp(66), dp(66)), gridParams(row, column));
    }
''',
    '''    private void addGridKey(GridLayout grid, String text, int keyCode, int row, int column) {
        Button button = keyButton(text, keyCode, dp(66), dp(66));
        button.setTag("face_" + text);
        restoreNestedControlPosition(button);
        grid.addView(button, gridParams(row, column));
    }
''',
    "individually movable A/B/C/D buttons",
)

# Let the face and special buttons render outside their original group while being spaced.
replace_once(
    '        parent.setMotionEventSplittingEnabled(true);\n        touchControlViews.clear();',
    '        parent.setMotionEventSplittingEnabled(true);\n        parent.setClipChildren(false);\n        parent.setClipToPadding(false);\n        touchControlViews.clear();',
    "allow repositioned controls outside groups",
)
replace_once(
    '        GridLayout action = new GridLayout(this);\n        action.setColumnCount(2); action.setRowCount(2);',
    '        GridLayout action = new GridLayout(this);\n        action.setClipChildren(false); action.setClipToPadding(false);\n        action.setColumnCount(2); action.setRowCount(2);',
    "unclip face-button group",
)
replace_once(
    '        specialControlsRow.setOrientation(android.widget.LinearLayout.HORIZONTAL);',
    '        specialControlsRow.setOrientation(android.widget.LinearLayout.HORIZONTAL);\n        specialControlsRow.setClipChildren(false); specialControlsRow.setClipToPadding(false);',
    "unclip special-button group",
)

# Add the drag editor and multi-pointer state before the control-position helpers.
insert_before = '    private String controlsScope() {\n'
editor = r'''    private boolean touchLayoutEditMode;
    private View touchEditorToolbar;
    private boolean touchEditorToolbarGesture;
    private int touchEditorToolbarPointerId = -1;
    private final java.util.HashMap<Integer, TouchControlDrag> activeTouchControlDrags = new java.util.HashMap<>();

    private static final class TouchControlDrag {
        final View view;
        final String id;
        final boolean nested;
        final float offsetX;
        final float offsetY;
        TouchControlDrag(View view, String id, boolean nested, float offsetX, float offsetY) {
            this.view = view; this.id = id; this.nested = nested;
            this.offsetX = offsetX; this.offsetY = offsetY;
        }
    }

    private void startTouchLayoutEditor() {
        if (gameOverlayRoot == null) {
            Toast.makeText(this, "Abra um jogo para mover os controles.", Toast.LENGTH_SHORT).show();
            return;
        }
        if (touchLayoutEditMode) return;
        touchLayoutEditMode = true;
        activeTouchControlDrags.clear();
        android.widget.LinearLayout toolbar = new android.widget.LinearLayout(this);
        toolbar.setOrientation(android.widget.LinearLayout.VERTICAL);
        toolbar.setGravity(Gravity.CENTER_HORIZONTAL);
        toolbar.setPadding(dp(8), dp(5), dp(8), dp(5));
        toolbar.setBackgroundColor(0xee14220d);
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Arraste para mover e afastar os botões");
        hint.setTextColor(0xffe5ffc9);
        hint.setTextSize(12);
        hint.setGravity(Gravity.CENTER);
        toolbar.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        android.widget.LinearLayout actions = new android.widget.LinearLayout(this);
        actions.setOrientation(android.widget.LinearLayout.HORIZONTAL);
        toolbar.addView(actions, new android.widget.LinearLayout.LayoutParams(-1, dp(42)));
        Button reset = menuButton("RESTAURAR");
        reset.setTextSize(10);
        reset.setOnClickListener(v -> resetTouchControlPositions());
        android.widget.LinearLayout.LayoutParams resetParams = new android.widget.LinearLayout.LayoutParams(0, dp(40), 1f);
        resetParams.rightMargin = dp(4);
        actions.addView(reset, resetParams);
        Button done = menuButton("CONCLUIR");
        done.setTextSize(10);
        done.setOnClickListener(v -> stopTouchLayoutEditor());
        android.widget.LinearLayout.LayoutParams doneParams = new android.widget.LinearLayout.LayoutParams(0, dp(40), 1f);
        doneParams.leftMargin = dp(4);
        actions.addView(done, doneParams);
        FrameLayout.LayoutParams toolbarParams = new FrameLayout.LayoutParams(-1, -2, Gravity.TOP | Gravity.CENTER_HORIZONTAL);
        toolbarParams.leftMargin = dp(12);
        toolbarParams.rightMargin = dp(12);
        toolbarParams.topMargin = dp(90);
        gameOverlayRoot.addView(toolbar, toolbarParams);
        toolbar.bringToFront();
        touchEditorToolbar = toolbar;
        Toast.makeText(this, "Arraste cada botão com o dedo. Dá para afastá-los sem sobrepor.", Toast.LENGTH_LONG).show();
    }

    private void stopTouchLayoutEditor() {
        for (TouchControlDrag drag : activeTouchControlDrags.values()) persistTouchControlDrag(drag);
        activeTouchControlDrags.clear();
        touchEditorToolbarGesture = false;
        touchEditorToolbarPointerId = -1;
        touchLayoutEditMode = false;
        if (touchEditorToolbar != null && touchEditorToolbar.getParent() instanceof android.view.ViewGroup)
            ((android.view.ViewGroup) touchEditorToolbar.getParent()).removeView(touchEditorToolbar);
        touchEditorToolbar = null;
        Toast.makeText(this, "Posições dos controles salvas para este jogo.", Toast.LENGTH_SHORT).show();
    }

    @Override public boolean dispatchTouchEvent(MotionEvent event) {
        if (!touchLayoutEditMode || gameOverlayRoot == null) return super.dispatchTouchEvent(event);
        int action = event.getActionMasked();
        if (touchEditorToolbarGesture) {
            if (action == MotionEvent.ACTION_CANCEL
                    || ((action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP)
                    && event.getPointerId(event.getActionIndex()) == touchEditorToolbarPointerId)) {
                touchEditorToolbarGesture = false;
                touchEditorToolbarPointerId = -1;
            }
            return super.dispatchTouchEvent(event);
        }
        if ((action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN)
                && activeTouchControlDrags.isEmpty()
                && isInsideTouchEditorToolbar(event, event.getActionIndex())) {
            touchEditorToolbarGesture = true;
            touchEditorToolbarPointerId = event.getPointerId(event.getActionIndex());
            return super.dispatchTouchEvent(event);
        }
        handleTouchLayoutEdit(event);
        return true;
    }

    private boolean isInsideTouchEditorToolbar(MotionEvent event, int pointerIndex) {
        if (touchEditorToolbar == null) return false;
        float x = event.getX(pointerIndex), y = event.getY(pointerIndex);
        int[] rootLocation = new int[2], toolbarLocation = new int[2];
        gameOverlayRoot.getLocationInWindow(rootLocation);
        touchEditorToolbar.getLocationInWindow(toolbarLocation);
        float sx = x + rootLocation[0], sy = y + rootLocation[1];
        return sx >= toolbarLocation[0] && sx <= toolbarLocation[0] + touchEditorToolbar.getWidth()
                && sy >= toolbarLocation[1] && sy <= toolbarLocation[1] + touchEditorToolbar.getHeight();
    }

    private void handleTouchLayoutEdit(MotionEvent event) {
        int action = event.getActionMasked();
        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            int index = event.getActionIndex();
            int pointerId = event.getPointerId(index);
            float x = event.getX(index), y = event.getY(index);
            View target = findTouchControlAt(x, y);
            for (TouchControlDrag active : activeTouchControlDrags.values())
                if (active.view == target) { target = null; break; }
            if (target != null) {
                int[] targetLocation = new int[2], rootLocation = new int[2];
                target.getLocationInWindow(targetLocation);
                gameOverlayRoot.getLocationInWindow(rootLocation);
                boolean nested = target.getParent() != gameOverlayRoot;
                String id = nested ? String.valueOf(target.getTag()) : touchControlIdForView(target);
                activeTouchControlDrags.put(pointerId, new TouchControlDrag(target, id, nested,
                        x + rootLocation[0] - targetLocation[0], y + rootLocation[1] - targetLocation[1]));
                target.setElevation(dp(18));
            }
            return;
        }
        if (action == MotionEvent.ACTION_MOVE) {
            int[] rootLocation = new int[2];
            gameOverlayRoot.getLocationInWindow(rootLocation);
            for (int i = 0; i < event.getPointerCount(); i++) {
                TouchControlDrag drag = activeTouchControlDrags.get(event.getPointerId(i));
                if (drag != null) moveTouchControlDrag(drag, event.getX(i) + rootLocation[0], event.getY(i) + rootLocation[1]);
            }
            return;
        }
        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP) {
            int pointerId = event.getPointerId(event.getActionIndex());
            TouchControlDrag drag = activeTouchControlDrags.remove(pointerId);
            if (drag != null) {
                persistTouchControlDrag(drag);
                drag.view.setElevation(0f);
            }
            return;
        }
        if (action == MotionEvent.ACTION_CANCEL) {
            for (TouchControlDrag drag : activeTouchControlDrags.values()) {
                persistTouchControlDrag(drag);
                drag.view.setElevation(0f);
            }
            activeTouchControlDrags.clear();
        }
    }

    private String touchControlIdForView(View view) {
        for (java.util.Map.Entry<String, View> entry : touchControlViews.entrySet())
            if (entry.getValue() == view) return entry.getKey();
        return null;
    }

    private boolean hasNestedMoveId(View view) {
        Object tag = view.getTag();
        if (!(tag instanceof String)) return false;
        String id = (String) tag;
        return id.startsWith("face_") || id.startsWith("special_");
    }

    private boolean pointInsideView(View view, float screenX, float screenY) {
        int[] location = new int[2];
        view.getLocationInWindow(location);
        int slop = dp(8);
        return screenX >= location[0] - slop && screenX <= location[0] + view.getWidth() + slop
                && screenY >= location[1] - slop && screenY <= location[1] + view.getHeight() + slop;
    }

    private View findTouchControlAt(float x, float y) {
        int[] rootLocation = new int[2];
        gameOverlayRoot.getLocationInWindow(rootLocation);
        float screenX = x + rootLocation[0], screenY = y + rootLocation[1];
        for (int i = gameOverlayRoot.getChildCount() - 1; i >= 0; i--) {
            View top = gameOverlayRoot.getChildAt(i);
            if (top == touchEditorToolbar || touchControlIdForView(top) == null || top.getVisibility() != View.VISIBLE) continue;
            if (top instanceof android.view.ViewGroup) {
                android.view.ViewGroup group = (android.view.ViewGroup) top;
                for (int j = group.getChildCount() - 1; j >= 0; j--) {
                    View child = group.getChildAt(j);
                    if (hasNestedMoveId(child) && child.getVisibility() == View.VISIBLE && pointInsideView(child, screenX, screenY)) return child;
                }
            }
            if (pointInsideView(top, screenX, screenY)) return top;
        }
        return null;
    }

    private void moveTouchControlDrag(TouchControlDrag drag, float screenX, float screenY) {
        View view = drag.view;
        if (view.getParent() == null || view.getWidth() <= 0 || view.getHeight() <= 0) return;
        float desiredLeft = screenX - drag.offsetX, desiredTop = screenY - drag.offsetY;
        int[] rootLocation = new int[2];
        gameOverlayRoot.getLocationInWindow(rootLocation);
        if (!drag.nested && view.getParent() == gameOverlayRoot) {
            int maxX = Math.max(0, gameOverlayRoot.getWidth() - view.getWidth());
            int maxY = Math.max(0, gameOverlayRoot.getHeight() - view.getHeight());
            int left = Math.max(0, Math.min(maxX, Math.round(desiredLeft - rootLocation[0])));
            int top = Math.max(0, Math.min(maxY, Math.round(desiredTop - rootLocation[1])));
            int x = maxX == 0 ? 0 : Math.round(left * 100f / maxX);
            int y = maxY == 0 ? 0 : Math.round(top * 100f / maxY);
            setTouchPosition(gameOverlayRoot, view, x, y);
            return;
        }
        if (view.getParent() instanceof android.view.ViewGroup) {
            android.view.ViewGroup parent = (android.view.ViewGroup) view.getParent();
            int[] parentLocation = new int[2];
            parent.getLocationInWindow(parentLocation);
            float baseLeft = parentLocation[0] + view.getLeft();
            float baseTop = parentLocation[1] + view.getTop();
            float minX = rootLocation[0] - baseLeft;
            float minY = rootLocation[1] - baseTop;
            float maxX = rootLocation[0] + gameOverlayRoot.getWidth() - view.getWidth() - baseLeft;
            float maxY = rootLocation[1] + gameOverlayRoot.getHeight() - view.getHeight() - baseTop;
            view.setTranslationX(Math.max(minX, Math.min(maxX, desiredLeft - baseLeft)));
            view.setTranslationY(Math.max(minY, Math.min(maxY, desiredTop - baseTop)));
        }
    }

    private void persistTouchControlDrag(TouchControlDrag drag) {
        if (drag.id == null || drag.view.getParent() == null) return;
        android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
        if (drag.nested) {
            float density = getResources().getDisplayMetrics().density;
            editor.putInt(touchKey(drag.id, "dx"), Math.round(drag.view.getTranslationX() / density));
            editor.putInt(touchKey(drag.id, "dy"), Math.round(drag.view.getTranslationY() / density));
        } else if (drag.view.getParent() == gameOverlayRoot) {
            FrameLayout.LayoutParams params = (FrameLayout.LayoutParams) drag.view.getLayoutParams();
            int maxX = Math.max(0, gameOverlayRoot.getWidth() - drag.view.getWidth());
            int maxY = Math.max(0, gameOverlayRoot.getHeight() - drag.view.getHeight());
            editor.putInt(touchKey(drag.id, "x"), maxX == 0 ? 0 : Math.round(params.leftMargin * 100f / maxX));
            editor.putInt(touchKey(drag.id, "y"), maxY == 0 ? 0 : Math.round(params.topMargin * 100f / maxY));
        }
        editor.apply();
    }

    private void restoreNestedControlPosition(View view) {
        if (!hasNestedMoveId(view)) return;
        String id = String.valueOf(view.getTag());
        android.content.SharedPreferences prefs = getPreferences(0);
        view.setTranslationX(dp(prefs.getInt(touchKey(id, "dx"), 0)));
        view.setTranslationY(dp(prefs.getInt(touchKey(id, "dy"), 0)));
    }

    private void resetTouchControlPositions() {
        android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
        for (String id : new String[]{"face_A", "face_B", "face_C", "face_D",
                "special_0", "special_1", "special_2", "special_3", "special_4", "special_5"})
            editor.remove(touchKey(id, "dx")).remove(touchKey(id, "dy"));
        for (java.util.Map.Entry<String, View> entry : touchControlViews.entrySet()) {
            int[] defaults = touchControlDefaults.get(entry.getKey());
            editor.remove(touchKey(entry.getKey(), "x")).remove(touchKey(entry.getKey(), "y"));
            if (defaults != null) setTouchPosition(gameOverlayRoot, entry.getValue(), defaults[0], defaults[1]);
            if (entry.getValue() instanceof android.view.ViewGroup) {
                android.view.ViewGroup group = (android.view.ViewGroup) entry.getValue();
                for (int i = 0; i < group.getChildCount(); i++) {
                    View child = group.getChildAt(i);
                    if (!hasNestedMoveId(child)) continue;
                    String id = String.valueOf(child.getTag());
                    editor.remove(touchKey(id, "dx")).remove(touchKey(id, "dy"));
                    child.setTranslationX(0f); child.setTranslationY(0f);
                }
            }
        }
        editor.apply();
        Toast.makeText(this, "Posições restauradas. Toque CONCLUIR para sair.", Toast.LENGTH_SHORT).show();
    }

'''
if s.count(insert_before) != 1:
    raise SystemExit("Could not find the touch-control helper insertion point")
s = s.replace(insert_before, editor + insert_before, 1)

if "Mover botões com o dedo" not in s or "startTouchLayoutEditor()" not in s:
    raise SystemExit("The touch-control drag editor was not installed")
main.write_text(s, encoding="utf-8")
print("Added per-game drag-to-reposition controls with multi-pointer editing")
