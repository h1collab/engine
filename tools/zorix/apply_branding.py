#!/usr/bin/env python3
from pathlib import Path
import io
import re

ROOT = Path(__file__).resolve().parents[2]
SVG = ROOT / "tools/zorix/zorix.svg"

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def replace(path, old, new, required=True):
    text = read(path)
    if old not in text:
        if required:
            raise RuntimeError(f"Expected text not found in {path}: {old[:100]!r}")
        return False
    write(path, text.replace(old, new))
    return True

def replace_translated_branding():
    # Only replace Godot inside translated user-facing strings.
    # Do not rename compatibility-sensitive class names, namespaces, file formats,
    # API keys or resource identifiers.
    wrapper = re.compile(r'((?:TTR|TTRC|TTRN|TTRNC)\(\s*")((?:\\.|[^"\\])*)(")')
    for base in [ROOT / "editor"]:
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in {".cpp", ".h"}:
                continue
            if p.name == "editor_about.cpp":
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            def repl(m):
                body = m.group(2).replace("Godot Engine", "Zorix Engine").replace("Godot", "Zorix")
                return m.group(1) + body + m.group(3)
            new = wrapper.sub(repl, text)
            if new != text:
                p.write_text(new, encoding="utf-8")

def brand_identity():
    replace("version.py", 'short_name = "godot"', 'short_name = "zorix"')
    replace("version.py", 'name = "Godot Engine"', 'name = "Zorix Engine"')
    replace("version.py", 'website = "https://godotengine.org"', 'website = "https://github.com/h1collab/engine"')

    # Android package identity and visible application name.
    replace("platform/android/java/editor/build.gradle",
            'applicationId "org.godotengine.editor.v4"',
            'applicationId "com.zorix.engine.editor.v4"')
    replace("platform/android/java/editor/build.gradle",
            'editorAppName: "Godot Engine 4"',
            'editorAppName: "Zorix Engine 4"')
    replace("platform/android/java/editor/build.gradle",
            'archivesName = "android_editor"',
            'archivesName = "zorix_android_editor"')

    # Android visible strings: resource identifiers remain unchanged.
    p = ROOT / "platform/android/java/editor/src/main/res/values/strings.xml"
    text = p.read_text(encoding="utf-8")
    text = text.replace("Godot Engine", "Zorix Engine").replace("Godot", "Zorix")
    if "storage_permission_ready_msg" not in text:
        text = text.replace("</resources>",
            '    <string name="storage_permission_ready_msg">Storage access enabled. Restarting Zorix workspace…</string>\n'
            '    <string name="zorix_starting">Starting Zorix Engine…</string>\n'
            '</resources>')
    p.write_text(text, encoding="utf-8")

    replace_translated_branding()

def brand_about():
    p = "editor/gui/editor_about.cpp"
    text = read(p)
    text = text.replace('set_title(TTRC("Thanks from the Godot community!"));',
                        'set_title(TTRC("About Zorix Engine"));')
    old = '''_about_text_label->set_text(
					String(U"© 2014-present ") + TTR("Godot Engine contributors") + ".\\n" +
					String(U"© 2007-2014 Juan Linietsky, Ariel Manzur.\\n"));'''
    new = '''_about_text_label->set_text(
					String("Zorix Engine 4.7.2 — based on Godot Engine.\\n") +
					String(U"© 2014-present ") + TTR("Godot Engine contributors") + ".\\n" +
					String(U"© 2007-2014 Juan Linietsky, Ariel Manzur.\\n"));'''
    if old in text:
        text = text.replace(old, new)
    text = text.replace(
        'TTRC("Godot Engine relies on a number of third-party free and open source libraries, all compatible with the terms of its MIT license.',
        'TTRC("Zorix Engine is based on Godot Engine and relies on a number of third-party free and open source libraries, all compatible with the terms of its MIT license.')
    write(p, text)

