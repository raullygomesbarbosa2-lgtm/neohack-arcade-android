#!/usr/bin/env python3
"""Configure release builds to use the repository's persistent Vortix signing bundle."""
from pathlib import Path

path = Path("app/build.gradle")
text = path.read_text(encoding="utf-8")
if "signingConfigs {" in text:
    raise SystemExit("Signing configuration already exists; refusing to duplicate it")
if text.count("    splits {") != 1:
    raise SystemExit("Expected exactly one ABI splits block")
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
text = text.replace("    splits {", block + "    splits {", 1)
path.write_text(text, encoding="utf-8")
print("Configured release signing to use the persistent GitHub Actions keystore secret.")
