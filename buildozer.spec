[app]
title = Albion Flip Calc
package.name = albionflip
package.domain = org.me
source.dir = .
source.include_exts = py,png,jpg,json
version = 1.0
requirements = python3,kivy==2.2.1,pyjnius @ git+https://github.com/kivy/pyjnius.git@753/head#egg=pyjnius,urllib3,openssl,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.ndk = 25b
android.ndk_path =
android.allow_backup = True
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
