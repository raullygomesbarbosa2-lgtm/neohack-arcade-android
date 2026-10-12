#!/usr/bin/env python3
"""Configure Vortix 0.9.12 release APK signing from GitHub Actions secrets."""
from pathlib import Path

build = Path("app/build.gradle")
text = build.read_text()
if "versionCode 21\n        versionName '0.9.12'" not in text:
    raise SystemExit("Expected Vortix 0.9.12 version marker before signing configuration")
if "signingConfigs {" in text:
    raise SystemExit("Signing configuration already exists; refusing to duplicate it")
block = '''    signingConfigs {
        release {
            storeFile file(System.getenv("VORTIX_KEYSTORE_PATH"))
            storePassword System.getenv("VORTIX_KEYSTORE_PASSWORD")
            keyAlias System.getenv("VORTIX_KEY_ALIAS")
            keyPassword System.getenv("VORTIX_KEY_PASSWORD")
            storeType System.getenv("VORTIX_KEYSTORE_TYPE")
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
        }
    }

'''
if text.count("    splits {") != 1:
    raise SystemExit("Expected one ABI splits block")
text = text.replace("    splits {", block + "    splits {", 1)
build.write_text(text)
print("Configured Vortix release APKs to use the stable signing key from Actions secrets.")
