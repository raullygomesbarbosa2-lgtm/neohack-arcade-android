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
lines = g.splitlines(keepends=True)
code_updated = name_updated = False
for index, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("versionCode "):
        parts = stripped.split()
        if len(parts) < 2 or not parts[1].isdigit():
            raise SystemExit("Generated versionCode is not numeric")
        next_code = max(int(parts[1]) + 1, 22)
        indent = line[:len(line) - len(line.lstrip())]
        newline = "\n" if line.endswith("\n") else ""
        lines[index] = f"{indent}versionCode {next_code}{newline}"
        code_updated = True
    elif stripped.startswith("versionName "):
        value = stripped[len("versionName "):].strip()
        if len(value) < 2 or value[0] not in ("'", '"') or value[-1] != value[0]:
            raise SystemExit("Generated versionName is not quoted")
        quote = value[0]
        name = value[1:-1]
        if not name.endswith("-demo"):
            name += "-demo"
        indent = line[:len(line) - len(line.lstrip())]
        newline = "\n" if line.endswith("\n") else ""
        lines[index] = f"{indent}versionName {quote}{name}{quote}{newline}"
        name_updated = True
if not code_updated or not name_updated:
    raise SystemExit("Could not update both generated version fields")
build.write_text("".join(lines), encoding="utf-8")

# No private Pix key is bundled in assets.
if Path("app/src/main/assets/pix_key.txt").exists():
    raise SystemExit("Pix-key asset must not be present in the demo")
print("Applied no-payment, no-Pix, no-expiry Vortix Demo configuration")
