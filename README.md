# NexoEmu — consoles clássicos (Android nativo)

O NexoEmu reúne os sistemas clássicos pedidos, sem PlayStation 1/2 ou consoles modernos. A interface é nativa do Android, com visual escuro e neon ciano; não usa WebView nem pede permissão de internet.

## Sistemas incluídos
- **CHIP-8:** interpretador próprio para arquivos `.ch8` e `.c8`.
- **Super Nintendo / SNES:** núcleo Snes9x.
- **Sega Mega Drive, Master System e Game Gear:** núcleo Genesis Plus GX.
- **Arcade clássico:** núcleo MAME 2003-Plus.
- **Controles na tela:** alavanca virtual para movimentar o personagem, além de botões de ação, Start e Select.

Os núcleos libretro são compilados para `armeabi-v7a` e `arm64-v8a`. O app mantém suporte previsto a Android 5.0 (API 21) ou posterior. Compatibilidade e velocidade dependem do aparelho; esta compilação deve ser testada em um telefone físico.

## Jogos e BIOS
O APK não inclui ROMs, jogos ou BIOS. Escolha seus próprios arquivos no seletor do Android e use apenas arquivos que você tenha direito de utilizar.

## Perfil e privacidade
- Perfil local com nome, avatares e foto escolhida na galeria; não há senha nem conta remota.
- O manifesto principal não solicita acesso à internet.
- Os avisos de licença dos núcleos usados são incluídos no APK.

## Compilação
A compilação nativa usa Android SDK 35, Java 17, Gradle 8.7 e NDK 27.2.12479018. O workflow do GitHub compila Snes9x, Genesis Plus GX e MAME 2003-Plus para Android.
