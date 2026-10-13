#!/usr/bin/env python3
"""Replace the local Pix-key UI with a native, keyless PagBank Sandbox flow."""
from pathlib import Path
import re

main = Path("app/src/main/java/br/com/raully/neohackarcade/MainActivity.java")
s = main.read_text(encoding="utf-8")

# Gate an expired local trial on a server-side entitlement check, without blocking the UI thread.
old = '''        if (isTrialExpired()) { showTrialExpired(); return; }
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        enterImmersiveMode();
        selectedAvatarIndex = getPreferences(0).getInt("profile_avatar", 0);
        selectedPhotoUri = getPreferences(0).getString("profile_photo", null);
        if (state != null) pendingCatalogCoreId = state.getString("pending_catalog_core_id");
        if (!getPreferences(0).contains("profile_name")) {
            getPreferences(0).edit().putString("profile_name", "Jogador").apply();
        }
        showLibrary();
    }
'''
new = '''        if (isTrialExpired()) {
            verifyOnlineLicense(false);
            return;
        }
        initializeMainUi(state);
    }

    private void initializeMainUi(Bundle state) {
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        enterImmersiveMode();
        selectedAvatarIndex = getPreferences(0).getInt("profile_avatar", 0);
        selectedPhotoUri = getPreferences(0).getString("profile_photo", null);
        if (state != null) pendingCatalogCoreId = state.getString("pending_catalog_core_id");
        if (!getPreferences(0).contains("profile_name")) {
            getPreferences(0).edit().putString("profile_name", "Jogador").apply();
        }
        showLibrary();
    }
'''
if old not in s:
    raise SystemExit("Could not find the expected onCreate/trial-gate block")
s = s.replace(old, new, 1)

old_button = '''        Button copyPix = menuButton("COPIAR CHAVE PIX • R$ 4,90/mês");
        copyPix.setContentDescription("Copiar chave Pix para pagamento");
        copyPix.setOnClickListener(v -> copyPixKey());
        copyPix.setOnLongClickListener(v -> { showPixKeySetupDialog(); return true; });
        LinearLayout.LayoutParams pixParams = buttonParams();
        pixParams.topMargin = dp(8);
        panel.addView(copyPix, pixParams);
'''
new_button = '''        Button payment = menuButton("PAGAR COM PAGBANK • R$ 4,90 / 30 DIAS");
        payment.setContentDescription("Gerar cobrança de teste pelo PagBank");
        payment.setOnClickListener(v -> promptCustomerAndCreatePayment());
        LinearLayout.LayoutParams paymentParams = buttonParams();
        paymentParams.topMargin = dp(8);
        panel.addView(payment, paymentParams);
'''
if old_button not in s:
    raise SystemExit("Could not find the expected local Pix button")
s = s.replace(old_button, new_button, 1)

# Remove manual key entry/copy methods entirely; no customer key belongs in the APK.
start = s.find("    private String readPixKey() {")
end = s.find("    private void showCoreCatalog() {", start)
if start < 0 or end < 0:
    raise SystemExit("Could not find the manual Pix-key methods")
s = s[:start] + s[end:]

