#!/usr/bin/env python3
"""Validate arcade ZIPs and surface Java-side MAME core load failures clearly."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
activity = ROOT / "app/src/main/java/br/com/raully/neohackarcade/MainActivity.java"
text = activity.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Could not apply Arcade 2010 guard ({label}); found {count} matches")
    text = text.replace(old, new, 1)


replace_once(
    '''        File selected = copyRom(uri);
        if (requestCode == REQUEST_AUTO_DETECT) {
            openAutoDetectedGame(selected);
            return;
        }
        if (!selected.getName().toLowerCase(java.util.Locale.ROOT).endsWith(".zip")) {''',
    '''        File selected = copyRom(uri);
        if (requestCode == REQUEST_AUTO_DETECT) {
            openAutoDetectedGame(selected);
            return;
        }
        String selectedName = selected.getName().toLowerCase(java.util.Locale.ROOT);
        if (requestCode == REQUEST_ARCADE) {
            if (!selectedName.endsWith(".zip")) {
                throw new IllegalArgumentException("Para Arcade, escolha o arquivo ZIP da ROM do jogo. MAME 2010 usa ROMset 0.139; arquivos .7z, .rar ou ROMsets de outra versão podem falhar.");
            }
            if (selected.length() == 0) throw new IllegalArgumentException("O arquivo ZIP do jogo está vazio.");
            try (java.util.zip.ZipFile archive = new java.util.zip.ZipFile(selected)) {
                if (!archive.entries().hasMoreElements())
                    throw new IllegalArgumentException("O ZIP não contém arquivos de ROM. Escolha o ZIP completo do jogo.");
            }
        }
        if (!selectedName.endsWith(".zip")) {''',
    "validate arcade zip before core selection",
)

replace_once(
    '''        new android.app.AlertDialog.Builder(this)
                .setTitle("Escolha o núcleo que combina com o ROMset")
                .setItems(labels, (dialog, which) -> {
                    try {
                        startRetroGame(rom, cores[which], "ARCADE • " + labels[which]);
                    } catch (Exception error) {
                        showGameOpenError(error);
                    }
                })''',
    '''        new android.app.AlertDialog.Builder(this)
                .setTitle("Escolha o núcleo que combina com o ROMset")
                .setMessage("MAME 2010 requer ROMset 0.139 em ZIP. Se o jogo veio de outro ROMset, escolha o MAME/FBNeo compatível; um conjunto de outra versão pode não abrir.")
                .setItems(labels, (dialog, which) -> {
                    try {
                        startRetroGame(rom, cores[which], "ARCADE • " + labels[which]);
                    } catch (LinkageError error) {
                        String detail = error.getMessage() == null ? "" : ": " + error.getMessage();
                        showGameOpenError(new IllegalStateException("Não consegui carregar o núcleo Arcade" + detail + ". Confira se o APK corresponde à arquitetura do celular.", error));
                    } catch (Exception error) {
                        showGameOpenError(error);
                    }
                })''',
    "show MAME 2010 ROMset guidance and catch linker failures",
)

activity.write_text(text)
print("Added Arcade ZIP validation and clearer Java-side core loading errors.")
