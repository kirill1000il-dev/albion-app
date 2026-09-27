[app]
title = Albion Flip Calc
package.name = albionflip
package.domain = org.me
source.dir = .
source.include_exts = py,png,jpg,json
version = 1.0
requirements = python3,kivy,urllib3,openssl,requests
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
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
