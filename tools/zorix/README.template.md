# Zorix Engine

Zorix Engine is a customized Android-focused editor distribution based on Godot Engine 4.7.2-stable.

## Highlights

- Zorix branding throughout visible editor surfaces
- Blue/cyan/teal visual system
- Touch-friendly spacing, rounded controls, larger Android editor toolbar targets
- Android editor application ID: `com.zorix.engine.editor.v4`
- Zorix launcher, splash, and engine icons generated from `tools/zorix/zorix.svg`
- Reproducible branding via `tools/zorix/apply_branding.py`

## Build Android editor APK

```bash
python -m pip install scons==4.10.1 cairosvg pillow
python tools/zorix/apply_branding.py
python misc/scripts/install_swappy_android.py
scons platform=android target=editor arch=arm64 production=yes dev_mode=yes module_text_server_fb_enabled=yes swappy=yes
cd platform/android/java
./gradlew generateGodotEditor
```

APK output is written under `bin/android_editor_builds/`.

## License

This repository is based on Godot Engine and retains Godot's MIT license, upstream copyrights, AUTHORS, and third-party notices. Zorix branding does not remove or replace those notices.
