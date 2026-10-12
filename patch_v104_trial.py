#!/usr/bin/env python3
"""Add an offline 30-day first-launch trial gate to the test build."""
from pathlib import Path

main = Path("app/src/main/java/br/com/raully/neohackarcade/MainActivity.java")
s = main.read_text(encoding="utf-8")

if "private boolean isTrialExpired()" not in s:
    anchor = "        super.onCreate(state);\n"
    if s.count(anchor) != 1:
        raise SystemExit("Trial patch could not find the unique Activity.onCreate anchor.")
    s = s.replace(anchor, anchor + "        if (isTrialExpired()) { showTrialExpired(); return; }\n", 1)

    anchor = "    private void showLibrary() {\n"
    trial_methods = '''    private static final long TRIAL_DURATION_MS = 30L * 24L * 60L * 60L * 1000L;

    // Offline test-build trial. Clearing app data/reinstalling can reset local storage;
    // this is not a server-verified commercial license system.
    private boolean isTrialExpired() {
        android.content.SharedPreferences prefs = getSharedPreferences("vortix_trial", MODE_PRIVATE);
        long now = System.currentTimeMillis();
        long first = prefs.getLong("first_launch_ms", 0L);
        if (first <= 0L) {
            prefs.edit().putLong("first_launch_ms", now).putLong("last_seen_ms", now).apply();
            return false;
        }
        if (prefs.getBoolean("clock_rollback", false)) return true;
        long last = prefs.getLong("last_seen_ms", first);
        if (now < first || now < last) {
            prefs.edit().putBoolean("clock_rollback", true).apply();
            return true;
        }
        if (now > last) prefs.edit().putLong("last_seen_ms", now).apply();
        return now - first >= TRIAL_DURATION_MS;
    }

    private void showTrialExpired() {
        new android.app.AlertDialog.Builder(this)
                .setTitle("Teste de 30 dias encerrado")
                .setMessage("O período de teste terminou. A ativação manual por código ainda não está disponível nesta versão de teste.")
                .setCancelable(false)
                .setPositiveButton("Fechar", (dialog, which) -> finish())
                .show();
    }

'''
    if s.count(anchor) != 1:
        raise SystemExit("Trial patch could not find the unique showLibrary anchor.")
    s = s.replace(anchor, trial_methods + anchor, 1)

banner_anchor = "        panel.addView(title, new LinearLayout.LayoutParams(-1, -2));\n"
banner = '''        panel.addView(title, new LinearLayout.LayoutParams(-1, -2));

        TextView trialNotice = new TextView(this);
        trialNotice.setText("TRIAL GRATUITO • 30 DIAS A PARTIR DO PRIMEIRO USO");
        trialNotice.setTextColor(0xff43efff);
        trialNotice.setTextSize(11);
        trialNotice.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams trialParams = new LinearLayout.LayoutParams(-1, -2);
        trialParams.setMargins(0, dp(2), 0, dp(5));
        panel.addView(trialNotice, trialParams);
'''
if "TRIAL GRATUITO • 30 DIAS A PARTIR DO PRIMEIRO USO" not in s:
    if s.count(banner_anchor) != 1:
        raise SystemExit("Trial patch could not find the unique library-title anchor.")
    s = s.replace(banner_anchor, banner, 1)

main.write_text(s, encoding="utf-8")
print("Added the local 30-day first-launch trial gate and notice")
