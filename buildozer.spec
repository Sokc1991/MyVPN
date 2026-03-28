[app]

title = MyVPN
package.name = myvpn
package.domain = com.sokc1991

source.dir = src
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy==2.1.0,kivymd==1.1.1

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True
android.ndk = 23b
android.sdk = 30
android.minapi = 21
android.api = 30
android.permissions = INTERNET

android.archs = arm64-v8a

[buildozer]

log_level = 2
warn_on_root = 1
