# Zorix Engine

Zorix Engine is a customized, rebranded build of Godot Engine focused on a touch-friendly Android editor experience and a distinct Zorix visual identity.

## Base

- Upstream: Godot Engine
- Baseline: `4.7.2-stable`
- Upstream source: https://github.com/godotengine/godot
- Zorix source: https://github.com/h1collab/engine

## Zorix customizations

- Product name and visible editor branding changed to **Zorix Engine**.
- Zorix blue/cyan/teal theme is the default editor appearance.
- Touch-oriented spacing, corner radius, controls and Android game-toolbar sizing are tuned for tablets/phones.
- Android editor application ID is `com.zorix.engine.editor.v4`.
- Android editor app label, play-window label, app icon and engine icon use Zorix branding.
- The supplied Zorix SVG is kept in `tools/zorix/zorix.svg`.
- GitHub Actions can rebuild the Android editor APK.

## License and attribution

Godot Engine is distributed under the MIT License. Zorix Engine retains the upstream license, copyright notices, AUTHORS, and other attribution files. Internal Godot namespaces/package names used by upstream code and dependencies are intentionally preserved where changing them would break API or build compatibility.

See `LICENSE.txt`, `COPYRIGHT.txt`, and upstream attribution files after source bootstrap.
