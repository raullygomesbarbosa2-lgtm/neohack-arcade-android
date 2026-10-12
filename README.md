# Vortix — consoles clássicos (Android nativo)

O Vortix reúne os sistemas clássicos pedidos, sem PlayStation 1/2 ou consoles modernos. A interface é nativa do Android, com visual escuro e neon ciano; não usa WebView nem pede permissão de internet.

## Catálogo experimental ARM64 (POC intermediária)

O repositório também contém um POC técnico com 190 candidatos ARM64: 165 núcleos Libretro e 25 módulos de engine/plataforma virtual. O workflow baixa os ZIPs oficiais Android ARM64 do Libretro Buildbot e normaliza cada pacote para conter exatamente um `.so` verificado, com SHA-256 e referência/licença de `libretro-core-info`. O payload agregado dos ZIPs de origem atualmente fixados no catálogo é 728.351.579 bytes (694,61 MiB). A compilação POC produz somente APK ARM64.

Este não é o catálogo final de 200 módulos: os dez módulos customizados restantes ainda exigem trabalho e revisão separados. O POC não é liberação comercial nem parecer jurídico. Há um conflito de licença documentado para Opera; consulte [CORE-CATALOG-LICENSES.md](CORE-CATALOG-LICENSES.md). Nenhuma ROM, jogo, BIOS ou conteúdo de usuário é incluído. Nenhuma chave Pix ou e-mail Pix é publicada.

## Sistemas incluídos
- **CHIP-8:** interpretador próprio para arquivos `.ch8` e `.c8`.
- **Super Nintendo / SNES:** núcleo Snes9x.
- **Sega Mega Drive, Master System e Game Gear:** núcleo Genesis Plus GX.
- **Arcade clássico:** núcleo MAME 2003-Plus.
- **NES / Famicom:** núcleo FCEUmm.
- **Game Boy / Game Boy Color:** núcleo Gambatte.
- **Game Boy Advance:** núcleo Beetle GBA.
- **Atari 2600 e 7800:** núcleos Stella 2014 e ProSystem.
- **PC Engine / TurboGrafx-16:** núcleo Beetle PCE Fast.
- **Atari Lynx:** núcleo Beetle Lynx.
- **Neo Geo Pocket / Color:** núcleo Beetle Neo Geo Pocket.
- **WonderSwan / Color:** núcleo Beetle WonderSwan.
- **Controles na tela:** alavanca virtual para movimentar o personagem, além de botões de ação, Start e Select.

Os núcleos do conjunto original são compilados para `armeabi-v7a` e `arm64-v8a`; o APK experimental do catálogo é limitado a `arm64-v8a`. O app mantém suporte previsto a Android 5.0 (API 21) ou posterior. Os novos sistemas foram escolhidos por serem clássicos e, em geral, leves, mas compatibilidade e velocidade dependem do aparelho; esta compilação deve ser testada em um telefone físico.

## Jogos e BIOS
O app não inclui ROMs, jogos ou BIOS. Toque no console e selecione o arquivo do jogo no seletor do Android; o APK é só o instalador, não uma ROM. Use apenas arquivos que você tenha direito de utilizar.

## Perfil e privacidade
- Perfil local com nome, avatares e foto escolhida na galeria; não há senha nem conta remota.
- O manifesto principal não solicita acesso à internet.
- Os avisos de licença dos núcleos usados são incluídos no APK.

## Compilação
A compilação nativa usa Android SDK 35, Java 17, Gradle 8.7 e NDK 27.2.12479018. O workflow do GitHub compila os núcleos Libretro para Android, incluindo Snes9x, Genesis Plus GX, MAME 2003-Plus e os nove sistemas retrô adicionais.
