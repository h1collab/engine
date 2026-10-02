#!/usr/bin/env python3
from pathlib import Path
import io
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SVG = ROOT / "tools/zorix/zorix.svg"

def replace(path, old, new, required=True):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if old not in text:
        if required:
            raise RuntimeError(f"Expected text not found in {path}: {old[:80]!r}")
        return False
    p.write_text(text.replace(old, new), encoding="utf-8")
    return True

def replace_regex(path, pattern, repl, required=True):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    new, n = re.subn(pattern, repl, text, flags=re.MULTILINE)
    if required and n == 0:
        raise RuntimeError(f"Pattern not found in {path}: {pattern}")
    p.write_text(new, encoding="utf-8")
    return n

def brand_text():
    replace("version.py", 'short_name = "godot"', 'short_name = "zorix"')
    replace("version.py", 'name = "Godot Engine"', 'name = "Zorix Engine"')
    replace("version.py", 'website = "https://godotengine.org"', 'website = "https://github.com/h1collab/engine"')

    # Android identity: retain upstream namespaces/classes for compatibility,
    # but use a distinct installable application ID and visible product name.
    replace("platform/android/java/editor/build.gradle",
            'applicationId "org.godotengine.editor.v4"',
            'applicationId "com.zorix.engine.editor.v4"')
    replace("platform/android/java/editor/build.gradle",
            'editorAppName: "Godot Engine 4"',
            'editorAppName: "Zorix Engine 4"')
    replace("platform/android/java/editor/src/main/res/values/strings.xml",
            "Godot Play window", "Zorix Play window")

    # User-facing phrases only; do not rename API classes/namespaces.
    for base in [ROOT / "editor", ROOT / "platform/android/java/editor", ROOT / "main"]:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".cpp", ".h", ".kt", ".java", ".xml", ".gradle"}:
                try:
                    t = p.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                nt = t.replace("Godot Engine", "Zorix Engine")
                nt = nt.replace("Godot Project Manager", "Zorix Project Manager")
                if nt != t:
                    p.write_text(nt, encoding="utf-8")

def brand_theme():
    p = "editor/settings/editor_settings.cpp"
    replace(p,
            'EDITOR_SETTING_BASIC(Variant::STRING, PROPERTY_HINT_ENUM, "interface/theme/spacing_preset", "Default", "Compact,Default,Spacious,Custom")',
            'EDITOR_SETTING_BASIC(Variant::STRING, PROPERTY_HINT_ENUM, "interface/theme/spacing_preset", "Spacious", "Compact,Default,Spacious,Custom")')
    replace(p,
            'EDITOR_SETTING_BASIC(Variant::COLOR, PROPERTY_HINT_NONE, "interface/theme/base_color", Color(0.14, 0.14, 0.14), "")',
            'EDITOR_SETTING_BASIC(Variant::COLOR, PROPERTY_HINT_NONE, "interface/theme/base_color", Color(0.075, 0.094, 0.133), "")')
    replace(p,
            'EDITOR_SETTING_BASIC(Variant::COLOR, PROPERTY_HINT_NONE, "interface/theme/accent_color", Color(0.34, 0.62, 1.0), "")',
            'EDITOR_SETTING_BASIC(Variant::COLOR, PROPERTY_HINT_NONE, "interface/theme/accent_color", Color(0.055, 0.647, 0.914), "")')
    replace(p,
            'EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/corner_radius", 4, "0,6,1")',
            'EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/corner_radius", 6, "0,6,1")')
    replace(p,
            'EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/base_spacing", 4, "0,8,1")',
            'EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/base_spacing", 5, "0,8,1")')
    replace(p,
            'EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/additional_spacing", 0, "0,8,1")',
            'EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/additional_spacing", 1, "0,8,1")')

    p = "editor/themes/editor_theme_manager.cpp"
    replace(p,
            'preset_accent_color = Color(0.337, 0.62, 1.0);\n\t\t\t\tpreset_base_color = Color(0.161, 0.161, 0.161);',
            'preset_accent_color = Color(0.055, 0.647, 0.914);\n\t\t\t\tpreset_base_color = Color(0.075, 0.094, 0.133);')

    p = "editor/themes/editor_theme_manager.h"
    replace(p, "Size2 dialogs_buttons_min_size = Size2(105, 34);",
            "Size2 dialogs_buttons_min_size = Size2(118, 42);")
    replace(p, "int inspector_property_height = 28;",
            "int inspector_property_height = 34;")
    replace(p, "const int default_corner_radius = 4;",
            "const int default_corner_radius = 6;")

    colors = ROOT / "platform/android/java/editor/src/main/res/values/colors.xml"
    text = colors.read_text(encoding="utf-8")
    text = text.replace("#e0e0e0", "#EAF8FF")
    text = text.replace("@android:color/holo_blue_light", "#0EA5E9")
    text = text.replace("@android:color/darker_gray", "#53657A")
    colors.write_text(text, encoding="utf-8")

    dims = ROOT / "platform/android/java/editor/src/main/res/values/dimens.xml"
    text = dims.read_text(encoding="utf-8")
    text = text.replace('<dimen name="game_menu_vseparator_vertical_margin">8dp</dimen>',
                        '<dimen name="game_menu_vseparator_vertical_margin">10dp</dimen>')
    text = text.replace('<dimen name="game_menu_vseparator_horizontal_margin">1dp</dimen>',
                        '<dimen name="game_menu_vseparator_horizontal_margin">3dp</dimen>')
    dims.write_text(text, encoding="utf-8")

    layout = ROOT / "platform/android/java/editor/src/main/res/layout/game_menu_fragment_layout.xml"
    text = layout.read_text(encoding="utf-8")
    text = text.replace('android:background="@android:color/black"',
                        'android:background="#101827"')
    text = text.replace('android:layout_width="48dp"', 'android:layout_width="56dp"')
    text = text.replace('android:layout_height="48dp"', 'android:layout_height="56dp"')
    text = text.replace('android:minHeight="48dp"', 'android:minHeight="56dp"')
    layout.write_text(text, encoding="utf-8")

