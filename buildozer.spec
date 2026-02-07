[app]
title = STATS MB
package.name = statsmb
package.domain = org.stats
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# sqlite3 standart kutubxona bo'lgani uchun requirementsga yozish shart emas, 
# lekin openssl qo'shish xavfsiz ulanish (https) uchun muhim
requirements = python3,kivy==2.2.1,requests,urllib3,chardet,idna,openssl

orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0

# RUXSATNOMALAR SHU YERDA TO'G'RILANDI:
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE

android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.api = 31
android.minapi = 21
android.sdk = 33
android.ndk = 23b
android.skip_update = False
android.accept_sdk_license = True

# Fayllarni tashqi xotiraga yozish uchun (Android 10+)
android.entrypoint = main.py
android.manifest.xml_api_level = 31

[buildozer]
log_level = 2
warn_on_root = 1
