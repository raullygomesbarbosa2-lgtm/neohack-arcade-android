from pathlib import Path

build = Path('app/build.gradle')
text = build.read_text()
old = "applicationId 'br.com.raully.neohackarcade'"
if text.count(old) != 1:
    raise SystemExit('Expected exactly one original Vortix applicationId')
build.write_text(text.replace(old, "applicationId 'br.com.raully.neohackarcade.test097'", 1))

manifest = Path('app/src/main/AndroidManifest.xml')
text = manifest.read_text()
old = 'android:label="Vortix"'
if text.count(old) != 1:
    raise SystemExit('Expected exactly one original Vortix launcher label')
manifest.write_text(text.replace(old, 'android:label="Vortix Test"', 1))
