[app]

source.dir = ./src
source.include_exts = py,png,jpg,kv,txt
version = 1.0
requirements = kivy,https://github.com/kivymd/kivymd/archive/master.zip,android,pyjnius,materialyoucolor,pillow,asynckivy,asyncgui

presplash.filename = ./assets/presplash.png
icon.filename = ./assets/ico.png
orientation = portrait
fullscreen = 0

[android]

title = NoDPI
package.name = nodpi
package.domain = com.gvcoder

services = Proxy:%(source.dir)s/service.py:foreground:sticky
android.permissions = INTERNET,FOREGROUND_SERVICE,POST_NOTIFICATIONS
android.accept_sdk_license = True

[buildozer]

log_level = 1