[app]

title = MyVPN
package.name = myvpn
package.domain = com.sokc1991

source.dir = src
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy==2.3.0,android,pyjnius

orientation = portrait
fullscreen = 0

# Android SDK/NDK настройки (стабильные)
android.accept_sdk_license = True
android.ndk = 25b
android.sdk = 33
android.api = 33
android.minapi = 21

# Разрешения
android.permissions = INTERNET, ACCESS_NETWORK_STATE, FOREGROUND_SERVICE, POST_NOTIFICATIONS

# Для уведомлений
android.no_stop_service = True
android.archs = arm64-v8a
p4a.branch = master

[buildozer]

log_level = 2
warn_on_root = 1
