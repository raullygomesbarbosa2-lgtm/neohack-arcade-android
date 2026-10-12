package br.com.raully.neohackarcade;

import android.content.Intent;
import android.database.Cursor;
import android.graphics.Color;
import android.graphics.BitmapFactory;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.FrameLayout;
import android.widget.GridLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.ComponentActivity;

import com.swordfish.libretrodroid.GLRetroView;
import com.swordfish.libretrodroid.GLRetroViewData;
import com.swordfish.libretrodroid.ShaderConfig;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.RandomAccessFile;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import org.json.JSONArray;
import org.json.JSONObject;

/** Native Android frontend for CHIP-8, SNES and classic Sega systems. */
public final class MainActivity extends ComponentActivity {
    private static final int REQUEST_CHIP8 = 43;
    private static final int REQUEST_ARCADE = 41;
    private static final int REQUEST_PROFILE_PHOTO = 44;
    private static final int REQUEST_SNES = 45;
    private static final int REQUEST_SEGA_8_16 = 46;
    private static final int REQUEST_NES = 47;
    private static final int REQUEST_GAMEBOY = 48;
    private static final int REQUEST_GBA = 49;
    private static final int REQUEST_ATARI2600 = 50;
    private static final int REQUEST_ATARI7800 = 51;
    private static final int REQUEST_PCE = 52;
    private static final int REQUEST_LYNX = 53;
    private static final int REQUEST_NGP = 54;
    private static final int REQUEST_WSWAN = 55;
    private static final int REQUEST_AUTO_DETECT = 56;
    private static final int REQUEST_CATALOG_GAME = 57;
    private static final String CORE_CATALOG_ASSET = "core_catalog.json";
    private static final String[] AVATAR_GLYPHS = {"⚡", "👾", "🎮", "🛸", "💎", "🔥"};
    private FrameLayout root;
    private GLRetroView retroView;
    private Chip8View chip8View;
    private EditText profileNameInput;
    private int selectedAvatarIndex;
    private String selectedPhotoUri;
    private File currentStateFile;
    private String activeCheatCode = "";
    private final android.os.Handler specialMacroHandler = new android.os.Handler(android.os.Looper.getMainLooper());
    private boolean specialMacroRunning;
    private boolean profileScreenActive;
    private boolean onboardingProfile;
    private String pendingCatalogCoreId;

    private static final class CoreCatalogEntry {
        final String id;
        final String name;
        final String system;
        final String coreZip;
        final String coreFile;
        final String sha256;

        CoreCatalogEntry(String id, String name, String system, String coreZip, String coreFile, String sha256) {
            this.id = id;
            this.name = name;
            this.system = system;
            this.coreZip = coreZip;
            this.coreFile = coreFile;
            this.sha256 = sha256;
        }
    }

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
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

    private void showLibrary() {
        profileScreenActive = false;
        if (chip8View != null) chip8View.pauseEmulation();
        chip8View = null;
        retroView = null;
        root = new FrameLayout(this);
        root.setBackground(arcadeBackdrop());
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setGravity(Gravity.CENTER);
        int horizontal = dp(28);
        panel.setPadding(horizontal, dp(8), horizontal, dp(8));

        TextView title = new TextView(this);
        title.setText("Vortix");
        title.setTextColor(0xffa9f7ff);
        title.setShadowLayer(dp(12), 0, 0, 0xff00d9ff);
        title.setTextSize(28);
        title.setGravity(Gravity.CENTER);
        panel.addView(title, new LinearLayout.LayoutParams(-1, -2));

        addProfileRow(panel);

        TextView info = new TextView(this);
        info.setText("CHIP-8 • SNES • Sega • Arcade • + 9 sistemas retrô");
        info.setTextColor(0xffc5eaf0);
        info.setTextSize(14);
        info.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams infoParams = new LinearLayout.LayoutParams(-1, -2);
        infoParams.setMargins(0, dp(5), 0, dp(8));
        panel.addView(info, infoParams);

        TextView romHelp = new TextView(this);
        romHelp.setText("ROM original ou hack já aplicado: escolha o console ou use detecção automática. Não escolha um APK.");
        romHelp.setTextColor(0xffa9d2dc);
        romHelp.setTextSize(12);
        romHelp.setGravity(Gravity.CENTER);
        panel.addView(romHelp, new LinearLayout.LayoutParams(-1, dp(30)));

        Button autoRom = menuButton("ABRIR ROM • DETECTAR SISTEMA");
        autoRom.setOnClickListener(v -> openPicker(REQUEST_AUTO_DETECT));
        panel.addView(autoRom, buttonParams());

        Button chip = menuButton("Jogar CHIP-8 — abrir arquivo .ch8 / .c8");
        chip.setOnClickListener(v -> openPicker(REQUEST_CHIP8));
        panel.addView(chip, buttonParams());

        Button snes = menuButton("SUPER NINTENDO • SNES9x — abrir ROM");
        snes.setOnClickListener(v -> openPicker(REQUEST_SNES));
        LinearLayout.LayoutParams snesParams = buttonParams();
        snesParams.topMargin = dp(6);
        panel.addView(snes, snesParams);

        Button sega = menuButton("SEGA • Genesis Plus GX — Mega Drive / Master System / Game Gear");
        sega.setOnClickListener(v -> openPicker(REQUEST_SEGA_8_16));
        LinearLayout.LayoutParams segaParams = buttonParams();
        segaParams.topMargin = dp(6);
        panel.addView(sega, segaParams);

        Button arcade = menuButton("ARCADE • FBNeo / MAME 2000, 2003, 2003+, 2010");
        arcade.setOnClickListener(v -> openPicker(REQUEST_ARCADE));
        LinearLayout.LayoutParams arcadeParams = buttonParams();
        arcadeParams.topMargin = dp(6);
        panel.addView(arcade, arcadeParams);

        Button moreSystems = menuButton("BIBLIOTECA DE NÚCLEOS • NES, GAME BOY, ATARI...");
        moreSystems.setOnClickListener(v -> showMoreSystemsDialog());
        LinearLayout.LayoutParams moreSystemsParams = buttonParams();
        moreSystemsParams.topMargin = dp(6);
        panel.addView(moreSystems, moreSystemsParams);

        Button coreBrowser = menuButton("NÚCLEOS • TESTE DO CATÁLOGO LOCAL");
        coreBrowser.setOnClickListener(v -> showCoreCatalog());
        LinearLayout.LayoutParams coreBrowserParams = buttonParams();
        coreBrowserParams.topMargin = dp(6);
        panel.addView(coreBrowser, coreBrowserParams);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setClipToPadding(false);
        scroll.addView(panel, new ScrollView.LayoutParams(-1, -2));
        root.addView(scroll, new FrameLayout.LayoutParams(-1, -1));
        setContentView(root);
    }

