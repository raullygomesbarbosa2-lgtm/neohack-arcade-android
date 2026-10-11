#!/usr/bin/env python3
"""Add Vortix Pro branding and a Pix copy button without storing the Pix key in source."""
from pathlib import Path

main = Path("app/src/main/java/br/com/raully/neohackarcade/MainActivity.java")
s = main.read_text()

def replace_once(old, new):
    global s
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"Expected source anchor missing: {old[:80]!r}")
    s = s.replace(old, new, 1)

replace_once("import android.content.Intent;\n", "import android.content.Intent;\nimport android.content.ClipData;\nimport android.content.ClipboardManager;\nimport android.content.Context;\n")
replace_once("    private static final int REQUEST_AUTO_DETECT = 56;\n", "    private static final int REQUEST_AUTO_DETECT = 56;\n")
replace_once('        title.setText("Vortix");\n', '        title.setText("Vortix Pro");\n')
replace_once("        addProfileRow(panel);\n\n        TextView info = new TextView(this);\n", "        addProfileRow(panel);\n\n        Button copyPix = menuButton(\"COPIAR CHAVE PIX • R$ 4,90/mês\");\n        copyPix.setContentDescription(\"Copiar chave Pix para pagamento\");\n        copyPix.setOnClickListener(v -> copyPixKey());\n        LinearLayout.LayoutParams pixParams = buttonParams();\n        pixParams.topMargin = dp(8);\n        panel.addView(copyPix, pixParams);\n\n        TextView info = new TextView(this);\n")
replace_once("    private void showMoreSystemsDialog() {\n", "    private String readPixKey() {\n        try (InputStream input = getAssets().open(\"pix_key.txt\");\n             ByteArrayOutputStream output = new ByteArrayOutputStream()) {\n            byte[] buffer = new byte[128];\n            int count;\n            while ((count = input.read(buffer)) != -1) output.write(buffer, 0, count);\n            return new String(output.toByteArray(), java.nio.charset.StandardCharsets.UTF_8).trim();\n        } catch (Exception ignored) {\n            return \"\";\n        }\n    }\n\n    private void copyPixKey() {\n        String pixKey = readPixKey();\n        if (pixKey.isEmpty()) {\n            Toast.makeText(this, \"Chave Pix indisponível nesta compilação.\", Toast.LENGTH_LONG).show();\n            return;\n        }\n        ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);\n        if (clipboard != null) {\n            clipboard.setPrimaryClip(ClipData.newPlainText(\"Chave Pix Vortix Pro\", pixKey));\n            Toast.makeText(this, \"Chave Pix copiada.\", Toast.LENGTH_LONG).show();\n        } else {\n            Toast.makeText(this, \"Não consegui copiar a chave Pix.\", Toast.LENGTH_SHORT).show();\n        }\n    }\n\n    private void showMoreSystemsDialog() {\n")
main.write_text(s)

manifest = Path("app/src/main/AndroidManifest.xml")
m = manifest.read_text().replace('android:label="Vortix"', 'android:label="Vortix Pro"')
manifest.write_text(m)

build = Path("app/build.gradle")
g = build.read_text().replace("applicationId 'br.com.raully.neohackarcade'", "applicationId 'br.com.raully.neohackarcade.pro'")
g = g.replace("versionCode 20", "versionCode 21").replace("versionName '0.9.11'", "versionName '1.0.0'")
build.write_text(g)
print("Applied Vortix Pro branding and keyless Pix button")
