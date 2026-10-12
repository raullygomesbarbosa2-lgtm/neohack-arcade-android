#!/usr/bin/env python3
"""Reapply the local ARM64 core-catalog browser to generated v1.0.0 sources."""
from pathlib import Path

main = Path("app/src/main/java/br/com/raully/neohackarcade/MainActivity.java")
s = main.read_text()


def add_once(old: str, new: str) -> None:
    global s
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"Core browser patch anchor missing: {old[:100]!r}")
    s = s.replace(old, new, 1)


add_once(
    "import java.io.InputStream;\n",
    "import java.io.InputStream;\n"
    "import java.io.RandomAccessFile;\n"
    "import java.security.MessageDigest;\n"
    "import java.util.ArrayList;\n"
    "import java.util.HashSet;\n"
    "import java.util.Locale;\n"
    "import java.util.Set;\n"
    "import java.util.zip.ZipEntry;\n"
    "import java.util.zip.ZipInputStream;\n\n"
    "import org.json.JSONArray;\n"
    "import org.json.JSONObject;\n",
)
add_once(
    "    private static final int REQUEST_AUTO_DETECT = 56;\n",
    "    private static final int REQUEST_AUTO_DETECT = 56;\n"
    "    private static final int REQUEST_CATALOG_GAME = 57;\n"
    '    private static final String CORE_CATALOG_ASSET = "core_catalog.json";\n',
)
add_once(
    "    private boolean onboardingProfile;\n",
    "    private boolean onboardingProfile;\n"
    "    private String pendingCatalogCoreId;\n\n"
    "    private static final class CoreCatalogEntry {\n"
    "        final String id;\n"
    "        final String name;\n"
    "        final String system;\n"
    "        final String coreZip;\n"
    "        final String coreFile;\n"
    "        final String sha256;\n\n"
    "        CoreCatalogEntry(String id, String name, String system, String coreZip, String coreFile, String sha256) {\n"
    "            this.id = id;\n"
    "            this.name = name;\n"
    "            this.system = system;\n"
    "            this.coreZip = coreZip;\n"
    "            this.coreFile = coreFile;\n"
    "            this.sha256 = sha256;\n"
    "        }\n"
    "    }\n",
)
add_once(
    '        selectedPhotoUri = getPreferences(0).getString("profile_photo", null);\n',
    '        selectedPhotoUri = getPreferences(0).getString("profile_photo", null);\n'
    '        if (state != null) pendingCatalogCoreId = state.getString("pending_catalog_core_id");\n',
)
add_once(
    "        panel.addView(moreSystems, moreSystemsParams);\n",
    "        panel.addView(moreSystems, moreSystemsParams);\n\n"
    '        Button coreBrowser = menuButton("NÚCLEOS • CATÁLOGO ARM64 • POC 190");\n'
    "        coreBrowser.setOnClickListener(v -> showCoreCatalog());\n"
    "        LinearLayout.LayoutParams coreBrowserParams = buttonParams();\n"
    "        coreBrowserParams.topMargin = dp(6);\n"
    "        panel.addView(coreBrowser, coreBrowserParams);\n",
)
add_once(
    "    private void showMoreSystemsDialog() {\n",
    "    private void showCoreCatalog() {\n"
    "        try {\n"
    '            if (!isArm64AppProcess()) throw new IllegalStateException("Este catálogo local contém apenas núcleos ARM64. Use a versão arm64-v8a do app.");\n'
    "            final ArrayList<CoreCatalogEntry> cores = loadCoreCatalog();\n"
    '            if (cores.isEmpty()) throw new IllegalStateException("O catálogo local não contém núcleos disponíveis.");\n'
    "            String[] labels = new String[cores.size()];\n"
    "            for (int i = 0; i < cores.size(); i++) {\n"
    "                CoreCatalogEntry core = cores.get(i);\n"
    '                labels[i] = core.name + " • " + core.system;\n'
    "            }\n"
    "            new android.app.AlertDialog.Builder(this)\n"
    '                    .setTitle("Núcleo local • escolha o jogo depois")\n'
    "                    .setItems(labels, (dialog, which) -> {\n"
    "                        pendingCatalogCoreId = cores.get(which).id;\n"
    "                        openPicker(REQUEST_CATALOG_GAME);\n"
    "                    })\n"
    '                    .setNegativeButton("Cancelar", null)\n'
    "                    .show();\n"
    "        } catch (Exception error) {\n"
    "            showGameOpenError(error);\n"
    "        }\n"
    "    }\n\n"
    "    private boolean isArm64AppProcess() {\n"
    '        String architecture = System.getProperty("os.arch", "").toLowerCase(Locale.ROOT);\n'
    '        return architecture.contains("aarch64") || architecture.contains("arm64");\n'
    "    }\n\n"
    "    private ArrayList<CoreCatalogEntry> loadCoreCatalog() throws Exception {\n"
    "        StringBuilder jsonText = new StringBuilder();\n"
    "        try (InputStream input = getAssets().open(CORE_CATALOG_ASSET);\n"
    '             java.io.InputStreamReader reader = new java.io.InputStreamReader(input, "UTF-8")) {\n'
    "            char[] buffer = new char[4096];\n"
    "            int count;\n"
    "            while ((count = reader.read(buffer)) != -1) {\n"
    '                if (jsonText.length() + count > 1024 * 1024) throw new IllegalArgumentException("O catálogo de núcleos excede o limite permitido.");\n'
    "                jsonText.append(buffer, 0, count);\n"
    "            }\n"
    "        }\n"
    "        JSONObject root = new JSONObject(jsonText.toString());\n"
    '        if (root.optInt("version", -1) != 1) throw new IllegalArgumentException("Versão de catálogo de núcleos incompatível.");\n'
    '        JSONArray items = root.getJSONArray("cores");\n'
    "        ArrayList<CoreCatalogEntry> cores = new ArrayList<>();\n"
    "        Set<String> ids = new HashSet<>();\n"
    "        for (int i = 0; i < items.length(); i++) {\n"
    "            JSONObject item = items.getJSONObject(i);\n"
    '            String id = item.getString("id");\n'
    '            String name = item.getString("name");\n'
    '            String system = item.getString("system");\n'
    '            String zip = item.getString("coreZip");\n'
    '            String file = item.getString("coreFile");\n'
    '            String hash = item.getString("sha256").toLowerCase(Locale.ROOT);\n'
    '            if (!"arm64-v8a".equals(item.getString("abi"))) throw new IllegalArgumentException("ABI não suportada para o núcleo " + id + ".");\n'
    '            if (!id.matches("[A-Za-z0-9_-]{1,48}") || !ids.add(id)) throw new IllegalArgumentException("ID inválido ou duplicado no catálogo: " + id);\n'
    '            if (name.trim().isEmpty() || system.trim().isEmpty()) throw new IllegalArgumentException("O nome e o sistema são obrigatórios para cada núcleo.");\n'
    '            if (!zip.matches("corepacks/[A-Za-z0-9._-]+[.]zip") || zip.contains("..")) throw new IllegalArgumentException("Caminho inválido para o pacote do núcleo " + id + ".");\n'
    '            if (!file.matches("[A-Za-z0-9._-]+[.]so") || file.contains("..")) throw new IllegalArgumentException("Nome de biblioteca inválido para o núcleo " + id + ".");\n'
    '            if (!hash.matches("[a-f0-9]{64}")) throw new IllegalArgumentException("SHA-256 inválido para o núcleo " + id + ".");\n'
    "            cores.add(new CoreCatalogEntry(id, name, system, zip, file, hash));\n"
    "        }\n"
    "        return cores;\n"
    "    }\n\n"
    "    private CoreCatalogEntry findCoreCatalogEntry(String id) throws Exception {\n"
    '        if (id == null) throw new IllegalStateException("A seleção do núcleo foi perdida. Escolha o núcleo novamente.");\n'
    "        for (CoreCatalogEntry entry : loadCoreCatalog()) if (entry.id.equals(id)) return entry;\n"
    '        throw new IllegalArgumentException("O núcleo selecionado não está mais no catálogo. Escolha outro núcleo.");\n'
    "    }\n\n"
    "    private File extractCatalogCore(CoreCatalogEntry core) throws Exception {\n"
    '        if (!isArm64AppProcess()) throw new IllegalStateException("Este núcleo exige uma versão ARM64 do app.");\n'
    '        File coresDir = new File(getFilesDir(), "cores");\n'
    '        File coreDir = new File(coresDir, core.id);\n'
    '        if (!coreDir.isDirectory() && !coreDir.mkdirs()) throw new IllegalStateException("Não foi possível preparar o armazenamento dos núcleos.");\n'
    '        File destination = new File(coreDir, core.coreFile);\n'
    "        boolean cacheValid = false;\n"
    "        if (destination.isFile() && destination.length() > 0) {\n"
    "            try { cacheValid = core.sha256.equals(sha256(destination)); }\n"
    "            catch (Exception ignored) { cacheValid = false; }\n"
    "        }\n"
    "        if (cacheValid) return destination;\n"
    '        if (destination.exists() && !destination.delete()) throw new IllegalStateException("Não foi possível substituir um núcleo em cache inválido.");\n\n'
    '        File temporary = new File(coreDir, core.coreFile + ".tmp");\n'
    '        if (temporary.exists() && !temporary.delete()) throw new IllegalStateException("Não foi possível limpar a extração anterior do núcleo.");\n'
    '        MessageDigest digest = MessageDigest.getInstance("SHA-256");\n'
    "        boolean foundCore = false;\n"
    "        long total = 0;\n"
    "        try (InputStream asset = getAssets().open(core.coreZip);\n"
    "             ZipInputStream zip = new ZipInputStream(asset)) {\n"
    "            ZipEntry entry;\n"
    "            while ((entry = zip.getNextEntry()) != null) {\n"
    "                if (entry.isDirectory()) continue;\n"
    '                if (foundCore || !core.coreFile.equals(entry.getName()) || entry.getName().contains("/") || entry.getName().contains("\\\\")) {\n'
    '                    throw new IllegalArgumentException("O pacote " + core.coreZip + " precisa conter somente " + core.coreFile + ".");\n'
    "                }\n"
    "                foundCore = true;\n"
    "                try (FileOutputStream output = new FileOutputStream(temporary)) {\n"
    "                    byte[] buffer = new byte[64 * 1024];\n"
    "                    int read;\n"
    "                    while ((read = zip.read(buffer)) != -1) {\n"
    "                        total += read;\n"
    '                        if (total > 1024L * 1024L * 1024L) throw new IllegalArgumentException("O núcleo excede o limite de 1 GiB.");\n'
    "                        digest.update(buffer, 0, read);\n"
    "                        output.write(buffer, 0, read);\n"
    "                    }\n"
    "                    output.getFD().sync();\n"
    "                }\n"
    "                zip.closeEntry();\n"
    "            }\n"
    '            if (!foundCore || total == 0) throw new IllegalArgumentException("O pacote não contém a biblioteca ARM64 esperada: " + core.coreFile);\n'
    '            if (!core.sha256.equals(toHex(digest.digest()))) throw new IllegalArgumentException("A verificação SHA-256 do núcleo falhou: " + core.name);\n'
    "        } catch (Exception error) {\n"
    "            temporary.delete();\n"
    "            throw error;\n"
    "        }\n"
    '        if (!isArm64Elf(temporary)) {\n'
    "            temporary.delete();\n"
    '            throw new IllegalArgumentException("A biblioteca do pacote não é um arquivo ELF ARM64 válido: " + core.coreFile);\n'
    "        }\n"
    "        if (!temporary.renameTo(destination)) {\n"
    "            temporary.delete();\n"
    '            throw new IllegalStateException("Não foi possível concluir a instalação do núcleo.");\n'
    "        }\n"
    "        return destination;\n"
    "    }\n\n"
    "    private String sha256(File file) throws Exception {\n"
    '        MessageDigest digest = MessageDigest.getInstance("SHA-256");\n'
    '        try (InputStream input = new java.io.FileInputStream(file)) {\n'
    "            byte[] buffer = new byte[64 * 1024];\n"
    "            int count;\n"
    "            while ((count = input.read(buffer)) != -1) digest.update(buffer, 0, count);\n"
    "        }\n"
    "        return toHex(digest.digest());\n"
    "    }\n\n"
    "    private String toHex(byte[] bytes) {\n"
    "        StringBuilder result = new StringBuilder(bytes.length * 2);\n"
    "        for (byte value : bytes) result.append(String.format(Locale.ROOT, \"%02x\", value & 0xff));\n"
    "        return result.toString();\n"
    "    }\n\n"
    "    private boolean isArm64Elf(File file) throws Exception {\n"
    '        try (RandomAccessFile input = new RandomAccessFile(file, "r")) {\n'
    "            if (input.length() < 20) return false;\n"
    "            byte[] header = new byte[20];\n"
    "            input.readFully(header);\n"
    "            return header[0] == 0x7f && header[1] == 'E' && header[2] == 'L' && header[3] == 'F'\n"
    "                    && header[4] == 2 && header[5] == 1 && (header[18] & 0xff) == 0xb7 && header[19] == 0;\n"
    "        }\n"
    "    }\n\n"
    "    private void showMoreSystemsDialog() {\n",
)
add_once(
    '        intent.putExtra(Intent.EXTRA_TITLE, requestCode == REQUEST_PROFILE_PHOTO ? "Escolha uma foto" : "Escolha a ROM do jogo (não o APK)");\n',
    '        String title = requestCode == REQUEST_PROFILE_PHOTO ? "Escolha uma foto" :\n'
    '                requestCode == REQUEST_CATALOG_GAME ? "Escolha seu arquivo de jogo (não o APK)" : "Escolha a ROM do jogo (não o APK)";\n'
    '        intent.putExtra(Intent.EXTRA_TITLE, title);\n',
)
add_once(
    '    @Override @SuppressWarnings("deprecation")\n    protected void onActivityResult(int requestCode, int resultCode, Intent data) {\n'
    '        super.onActivityResult(requestCode, resultCode, data);\n',
    '    @Override protected void onSaveInstanceState(Bundle outState) {\n'
    '        if (pendingCatalogCoreId != null) outState.putString("pending_catalog_core_id", pendingCatalogCoreId);\n'
    '        super.onSaveInstanceState(outState);\n'
    '    }\n\n'
    '    @Override @SuppressWarnings("deprecation")\n'
    '    protected void onActivityResult(int requestCode, int resultCode, Intent data) {\n'
    '        super.onActivityResult(requestCode, resultCode, data);\n'
    '        if (requestCode == REQUEST_CATALOG_GAME && (resultCode != RESULT_OK || data == null || data.getData() == null)) {\n'
    '            pendingCatalogCoreId = null;\n'
    '        }\n',
)
add_once(
    '                showProfileScreen(!getPreferences(0).contains("profile_name"), draft);\n'
    '            } else if (requestCode != REQUEST_PROFILE_PHOTO) {\n',
    '                showProfileScreen(!getPreferences(0).contains("profile_name"), draft);\n'
    '            } else if (requestCode == REQUEST_CATALOG_GAME) {\n'
    '                openCatalogGame(uri);\n'
    '            } else if (requestCode != REQUEST_PROFILE_PHOTO) {\n',
)
add_once(
    '    private void openSelectedGame(Uri uri, int requestCode) throws Exception {\n',
    '    private void openCatalogGame(Uri uri) throws Exception {\n'
    '        enterImmersiveMode();\n'
    '        CoreCatalogEntry core = findCoreCatalogEntry(pendingCatalogCoreId);\n'
    '        pendingCatalogCoreId = null;\n'
    '        File game = copyRom(uri);\n'
    '        File library = extractCatalogCore(core);\n'
    '        startRetroGame(game, library, core.coreFile, core.name + " • " + core.system);\n'
    '    }\n\n'
    '    private void openSelectedGame(Uri uri, int requestCode) throws Exception {\n',
)
add_once(
    '    private void startRetroGame(File rom, String coreLibrary, String systemLabel) {\n'
    '        File systemDir = new File(getFilesDir(), "system");\n'
    '        File savesDir = new File(getFilesDir(), "saves");\n',
    '    private void startRetroGame(File rom, String coreLibrary, String systemLabel) {\n'
    '        File nativeCore = new File(getApplicationInfo().nativeLibraryDir, coreLibrary);\n'
    '        startRetroGame(rom, nativeCore, coreLibrary, systemLabel);\n'
    '    }\n\n'
    '    private void startRetroGame(File rom, File nativeCore, String coreLibrary, String systemLabel) {\n'
    '        File systemDir = new File(getFilesDir(), "system");\n'
    '        File savesDir = new File(getFilesDir(), "saves");\n',
)
add_once(
    '        systemDir.mkdirs();\n'
    '        savesDir.mkdirs();\n',
    '        if (!systemDir.isDirectory() && !systemDir.mkdirs()) throw new IllegalStateException("Não foi possível preparar a pasta do sistema.");\n'
    '        if (!savesDir.isDirectory() && !savesDir.mkdirs()) throw new IllegalStateException("Não foi possível preparar a pasta de salvamentos.");\n',
)
add_once(
    '        GLRetroViewData data = new GLRetroViewData(this);\n'
    '        File nativeCore = new File(getApplicationInfo().nativeLibraryDir, coreLibrary);\n'
    '        if (!nativeCore.isFile()) {\n'
    '            throw new IllegalStateException("Núcleo de emulação não encontrado no APK: " + coreLibrary);\n'
    '        }\n',
    '        GLRetroViewData data = new GLRetroViewData(this);\n'
    '        if (nativeCore == null || !nativeCore.isFile() || nativeCore.length() == 0) {\n'
    '            throw new IllegalStateException("Arquivo do núcleo de emulação não encontrado: " + coreLibrary);\n'
    '        }\n',
)

main.write_text(s)

build = Path("app/build.gradle")
gradle = build.read_text()
abi_line = "include 'armeabi-v7a', 'arm64-v8a'"
if abi_line in gradle:
    gradle = gradle.replace(abi_line, "include 'arm64-v8a'")
elif "include 'arm64-v8a'" not in gradle:
    raise SystemExit("Could not restrict the POC APK split to the ARM64 ABI.")
filter_line = "abiFilters 'armeabi-v7a', 'arm64-v8a'"
if filter_line in gradle:
    gradle = gradle.replace(filter_line, "abiFilters 'arm64-v8a'")
build.write_text(gradle)
print("Applied reproducible ARM64-only core-catalog browser patch")