    private void showMoreSystemsDialog() {
        final int[] requestCodes = {
                REQUEST_NES, REQUEST_GAMEBOY, REQUEST_GBA, REQUEST_ATARI2600,
                REQUEST_ATARI7800, REQUEST_PCE, REQUEST_LYNX, REQUEST_NGP, REQUEST_WSWAN
        };
        String[] systems = {
                "NES / Famicom • FCEUmm", "Game Boy / Color • Gambatte", "Game Boy Advance • Beetle GBA",
                "Atari 2600 • Stella 2014", "Atari 7800 • ProSystem", "PC Engine • Beetle PCE Fast",
                "Atari Lynx • Beetle Lynx", "Neo Geo Pocket • Beetle NGP", "WonderSwan • Beetle WonderSwan"
        };
        new android.app.AlertDialog.Builder(this)
                .setTitle("Biblioteca de consoles e núcleos")
                .setItems(systems, (dialog, which) -> openPicker(requestCodes[which]))
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private void showCoreCatalog() {
        try {
            if (!isArm64AppProcess()) throw new IllegalStateException("Este catálogo local contém apenas núcleos ARM64. Use a versão arm64-v8a do app.");
            final ArrayList<CoreCatalogEntry> cores = loadCoreCatalog();
            if (cores.isEmpty()) throw new IllegalStateException("O catálogo local não contém núcleos disponíveis.");
            String[] labels = new String[cores.size()];
            for (int i = 0; i < cores.size(); i++) {
                CoreCatalogEntry core = cores.get(i);
                labels[i] = core.name + " • " + core.system;
            }
            new android.app.AlertDialog.Builder(this)
                    .setTitle("Núcleo local • escolha o jogo depois")
                    .setItems(labels, (dialog, which) -> {
                        pendingCatalogCoreId = cores.get(which).id;
                        openPicker(REQUEST_CATALOG_GAME);
                    })
                    .setNegativeButton("Cancelar", null)
                    .show();
        } catch (Exception error) {
            showGameOpenError(error);
        }
    }

    private boolean isArm64AppProcess() {
        String architecture = System.getProperty("os.arch", "").toLowerCase(Locale.ROOT);
        return architecture.contains("aarch64") || architecture.contains("arm64");
    }

    private ArrayList<CoreCatalogEntry> loadCoreCatalog() throws Exception {
        StringBuilder jsonText = new StringBuilder();
        try (InputStream input = getAssets().open(CORE_CATALOG_ASSET);
             java.io.InputStreamReader reader = new java.io.InputStreamReader(input, "UTF-8")) {
            char[] buffer = new char[4096];
            int count;
            while ((count = reader.read(buffer)) != -1) {
                if (jsonText.length() + count > 1024 * 1024) throw new IllegalArgumentException("O catálogo de núcleos excede o limite permitido.");
                jsonText.append(buffer, 0, count);
            }
        }
        JSONObject root = new JSONObject(jsonText.toString());
        if (root.optInt("version", -1) != 1) throw new IllegalArgumentException("Versão de catálogo de núcleos incompatível.");
        JSONArray items = root.getJSONArray("cores");
        ArrayList<CoreCatalogEntry> cores = new ArrayList<>();
        Set<String> ids = new HashSet<>();
        for (int i = 0; i < items.length(); i++) {
            JSONObject item = items.getJSONObject(i);
            String id = item.getString("id");
            String name = item.getString("name");
            String system = item.getString("system");
            String zip = item.getString("coreZip");
            String file = item.getString("coreFile");
            String hash = item.getString("sha256").toLowerCase(Locale.ROOT);
            if (!"arm64-v8a".equals(item.getString("abi"))) throw new IllegalArgumentException("ABI não suportada para o núcleo " + id + ".");
            if (!id.matches("[A-Za-z0-9_-]{1,48}") || !ids.add(id)) throw new IllegalArgumentException("ID inválido ou duplicado no catálogo: " + id);
            if (name.trim().isEmpty() || system.trim().isEmpty()) throw new IllegalArgumentException("O nome e o sistema são obrigatórios para cada núcleo.");
            if (!zip.matches("corepacks/[A-Za-z0-9._-]+[.]zip") || zip.contains("..")) throw new IllegalArgumentException("Caminho inválido para o pacote do núcleo " + id + ".");
            if (!file.matches("[A-Za-z0-9._-]+[.]so") || file.contains("..")) throw new IllegalArgumentException("Nome de biblioteca inválido para o núcleo " + id + ".");
            if (!hash.matches("[a-f0-9]{64}")) throw new IllegalArgumentException("SHA-256 inválido para o núcleo " + id + ".");
            cores.add(new CoreCatalogEntry(id, name, system, zip, file, hash));
        }
        return cores;
    }

    private CoreCatalogEntry findCoreCatalogEntry(String id) throws Exception {
        if (id == null) throw new IllegalStateException("A seleção do núcleo foi perdida. Escolha o núcleo novamente.");
        for (CoreCatalogEntry entry : loadCoreCatalog()) if (entry.id.equals(id)) return entry;
        throw new IllegalArgumentException("O núcleo selecionado não está mais no catálogo. Escolha outro núcleo.");
    }

    private File extractCatalogCore(CoreCatalogEntry core) throws Exception {
        if (!isArm64AppProcess()) throw new IllegalStateException("Este núcleo exige uma versão ARM64 do app.");
        File coresDir = new File(getFilesDir(), "cores");
        File coreDir = new File(coresDir, core.id);
        if (!coreDir.isDirectory() && !coreDir.mkdirs()) throw new IllegalStateException("Não foi possível preparar o armazenamento dos núcleos.");
        File destination = new File(coreDir, core.coreFile);
        boolean cacheValid = false;
        if (destination.isFile() && destination.length() > 0) {
            try { cacheValid = core.sha256.equals(sha256(destination)); }
            catch (Exception ignored) { cacheValid = false; }
        }
        if (cacheValid) return destination;
        if (destination.exists() && !destination.delete()) throw new IllegalStateException("Não foi possível substituir um núcleo em cache inválido.");

        File temporary = new File(coreDir, core.coreFile + ".tmp");
        if (temporary.exists() && !temporary.delete()) throw new IllegalStateException("Não foi possível limpar a extração anterior do núcleo.");
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        boolean foundCore = false;
        long total = 0;
        try (InputStream asset = getAssets().open(core.coreZip);
             ZipInputStream zip = new ZipInputStream(asset)) {
            ZipEntry entry;
            while ((entry = zip.getNextEntry()) != null) {
                if (entry.isDirectory()) continue;
                if (foundCore || !core.coreFile.equals(entry.getName()) || entry.getName().contains("/") || entry.getName().contains("\\\\")) {
                    throw new IllegalArgumentException("O pacote " + core.coreZip + " precisa conter somente " + core.coreFile + ".");
                }
                foundCore = true;
                try (FileOutputStream output = new FileOutputStream(temporary)) {
                    byte[] buffer = new byte[64 * 1024];
                    int count;
                    while ((count = zip.read(buffer)) != -1) {
                        total += count;
                        if (total > 256L * 1024L * 1024L) throw new IllegalArgumentException("O pacote do núcleo excede 256 MB.");
                        digest.update(buffer, 0, count);
                        output.write(buffer, 0, count);
                    }
                    output.getFD().sync();
                }
                zip.closeEntry();
            }
            if (!foundCore || total == 0) throw new IllegalArgumentException("O pacote não contém a biblioteca ARM64 esperada: " + core.coreFile);
            if (!core.sha256.equals(toHex(digest.digest()))) throw new IllegalArgumentException("A verificação SHA-256 do núcleo falhou: " + core.name);
        } catch (Exception error) {
            temporary.delete();
            throw error;
        }
        if (!isArm64Elf(temporary)) {
            temporary.delete();
            throw new IllegalArgumentException("A biblioteca do pacote não é um arquivo ELF ARM64 válido: " + core.coreFile);
        }
        if (!temporary.renameTo(destination)) {
            temporary.delete();
            throw new IllegalStateException("Não foi possível concluir a instalação do núcleo.");
        }
        return destination;
    }

    private String sha256(File file) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        try (InputStream input = new java.io.FileInputStream(file)) {
            byte[] buffer = new byte[64 * 1024];
            int count;
            while ((count = input.read(buffer)) != -1) digest.update(buffer, 0, count);
        }
        return toHex(digest.digest());
    }

