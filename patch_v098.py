from pathlib import Path

# This patch runs after the native project and Vortix 0.9.7 patches have generated
# MainActivity.java. Make the library immediately usable on fresh installs.
activity = Path('app/src/main/java/br/com/raully/neohackarcade/MainActivity.java')
text = activity.read_text()
old = '''        if (getPreferences(0).contains("profile_name")) showLibrary();
        else showProfileScreen(true, "");'''
new = '''        if (!getPreferences(0).contains("profile_name")) {
            getPreferences(0).edit().putString("profile_name", "Jogador").apply();
        }
        showLibrary();'''
if text.count(old) != 1:
    raise SystemExit('Expected exactly one first-run profile gate in MainActivity')
text = text.replace(old, new, 1)
old = 'profileNameInput.setSingleLine(true); profileNameInput.setTextSize(17); profileNameInput.setTextColor(Color.WHITE);'
new = 'profileNameInput.setSingleLine(true); profileNameInput.setTextSize(17); profileNameInput.setTextColor(0xff12323f);'
if text.count(old) != 1:
    raise SystemExit('Expected exactly one profile name input style')
activity.write_text(text.replace(old, new, 1))

build = Path('app/build.gradle')
text = build.read_text()
old = "applicationId 'br.com.raully.neohackarcade.test097'"
if text.count(old) != 1:
    raise SystemExit('Expected exactly one Vortix Test 0.9.7 applicationId')
text = text.replace(old, "applicationId 'br.com.raully.neohackarcade.test098'", 1)
old = "versionCode 16\n        versionName '0.9.7-special-macros'"
if text.count(old) != 1:
    raise SystemExit('Expected exactly one Vortix 0.9.7 version declaration')
text = text.replace(old, "versionCode 17\n        versionName '0.9.8-first-run-fix'", 1)
build.write_text(text)

manifest = Path('app/src/main/AndroidManifest.xml')
text = manifest.read_text()
old = 'android:label="Vortix Test"'
if text.count(old) != 1:
    raise SystemExit('Expected exactly one Vortix Test launcher label')
manifest.write_text(text.replace(old, 'android:label="Vortix Test 2"', 1))

print('Applied Vortix 0.9.8 fresh-library, visible-profile-input and distinct-test-app changes')