def modernize_project_manager():
    p = "editor/project_manager/project_manager.cpp"
    text = read(p)
    text = text.replace('TTR("Project Manager", "Application")', 'TTR("Zorix Hub", "Application")')
    text = text.replace('title_bar_logo->set_tooltip_text(TTR("About Godot"));',
                        'title_bar_logo->set_tooltip_text(TTR("About Zorix Engine"));')

    marker = '''		title_bar_logo->connect(SceneStringName(pressed), callable_mp(this, &ProjectManager::_show_about));'''
    insert = marker + '''

		Label *zorix_brand = memnew(Label(TTRC("Zorix Engine")));
		zorix_brand->set_theme_type_variation("HeaderSmall");
		zorix_brand->set_tooltip_text(TTRC("Zorix Engine Studio"));
		left_hbox->add_child(zorix_brand);'''
    if marker in text and "Zorix Engine Studio" not in text:
        text = text.replace(marker, insert)

    marker2 = '''		_add_main_view(MAIN_VIEW_PROJECTS, TTRC("Projects"), Ref<Texture2D>(), local_projects_vb);'''
    insert2 = marker2 + '''

		VBoxContainer *zorix_welcome = memnew(VBoxContainer);
		zorix_welcome->add_theme_constant_override("separation", 2 * EDSCALE);
		local_projects_vb->add_child(zorix_welcome);
		Label *zorix_welcome_title = memnew(Label(TTRC("Build something extraordinary.")));
		zorix_welcome_title->set_theme_type_variation("HeaderSmall");
		zorix_welcome->add_child(zorix_welcome_title);
		Label *zorix_welcome_subtitle = memnew(Label(TTRC("Zorix Hub · Projects · Assets · Forward+")));
		zorix_welcome_subtitle->set_modulate(Color(1, 1, 1, 0.62));
		zorix_welcome->add_child(zorix_welcome_subtitle);'''
    if marker2 in text and "Build something extraordinary." not in text:
        text = text.replace(marker2, insert2)

    text = text.replace('project_list_sidebar->set_custom_minimum_size(Size2(120, 120));',
                        'project_list_sidebar->set_custom_minimum_size(Size2(168, 120));')
    text = text.replace('create_btn->set_text(TTRC("Create"));',
                        'create_btn->set_text(TTRC("New Project"));')
    text = text.replace('scan_btn->set_text(TTRC("Scan"));',
                        'scan_btn->set_text(TTRC("Discover"));')
    text = text.replace('open_btn->set_text(TTRC("Edit"));',
                        'open_btn->set_text(TTRC("Open Editor"));')
    text = text.replace('donate_btn->set_text(TTRC("Donate"));',
                        'donate_btn->set_text(TTRC("Source"));')
    text = text.replace('OS::get_singleton()->shell_open("https://fund.godotengine.org/?ref=project_manager");',
                        'OS::get_singleton()->shell_open("https://github.com/h1collab/engine");')
    text = text.replace('TTRC("Asset Store")', 'TTRC("Assets")')
    text = text.replace('TTRC("Open Asset Store")', 'TTRC("Browse Assets")')
    write(p, text)

def modernize_project_dialog():
    p = "editor/project_manager/project_dialog.cpp"
    text = read(p)
    text = text.replace('rs_button->set_text(TTRC("Forward+"));',
                        'rs_button->set_text(TTRC("Zorix Ultra (Forward+)"));')
    text = text.replace('rs_button->set_text(TTRC("Mobile"));',
                        'rs_button->set_text(TTRC("Zorix Mobile"));')
    text = text.replace(
        'String::utf8("•  ") + TTR("Advanced 3D graphics available.") +',
        'String::utf8("•  ") + TTR("High-quality Vulkan 3D pipeline.") +')
    text = text.replace(
        'String::utf8("\\n•  ") + TTR("Can scale to large complex scenes.") +',
        'String::utf8("\\n•  ") + TTR("Designed for complex scenes, lighting and effects.") +')
    write(p, text)

