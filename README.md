# Zorix Browser

Zorix is now an independent Android browser, not a game engine.

## Architecture

- **Native Zorix UI:** the address bar, start page, navigation controls, and menus are regular Android views.
- **Gecko engine:** web pages are rendered by Mozilla GeckoView, not Android WebView.
- **No Godot:** the previous Godot bootstrap/build pipeline has been removed.
- **ARM64 APK:** the current build targets modern 64-bit Android devices.

The visual direction is deliberately minimal: warm white surfaces, restrained borders, rounded controls, strong typography, and a quiet black/white interface inspired by modern AI tools without copying another product's branding.

## Build

GitHub Actions builds the APK with Android Gradle Plugin 9.4, Gradle 9.6, Java 17, Android API 37, and GeckoView 156 stable.

The workflow publishes:

`zorix-browser-android-apk`

containing:

`zorix-browser.apk`

## Current browser features

- Native Zorix start page
- Address/search input
- Gecko-powered page rendering
- Back / forward / reload / home
- HTTP and HTTPS intent handling
- Progress indicator
- OpenAI, GitHub, and Wikipedia start-page shortcuts

This project intentionally does not use `android.webkit.WebView`.
