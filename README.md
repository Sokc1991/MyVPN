<div align="center">
  <p>
    <a href="#"><img src="./assets/ico.png" height="150px" alt="logo" /></a>
  </p>
</div>


# NoDPI4Android
*Say NO to blocking!*

[![Visitors](https://visitor-badge.laobi.icu/badge?page_id=GVCoder09.NoDPI4Android)]()

> [!IMPORTANT]
> **Do not confuse with https://github.com/raspabamos/nodpi !**

## Description / Описание
NoDPI4Android is a graphical add-on [NoDPI](https://github.com/GVCoder09/NoDPI). This application is designed to run on Android devices only, Windows and Linux version available [here](https://github.com/GVCoder09/NoDPI/releases)

NoDPI is a utility for bypassing the DPI (Deep Packet Inspection) system. DPI is widely used by Internet providers and government agencies to block access to Internet resources. This utility allows you to bypass such blocking and freely use the Internet. In particular, it allows you to eliminate the blocking of YouTube in Russia.

Unfortunately, I cannot guarantee the absolute functionality of the program in all conditions and with all providers, but in most cases it copes with its task perfectly.
The utility works on the principle of an HTTP proxy. It analyzes all TLS handshakes passing through it and fragments them if they are addressed to blocked domains. Currently, DPI does not have the capacity to collect these fragments and analyze them, so NoDPI manages to "fool" it.

All code is written entirely in Python and uses libraries such as Kivy and KivyMD

<hr>

NoDPI4Android — это графическая надстройка над [NoDPI](https://github.com/GVCoder09/NoDPI). Это приложение предназначено для работы только на устройствах Android, версии для Windows и Linux доступны [здесь](https://github.com/GVCoder09/NoDPI/releases)

NoDPI - это утилита для обхода системы DPI (Deep Packet Inspection). DPI широко используется интерент-провайдерами и гос. органами для блокировки доступа к интерент-ресурсам. Данная утилита позволяет обходить такие блокировки и свободно пользоваться Интернетом. В частности, она позволяет устранить блокировку YouTube в России.

К сожалению, я не могу гарантировать абсолютную работоспособность программы во всех условиях и у всех провайдеров, но в большинстве случаев она отлично справляется со своей задачей.

Утилита работает по принципу HTTP прокси. Она анализирует все  проходящие через нее TLS handshake и фрагментирует их, если они адресованы заблокированным доменам. В настоящее время у DPI нет таких мощностей, чтобы собиртаь эти фрагменты и анализировать их, поэтому NoDPI получается ее "обмануть".

Весь код написан полностью на Python и использует такие библиотеки, как Kivy и KivyMD.

<div align="center">
  <p>
    <img src="./assets/screenshot.png" height="600px"/>
  </p>
</div>

### System requirements / Системные требования
The application requires Android 5.0 and above.
The application also uses permission to send notifications. For the correct operation of the proxy service, it is recommended to disable energy consumption optimization in the application's system settings

<hr/>

Для работы приложения требуется Андроид 5.0 и выше.
Также приложение использует разрешение на отправку уведомлений. Для корректной работы сервиса прокси рекомендуется отключить оптимизацию энергопотребления в системных настройках приложения

### Alternatives / Альтернативы

#### Android
- **[DPI Tunnel for Android](https://github.com/nomoresat/DPITunnel-android)** by @zhenyolka (for Android)
- **[PowerTunnel for Android](https://github.com/krlvm/PowerTunnel-Android)** by @krlvm (for Android)
- **[ByeDPIAndroid](https://github.com/dovecoteescapee/ByeDPIAndroid/)** for Android

#### Other platforms
- **[NoDPI](https://github.com/GVCoder09/GoodbyeDPI)** by @GVCoder09 (for Windows and Linux)
- **[GoodbyeDPI](https://github.com/ValdikSS/GoodbyeDPI)** by @ValdikSS (for Windows)
- **[zapret](https://github.com/bol-van/zapret)** by @bol-van (for MacOS, Linux and Windows)
- **[Green Tunnel](https://github.com/SadeghHayeri/GreenTunnel)** by @SadeghHayeri (for MacOS, Linux and Windows)
- **[DPI Tunnel CLI](https://github.com/nomoresat/DPITunnel-cli)** by @zhenyolka (for Linux and routers)
- **[PowerTunnel](https://github.com/krlvm/PowerTunnel)** by @krlvm (for Windows, MacOS and Linux)
- **[SpoofDPI](https://github.com/xvzc/SpoofDPI)** by @xvzc (for macOS and Linux)
- **[GhosTCP](https://github.com/macronut/ghostcp)** by @macronut (for Windows)
- **[ByeDPI](https://github.com/hufrea/byedpi)** for Linux/Windows
- **[youtubeUnblock](https://github.com/Waujito/youtubeUnblock/)** by @Waujito (for OpenWRT/Entware routers and Linux)

## Terms of Use and Disclaimer / Условия использования и отказ от ответственности
> [!IMPORTANT]
> This provision is in addition to the license and takes precedence over it.

The developer and/or supplier of this software shall not be liable for any loss or damage, including but not limited to direct, indirect, incidental, punitive or consequential damages arising out of the use of or inability to use this software, even if the developer or supplier has been advised of the possibility of such damages.

The developer and/or supplier of this software shall not be liable for any legal consequences arising out of the use of this software. This includes, but is not limited to, violation of laws, rules or regulations, as well as any claims or suits arising out of the use of this software. The user is solely responsible for compliance with all applicable laws and regulations when using this software.

The developer and/or supplier of this software shall not be liable for any loss or damage arising out of the unauthorized use of this software. Unauthorized use includes, but is not limited to, using the software for illegal purposes, infringing copyrights, patents, trademarks or other intellectual property rights, or using the software in violation of the license terms of the software.

This software may not be used for illegal or unlawful purposes. Any use of the software for illegal activities, including but not limited to fraud, hacking, privacy violation, distribution of malware or any other actions contrary to the code and regulations is strictly prohibited. The user is fully responsible for any legal consequences arising from the use of this software for illegal purposes.

Your use of this software constitutes your agreement to the terms of this disclaimer. If you do not agree to these terms, you must stop using this software immediately.

<hr>

> [!IMPORTANT]
> Данное положение является дополнением к лицензии и является приоритетным по отношению к ней.

Разработчик и/или поставщик данного программного обеспечения не несет никакой ответственности за любые убытки или ущерб, включая, но не ограничиваясь, прямые, косвенные, случайные, штрафные или косвенные убытки, возникшие в результате использования или невозможности использования данного программного обеспечения, даже если разработчик или поставщик были уведомлены о возможности таких убытков.

Разработчик и/или поставщик данного программного обеспечения не несут ответственности за любые юридические последствия, возникшие в результате использования данного программного обеспечения. Это включает, но не ограничивается, нарушение законодательства, правил или нормативных актов, а также любые претензии или иски, возникшие в результате использования данного программного обеспечения. Пользователь несет полную ответственность за соблюдение всех применимых законов и нормативных актов при использовании данного программного обеспечения.

Разработчик и/или поставщик данного программного обеспечения не несут ответственности за любые убытки или ущерб, возникшие в результате неправомерного использования данного программного обеспечения. Неправомерное использование включает, но не ограничивается, использование программного обеспечения для незаконных целей, нарушение авторских прав, патентных прав, торговых марок или других прав интеллектуальной собственности, а также использование программного обеспечения в нарушение условий лицензии данного программного обеспечения.

Данное программное обеспечение не может использоваться в противоправных целях или целях, нарушающих законодательство. Любое использование программного обеспечения для незаконных действий, включая, но не ограничиваясь, мошенничество, взлом, нарушение конфиденциальности, распространение вредоносного ПО или любые другие действия, противоречащие закодательству и нормативным актам, строго запрещено. Пользователь несет полную ответственность за любые юридические последствия, возникшие в результате использования данного программного обеспечения в противоправных целях.

Использование данного программного обеспечения означает ваше согласие с условиями данного отказа от ответственности. Если вы не согласны с этими условиями, вы должны немедленно прекратить использование данного программного обеспечения.

## Quick start / Быстрый старт
1) Download the latest version from [the Releases page](https://github.com/GVCoder09/NoDPI4Android/releases) and install it
2) Start server in the app
3) In the Settings of Android set the proxy to 0.0.0.0:8881
4) Enjoy!

Please report any problems and malfunctions to us on [the Issues page](https://github.com/GVCoder09/NoDPI4Android/issues)

<hr>

1) [Скачайте](https://github.com/GVCoder09/NoDPI4Android/releases) последнюю версию утилиты и установите ее
2) Запустите прокси, нажав кнопку **START SERVER** в приложении
3) В настройках Android настройте прокси на 0.0.0.0:8881
5) Наслаждайтесь!

О всех проблемах и неполадках, пожалуйста, сообщайте нам в [Issues](https://github.com/GVCoder09/NoDPI4Android/issues)


## Building apk from source code / Сборка apk из исходного кода

> [!WARNING]
> You can only perform the building in Linux!

1) Make sure you have Python 3.9 or higher installed.
2) Run the commands
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade Cython==0.29.33 virtualenv  # the --user should be removed if you do this in a venv

# add the following line at the end of your ~/.bashrc file
export PATH=$PATH:~/.local/bin/
```
3) Go to the main directory and run the building with the command
```bash
buildozer android debug
```
3) Ready! You can connect the device via adb and deploy the application:
```bash
buildozer android deploy run
```

For more information, see [here](https://habr.com/ru/articles/479236/) or [the documentation page](https://buildozer.readthedocs.io/en/latest/installation.html)

<hr>

> [!WARNING]
> Вы можете выполнить сборку только в  Linux!

1) Убедитесь что у вас установлен Python версии 3.9 и выше.
2) Выполните команды
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade Cython==0.29.33 virtualenv  # the --user should be removed if you do this in a venv

# add the following line at the end of your ~/.bashrc file
export PATH=$PATH:~/.local/bin/
```
3) Перейдите в основной каталог и запустите сборку командой
```bash
buildozer android debug
```
3) Готово! Вы можете подключить свое устройство через adb и развернуть на нем приложение:
```bash
buildozer android deploy run
```

За дополнительной информацией обращайтесь [сюда](https://habr.com/ru/articles/479236/) или на [страницу официальной документации](https://buildozer.readthedocs.io/en/latest/installation.html)

## Known bugs / Известные проблемы

- Doesn't work at all. Yes, that can happen :(
- Doesn't bypass IP block
- Only TCP and HTTPS (HTTP ignored)
- Not working with sites with old TLS
- In some Android shells the service may die

<hr>

- Не работает вообще. Да, такое может быть :(
- Не работает, если сайт заблокирован по IP
- Только для TCP и HTTPS (HTTP игнорируется)
- Не работает для сайтов со старым TLS
- В некоторых Android оболочках сервис может умирать

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=GVCoder09/NoDPI4Android&type=Date)](https://www.star-history.com/#GVCoder09/NoDPI4Android&Date)

## Thanks to the project participants / Благодарность участникам проекта

[![Contributors](https://contrib.rocks/image?repo=GVCoder09/NoDPI4Android)](https://github.com/GVCoder09/NoDPI4Android/graphs/contributors)