anchor = "    private void showCoreCatalog() {\n"
payment_methods = r'''    private static final String PAYMENT_API_BASE = "https://vortix-pro-api.raullygomesbarbosa2.workers.dev";

    private String paymentDeviceId() {
        String androidId = android.provider.Settings.Secure.getString(getContentResolver(), android.provider.Settings.Secure.ANDROID_ID);
        if (androidId != null && androidId.matches("[A-Za-z0-9_-]{16,100}")) return androidId;
        android.content.SharedPreferences prefs = getSharedPreferences("vortix_payment", MODE_PRIVATE);
        String fallback = prefs.getString("device_id", "");
        if (!fallback.matches("[A-Za-z0-9_-]{16,100}")) {
            fallback = java.util.UUID.randomUUID().toString().replace("-", "");
            prefs.edit().putString("device_id", fallback).apply();
        }
        return fallback;
    }

    private org.json.JSONObject paymentApiRequest(String path, String method, org.json.JSONObject body) throws Exception {
        java.net.HttpURLConnection connection = null;
        try {
            java.net.URL url = new java.net.URL(PAYMENT_API_BASE + path);
            connection = (java.net.HttpURLConnection) url.openConnection();
            connection.setRequestMethod(method);
            connection.setConnectTimeout(12000);
            connection.setReadTimeout(15000);
            connection.setRequestProperty("Accept", "application/json");
            if (body != null) {
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                byte[] data = body.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8);
                try (java.io.OutputStream output = connection.getOutputStream()) { output.write(data); }
            }
            int code = connection.getResponseCode();
            java.io.InputStream stream = code >= 200 && code < 300 ? connection.getInputStream() : connection.getErrorStream();
            java.io.ByteArrayOutputStream bytes = new java.io.ByteArrayOutputStream();
            if (stream != null) {
                try (java.io.InputStream input = stream) {
                    byte[] buffer = new byte[2048];
                    int count;
                    while ((count = input.read(buffer)) != -1) bytes.write(buffer, 0, count);
                }
            }
            String text = new String(bytes.toByteArray(), java.nio.charset.StandardCharsets.UTF_8);
            org.json.JSONObject result = text.isEmpty() ? new org.json.JSONObject() : new org.json.JSONObject(text);
            if (code < 200 || code >= 300) {
                String reason = result.optString("error", "");
                throw new java.io.IOException("A cobrança não foi concluída" + (reason.isEmpty() ? "." : " (" + reason + ")."));
            }
            return result;
        } finally {
            if (connection != null) connection.disconnect();
        }
    }

    private void promptCustomerAndCreatePayment() {
        LinearLayout fields = new LinearLayout(this);
        fields.setOrientation(LinearLayout.VERTICAL);
        fields.setPadding(dp(20), dp(4), dp(20), 0);
        EditText name = new EditText(this);
        name.setSingleLine(true);
        name.setHint("Nome completo");
        fields.addView(name, new LinearLayout.LayoutParams(-1, -2));
        EditText email = new EditText(this);
        email.setSingleLine(true);
        email.setHint("E-mail");
        email.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        fields.addView(email, new LinearLayout.LayoutParams(-1, -2));
        EditText taxId = new EditText(this);
        taxId.setSingleLine(true);
        taxId.setHint("CPF ou CNPJ (somente números)");
        taxId.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        fields.addView(taxId, new LinearLayout.LayoutParams(-1, -2));
        new android.app.AlertDialog.Builder(this)
                .setTitle("Cobrança PagBank • Sandbox")
                .setMessage("R$ 4,90 por 30 dias. Renovação manual; sem cobrança recorrente. Nome, e-mail e CPF/CNPJ serão enviados ao PagBank pelo backend protegido para criar a cobrança. Este ambiente de teste não recebe pagamentos reais.")
                .setView(fields)
                .setPositiveButton("Gerar cobrança", (dialog, which) -> {
                    String customerName = name.getText().toString().trim();
                    String customerEmail = email.getText().toString().trim();
                    String document = taxId.getText().toString().replaceAll("\\D", "");
                    if (customerName.isEmpty() || customerEmail.isEmpty() || !(document.length() == 11 || document.length() == 14)) {
                        new android.app.AlertDialog.Builder(this).setMessage("Informe nome, e-mail e CPF (11 dígitos) ou CNPJ (14 dígitos).")
                                .setPositiveButton("OK", null).show();
                        return;
                    }
                    createPayment(customerName, customerEmail, document);
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private void createPayment(String name, String email, String taxId) {
        showPaymentMessage("Conectando ao PagBank Sandbox…");
        new Thread(() -> {
            try {
                org.json.JSONObject customer = new org.json.JSONObject();
                customer.put("name", name);
                customer.put("email", email);
                customer.put("tax_id", taxId);
                org.json.JSONObject request = new org.json.JSONObject();
                request.put("device_id", paymentDeviceId());
                request.put("customer", customer);
                org.json.JSONObject result = paymentApiRequest("/api/create-payment", "POST", request);
                runOnUiThread(() -> {
                    if (result.optBoolean("active", false)) {
                        verifyOnlineLicense(true);
                    } else {
                        showPaymentCode(result.optString("qr_code", ""), result.optString("expires_at", ""));
                    }
                });
            } catch (Exception error) {
                runOnUiThread(() -> showPaymentWall("Não foi possível criar a cobrança. Confira a conexão e tente novamente."));
            }
        }, "vortix-payment-create").start();
    }

    private void showPaymentCode(String code, String expiresAt) {
        if (code == null || code.trim().isEmpty()) {
            showPaymentWall("O PagBank não retornou o código de pagamento.");
            return;
        }
        EditText copyableCode = new EditText(this);
        copyableCode.setText(code);
        copyableCode.setTextIsSelectable(true);
        copyableCode.setFocusable(false);
        copyableCode.setTextSize(11);
        copyableCode.setMaxLines(5);
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(18), dp(4), dp(18), 0);
        box.addView(copyableCode, new LinearLayout.LayoutParams(-1, -2));
        String expiryMessage = expiresAt == null || expiresAt.isEmpty() ? "" : "\nValidade informada pelo PagBank: " + expiresAt;
        new android.app.AlertDialog.Builder(this)
                .setTitle("Código QR PagBank • Sandbox")
                .setMessage("Copie o código para testar no ambiente PagBank. A documentação consultada descreve este QR como Pagar com PagBank; pagamento por outros bancos não foi confirmado." + expiryMessage)
                .setView(box)
                .setPositiveButton("Copiar código", (dialog, which) -> {
                    android.content.ClipboardManager clipboard = (android.content.ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
                    if (clipboard != null) clipboard.setPrimaryClip(android.content.ClipData.newPlainText("Código de cobrança PagBank", code));
                    android.widget.Toast.makeText(this, "Código copiado.", android.widget.Toast.LENGTH_LONG).show();
                })
                .setNeutralButton("Verificar pagamento", (dialog, which) -> verifyOnlineLicense(true))
                .setNegativeButton("Fechar", null)
                .show();
    }

    private void verifyOnlineLicense(boolean showResult) {
        showPaymentMessage("Verificando acesso online…");
        new Thread(() -> {
            try {
                String query = java.net.URLEncoder.encode(paymentDeviceId(), "UTF-8");
                org.json.JSONObject result = paymentApiRequest("/api/status?device_id=" + query, "GET", null);
                boolean active = result.optBoolean("active", false);
                runOnUiThread(() -> {
                    if (active) {
                        initializeMainUi(null);
                        if (showResult) android.widget.Toast.makeText(this, "Pagamento confirmado: acesso ativo por 30 dias.", android.widget.Toast.LENGTH_LONG).show();
                    } else {
                        showPaymentWall(showResult ? "Ainda não há um pagamento confirmado para este aparelho. Cada pagamento libera 30 dias; a renovação é manual." : "O teste local terminou. Cada pagamento de R$ 4,90 libera 30 dias; a renovação é manual.");
                    }
                });
            } catch (Exception error) {
                runOnUiThread(() -> showPaymentWall("Não foi possível verificar o acesso online. Confira a conexão e tente novamente."));
            }
        }, "vortix-payment-status").start();
    }

    private void showPaymentWall(String message) {
        new android.app.AlertDialog.Builder(this)
                .setTitle("Acesso Vortix Pro")
                .setMessage(message + "\n\nA cobrança disponível nesta compilação é apenas de teste PagBank Sandbox; não faça pagamento real.")
                .setCancelable(false)
                .setPositiveButton("Gerar cobrança de teste", (dialog, which) -> promptCustomerAndCreatePayment())
                .setNeutralButton("Tentar novamente", (dialog, which) -> verifyOnlineLicense(false))
                .setNegativeButton("Sair", (dialog, which) -> finish())
                .show();
    }

    private void showPaymentMessage(String message) {
        runOnUiThread(() -> android.widget.Toast.makeText(this, message, android.widget.Toast.LENGTH_LONG).show());
    }

'''
if s.count(anchor) != 1:
    raise SystemExit("Could not find unique payment-method insertion anchor")
s = s.replace(anchor, payment_methods + anchor, 1)
main.write_text(s, encoding="utf-8")

manifest = Path("app/src/main/AndroidManifest.xml")
m = manifest.read_text(encoding="utf-8")
if "android.permission.INTERNET" not in m:
    match = re.search(r"<manifest\b[^>]*>", m)
    if not match:
        raise SystemExit("Could not locate the manifest root")
    m = m[:match.end()] + '\n    <uses-permission android:name="android.permission.INTERNET" />' + m[match.end():]
manifest.write_text(m, encoding="utf-8")

# Defensive validation: the test APK never receives a Pix-key asset/secret.
if "pix_key.txt" in main.read_text(encoding="utf-8") or "COPIAR CHAVE PIX" in main.read_text(encoding="utf-8"):
    raise SystemExit("A Pix-key UI/reference remains in the generated app source")
print("Applied native PagBank Sandbox payment flow; no Pix key or access token is embedded")
