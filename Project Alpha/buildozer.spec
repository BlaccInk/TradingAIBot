[app]

# (str) Title of your application
title = TradingAIBot

# (str) Package name
package.name = tradingaibot

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (source.dir) Source code directory (where your main.py is)
source.dir = .

# (list) Source files to include (let empty to include all the .py files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,requests

# (str) Supported orientation (landscape, sensorLandscape, portrait or sensorPortrait)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash of the application (image or drawable resource)
#presplash.filename = %(source.dir)s/data/presplash.png

# (string) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 30

# (str) Android NDK version to use
#android.ndk = 23b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android app theme, default is ok for Kivy-based app
# android.theme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) enables Android auto backup & restore. Possible values are True or False
android.allow_backup = True

# (str) XML file for custom backup agent
# android.backup_agent = 

# (str) The Java package name of the backup agent. Only used if android.backup_agent is set.
# android.backup_agent_package = 

# (list) Lists of Java files to add to the build
#android.add_src =

# (list) Gradle dependencies
#android.gradle_dependencies =

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled.
#android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file for custom backup agent
#android.backup_agent = 

# (str) The Java package name of the backup agent. Only used if android.backup_agent is set.
#android.backup_agent_package = 

# (list) Lists of Java files to add to the build
#android.add_src =

# (str) Presplash of the application (image or drawable resource)
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning ; 1 = warn, 0 = info
warn_on_root = 1

# (str) Path to build directory where the built files are stored
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .buildozer/android/platform/build-<arch>/<app>)
# bin_dir = ./bin

