with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Remove language from inside if block
code = code.replace(
    "      key = await _settings.getApiKey(provider);\n      final language = await _settings.getLanguage();",
    "      key = await _settings.getApiKey(provider);"
)

# Add language before if (!isYolo)
code = code.replace(
    "    final isYolo = provider == 'yolo';\n    String? key;",
    "    final isYolo = provider == 'yolo';\n    final language = await _settings.getLanguage();\n    String? key;"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