def render_assets():
    try:
        import cairosvg
        from PIL import Image
    except Exception as exc:
        raise RuntimeError("Install cairosvg and Pillow before running branding") from exc

    svg = SVG.read_bytes()

    def render(size):
        png = cairosvg.svg2png(bytestring=svg, output_width=size, output_height=size)
        return Image.open(io.BytesIO(png)).convert("RGBA")

    icon = render(512)
    icon.resize((128,128), Image.Resampling.LANCZOS).save(ROOT / "main/app_icon.png")

    # Engine splash: dark Zorix canvas with centered identity mark.
    splash = Image.new("RGBA", (960, 540), "#101827")
    mark = render(260)
    splash.alpha_composite(mark, ((960-260)//2, 90))
    splash.convert("RGB").save(ROOT / "main/splash.png")
    splash.convert("RGB").save(ROOT / "main/splash_editor.png")

    mip = {
        "mipmap": 512,
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }
    lib = ROOT / "platform/android/java/lib/src/main/res"
    for folder, size in mip.items():
        d = lib / folder
        if not d.exists():
            continue
        full = render(size).convert("RGB")
        full.save(d / "icon.webp", "WEBP", quality=96)

        bg = Image.new("RGB", (size, size), "#101827")
        bg.save(d / "icon_background.webp", "WEBP", quality=96)

        canvas = Image.new("RGBA", (size, size), (0,0,0,0))
        fg = render(max(1, int(size * 0.76)))
        canvas.alpha_composite(fg, ((size-fg.width)//2, (size-fg.height)//2))
        canvas.save(d / "icon_foreground.webp", "WEBP", quality=96)

        mono = canvas.convert("L").convert("RGBA")
        mono.save(d / "icon_monochrome.webp", "WEBP", quality=96)

def write_brand_info():
    info = ROOT / "ZORIX.md"
    info.write_text("""# Zorix Engine branding layer

This source tree is based on Godot Engine 4.7.2-stable.

Zorix changes the visible product identity, editor palette, spacing/corner geometry,
Android editor application ID, launcher/splash imagery, and touch-oriented controls.
Godot's MIT license, copyright notices, AUTHORS, third-party notices, API namespaces,
and compatibility-sensitive package/class names remain intact.

Zorix palette:
- Blue: #1D4ED8
- Cyan: #0EA5E9
- Teal: #14B8A6
- Dark surface: #101827
""", encoding="utf-8")

def main():
    brand_text()
    brand_theme()
    render_assets()
    write_brand_info()
    print("Zorix branding applied successfully.")

if __name__ == "__main__":
    main()