    private String toHex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) result.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        return result.toString();
    }

    private boolean isArm64Elf(File file) throws Exception {
        try (RandomAccessFile input = new RandomAccessFile(file, "r")) {
            if (input.length() < 20) return false;
            byte[] header = new byte[20];
            input.readFully(header);
            return header[0] == 0x7f && header[1] == 'E' && header[2] == 'L' && header[3] == 'F'
                    && header[4] == 2 && header[5] == 1 && (header[18] & 0xff) == 0xb7 && header[19] == 0;
        }
    }

    private Button menuButton(String label) {
        Button button = new Button(this);
        button.setText(label);
        button.setTextSize(14);
        button.setAllCaps(false);
        styleNeonButton(button, false);
        return button;
    }

    private LinearLayout.LayoutParams buttonParams() { return new LinearLayout.LayoutParams(-1, dp(48)); }

    private GradientDrawable arcadeBackdrop() {
        return new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[]{0xff03070d, 0xff07131c, 0xff030810});
    }

    private void styleNeonButton(Button button, boolean filled) {
        GradientDrawable shape = new GradientDrawable();
        shape.setColor(filled ? 0xff07333f : 0xff101b24);
        shape.setCornerRadius(dp(14));
        shape.setStroke(dp(2), 0xff00e5ff);
        button.setBackground(shape);
        button.setTextColor(0xffe8fbff);
        button.setShadowLayer(dp(4), 0, 0, 0xff00bde8);
        button.setLayerType(View.LAYER_TYPE_SOFTWARE, null);
        button.setElevation(dp(5));
    }

    private void addProfileRow(LinearLayout panel) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setPadding(dp(12), dp(6), dp(12), dp(6));
        GradientDrawable box = new GradientDrawable();
        box.setColor(0xee0a1720); box.setCornerRadius(dp(18)); box.setStroke(dp(1), 0xff00bde8);
        row.setBackground(box);
        FrameLayout badge = makeAvatarBadge(36);
        row.addView(badge, new LinearLayout.LayoutParams(dp(36), dp(36)));
        TextView name = new TextView(this);
        name.setText(getPreferences(0).getString("profile_name", "Jogador"));
        name.setTextColor(0xffe8fbff); name.setTextSize(16); name.setShadowLayer(dp(5), 0, 0, 0xff00cfff);
        LinearLayout.LayoutParams nameParams = new LinearLayout.LayoutParams(0, -2, 1);
        nameParams.leftMargin = dp(12); row.addView(name, nameParams);
        TextView edit = new TextView(this);
        edit.setText("EDITAR PERFIL"); edit.setTextColor(0xff00e5ff); edit.setTextSize(11);
        row.addView(edit, new LinearLayout.LayoutParams(-2, -2));
        row.setOnClickListener(v -> showProfileScreen(false, getPreferences(0).getString("profile_name", "")));
        LinearLayout.LayoutParams rowParams = new LinearLayout.LayoutParams(-1, dp(48));
        rowParams.setMargins(dp(4), dp(3), dp(4), dp(6)); panel.addView(row, rowParams);
    }

    private FrameLayout makeAvatarBadge(int sizeDp) {
        FrameLayout badge = new FrameLayout(this);
        GradientDrawable circle = new GradientDrawable();
        circle.setShape(GradientDrawable.OVAL); circle.setColor(0xff0a2832); circle.setStroke(dp(2), 0xff00e5ff);
        badge.setBackground(circle);
        TextView glyph = new TextView(this);
        glyph.setText(AVATAR_GLYPHS[((selectedAvatarIndex % AVATAR_GLYPHS.length) + AVATAR_GLYPHS.length) % AVATAR_GLYPHS.length]);
        glyph.setTextSize(sizeDp * .43f); glyph.setGravity(Gravity.CENTER); glyph.setTextColor(0xffd7fbff);
        badge.addView(glyph, new FrameLayout.LayoutParams(-1, -1));
        if (selectedPhotoUri != null && !selectedPhotoUri.isEmpty()) {
            ImageView photo = new ImageView(this);
            photo.setScaleType(ImageView.ScaleType.CENTER_CROP);
            photo.setBackground(circle); photo.setClipToOutline(true);
            loadProfileImage(photo);
            badge.addView(photo, new FrameLayout.LayoutParams(-1, -1));
        }
        return badge;
    }

    private void loadProfileImage(ImageView image) {
        try {
            android.graphics.BitmapFactory.Options bounds = new android.graphics.BitmapFactory.Options();
            bounds.inJustDecodeBounds = true;
            try (InputStream input = getContentResolver().openInputStream(Uri.parse(selectedPhotoUri))) {
                if (input != null) BitmapFactory.decodeStream(input, null, bounds);
            }
            int sample = 1;
            while (bounds.outWidth / sample > 256 || bounds.outHeight / sample > 256) sample *= 2;
            android.graphics.BitmapFactory.Options options = new android.graphics.BitmapFactory.Options();
            options.inSampleSize = sample;
            try (InputStream input = getContentResolver().openInputStream(Uri.parse(selectedPhotoUri))) {
                if (input != null) image.setImageBitmap(BitmapFactory.decodeStream(input, null, options));
            }
        } catch (Exception ignored) { }
    }

    private void showProfileScreen(boolean onboarding, String draftName) {
        profileScreenActive = true;
        onboardingProfile = onboarding;
        root = new FrameLayout(this); root.setBackground(arcadeBackdrop());
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL); panel.setGravity(Gravity.CENTER_HORIZONTAL);
        panel.setPadding(dp(20), dp(4), dp(20), dp(4));
        TextView title = new TextView(this);
        title.setText(onboarding ? "CRIE SEU PERFIL" : "PERSONALIZAR PERFIL");
        title.setTextColor(0xffa9f7ff); title.setTextSize(20); title.setGravity(Gravity.CENTER);
        title.setShadowLayer(dp(10), 0, 0, 0xff00d9ff); panel.addView(title, new LinearLayout.LayoutParams(-1, dp(28)));
        TextView hint = new TextView(this);
        hint.setText("Só um nome, sem senha. O perfil fica salvo neste aparelho.");
        hint.setTextColor(0xffb2dce4); hint.setTextSize(12); hint.setGravity(Gravity.CENTER);
        panel.addView(hint, new LinearLayout.LayoutParams(-1, dp(22)));

        profileNameInput = new EditText(this);
        profileNameInput.setSingleLine(true); profileNameInput.setTextSize(17); profileNameInput.setTextColor(0xffedfcff);
        profileNameInput.setHintTextColor(0xff80aeb8); profileNameInput.setHint("Seu nome de jogador");
        profileNameInput.setText(draftName == null ? "" : draftName);
        profileNameInput.setPadding(dp(12), 0, dp(12), 0);
        GradientDrawable inputBg = new GradientDrawable(); inputBg.setColor(0xff0d1a23); inputBg.setCornerRadius(dp(12)); inputBg.setStroke(dp(1), 0xff00cde8);
        profileNameInput.setBackground(inputBg);
        LinearLayout.LayoutParams inputParams = new LinearLayout.LayoutParams(-1, dp(42));
        inputParams.setMargins(dp(24), dp(2), dp(24), dp(5)); panel.addView(profileNameInput, inputParams);

        FrameLayout preview = makeAvatarBadge(54);
        LinearLayout.LayoutParams previewParams = new LinearLayout.LayoutParams(dp(54), dp(54));
        previewParams.bottomMargin = dp(2); panel.addView(preview, previewParams);
        TextView choose = new TextView(this); choose.setText("ESCOLHA SEU AVATAR"); choose.setTextColor(0xff00e5ff); choose.setTextSize(11); choose.setGravity(Gravity.CENTER);
        panel.addView(choose, new LinearLayout.LayoutParams(-1, dp(18)));
        GridLayout avatars = new GridLayout(this); avatars.setColumnCount(6);
        for (int n = 0; n < AVATAR_GLYPHS.length; n++) {
            final int index = n;
            Button option = new Button(this); option.setText(AVATAR_GLYPHS[n]); option.setTextSize(21); option.setAllCaps(false);
            styleNeonButton(option, n == selectedAvatarIndex && (selectedPhotoUri == null || selectedPhotoUri.isEmpty()));
            GridLayout.LayoutParams optionParams = new GridLayout.LayoutParams();
            optionParams.width = dp(48); optionParams.height = dp(42); optionParams.setMargins(dp(2), dp(1), dp(2), dp(1));
            avatars.addView(option, optionParams);
            option.setOnClickListener(v -> {
                String currentName = profileNameInput.getText().toString();
                selectedAvatarIndex = index; selectedPhotoUri = null;
                showProfileScreen(onboarding, currentName);
            });
        }
        panel.addView(avatars, new LinearLayout.LayoutParams(-2, dp(44)));

        Button gallery = menuButton("ESCOLHER FOTO DA GALERIA");
        gallery.setOnClickListener(v -> openPicker(REQUEST_PROFILE_PHOTO));
        LinearLayout.LayoutParams galleryParams = new LinearLayout.LayoutParams(-1, dp(40));
        galleryParams.setMargins(dp(24), dp(2), dp(24), dp(4)); panel.addView(gallery, galleryParams);
        Button save = menuButton(onboarding ? "ENTRAR NA ARCADE" : "SALVAR PERFIL");
        styleNeonButton(save, true);
        save.setOnClickListener(v -> {
            String name = profileNameInput.getText().toString().trim();
            if (name.isEmpty()) { profileNameInput.setError("Digite seu nome de jogador"); return; }
            getPreferences(0).edit().putString("profile_name", name).putInt("profile_avatar", selectedAvatarIndex)
                    .putString("profile_photo", selectedPhotoUri == null ? "" : selectedPhotoUri).apply();
            showLibrary();
        });
        LinearLayout.LayoutParams saveParams = new LinearLayout.LayoutParams(-1, dp(42));
        saveParams.setMargins(dp(24), 0, dp(24), 0); panel.addView(save, saveParams);
        if (!onboarding) {
            Button cancel = menuButton("VOLTAR");
            cancel.setOnClickListener(v -> { restoreSavedProfile(); showLibrary(); });
            LinearLayout.LayoutParams cancelParams = new LinearLayout.LayoutParams(-1, dp(32));
            cancelParams.setMargins(dp(24), dp(3), dp(24), 0); panel.addView(cancel, cancelParams);
        }
        root.addView(panel, new FrameLayout.LayoutParams(-1, -2, Gravity.CENTER));
        setContentView(root);
    }

    private void restoreSavedProfile() {
        selectedAvatarIndex = getPreferences(0).getInt("profile_avatar", 0);
        selectedPhotoUri = getPreferences(0).getString("profile_photo", "");
    }

    private void openPicker(int requestCode) {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType(requestCode == REQUEST_PROFILE_PHOTO ? "image/*" : "*/*");
        String title = requestCode == REQUEST_PROFILE_PHOTO ? "Escolha uma foto" :
                requestCode == REQUEST_CATALOG_GAME ? "Escolha seu arquivo de jogo (não o APK)" : "Escolha a ROM do jogo (não o APK)";
        intent.putExtra(Intent.EXTRA_TITLE, title);
        enterImmersiveMode();
        startActivityForResult(intent, requestCode);
    }

    private void rejectInstallerFile(Uri uri) {
        String name = displayName(uri);
        if (name == null) return;
        String lower = name.toLowerCase(java.util.Locale.ROOT);
        if (lower.endsWith(".apk") || lower.endsWith(".xapk") || lower.endsWith(".apks")) {
            throw new IllegalArgumentException("Esse arquivo é um instalador APK, não um jogo. Volte e escolha uma ROM, por exemplo .sfc, .nes, .gba ou .zip.");
        }
    }

    @Override protected void onSaveInstanceState(Bundle outState) {
        if (pendingCatalogCoreId != null) outState.putString("pending_catalog_core_id", pendingCatalogCoreId);
        super.onSaveInstanceState(outState);
    }

    @Override @SuppressWarnings("deprecation")
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CATALOG_GAME && (resultCode != RESULT_OK || data == null || data.getData() == null)) {
            pendingCatalogCoreId = null;
        }
        if (resultCode != RESULT_OK || data == null || data.getData() == null) return;
        try {
            Uri uri = data.getData();
            if (requestCode != REQUEST_PROFILE_PHOTO) rejectInstallerFile(uri);
            if (requestCode == REQUEST_PROFILE_PHOTO) {
                int readFlag = data.getFlags() & Intent.FLAG_GRANT_READ_URI_PERMISSION;
                if (readFlag != 0) {
                    try { getContentResolver().takePersistableUriPermission(uri, readFlag); }
                    catch (SecurityException ignored) { }
                }
                String draft = profileNameInput == null ? "" : profileNameInput.getText().toString();
                selectedPhotoUri = uri.toString();
                showProfileScreen(!getPreferences(0).contains("profile_name"), draft);
            } else if (requestCode == REQUEST_CATALOG_GAME) {
                openCatalogGame(uri);
            } else if (requestCode != REQUEST_PROFILE_PHOTO) {
                openSelectedGame(uri, requestCode);
            }
        } catch (Exception error) {
            showLibrary();
            new android.app.AlertDialog.Builder(this)
                    .setTitle("Não consegui abrir o jogo")
                    .setMessage(error.getMessage() == null ? "Confira o arquivo selecionado e tente de novo." : error.getMessage())
                    .setPositiveButton("OK", null)
                    .show();
        }
    }

    private void openCatalogGame(Uri uri) throws Exception {
        enterImmersiveMode();
        CoreCatalogEntry core = findCoreCatalogEntry(pendingCatalogCoreId);
        pendingCatalogCoreId = null;
        File game = copyRom(uri);
        File library = extractCatalogCore(core);
        startRetroGame(game, library, core.coreFile, core.name + " • " + core.system);
    }

    private void openSelectedGame(Uri uri, int requestCode) throws Exception {
        enterImmersiveMode();
        File selected = copyRom(uri);
        if (requestCode == REQUEST_AUTO_DETECT) {
            openAutoDetectedGame(selected);
            return;
        }
        if (!selected.getName().toLowerCase(java.util.Locale.ROOT).endsWith(".zip")) {
            launchSelectedGame(selected, requestCode);
            return;
        }
        java.util.ArrayList<String> matches = listMatchingZipEntries(selected, requestCode);
        if (requestCode == REQUEST_ARCADE && matches.isEmpty()) {
            // A MAME game is commonly itself a ZIP set; pass it through unchanged.
            launchSelectedGame(selected, requestCode);
            return;
        }
        if (matches.isEmpty()) {
            throw new IllegalArgumentException("Esse ZIP não contém uma ROM compatível com o console selecionado. Abra o ZIP e escolha o arquivo do jogo correto.");
        }
        if (matches.size() == 1) {
            launchSelectedGame(extractZipEntry(selected, matches.get(0)), requestCode);
            return;
        }
        final File archive = selected;
        new android.app.AlertDialog.Builder(this)
                .setTitle("Escolha a ROM dentro do ZIP")
                .setItems(matches.toArray(new String[matches.size()]), (dialog, which) -> {
                    try {
                        launchSelectedGame(extractZipEntry(archive, matches.get(which)), requestCode);
                    } catch (Exception error) {
                        showGameOpenError(error);
                    }
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private int detectRomSystem(String filename) {
        String name = filename.toLowerCase(java.util.Locale.ROOT);
        if (name.endsWith(".ch8") || name.endsWith(".c8") || name.endsWith(".chip8")) return REQUEST_CHIP8;
        if (name.endsWith(".sfc") || name.endsWith(".smc") || name.endsWith(".fig") || name.endsWith(".swc")) return REQUEST_SNES;
        if (name.endsWith(".md") || name.endsWith(".gen") || name.endsWith(".sms") || name.endsWith(".gg") || name.endsWith(".sg")) return REQUEST_SEGA_8_16;
        if (name.endsWith(".nes") || name.endsWith(".unf") || name.endsWith(".unif")) return REQUEST_NES;
        if (name.endsWith(".gb") || name.endsWith(".gbc")) return REQUEST_GAMEBOY;
        if (name.endsWith(".gba")) return REQUEST_GBA;
        if (name.endsWith(".a26")) return REQUEST_ATARI2600;
        if (name.endsWith(".a78")) return REQUEST_ATARI7800;
        if (name.endsWith(".pce")) return REQUEST_PCE;
        if (name.endsWith(".lnx")) return REQUEST_LYNX;
        if (name.endsWith(".ngp") || name.endsWith(".ngc")) return REQUEST_NGP;
        if (name.endsWith(".ws") || name.endsWith(".wsc")) return REQUEST_WSWAN;
        if (name.endsWith(".bin")) return -2;
        return -1;
    }

    private String coreLabelForSystem(int requestCode) {
        switch (requestCode) {
            case REQUEST_CHIP8: return "CHIP-8 interno";
            case REQUEST_SNES: return "SNES9x";
            case REQUEST_SEGA_8_16: return "Genesis Plus GX";
            case REQUEST_ARCADE: return "FBNeo / MAME 2000, 2003, 2003-Plus, 2010";
            case REQUEST_NES: return "FCEUmm";
            case REQUEST_GAMEBOY: return "Gambatte";
            case REQUEST_GBA: return "Beetle GBA";
            case REQUEST_ATARI2600: return "Stella 2014";
            case REQUEST_ATARI7800: return "ProSystem";
            case REQUEST_PCE: return "Beetle PCE Fast";
            case REQUEST_LYNX: return "Beetle Lynx";
            case REQUEST_NGP: return "Beetle NGP";
            case REQUEST_WSWAN: return "Beetle WonderSwan";
            default: return "núcleo não identificado";
        }
    }

    private void openAutoDetectedGame(File selected) throws Exception {
        String name = selected.getName().toLowerCase(java.util.Locale.ROOT);
        if (name.endsWith(".zip")) {
            java.util.ArrayList<String> entries = new java.util.ArrayList<>();
            java.util.ArrayList<Integer> systems = new java.util.ArrayList<>();
            try (java.util.zip.ZipFile zip = new java.util.zip.ZipFile(selected)) {
                java.util.Enumeration<? extends java.util.zip.ZipEntry> it = zip.entries();
                while (it.hasMoreElements()) {
                    java.util.zip.ZipEntry entry = it.nextElement();
                    if (entry.isDirectory()) continue;
                    int system = detectRomSystem(entry.getName());
                    if (system >= 0) {
                        entries.add(entry.getName());
                        systems.add(system);
                    }
                }
            }
            if (entries.size() == 1) {
                launchSelectedGame(extractZipEntry(selected, entries.get(0)), systems.get(0));
                return;
            }
            if (!entries.isEmpty()) {
                String[] labels = new String[entries.size()];
                for (int i = 0; i < labels.length; i++) labels[i] = entries.get(i) + " • " + coreLabelForSystem(systems.get(i));
                new android.app.AlertDialog.Builder(this)
                        .setTitle("Escolha a ROM e o núcleo compatível")
                        .setItems(labels, (dialog, which) -> {
                            try {
                                launchSelectedGame(extractZipEntry(selected, entries.get(which)), systems.get(which));
                            } catch (Exception error) {
                                showGameOpenError(error);
                            }
                        })
                        .setNegativeButton("Cancelar", null)
                        .show();
                return;
            }
            showAutoCoreChooser(selected, true);
            return;
        }
        int system = detectRomSystem(selected.getName());
        if (system == -2) {
            showAutoCoreChooser(selected, false);
        } else if (system >= 0) {
            launchSelectedGame(selected, system);
        } else {
            throw new IllegalArgumentException("Não reconheci o formato desta ROM. Abra a biblioteca e escolha o console/núcleo correspondente.");
        }
    }

    private void showAutoCoreChooser(File selected, boolean isZip) {
        final int[] systems = {REQUEST_ARCADE, REQUEST_SNES, REQUEST_SEGA_8_16, REQUEST_NES,
                REQUEST_GAMEBOY, REQUEST_GBA, REQUEST_ATARI2600, REQUEST_ATARI7800, REQUEST_PCE,
                REQUEST_LYNX, REQUEST_NGP, REQUEST_WSWAN};
        String[] labels = new String[systems.length];
        for (int i = 0; i < systems.length; i++) {
            String platform = systems[i] == REQUEST_ARCADE ? "Arcade" : systems[i] == REQUEST_SNES ? "Super Nintendo" :
                    systems[i] == REQUEST_SEGA_8_16 ? "Mega Drive / Master System / Game Gear" :
                    systems[i] == REQUEST_NES ? "NES / Famicom" : systems[i] == REQUEST_GAMEBOY ? "Game Boy / Color" :
                    systems[i] == REQUEST_GBA ? "Game Boy Advance" : systems[i] == REQUEST_ATARI2600 ? "Atari 2600" :
                    systems[i] == REQUEST_ATARI7800 ? "Atari 7800" : systems[i] == REQUEST_PCE ? "PC Engine" :
                    systems[i] == REQUEST_LYNX ? "Atari Lynx" : systems[i] == REQUEST_NGP ? "Neo Geo Pocket" : "WonderSwan";
            labels[i] = platform + " • " + coreLabelForSystem(systems[i]);
        }
        new android.app.AlertDialog.Builder(this)
                .setTitle(isZip ? "Escolha o sistema/núcleo para este ZIP" : "Formato .bin: escolha o sistema")
                .setItems(labels, (dialog, which) -> {
                    try {
                        openDetectedFile(selected, systems[which]);
                    } catch (Exception error) {
                        showGameOpenError(error);
                    }
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private void openDetectedFile(File selected, int requestCode) throws Exception {
        if (!selected.getName().toLowerCase(java.util.Locale.ROOT).endsWith(".zip") || requestCode == REQUEST_ARCADE) {
            launchSelectedGame(selected, requestCode);
            return;
        }
        java.util.ArrayList<String> matches = listMatchingZipEntries(selected, requestCode);
        if (matches.isEmpty()) {
            throw new IllegalArgumentException("Esse ZIP não contém um arquivo ROM compatível com " + coreLabelForSystem(requestCode) + ".");
        }
        if (matches.size() == 1) {
            launchSelectedGame(extractZipEntry(selected, matches.get(0)), requestCode);
            return;
        }
        String[] labels = new String[matches.size()];
        for (int i = 0; i < labels.length; i++) labels[i] = matches.get(i) + " • " + coreLabelForSystem(requestCode);
        new android.app.AlertDialog.Builder(this)
                .setTitle("Escolha a ROM e o núcleo")
                .setItems(labels, (dialog, which) -> {
                    try {
                        launchSelectedGame(extractZipEntry(selected, matches.get(which)), requestCode);
                    } catch (Exception error) {
                        showGameOpenError(error);
                    }
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private java.util.ArrayList<String> listMatchingZipEntries(File archive, int requestCode) throws Exception {
        String[] extensions = getRomExtensions(requestCode);
        java.util.ArrayList<String> matches = new java.util.ArrayList<>();
        try (java.util.zip.ZipFile zip = new java.util.zip.ZipFile(archive)) {
            java.util.Enumeration<? extends java.util.zip.ZipEntry> entries = zip.entries();
            while (entries.hasMoreElements()) {
                java.util.zip.ZipEntry entry = entries.nextElement();
                if (entry.isDirectory()) continue;
                String lower = entry.getName().toLowerCase(java.util.Locale.ROOT);
                for (String extension : extensions) {
                    if (lower.endsWith(extension)) {
                        matches.add(entry.getName());
                        break;
                    }
                }
            }
        }
        return matches;
    }

    private String[] getRomExtensions(int requestCode) {
        if (requestCode == REQUEST_CHIP8) return new String[]{".ch8", ".c8", ".chip8"};
        if (requestCode == REQUEST_SNES) return new String[]{".sfc", ".smc", ".fig", ".swc", ".bin"};
        if (requestCode == REQUEST_SEGA_8_16) return new String[]{".md", ".gen", ".bin", ".sms", ".gg", ".sg"};
        if (requestCode == REQUEST_ARCADE) return new String[]{".zip"};
        switch (requestCode) {
            case REQUEST_NES: return new String[]{".nes", ".unf", ".unif"};
            case REQUEST_GAMEBOY: return new String[]{".gb", ".gbc"};
            case REQUEST_GBA: return new String[]{".gba"};
            case REQUEST_ATARI2600: return new String[]{".a26", ".bin"};
            case REQUEST_ATARI7800: return new String[]{".a78", ".bin"};
            case REQUEST_PCE: return new String[]{".pce"};
            case REQUEST_LYNX: return new String[]{".lnx"};
            case REQUEST_NGP: return new String[]{".ngp", ".ngc"};
            case REQUEST_WSWAN: return new String[]{".ws", ".wsc"};
            default: return new String[0];
        }
    }

    private File extractZipEntry(File archive, String entryName) throws Exception {
        File romDir = new File(getFilesDir(), "roms");
        if (!romDir.exists() && !romDir.mkdirs()) throw new IllegalStateException("Não foi possível preparar o armazenamento do app.");
        String baseName = new java.io.File(entryName).getName().replaceAll("[^A-Za-z0-9._ -]", "_");
        File destination = new File(romDir, "zip_" + System.currentTimeMillis() + "_" + baseName);
        try (java.util.zip.ZipFile zip = new java.util.zip.ZipFile(archive)) {
            java.util.zip.ZipEntry entry = zip.getEntry(entryName);
            if (entry == null || entry.isDirectory()) throw new IllegalArgumentException("A ROM selecionada não foi encontrada dentro do ZIP.");
            try (InputStream input = zip.getInputStream(entry);
                 FileOutputStream output = new FileOutputStream(destination)) {
                byte[] buffer = new byte[64 * 1024];
                int count;
                long total = 0;
                while ((count = input.read(buffer)) != -1) {
                    total += count;
                    if (total > 64L * 1024L * 1024L) throw new IllegalArgumentException("A ROM dentro do ZIP excede 64 MB.");
                    output.write(buffer, 0, count);
                }
            }
        }
        return destination;
    }

    private void showArcadeCoreChooser(File rom) {
        String[] labels = {
                "FBNeo — arcade e Neo Geo",
                "MAME 2000 — ROMset 0.37b5",
                "MAME 2003 — ROMset 0.78",
                "MAME 2003-Plus — ROMset 0.78+",
                "MAME 2010 — ROMset 0.139"
        };
        String[] cores = {
                "libfbneo_libretro_android.so",
                "libmame2000_libretro_android.so",
                "libmame2003_libretro_android.so",
                "libmame2003_plus_libretro_android.so",
                "libmame2010_libretro_android.so"
        };
        new android.app.AlertDialog.Builder(this)
                .setTitle("Escolha o núcleo que combina com o ROMset")
                .setItems(labels, (dialog, which) -> {
                    try {
                        startRetroGame(rom, cores[which], "ARCADE • " + labels[which]);
                    } catch (Exception error) {
                        showGameOpenError(error);
                    }
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private void launchSelectedGame(File file, int requestCode) {
        try {
            if (requestCode == REQUEST_CHIP8) {
                startChip8(readChip8RomFile(file), file.getName());
            } else if (requestCode == REQUEST_ARCADE) {
                showArcadeCoreChooser(file);
            } else if (requestCode == REQUEST_SNES) {
                startRetroGame(file, "libsnes9x_libretro_android.so", "SUPER NINTENDO • SNES9x");
            } else if (requestCode == REQUEST_SEGA_8_16) {
                startRetroGame(file, "libgenesis_plus_gx_libretro_android.so", "SEGA • Mega Drive / Master System / Game Gear");
            } else if (requestCode >= REQUEST_NES && requestCode <= REQUEST_WSWAN) {
                String[] system = getAdditionalSystem(requestCode);
                startRetroGame(file, system[0], system[1]);
            } else {
                throw new IllegalArgumentException("Console não reconhecido.");
            }
        } catch (Exception error) {
            showGameOpenError(error);
        }
    }

    private byte[] readChip8RomFile(File file) throws Exception {
        try (InputStream input = new java.io.FileInputStream(file);
             java.io.ByteArrayOutputStream output = new java.io.ByteArrayOutputStream()) {
            byte[] buffer = new byte[4096];
            int count;
            while ((count = input.read(buffer)) != -1) {
                output.write(buffer, 0, count);
                if (output.size() > 3584) throw new IllegalArgumentException("A ROM CHIP-8 precisa ter no máximo 3584 bytes. Selecione o arquivo .ch8 ou .c8 extraído do ZIP.");
            }
            byte[] bytes = output.toByteArray();
            if (bytes.length == 0) throw new IllegalArgumentException("O arquivo CHIP-8 está vazio.");
            return bytes;
        }
    }

    private void showGameOpenError(Exception error) {
        showLibrary();
        new android.app.AlertDialog.Builder(this)
                .setTitle("Não consegui abrir o jogo")
                .setMessage(error.getMessage() == null ? "Confira o arquivo selecionado e tente de novo." : error.getMessage())
                .setPositiveButton("OK", null)
                .show();
    }

    private String[] getAdditionalSystem(int requestCode) {
        switch (requestCode) {
            case REQUEST_NES: return new String[]{"libfceumm_libretro_android.so", "NINTENDO • NES / Famicom"};
            case REQUEST_GAMEBOY: return new String[]{"libgambatte_libretro_android.so", "NINTENDO • Game Boy / Game Boy Color"};
            case REQUEST_GBA: return new String[]{"libmednafen_gba_libretro_android.so", "NINTENDO • Game Boy Advance (Beetle GBA)"};
            case REQUEST_ATARI2600: return new String[]{"libstella2014_libretro_android.so", "ATARI • 2600"};
            case REQUEST_ATARI7800: return new String[]{"libprosystem_libretro_android.so", "ATARI • 7800"};
            case REQUEST_PCE: return new String[]{"libmednafen_pce_fast_libretro_android.so", "PC ENGINE • TurboGrafx-16"};
            case REQUEST_LYNX: return new String[]{"libmednafen_lynx_libretro_android.so", "ATARI • Lynx"};
            case REQUEST_NGP: return new String[]{"libmednafen_ngp_libretro_android.so", "SNK • Neo Geo Pocket / Color"};
            case REQUEST_WSWAN: return new String[]{"libmednafen_wswan_libretro_android.so", "BANDAI • WonderSwan / Color"};
            default: throw new IllegalArgumentException("Sistema retrô desconhecido.");
        }
    }

    private byte[] readChip8Rom(Uri uri) throws Exception {
        try (InputStream input = getContentResolver().openInputStream(uri);
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            if (input == null) throw new IllegalArgumentException("Não consegui ler esse arquivo.");
            byte[] buffer = new byte[4096];
            int count;
            while ((count = input.read(buffer)) != -1) {
                output.write(buffer, 0, count);
                if (output.size() > 3584) throw new IllegalArgumentException("Essa ROM é maior que o limite do CHIP-8 (3584 bytes). Selecione um arquivo .ch8 ou .c8 válido.");
            }
            byte[] bytes = output.toByteArray();
            if (bytes.length == 0) throw new IllegalArgumentException("O arquivo CHIP-8 está vazio.");
            return bytes;
        }
    }

    private File copyRom(Uri uri) throws Exception {
        File romDir = new File(getFilesDir(), "roms");
        String name = displayName(uri);
        if (name == null || name.trim().isEmpty()) name = "jogo.zip";
        name = name.replaceAll("[^A-Za-z0-9._ -]", "_");
        File destination = new File(romDir, name);
        copyUri(uri, destination);
        return destination;
    }

    private String displayName(Uri uri) {
        try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (index >= 0) return cursor.getString(index);
            }
        } catch (Exception ignored) { }
        return null;
    }

    private void copyUri(Uri uri, File destination) throws Exception {
        File parent = destination.getParentFile();
        if (parent != null && !parent.exists() && !parent.mkdirs()) throw new IllegalStateException("Não foi possível preparar o armazenamento do app.");
        try (InputStream input = getContentResolver().openInputStream(uri);
             FileOutputStream output = new FileOutputStream(destination)) {
            if (input == null) throw new IllegalStateException("Não consegui ler o arquivo selecionado.");
            byte[] buffer = new byte[64 * 1024];
            int count;
            while ((count = input.read(buffer)) != -1) output.write(buffer, 0, count);
        }
    }

    private void startChip8(byte[] rom, String name) {
        chip8View = new Chip8View(this, rom);
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        root.addView(chip8View, new FrameLayout.LayoutParams(-1, -1));
        TextView back = new TextView(this);
        back.setText("‹  MENU");
        back.setTextColor(0xffd8e0e4);
        back.setTextSize(12);
        back.setPadding(dp(12), dp(7), dp(12), dp(7));
        back.setBackgroundColor(0x88000000);
        back.setOnClickListener(v -> showLibrary());
        FrameLayout.LayoutParams backParams = new FrameLayout.LayoutParams(-2, -2, Gravity.TOP | Gravity.LEFT);
        root.addView(back, backParams);
        setContentView(root);
        chip8View.resumeEmulation();
        Toast.makeText(this, "CHIP-8: " + (name == null ? "ROM carregada" : name), Toast.LENGTH_SHORT).show();
    }

    private void startRetroGame(File rom, String coreLibrary, String systemLabel) {
        File nativeCore = new File(getApplicationInfo().nativeLibraryDir, coreLibrary);
        startRetroGame(rom, nativeCore, coreLibrary, systemLabel);
    }

    private void startRetroGame(File rom, File nativeCore, String coreLibrary, String systemLabel) {
        File systemDir = new File(getFilesDir(), "system");
        File savesDir = new File(getFilesDir(), "saves");
        if (!systemDir.isDirectory() && !systemDir.mkdirs()) throw new IllegalStateException("Não foi possível preparar a pasta do sistema.");
        if (!savesDir.isDirectory() && !savesDir.mkdirs()) throw new IllegalStateException("Não foi possível preparar a pasta de salvamentos.");
        String stateBase = (coreLibrary + "_" + rom.getName()).replaceAll("[^A-Za-z0-9._-]", "_");
        if (stateBase.length() > 120) stateBase = stateBase.substring(0, 120);
        currentStateFile = new File(savesDir, stateBase + ".state");
        activeCheatCode = "";
        GLRetroViewData data = new GLRetroViewData(this);
        if (nativeCore == null || !nativeCore.isFile() || nativeCore.length() == 0) {
            throw new IllegalStateException("Arquivo do núcleo de emulação não encontrado: " + coreLibrary);
        }
        data.setCoreFilePath(nativeCore.getAbsolutePath());
        data.setGameFilePath(rom.getAbsolutePath());
        data.setSystemDirectory(systemDir.getAbsolutePath());
        data.setSavesDirectory(savesDir.getAbsolutePath());
        data.setPreferLowLatencyAudio(true);
        data.setSkipDuplicateFrames(true);

        root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        retroView = new GLRetroView(this, data);
        root.addView(retroView, new FrameLayout.LayoutParams(-1, -1));
        addTouchControls(root, systemLabel);
        setContentView(root);
        getLifecycle().addObserver(retroView);
        retroView.setFocusableInTouchMode(true);
        retroView.requestFocus();
    }

    @Override public void onBackPressed() {
        if (chip8View != null) { showLibrary(); return; }
        if (retroView != null) { returnToRomSelection(); return; }
        if (profileScreenActive) {
            if (!onboardingProfile) { restoreSavedProfile(); showLibrary(); }
            return;
        }
        super.onBackPressed();
    }

    @Override protected void onPause() {
        if (chip8View != null) chip8View.pauseEmulation();
        super.onPause();
    }

    @Override protected void onResume() {
        super.onResume();
        if (chip8View != null) chip8View.resumeEmulation();
        enterImmersiveMode();
    }

    private void addTouchControls(FrameLayout parent, String systemLabel) {
        TextView label = new TextView(this);
        label.setText("Vortix • " + systemLabel);
        label.setTextColor(0xbfffffff);
        label.setTextSize(12);
        FrameLayout.LayoutParams labelParams = new FrameLayout.LayoutParams(-2, -2, Gravity.TOP | Gravity.CENTER_HORIZONTAL);
        labelParams.topMargin = dp(6);
        parent.addView(label, labelParams);

        Button shoulderL = keyButton("L", KeyEvent.KEYCODE_BUTTON_L1, dp(52), dp(42));
        FrameLayout.LayoutParams shoulderLParams = new FrameLayout.LayoutParams(dp(52), dp(42), Gravity.TOP | Gravity.LEFT);
        shoulderLParams.leftMargin = dp(12);
        shoulderLParams.topMargin = dp(28);
        parent.addView(shoulderL, shoulderLParams);

        Button shoulderR = keyButton("R", KeyEvent.KEYCODE_BUTTON_R1, dp(52), dp(42));
        FrameLayout.LayoutParams shoulderRParams = new FrameLayout.LayoutParams(dp(52), dp(42), Gravity.TOP | Gravity.RIGHT);
        shoulderRParams.rightMargin = dp(12);
        shoulderRParams.topMargin = dp(28);
        parent.addView(shoulderR, shoulderRParams);

        Button changeRom = overlayMenuButton("ROM");
        changeRom.setOnClickListener(v -> returnToRomSelection());
        FrameLayout.LayoutParams changeRomParams = new FrameLayout.LayoutParams(dp(72), dp(36), Gravity.TOP | Gravity.LEFT);
        changeRomParams.leftMargin = dp(12);
        changeRomParams.topMargin = dp(76);
        parent.addView(changeRom, changeRomParams);

        Button options = overlayMenuButton("MENU");
        options.setOnClickListener(v -> showGameOptions());
        FrameLayout.LayoutParams optionsParams = new FrameLayout.LayoutParams(dp(72), dp(36), Gravity.TOP | Gravity.RIGHT);
        optionsParams.rightMargin = dp(12);
        optionsParams.topMargin = dp(76);
        parent.addView(options, optionsParams);

        VirtualJoystickView joystick = new VirtualJoystickView();
        FrameLayout.LayoutParams joystickParams = new FrameLayout.LayoutParams(dp(144), dp(144), Gravity.BOTTOM | Gravity.LEFT);
        joystickParams.leftMargin = dp(18); joystickParams.bottomMargin = dp(14);
        parent.addView(joystick, joystickParams);

        GridLayout action = new GridLayout(this);
        action.setColumnCount(2); action.setRowCount(2);
        addGridKey(action, "A", KeyEvent.KEYCODE_BUTTON_A, 0, 0);
        addGridKey(action, "B", KeyEvent.KEYCODE_BUTTON_B, 0, 1);
        addGridKey(action, "C", KeyEvent.KEYCODE_BUTTON_X, 1, 0);
        addGridKey(action, "D", KeyEvent.KEYCODE_BUTTON_Y, 1, 1);
        FrameLayout.LayoutParams actionParams = new FrameLayout.LayoutParams(-2, -2, Gravity.BOTTOM | Gravity.RIGHT);
        actionParams.rightMargin = dp(12); actionParams.bottomMargin = dp(10); parent.addView(action, actionParams);

        Button start = keyButton("START", KeyEvent.KEYCODE_BUTTON_START, dp(70), dp(42));
        FrameLayout.LayoutParams startParams = new FrameLayout.LayoutParams(dp(70), dp(42), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        startParams.bottomMargin = dp(12); startParams.rightMargin = dp(40); parent.addView(start, startParams);
        Button coin = keyButton("SELECT", KeyEvent.KEYCODE_BUTTON_SELECT, dp(70), dp(42));
        FrameLayout.LayoutParams coinParams = new FrameLayout.LayoutParams(dp(70), dp(42), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        coinParams.bottomMargin = dp(12); coinParams.leftMargin = dp(40); parent.addView(coin, coinParams);
    }

    private Button overlayMenuButton(String text) {
        Button button = menuButton(text);
        button.setTextSize(10);
        button.setMinHeight(dp(32));
        button.setMinWidth(0);
        button.setPadding(0, 0, 0, 0);
        return button;
    }

    private void returnToRomSelection() {
        recreate();
    }

    private void showGameOptions() {
        String[] options = {"Salvar estado", "Carregar estado", "Cheats", "Filtro de imagem", "Configurar especiais"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Opções do jogo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) saveCurrentState();
                    else if (which == 1) loadCurrentState();
                    else if (which == 2) showCheatDialog();
                    else if (which == 3) showImageFilterDialog();
                    else showSpecialConfigDialog();
                })
                .setNegativeButton("Fechar", null)
                .show();
    }

    private void saveCurrentState() {
        final GLRetroView view = retroView;
        final File target = currentStateFile;
        if (view == null || target == null) return;
        new Thread(() -> {
            try {
                byte[] state = view.serializeState(true);
                if (state == null || state.length == 0 || state.length > 128 * 1024 * 1024) {
                    throw new IllegalStateException("Estado vazio ou grande demais.");
                }
                File temporary = new File(target.getParentFile(), target.getName() + ".tmp");
                try (FileOutputStream output = new FileOutputStream(temporary)) {
                    output.write(state);
                    output.getFD().sync();
                }
                if (target.exists() && !target.delete()) throw new IllegalStateException("Não consegui substituir o save anterior.");
                if (!temporary.renameTo(target)) throw new IllegalStateException("Não consegui gravar o save.");
                runOnUiThread(() -> Toast.makeText(this, "Jogo salvo.", Toast.LENGTH_SHORT).show());
            } catch (Exception error) {
                runOnUiThread(() -> Toast.makeText(this, "Não foi possível salvar o estado.", Toast.LENGTH_LONG).show());
            }
        }, "vortix-save-state").start();
    }

    private void loadCurrentState() {
        final GLRetroView view = retroView;
        final File source = currentStateFile;
        if (view == null || source == null) return;
        if (!source.isFile()) {
            Toast.makeText(this, "Ainda não existe um save para este jogo.", Toast.LENGTH_SHORT).show();
            return;
        }
        new Thread(() -> {
            try (InputStream input = new java.io.FileInputStream(source);
                 ByteArrayOutputStream output = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[64 * 1024];
                int count;
                long total = 0;
                while ((count = input.read(buffer)) != -1) {
                    total += count;
                    if (total > 128L * 1024L * 1024L) throw new IllegalStateException("Save grande demais.");
                    output.write(buffer, 0, count);
                }
                if (!view.unserializeState(output.toByteArray(), true)) {
                    throw new IllegalStateException("O núcleo recusou o save.");
                }
                runOnUiThread(() -> Toast.makeText(this, "Save carregado.", Toast.LENGTH_SHORT).show());
            } catch (Exception error) {
                runOnUiThread(() -> Toast.makeText(this, "Não foi possível carregar o save deste jogo.", Toast.LENGTH_LONG).show());
            }
        }, "vortix-load-state").start();
    }

    private void showCheatDialog() {
        final EditText input = new EditText(this);
        input.setSingleLine(true);
        input.setHint("Código compatível com este console");
        if (!activeCheatCode.isEmpty()) input.setText(activeCheatCode);
        android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this)
                .setTitle("Cheat")
                .setMessage("O formato do código depende do núcleo e do jogo.")
                .setView(input)
                .setPositiveButton("Ativar", (dialog, which) -> {
                    String code = input.getText().toString().trim();
                    if (code.isEmpty() || retroView == null) return;
                    try {
                        retroView.setCheat(0, true, code, true);
                        activeCheatCode = code;
                        Toast.makeText(this, "Cheat ativado.", Toast.LENGTH_SHORT).show();
                    } catch (Exception error) {
                        Toast.makeText(this, "Esse código não foi aceito pelo núcleo.", Toast.LENGTH_LONG).show();
                    }
                })
                .setNegativeButton("Cancelar", null);
        if (!activeCheatCode.isEmpty()) {
            builder.setNeutralButton("Desativar", (dialog, which) -> {
                try {
                    if (retroView != null) retroView.setCheat(0, false, activeCheatCode, true);
                    activeCheatCode = "";
                    Toast.makeText(this, "Cheat desativado.", Toast.LENGTH_SHORT).show();
                } catch (Exception error) {
                    Toast.makeText(this, "Não foi possível desativar o cheat.", Toast.LENGTH_LONG).show();
                }
            });
        }
        builder.show();
    }

    private String specialMovePreferenceKey(int slot) {
        String game = currentStateFile == null ? "default" : currentStateFile.getName();
        return "special_move_" + game + "_" + slot;
    }

    private int specialSlotForKey(int keyCode) {
        if (keyCode == KeyEvent.KEYCODE_BUTTON_A) return 0;
        if (keyCode == KeyEvent.KEYCODE_BUTTON_B) return 1;
        if (keyCode == KeyEvent.KEYCODE_BUTTON_X) return 2;
        if (keyCode == KeyEvent.KEYCODE_BUTTON_Y) return 3;
        return -1;
    }

    private String specialTriggerPreferenceKey(int slot) {
        String game = currentStateFile == null ? "default" : currentStateFile.getName();
        return "special_trigger_" + game + "_" + slot;
    }

    private String specialTriggerForSlot(int slot) {
        if (slot < 0 || slot > 1) return "";
        String key = specialTriggerPreferenceKey(slot);
        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        return slot == 0 ? "A+B" : "C+D";
    }

    private int[] parseSpecialTrigger(String raw) {
        String[] parts = raw == null ? new String[0] : raw.trim().toUpperCase(java.util.Locale.ROOT).split("\\+");
        if (parts.length != 2) throw new IllegalArgumentException("O gatilho deve conter exatamente dois botões, por exemplo A+B ou C+D.");
        int first = specialKeyCode(parts[0]);
        int second = specialKeyCode(parts[1]);
        if (!isFaceButton(first) || !isFaceButton(second) || first == second)
            throw new IllegalArgumentException("Use dois botões diferentes entre A, B, C e D.");
        return new int[]{first, second};
    }

    private boolean isFaceButton(int key) {
        return key == KeyEvent.KEYCODE_BUTTON_A || key == KeyEvent.KEYCODE_BUTTON_B
                || key == KeyEvent.KEYCODE_BUTTON_X || key == KeyEvent.KEYCODE_BUTTON_Y;
    }

    private int specialMacroSlotForPair(int first, int second) {
        for (int slot = 0; slot < 2; slot++) {
            int[] pair;
            try { pair = parseSpecialTrigger(specialTriggerForSlot(slot)); }
            catch (IllegalArgumentException ignored) { continue; }
            if ((pair[0] == first && pair[1] == second) || (pair[0] == second && pair[1] == first)) return slot;
        }
        return -1;
    }

    private String specialMacroForSlot(int slot) {
        if (slot < 0 || slot > 3) return "";
        String key = specialMovePreferenceKey(slot);
        if (getPreferences(0).contains(key)) return getPreferences(0).getString(key, "").trim();
        if (slot == 0) return "A+B";
        if (slot == 1) return "C+D";
        return "";
    }

    private boolean hasSpecialMacro(int slot) {
        return !specialMacroForSlot(slot).isEmpty();
    }

    private int specialKeyCode(String token) {
        switch (token.trim().toUpperCase(java.util.Locale.ROOT)) {
            case "UP": case "CIMA": return KeyEvent.KEYCODE_DPAD_UP;
            case "DOWN": case "BAIXO": return KeyEvent.KEYCODE_DPAD_DOWN;
            case "LEFT": case "ESQUERDA": return KeyEvent.KEYCODE_DPAD_LEFT;
            case "RIGHT": case "DIREITA": return KeyEvent.KEYCODE_DPAD_RIGHT;
            case "A": return KeyEvent.KEYCODE_BUTTON_A;
            case "B": return KeyEvent.KEYCODE_BUTTON_B;
            case "C": case "X": return KeyEvent.KEYCODE_BUTTON_X;
            case "D": case "Y": return KeyEvent.KEYCODE_BUTTON_Y;
            case "L": return KeyEvent.KEYCODE_BUTTON_L1;
            case "R": return KeyEvent.KEYCODE_BUTTON_R1;
            case "START": return KeyEvent.KEYCODE_BUTTON_START;
            case "SELECT": return KeyEvent.KEYCODE_BUTTON_SELECT;
            default: return -1;
        }
    }

    private java.util.ArrayList<java.util.ArrayList<Integer>> parseSpecialSequence(String sequence) {
        java.util.ArrayList<java.util.ArrayList<Integer>> steps = new java.util.ArrayList<>();
        if (sequence == null || sequence.trim().isEmpty()) return steps;
        String[] tokens = sequence.split(",");
        if (tokens.length > 16) throw new IllegalArgumentException("Use até 16 etapas por especial.");
        for (String token : tokens) {
            String[] simultaneous = token.trim().split("\\+");
            if (simultaneous.length > 4) throw new IllegalArgumentException("Use no máximo quatro botões simultâneos por etapa.");
            java.util.ArrayList<Integer> keys = new java.util.ArrayList<>();
            for (String part : simultaneous) {
                int key = specialKeyCode(part);
                if (key < 0) throw new IllegalArgumentException("Comando inválido: " + part.trim());
                keys.add(key);
            }
            steps.add(keys);
        }
        return steps;
    }

    private void showSpecialConfigDialog() {
        android.widget.LinearLayout form = new android.widget.LinearLayout(this);
        form.setOrientation(android.widget.LinearLayout.VERTICAL);
        int padding = dp(18);
        form.setPadding(padding, dp(8), padding, dp(8));
        android.widget.TextView hint = new android.widget.TextView(this);
        hint.setText("Gatilhos simultâneos configuráveis só para este jogo: pressione os dois botões do gatilho juntos (ex.: A+B) na tela ou no controle Bluetooth. Janela de reconhecimento: 130 ms; toques/pressionamentos individuais continuam funcionando normalmente. Configure a sequência de saída abaixo: vírgula separa etapas e + aperta botões juntos (ex.: BAIXO, BAIXO+DIREITA, DIREITA, A). Deixe a sequência vazia para desativar o gatilho neste jogo.");
        hint.setTextColor(0xffc8f6ff);
        form.setBackgroundColor(0xff08131b);
        form.addView(hint, new android.widget.LinearLayout.LayoutParams(-1, -2));
        EditText[] triggers = new EditText[2];
        EditText[] sequences = new EditText[2];
        for (int i = 0; i < 2; i++) {
            android.widget.TextView triggerLabel = new android.widget.TextView(this);
            triggerLabel.setText("Gatilho simultâneo " + (i + 1) + " (dois botões)");
            triggerLabel.setTextColor(0xff00e5ff);
            android.widget.LinearLayout.LayoutParams labelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            labelParams.topMargin = dp(10);
            form.addView(triggerLabel, labelParams);
            triggers[i] = new EditText(this);
            triggers[i].setSingleLine(true);
            triggers[i].setHint(i == 0 ? "A+B" : "C+D");
            triggers[i].setHintTextColor(0xff80aeb8);
            triggers[i].setTextColor(0xffedfcff);
            triggers[i].setText(specialTriggerForSlot(i));
            GradientDrawable triggerBg = new GradientDrawable();
            triggerBg.setColor(0xff10212b); triggerBg.setCornerRadius(dp(8)); triggerBg.setStroke(dp(1), 0xff00bfd8);
            triggers[i].setBackground(triggerBg);
            form.addView(triggers[i], new android.widget.LinearLayout.LayoutParams(-1, -2));

            android.widget.TextView sequenceLabel = new android.widget.TextView(this);
            sequenceLabel.setText("Sequência de saída para " + specialTriggerForSlot(i));
            sequenceLabel.setTextColor(0xff00e5ff);
            android.widget.LinearLayout.LayoutParams sequenceLabelParams = new android.widget.LinearLayout.LayoutParams(-1, -2);
            sequenceLabelParams.topMargin = dp(6);
            form.addView(sequenceLabel, sequenceLabelParams);
            triggers[i].addTextChangedListener(new android.text.TextWatcher() {
                @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) { }
                @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                    sequenceLabel.setText("Sequência de saída para " + s.toString().trim());
                }
                @Override public void afterTextChanged(android.text.Editable editable) { }
            });
            sequences[i] = new EditText(this);
            sequences[i].setSingleLine(true);
            sequences[i].setHint("BAIXO, BAIXO+DIREITA, DIREITA, A");
            sequences[i].setHintTextColor(0xff80aeb8);
            sequences[i].setTextColor(0xffedfcff);
            sequences[i].setText(specialMacroForSlot(i));
            GradientDrawable sequenceBg = new GradientDrawable();
            sequenceBg.setColor(0xff10212b); sequenceBg.setCornerRadius(dp(8)); sequenceBg.setStroke(dp(1), 0xff00bfd8);
            sequences[i].setBackground(sequenceBg);
            form.addView(sequences[i], new android.widget.LinearLayout.LayoutParams(-1, -2));
        }
        android.widget.ScrollView scroll = new android.widget.ScrollView(this);
        scroll.addView(form);
        android.app.AlertDialog dialog = new android.app.AlertDialog.Builder(this)
                .setTitle("Configurar especiais deste jogo")
                .setView(scroll)
                .setPositiveButton("Salvar", (d, which) -> {
                    String[] triggerValues = new String[2];
                    String[] sequenceValues = new String[2];
                    try {
                        for (int i = 0; i < 2; i++) {
                            triggerValues[i] = triggers[i].getText().toString().trim().toUpperCase(java.util.Locale.ROOT);
                            parseSpecialTrigger(triggerValues[i]);
                            sequenceValues[i] = sequences[i].getText().toString().trim();
                            parseSpecialSequence(sequenceValues[i]);
                        }
                        int[] firstTrigger = parseSpecialTrigger(triggerValues[0]);
                        int[] secondTrigger = parseSpecialTrigger(triggerValues[1]);
                        if ((firstTrigger[0] == secondTrigger[0] && firstTrigger[1] == secondTrigger[1])
                                || (firstTrigger[0] == secondTrigger[1] && firstTrigger[1] == secondTrigger[0]))
                            throw new IllegalArgumentException("Escolha dois gatilhos diferentes.");
                    } catch (IllegalArgumentException error) {
                        Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
                        return;
                    }
                    android.content.SharedPreferences.Editor editor = getPreferences(0).edit();
                    for (int i = 0; i < 2; i++) {
                        editor.putString(specialTriggerPreferenceKey(i), triggerValues[i]);
                        editor.putString(specialMovePreferenceKey(i), sequenceValues[i]);
                    }
                    editor.apply();
                    Toast.makeText(this, "Gatilhos e sequências salvos para este jogo.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .create();
        dialog.show();
    }

    private void triggerSpecialMacro(int slot) {
        if (specialMacroRunning || retroView == null) return;
        String raw = specialMacroForSlot(slot);
        if (raw.trim().isEmpty()) {
            Toast.makeText(this, "Configure o especial deste botão no MENU.", Toast.LENGTH_SHORT).show();
            return;
        }
        final java.util.ArrayList<java.util.ArrayList<Integer>> sequence;
        try {
            sequence = parseSpecialSequence(raw);
        } catch (IllegalArgumentException error) {
            Toast.makeText(this, error.getMessage(), Toast.LENGTH_LONG).show();
            return;
        }
        if (sequence.isEmpty()) return;
        specialMacroRunning = true;
        playSpecialMacroStep(sequence, 0);
    }

    private static final long SPECIAL_CHORD_WINDOW_MS = 130L;
    private final java.util.HashSet<Integer> specialKeysPressed = new java.util.HashSet<>();
    private final java.util.HashSet<Integer> specialKeysConsumed = new java.util.HashSet<>();
    private final java.util.HashMap<Integer, Long> specialKeyDownTimes = new java.util.HashMap<>();
    private final java.util.HashMap<Integer, Runnable> pendingSpecialKeyDowns = new java.util.HashMap<>();
    private final java.util.HashSet<Integer> forwardedSpecialKeys = new java.util.HashSet<>();

    private boolean handleConfiguredChordKey(int keyCode, boolean down) {
        if (!isFaceButton(keyCode)) return false;
        boolean participates = false;
        for (int slot = 0; slot < 2; slot++) {
            try {
                int[] pair = parseSpecialTrigger(specialTriggerForSlot(slot));
                if (pair[0] == keyCode || pair[1] == keyCode) { participates = true; break; }
            } catch (IllegalArgumentException ignored) { }
        }
        if (!participates) return false;
        if (down) {
            if (!specialKeysPressed.add(keyCode)) return true; // Ignore hardware key-repeat events.
            long now = android.os.SystemClock.uptimeMillis();
            specialKeyDownTimes.put(keyCode, now);
            int matchedPartner = -1;
            int matchedSlot = -1;
            for (int slot = 0; slot < 2; slot++) {
                try {
                    int[] pair = parseSpecialTrigger(specialTriggerForSlot(slot));
                    int partner = pair[0] == keyCode ? pair[1] : pair[1] == keyCode ? pair[0] : -1;
                    if (partner >= 0 && specialKeysPressed.contains(partner)) {
                        Long partnerTime = specialKeyDownTimes.get(partner);
                        if (partnerTime != null && Math.abs(now - partnerTime) <= SPECIAL_CHORD_WINDOW_MS) {
                            matchedPartner = partner;
                            matchedSlot = slot;
                            break;
                        }
                    }
                } catch (IllegalArgumentException ignored) { }
            }
            if (matchedPartner >= 0) {
                for (int key : new int[]{keyCode, matchedPartner}) {
                    Runnable pending = pendingSpecialKeyDowns.remove(key);
                    if (pending != null) specialMacroHandler.removeCallbacks(pending);
                    if (forwardedSpecialKeys.remove(key) && retroView != null)
                        retroView.sendKeyEvent(KeyEvent.ACTION_UP, key, 0);
                    specialKeysConsumed.add(key);
                }
                triggerSpecialMacro(matchedSlot);
                return true;
            }
            final int pendingKey = keyCode;
            Runnable pending = () -> {
                pendingSpecialKeyDowns.remove(pendingKey);
                if (specialKeysPressed.contains(pendingKey) && !specialKeysConsumed.contains(pendingKey)
                        && retroView != null) {
                    retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, pendingKey, 0);
                    forwardedSpecialKeys.add(pendingKey);
                }
            };
            pendingSpecialKeyDowns.put(keyCode, pending);
            specialMacroHandler.postDelayed(pending, SPECIAL_CHORD_WINDOW_MS);
            return true;
        }
        specialKeysPressed.remove(keyCode);
        specialKeyDownTimes.remove(keyCode);
        if (specialKeysConsumed.remove(keyCode)) return true;
        Runnable pending = pendingSpecialKeyDowns.remove(keyCode);
        if (pending != null) specialMacroHandler.removeCallbacks(pending);
        if (retroView != null) {
            if (forwardedSpecialKeys.remove(keyCode)) {
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            } else {
                // Preserve short taps that end before the chord-recognition window.
                retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
                retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            }
        }
        return true;
    }

    private void playSpecialMacroStep(java.util.ArrayList<java.util.ArrayList<Integer>> sequence, int index) {
        if (retroView == null || index >= sequence.size()) {
            specialMacroRunning = false;
            return;
        }
        java.util.ArrayList<Integer> keys = sequence.get(index);
        for (Integer key : keys) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, key, 0);
        specialMacroHandler.postDelayed(() -> {
            if (retroView != null) {
                for (Integer key : keys) retroView.sendKeyEvent(KeyEvent.ACTION_UP, key, 0);
            }
            specialMacroHandler.postDelayed(() -> playSpecialMacroStep(sequence, index + 1), 70);
        }, 120);
    }

    private void showImageFilterDialog() {
        String[] filters = {"Padrão", "Nítido", "CRT", "LCD"};
        new android.app.AlertDialog.Builder(this)
                .setTitle("Filtro de imagem")
                .setItems(filters, (dialog, which) -> {
                    if (retroView == null) return;
                    if (which == 0) retroView.setShader(ShaderConfig.Default.INSTANCE);
                    else if (which == 1) retroView.setShader(ShaderConfig.Sharp.INSTANCE);
                    else if (which == 2) retroView.setShader(ShaderConfig.CRT.INSTANCE);
                    else retroView.setShader(ShaderConfig.LCD.INSTANCE);
                    Toast.makeText(this, "Filtro aplicado.", Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }

    private final class VirtualJoystickView extends View {
        private final android.graphics.Paint paint = new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
        private float knobX, knobY;
        private boolean up, down, left, right;
        private boolean dragging;
        private int pointerId = MotionEvent.INVALID_POINTER_ID;

        VirtualJoystickView() {
            super(MainActivity.this);
            setContentDescription("Alavanca virtual para movimentar o personagem");
            setFocusable(false);
            setLayerType(View.LAYER_TYPE_SOFTWARE, null);
        }

        @Override protected void onDraw(android.graphics.Canvas canvas) {
            super.onDraw(canvas);
            float cx = getWidth() / 2f, cy = getHeight() / 2f;
            float radius = Math.min(cx, cy) - dp(8);
            paint.setStyle(android.graphics.Paint.Style.FILL);
            paint.setColor(0xb5152630);
            canvas.drawCircle(cx, cy, radius, paint);
            paint.setStyle(android.graphics.Paint.Style.STROKE);
            paint.setStrokeWidth(dp(2));
            paint.setColor(0xff00d9ff);
            canvas.drawCircle(cx, cy, radius, paint);
            paint.setStrokeWidth(dp(1));
            paint.setColor(0x8858eaff);
            canvas.drawCircle(cx, cy, radius * 0.58f, paint);
            float drawX = dragging ? knobX : 0f;
            float drawY = dragging ? knobY : 0f;
            float knobRadius = radius * 0.34f;
            paint.setStyle(android.graphics.Paint.Style.FILL);
            paint.setColor(0xdd14536a);
            canvas.drawCircle(cx + drawX, cy + drawY, knobRadius, paint);
            paint.setStyle(android.graphics.Paint.Style.STROKE);
            paint.setStrokeWidth(dp(2));
            paint.setColor(0xff71f0ff);
            canvas.drawCircle(cx + drawX, cy + drawY, knobRadius, paint);
        }

        @Override public boolean onTouchEvent(MotionEvent event) {
            int action = event.getActionMasked();
            int index = event.getActionIndex();
            if ((action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN)
                    && pointerId == MotionEvent.INVALID_POINTER_ID) {
                pointerId = event.getPointerId(index);
                dragging = true;
                updateStick(event.getX(index), event.getY(index));
                invalidate();
                return true;
            }
            if (action == MotionEvent.ACTION_MOVE && pointerId != MotionEvent.INVALID_POINTER_ID) {
                int trackedIndex = event.findPointerIndex(pointerId);
                if (trackedIndex >= 0) updateStick(event.getX(trackedIndex), event.getY(trackedIndex));
                invalidate();
                return true;
            }
            if ((action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP)
                    && event.getPointerId(index) == pointerId) {
                releaseDirections();
                performClick();
                return true;
            }
            if (action == MotionEvent.ACTION_CANCEL) {
                releaseDirections();
                return true;
            }
            return true;
        }

        private void releaseDirections() {
            dragging = false;
            pointerId = MotionEvent.INVALID_POINTER_ID;
            knobX = knobY = 0f;
            setDirection(up, false, KeyEvent.KEYCODE_DPAD_UP);
            setDirection(down, false, KeyEvent.KEYCODE_DPAD_DOWN);
            setDirection(left, false, KeyEvent.KEYCODE_DPAD_LEFT);
            setDirection(right, false, KeyEvent.KEYCODE_DPAD_RIGHT);
            up = down = left = right = false;
            invalidate();
        }

        @Override public boolean performClick() {
            super.performClick();
            return true;
        }

        private void updateStick(float x, float y) {
            float cx = getWidth() / 2f, cy = getHeight() / 2f;
            float radius = Math.min(cx, cy) - dp(8);
            float dx = x - cx, dy = y - cy;
            float distance = (float)Math.sqrt(dx * dx + dy * dy);
            float maxTravel = radius * 0.56f;
            if (distance > maxTravel) {
                dx = dx * maxTravel / distance;
                dy = dy * maxTravel / distance;
            }
            knobX = dx; knobY = dy;
            float nx = dx / maxTravel, ny = dy / maxTravel;
            float magnitude = (float)Math.sqrt(nx * nx + ny * ny);
            boolean nextLeft = magnitude > 0.24f && nx < -0.34f;
            boolean nextRight = magnitude > 0.24f && nx > 0.34f;
            boolean nextUp = magnitude > 0.24f && ny < -0.34f;
            boolean nextDown = magnitude > 0.24f && ny > 0.34f;
            setDirection(up, nextUp, KeyEvent.KEYCODE_DPAD_UP);
            setDirection(down, nextDown, KeyEvent.KEYCODE_DPAD_DOWN);
            setDirection(left, nextLeft, KeyEvent.KEYCODE_DPAD_LEFT);
            setDirection(right, nextRight, KeyEvent.KEYCODE_DPAD_RIGHT);
            up = nextUp; down = nextDown; left = nextLeft; right = nextRight;
        }

        private void setDirection(boolean wasPressed, boolean pressed, int keyCode) {
            if (wasPressed == pressed || retroView == null) return;
            retroView.sendKeyEvent(pressed ? KeyEvent.ACTION_DOWN : KeyEvent.ACTION_UP, keyCode, 0);
        }
    }

    private void addGridKey(GridLayout grid, String text, int keyCode, int row, int column) {
        grid.addView(keyButton(text, keyCode, dp(54), dp(54)), gridParams(row, column));
    }

    private GridLayout.LayoutParams gridParams(int row, int column) {
        GridLayout.LayoutParams params = new GridLayout.LayoutParams(GridLayout.spec(row), GridLayout.spec(column));
        params.width = dp(54); params.height = dp(54); params.setMargins(dp(2), dp(2), dp(2), dp(2));
        return params;
    }

    private Button keyButton(String text, int keyCode, int width, int height) {
        Button button = new Button(this);
        button.setText(text); button.setTextColor(0xffe8fbff); button.setTextSize(text.length() > 1 ? 11 : 17);
        button.setAllCaps(false); button.setPadding(0, 0, 0, 0);
        int specialSlot = specialSlotForKey(keyCode);
        GradientDrawable background = new GradientDrawable();
        if (specialSlot >= 0) {
            int[] neon = {0xff00e5ff, 0xff00e5ff, 0xff00e5ff, 0xff00e5ff};
            background.setShape(GradientDrawable.OVAL);
            background.setColor(0xdd101820);
            background.setStroke(dp(2), neon[specialSlot]);
            button.setTextColor(neon[specialSlot]);
            button.setShadowLayer(dp(8), 0, 0, neon[specialSlot]);
        } else {
            background.setColor(0x990b1018);
            background.setCornerRadius(dp(24));
            background.setStroke(dp(1), 0xff00bfd8);
        }
        button.setBackground(background);
        button.setOnTouchListener((view, event) -> {
            if (retroView == null) return true;
            int action = event.getActionMasked();
            if (action == MotionEvent.ACTION_DOWN) {
                if (specialSlot < 0 || !handleConfiguredChordKey(keyCode, true))
                    retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
                if (specialSlot < 0 || !handleConfiguredChordKey(keyCode, false))
                    retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
                // Cancellation is treated as a proper release by the chord handler.
            }
            return true;
        });
        button.setLayoutParams(new FrameLayout.LayoutParams(width, height));
        return button;
    }

    @Override public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (retroView != null && keyCode != KeyEvent.KEYCODE_VOLUME_UP && keyCode != KeyEvent.KEYCODE_VOLUME_DOWN) {
            if (!handleConfiguredChordKey(keyCode, true)) retroView.sendKeyEvent(KeyEvent.ACTION_DOWN, keyCode, 0);
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
    @Override public boolean onKeyUp(int keyCode, KeyEvent event) {
        if (retroView != null && keyCode != KeyEvent.KEYCODE_VOLUME_UP && keyCode != KeyEvent.KEYCODE_VOLUME_DOWN) {
            if (!handleConfiguredChordKey(keyCode, false)) retroView.sendKeyEvent(KeyEvent.ACTION_UP, keyCode, 0);
            return true;
        }
        return super.onKeyUp(keyCode, event);
    }
    @Override public boolean onGenericMotionEvent(MotionEvent event) {
        if (retroView != null) {
            retroView.sendMotionEvent(GLRetroView.MOTION_SOURCE_DPAD, event.getAxisValue(MotionEvent.AXIS_HAT_X), event.getAxisValue(MotionEvent.AXIS_HAT_Y), 0);
            retroView.sendMotionEvent(GLRetroView.MOTION_SOURCE_ANALOG_LEFT, event.getAxisValue(MotionEvent.AXIS_X), event.getAxisValue(MotionEvent.AXIS_Y), 0);
            return true;
        }
        return super.onGenericMotionEvent(event);
    }

    @Override public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) enterImmersiveMode();
    }

    private void enterImmersiveMode() {
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }
    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
}
