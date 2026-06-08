with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "    final provider = await _settings.getProvider();\n    final key = await _settings.getApiKey(provider);",
    "    final provider = await _settings.getProvider();\n    final key = await _settings.getApiKey(provider);\n    final language = await _settings.getLanguage();"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