def brand_theme():
    p = "editor/settings/editor_settings.cpp"
    replacements = [
        ('EDITOR_SETTING_BASIC(Variant::STRING, PROPERTY_HINT_ENUM, "interface/theme/spacing_preset", "Default", "Compact,Default,Spacious,Custom")',
         'EDITOR_SETTING_BASIC(Variant::STRING, PROPERTY_HINT_ENUM, "interface/theme/spacing_preset", "Spacious", "Compact,Default,Spacious,Custom")'),
        ('EDITOR_SETTING_BASIC(Variant::COLOR, PROPERTY_HINT_NONE, "interface/theme/base_color", Color(0.14, 0.14, 0.14), "")',
         'EDITOR_SETTING_BASIC(Variant::COLOR, PROPERTY_HINT_NONE, "interface/theme/base_color", Color(0.055, 0.067, 0.086), "")'),
        ('EDITOR_SETTING_BASIC(Variant::COLOR, PROPERTY_HINT_NONE, "interface/theme/accent_color", Color(0.34, 0.62, 1.0), "")',
         'EDITOR_SETTING_BASIC(Variant::COLOR, PROPERTY_HINT_NONE, "interface/theme/accent_color", Color(0.055, 0.647, 0.914), "")'),
        ('EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/corner_radius", 4, "0,6,1")',
         'EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/corner_radius", 6, "0,6,1")'),
        ('EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/base_spacing", 4, "0,8,1")',
         'EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/base_spacing", 6, "0,8,1")'),
        ('EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/additional_spacing", 0, "0,8,1")',
         'EDITOR_SETTING(Variant::INT, PROPERTY_HINT_RANGE, "interface/theme/additional_spacing", 2, "0,8,1")'),
        ('EDITOR_SETTING_BASIC(Variant::INT, PROPERTY_HINT_RANGE, "interface/editor/fonts/main_font_size", 14, "8,48,1")',
         'EDITOR_SETTING_BASIC(Variant::INT, PROPERTY_HINT_RANGE, "interface/editor/fonts/main_font_size", 15, "8,48,1")'),
        ('EDITOR_SETTING_BASIC(Variant::INT, PROPERTY_HINT_RANGE, "interface/editor/fonts/code_font_size", 14, "8,48,1")',
         'EDITOR_SETTING_BASIC(Variant::INT, PROPERTY_HINT_RANGE, "interface/editor/fonts/code_font_size", 15, "8,48,1")'),
    ]
    for old, new in replacements:
        replace(p, old, new, required=False)

    p = "editor/themes/editor_theme_manager.cpp"
    replace(p,
            'preset_accent_color = Color(0.337, 0.62, 1.0);\n\t\t\t\tpreset_base_color = Color(0.161, 0.161, 0.161);',
            'preset_accent_color = Color(0.055, 0.647, 0.914);\n\t\t\t\tpreset_base_color = Color(0.055, 0.067, 0.086);',
            required=False)

    p = "editor/themes/editor_theme_manager.h"
    replace(p, "Size2 dialogs_buttons_min_size = Size2(105, 34);",
            "Size2 dialogs_buttons_min_size = Size2(124, 44);", required=False)
    replace(p, "int inspector_property_height = 28;",
            "int inspector_property_height = 36;", required=False)
    replace(p, "const int default_corner_radius = 4;",
            "const int default_corner_radius = 6;", required=False)

    # Android game toolbar.
    p = ROOT / "platform/android/java/editor/src/main/res/layout/game_menu_fragment_layout.xml"
    text = p.read_text(encoding="utf-8")
    text = text.replace('android:background="@android:color/black"', 'android:background="#0E131B"')
    text = text.replace('android:layout_width="48dp"', 'android:layout_width="56dp"')
    text = text.replace('android:layout_height="48dp"', 'android:layout_height="56dp"')
    text = text.replace('android:minHeight="48dp"', 'android:minHeight="56dp"')
    p.write_text(text, encoding="utf-8")

