# RTP Play Kodi video addon

[Português](#português) · [English](#english)

## Português

Veja a [RTP Play](https://www.rtp.pt/play) no Kodi: TV e rádio em direto, o
catálogo a pedido e, com uma conta RTP, os seus favoritos e o Continuar a ver.

Aviso: Este addon não é oficial nem é apoiado pela RTP. A RTP pode alterar o
seu site a qualquer momento, o que pode fazer com que o addon deixe de
funcionar.

### Funcionalidades

- TV em direto (RTP1, RTP2, RTP Notícias, RTP Memória, RTP Internacional, ...)
  e rádio em direto (Antena 1, 2, 3, ...)
- Programas por categoria, com todos os episódios
- Pesquisa
- Início de sessão opcional na conta RTP, para **Os seus favoritos** e
  **Continuar a ver**, sincronizados com o site e as aplicações RTP Play

### Requisitos

- Kodi 19 (Matrix) ou posterior. Testado no Kodi 21 (Omega) e 22 (Piers).
- [inputstream.adaptive](https://github.com/xbmc/inputstream.adaptive), para a
  RTP2 em direto e a maior parte da TV a pedido, que estão protegidas com DRM
  Widevine. Muitas versões do Kodi já o incluem; no Debian e no Ubuntu,
  instale o pacote `kodi-inputstream-adaptive`.
- O próprio Widevine é instalado pelo addon da primeira vez que reproduz um
  conteúdo protegido (através do
  [InputStream Helper](https://github.com/emilsvennesson/script.module.inputstreamhelper)).
  Basta aceitar quando for perguntado.

Os conteúdos têm restrições geográficas da RTP, e alguns programas só estão
disponíveis em Portugal.

### Instalação

#### A partir do repositório do Kodi

A RTP Play está no repositório oficial de addons do Kodi. No Kodi, vá a
**Add-ons → Instalar a partir do repositório → Kodi Add-on repository →
Add-ons de vídeo → RTP Play** e selecione **Instalar**. As dependências são
instaladas automaticamente.

As novas versões só chegam ao repositório depois de revistas, por isso as
alterações mais recentes podem estar disponíveis apenas através de um ficheiro
zip.

#### A partir de um ficheiro zip

1. Crie o zip a partir de um clone deste repositório. A pasta dentro do zip
   tem de se chamar `plugin.video.rtpplay`, por isso use `git archive` em vez
   da opção *Download ZIP* do GitHub:

   ```sh
   git archive --prefix=plugin.video.rtpplay/ -o plugin.video.rtpplay.zip HEAD
   ```

2. Copie o zip para o dispositivo onde corre o Kodi, por exemplo através de
   uma partilha de rede ou de uma pen USB.
3. No Kodi, ative **Definições → Sistema → Add-ons → Fontes desconhecidas**.
4. Vá a **Add-ons → Instalar a partir de ficheiro zip** e escolha
   `plugin.video.rtpplay.zip`. O Kodi instala as dependências a partir do seu
   repositório oficial.

#### Para desenvolvimento

Ligue um clone diretamente à pasta de addons do Kodi, para que as alterações
tenham efeito da próxima vez que o addon for executado:

```sh
ln -s "$PWD" ~/.kodi/addons/plugin.video.rtpplay
```

Reinicie o Kodi para ele detetar um addon novo, ou alterações ao `addon.xml`,
ao `settings.xml` e às traduções. O Kodi regista como desativados os addons
copiados manualmente, por isso ative-o em **Add-ons → Os meus add-ons →
Add-ons de vídeo**. As dependências (`script.module.routing`,
`script.module.requests` e `script.module.inputstreamhelper`) também têm de
estar instaladas, por exemplo instalando o addon uma vez a partir de um zip.

### Iniciar sessão na sua conta RTP

Iniciar sessão é opcional. Sem sessão iniciada, funciona tudo exceto os
favoritos e o Continuar a ver.

1. Abra a RTP Play e selecione **Iniciar sessão na sua conta RTP**. Esta opção
   também está nas definições do addon, em **Conta**.
2. O Kodi mostra um endereço e um código. No telemóvel ou no computador, abra
   o endereço, inicie sessão na sua conta RTP (ou crie uma) e introduza o
   código.
3. O Kodi inicia sessão automaticamente assim que aprovar, e **Os seus
   favoritos** e **Continuar a ver** aparecem no menu principal.

A sua palavra-passe só é introduzida na própria página de início de sessão da
RTP. O Kodi guarda apenas os tokens de sessão e renova-os para que a sessão se
mantenha. Para terminar a sessão, use **Terminar sessão** nas definições do
addon.

Com a sessão iniciada:

- Adicione ou remova um programa dos favoritos através do respetivo menu de
  contexto.
- Os episódios que viu em parte permitem retomar onde parou, e o seu progresso
  é guardado na conta enquanto vê.

## English

Watch [RTP Play](https://www.rtp.pt/play) in Kodi: live TV and radio, the
on-demand catalogue, and, with an RTP account, your favourites and continue
watching.

Disclaimer: This plugin is not official and is not endorsed by RTP. RTP can
change its website at any time, which may break the add-on.

### Features

- Live TV (RTP1, RTP2, RTP Notícias, RTP Memória, RTP Internacional, ...) and
  live radio (Antena 1, 2, 3, ...)
- Programs by category, with all their episodes
- Search
- Optional RTP account login, for **Os seus favoritos** and **Continuar a ver**,
  kept in sync with the RTP Play website and apps

### Requirements

- Kodi 19 (Matrix) or later. Tested on Kodi 21 (Omega) and 22 (Piers).
- [inputstream.adaptive](https://github.com/xbmc/inputstream.adaptive), for
  RTP2 live and most on-demand TV. These are protected with Widevine DRM.
  Many Kodi builds already include it; on Debian and Ubuntu install the
  `kodi-inputstream-adaptive` package.
- Widevine itself is installed by the add-on the first time you play a
  protected stream (through
  [InputStream Helper](https://github.com/emilsvennesson/script.module.inputstreamhelper)).
  Just accept the prompt.

Content is geo-restricted by RTP, and some programs are only available in
Portugal.

### Installation

#### From the Kodi repository

RTP Play is in the official Kodi add-on repository. In Kodi go to
**Add-ons → Install from repository → Kodi Add-on repository → Video add-ons →
RTP Play**, then select **Install**. Dependencies are installed automatically.

New versions reach the repository after they have been reviewed, so the
latest changes may only be available by installing from a zip.

#### From a zip file

1. Build the zip from a clone of this repository. The folder inside the zip
   must be called `plugin.video.rtpplay`, so use `git archive` rather than
   GitHub's *Download ZIP*:

   ```sh
   git archive --prefix=plugin.video.rtpplay/ -o plugin.video.rtpplay.zip HEAD
   ```

2. Copy the zip to the device running Kodi, for example over a network share
   or a USB stick.
3. In Kodi, enable **Settings → System → Add-ons → Unknown sources**.
4. Go to **Add-ons → Install from zip file** and choose
   `plugin.video.rtpplay.zip`. Kodi installs the dependencies from its
   official repository.

#### For development

Link a clone straight into Kodi's add-on folder, so changes take effect the
next time the add-on runs:

```sh
ln -s "$PWD" ~/.kodi/addons/plugin.video.rtpplay
```

Restart Kodi to pick up a new add-on, or changes to `addon.xml`,
`settings.xml` and the translations. Kodi registers add-ons copied in by hand
as disabled, so enable it under **Add-ons → My add-ons → Video add-ons**. Its
dependencies (`script.module.routing`, `script.module.requests` and
`script.module.inputstreamhelper`) must be installed too, for example by
installing the add-on once from a zip.

### Logging in to your RTP account

Logging in is optional. Without it, everything except favourites and continue
watching works.

1. Open RTP Play and select **Log in to your RTP account**. This is also under
   the add-on's settings, in **Account**.
2. Kodi shows a web address and a code. On your phone or computer, open the
   address, sign in to your RTP account (or create one) and enter the code.
3. Kodi logs in automatically once you approve, and **Os seus favoritos** and
   **Continuar a ver** appear in the main menu.

Your password is only typed on RTP's own login page. Kodi stores just the
login tokens, and renews them so you stay logged in. To log out, use
**Log out** in the add-on's settings.

Once logged in:

- Add or remove a program from your favourites through its context menu.
- Episodes you have partly watched offer to resume where you left off, and
  your progress is saved to your account as you watch.
