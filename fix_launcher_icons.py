with open("pubspec.yaml", encoding="utf-8") as f:
    code = f.read()

if "flutter_launcher_icons:" not in code:
    code = code + """
flutter_launcher_icons:
  android: true
  ios: false
  image_path: "assets/icon/icon.png"
  min_sdk_android: 24
  adaptive_icon_background: "#040D1E"
  adaptive_icon_foreground: "assets/icon/icon.png"
"""

with open("pubspec.yaml", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