def android_shell():
    # Modern native shell above the engine surface. It is deliberately simple,
    # high-contrast and touch friendly, with the Zorix mark always visible.
    layout = r'''<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#0B0F15"
    android:fitsSystemWindows="true"
    tools:background="#0B0F15">

    <LinearLayout
        android:id="@+id/zorix_top_bar"
        android:layout_width="0dp"
        android:layout_height="56dp"
        android:orientation="horizontal"
        android:gravity="center_vertical"
        android:paddingStart="14dp"
        android:paddingEnd="14dp"
        android:background="@drawable/zorix_top_bar"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent">

        <ImageView
            android:layout_width="34dp"
            android:layout_height="34dp"
            android:src="@mipmap/themed_icon"
            android:contentDescription="Zorix Engine" />

        <LinearLayout
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:orientation="vertical"
            android:paddingStart="10dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Zorix Engine"
                android:textColor="#F7FBFF"
                android:textStyle="bold"
                android:textSize="17sp" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Studio · Vulkan · Forward+"
                android:textColor="#9CB0C5"
                android:textSize="11sp" />
        </LinearLayout>

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="32dp"
            android:gravity="center"
            android:paddingStart="12dp"
            android:paddingEnd="12dp"
            android:background="@drawable/zorix_pill"
            android:text="ZORIX"
            android:textColor="#DDF8FF"
            android:textStyle="bold"
            android:textSize="11sp" />
    </LinearLayout>

    <FrameLayout
        android:id="@+id/godot_fragment_container"
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toBottomOf="@id/zorix_top_bar"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"/>

    <FrameLayout
        android:id="@+id/embedded_game_view_container_window"
        android:layout_width="0dp"
        android:layout_height="0dp"
        android:background="#33000000"
        android:visibility="gone"
        tools:visibility="visible"
        app:layout_constraintTop_toBottomOf="@id/zorix_top_bar"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent">

        <androidx.constraintlayout.widget.ConstraintLayout
            android:id="@+id/embedded_game_view_container"
            android:layout_width="@dimen/embed_game_window_default_width"
            android:layout_height="@dimen/embed_game_window_default_height"
            android:background="@drawable/game_menu_message_bg"
            android:layout_gravity="bottom|end">

            <FrameLayout
                android:id="@+id/game_menu_fragment_container"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                app:layout_constraintTop_toTopOf="parent" />

            <TextView
                android:id="@+id/embedded_game_state_label"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:gravity="center"
                android:text="@string/embedded_game_not_running_message"
                android:drawableBottom="@drawable/play_48dp"
                android:textColor="@android:color/white"
                android:textSize="18sp"
                android:textStyle="bold"
                app:layout_constraintTop_toBottomOf="@+id/game_menu_fragment_container"
                app:layout_constraintBottom_toBottomOf="parent"
                app:layout_constraintStart_toStartOf="parent"
                app:layout_constraintEnd_toEndOf="parent"/>
        </androidx.constraintlayout.widget.ConstraintLayout>
    </FrameLayout>

    <LinearLayout
        android:id="@+id/editor_loading_indicator"
        android:layout_width="260dp"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:gravity="center"
        android:padding="22dp"
        android:background="@drawable/zorix_loading_card"
        app:layout_constraintTop_toTopOf="@id/godot_fragment_container"
        app:layout_constraintBottom_toBottomOf="@id/godot_fragment_container"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent">

        <ImageView
            android:layout_width="72dp"
            android:layout_height="72dp"
            android:src="@mipmap/themed_icon"
            android:contentDescription="Zorix Engine" />

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="12dp"
            android:text="@string/zorix_starting"
            android:textColor="#F7FBFF"
            android:textStyle="bold"
            android:textSize="16sp" />

        <ProgressBar
            style="@android:style/Widget.Material.ProgressBar.Horizontal"
            android:layout_width="match_parent"
            android:layout_height="4dp"
            android:layout_marginTop="16dp"
            android:indeterminate="true"
            android:indeterminateTint="#0EA5E9" />

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_marginTop="10dp"
            android:text="Preparing editor workspace"
            android:textColor="#8EA3B8"
            android:textSize="12sp" />
    </LinearLayout>
</androidx.constraintlayout.widget.ConstraintLayout>
'''
    write("platform/android/java/editor/src/main/res/layout/godot_editor_layout.xml", layout)

    write("platform/android/java/editor/src/main/res/drawable/zorix_top_bar.xml", '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <gradient android:angle="0" android:startColor="#111827" android:centerColor="#0D1824" android:endColor="#0A2021"/>
    <stroke android:width="1dp" android:color="#263646"/>
</shape>
''')
    write("platform/android/java/editor/src/main/res/drawable/zorix_pill.xml", '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#172B34"/>
    <stroke android:width="1dp" android:color="#0EA5E9"/>
    <corners android:radius="16dp"/>
</shape>
''')
    write("platform/android/java/editor/src/main/res/drawable/zorix_loading_card.xml", '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#F20F151E"/>
    <stroke android:width="1dp" android:color="#334B61"/>
    <corners android:radius="24dp"/>
    <padding android:left="4dp" android:top="4dp" android:right="4dp" android:bottom="4dp"/>
</shape>
''')

def permission_recovery():
    p = "platform/android/java/editor/src/main/java/org/godotengine/editor/BaseGodotEditor.kt"
    text = read(p)
    old = '''			PermissionsUtil.REQUEST_MANAGE_EXTERNAL_STORAGE_REQ_CODE -> {
				if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R && !Environment.isExternalStorageManager()) {
					Toast.makeText(
						this,
						R.string.denied_storage_permission_error_msg,
						Toast.LENGTH_LONG
					).show()
				}
			}'''
    new = '''			PermissionsUtil.REQUEST_MANAGE_EXTERNAL_STORAGE_REQ_CODE -> {
				if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
					if (!Environment.isExternalStorageManager()) {
						Toast.makeText(
							this,
							R.string.denied_storage_permission_error_msg,
							Toast.LENGTH_LONG
						).show()
					} else {
						Toast.makeText(
							this,
							R.string.storage_permission_ready_msg,
							Toast.LENGTH_SHORT
						).show()
						// Some Android builds return from the all-files-access screen while
						// the native editor is still waiting on filesystem initialization.
						// If the Zorix loading card is still visible, rebuild the Activity
						// once with the permission already granted.
						editorLoadingIndicator?.postDelayed({
							if (editorLoadingIndicator?.isVisible == true) {
								recreate()
							}
						}, 450)
					}
				}
			}'''
    if old in text:
        text = text.replace(old, new)
    else:
        raise RuntimeError("Unable to patch Android storage-permission recovery.")
    write(p, text)

def render_assets():
    try:
        import cairosvg
        from PIL import Image, ImageDraw
    except Exception as exc:
        raise RuntimeError("Install cairosvg and Pillow before running branding") from exc

    svg = SVG.read_bytes()

    # The editor's own titlebar/logo sources, not just the Android launcher.
    for name in ["icon.svg", "logo.svg", "icon_outlined.svg", "logo_outlined.svg"]:
        (ROOT / name).write_bytes(svg)

    def render(size):
        png = cairosvg.svg2png(bytestring=svg, output_width=size, output_height=size)
        return Image.open(io.BytesIO(png)).convert("RGBA")

    icon = render(512)
    icon.resize((128, 128), Image.Resampling.LANCZOS).save(ROOT / "main/app_icon.png")

    # Zorix launch canvas.
    splash = Image.new("RGBA", (1280, 720), "#0B0F15")
    draw = ImageDraw.Draw(splash)
    draw.rectangle((0, 0, 1280, 8), fill="#0EA5E9")
    mark = render(280)
    splash.alpha_composite(mark, ((1280 - 280) // 2, 150))
    draw.text((520, 470), "ZORIX ENGINE", fill="#F7FBFF")
    draw.text((535, 500), "CREATE  •  CODE  •  RENDER", fill="#8EA3B8")
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
        full.save(d / "icon.webp", "WEBP", quality=98)

        bg = Image.new("RGB", (size, size), "#0B0F15")
        bg.save(d / "icon_background.webp", "WEBP", quality=98)

        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        fg = render(max(1, int(size * 0.80)))
        canvas.alpha_composite(fg, ((size - fg.width) // 2, (size - fg.height) // 2))
        canvas.save(d / "icon_foreground.webp", "WEBP", quality=98)

        mono = canvas.convert("L").convert("RGBA")
        mono.save(d / "icon_monochrome.webp", "WEBP", quality=98)

def write_brand_info():
    write("ZORIX.md", """# Zorix Engine 4.7.2

Zorix Engine is a branded editor distribution based on Godot Engine 4.7.2-stable.

## Zorix Studio layer
- Zorix product identity and logo across Android launcher, native shell, splash,
  project hub, editor title surfaces, and visible translated strings.
- Modern dark studio UI with blue/cyan/teal accents, rounded surfaces, larger
  touch targets, wider project actions, and a persistent Android Zorix shell.
- Zorix Ultra maps to the upstream Forward+ RenderingDevice/Vulkan pipeline.
- Android permission recovery restarts the editor once when all-files access was
  granted but native filesystem initialization is still waiting.
- About Zorix Engine retains the required upstream Godot attribution.

Compatibility-sensitive package names, C++ classes, Android namespaces,
project.godot format identifiers, API names and upstream license text are kept
internally so existing Godot projects and extensions remain compatible.
""")

def main():
    brand_identity()
    brand_about()
    modernize_project_manager()
    modernize_project_dialog()
    brand_theme()
    android_shell()
    permission_recovery()
    render_assets()
    write_brand_info()
    print("Zorix Engine v2 branding and studio UI applied successfully.")

if __name__ == "__main__":
    main()
