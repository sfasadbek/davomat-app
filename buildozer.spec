[app]
title = STATS MB
package.name = statsmb
package.domain = org.stats
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Kerakli kutubxonalar
requirements = python3,kivy==2.2.1,requests,urllib3,chardet,idna,openssl

orientation = portrait
fullscreen = 0

# Ruxsatnomalar (Fayl saqlash va Internet)
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE

# Arxitektura va API versiyalari
android.archs = arm64-v8a, armeabi-v7a
android.api = 31
android.minapi = 21
android.sdk = 33
android.ndk = 23b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
