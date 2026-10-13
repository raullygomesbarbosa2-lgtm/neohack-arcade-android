#!/usr/bin/env python3
"""Create a private 178-core demo build with no Pix/payment UI or expiry gate."""
from pathlib import Path
import re

main = Path("app/src/main/java/br/com/raully/neohackarcade/MainActivity.java")
s = main.read_text(encoding="utf-8")

# Remove the Pix/payment control inserted by the branding and local-Pix patches.
button_re = re.compile(
    r'(?ms)^\s*Button copyPix = menuButton\("COPIAR CHAVE PIX[^\"]*"\);\n'
    r'.*?^\s*panel\.addView\(copyPix, pixParams\);\n'
)
s, button_count = button_re.subn("", s)
if button_count != 1:
    raise SystemExit(f"Expected one Pix button block, found {button_count}")

# Remove local Pix-key read/configuration/copy helpers while retaining the catalog method.
start_marker = "    private String readPixKey() {\n"
end_marker = "    private void showCoreCatalog() {\n"
start = s.find(start_marker)
end = s.find(end_marker, start + len(start_marker)) if start >= 0 else -1
if start < 0 or end < 0:
    raise SystemExit("Could not locate local Pix-key methods")
s = s[:start] + s[end:]

for forbidden in (
    "copyPix", "readPixKey", "copyPixKey", "showPixKeySetupDialog",
    "pix_key_local", "pix_key.txt", "COPIAR CHAVE PIX",
    "PAGAR COM PAGBANK", "promptCustomerAndCreatePayment",
    "paymentApiRequest", "verifyOnlineLicense", "TRIAL_DURATION_MS",
    "isTrialExpired", "showTrialExpired",
):
    if forbidden in s:
        raise SystemExit(f"Demo source still contains payment/Pix/trial reference: {forbidden}")

main.write_text(s, encoding="utf-8")

# Preserve the Pro package ID and signing identity, but make this a newer demo build.
build = Path("app/build.gradle")
g = build.read_text(encoding="utf-8")
if "applicationId 'br.com.raully.neohackarcade.pro'" not in g:
    raise SystemExit("Expected Vortix Pro applicationId not found")
if "versionCode 21" not in g or "versionName '1.0.0'" not in g:
    raise SystemExit("Unexpected version anchors; refusing to alter build metadata")
g = g.replace("versionCode 21", "versionCode 22", 1)
g = g.replace("versionName '1.0.0'", "versionName '1.0.1-demo'", 1)
build.write_text(g, encoding="utf-8")

# No private Pix key is bundled in assets.
if Path("app/src/main/assets/pix_key.txt").exists():
    raise SystemExit("Pix-key asset must not be present in the demo")
print("Applied no-payment, no-Pix, no-expiry Vortix Demo configuration")
