[app]

# Title of your application
title = Trading AI Bot

# Package name (for APK)
package.name = tradingbot

# Python version
python_version = 3.11

# Python requirements (comma separated)
requirements = kivy,requests,pillow,matplotlib,kivy-garden

# App orientation (portrait or landscape)
orientation = portrait

# Icon and presplash (paths)
# icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,CHANGE_NETWORK_STATE

# Features
android.features = android.hardware.internet

# Gradle dependencies
android.gradle_dependencies = 

# Java classes (for native modules)
android.add_src = 

# Meta-data
android.meta_data = 

# Arch (armeabi-v7a, arm64-v8a, x86, x86_64)
android.archs = arm64-v8a,armeabi-v7a

# Minimum SDK version
android.minapi = 21

# Target SDK version
android.targetapi = 33

# Bootstrap
p4a.bootstrap = sdl2

# Enable logcat
log_level = 2

# Source directory
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Display warnings
warn_on_root = 1

# Android specific
android.sdk = /path/to/android-sdk
android.ndk = /path/to/android-ndk
android.accept_sdk_license = True
