with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Load language with provider and key
code = code.replace(
    "    final provider = await _settings.getProvider();\n    final key = await _settings.getApiKey(provider);",
    "    final provider = await _settings.getProvider();\n    final key = await _settings.getApiKey(provider);\n    final language = await _settings.getLanguage();"
)

# Add language to each prompt
code = code.replace(
    "      if (_mode == SpotMode.identify) {\n        prompt = 'What is the main object?",
    "      final langSuffix = ' Reply in $language.';\n      if (_mode == SpotMode.identify) {\n        prompt = 'What is the main object?"
)

code = code.replace(
    "where N is count of similar objects visible.';\n      } else if (_mode == SpotMode.countOne) {",
    "where N is count of similar objects visible.' + langSuffix;\n      } else if (_mode == SpotMode.countOne) {"
)

code = code.replace(
    "where N is total count of this object.';\n      } else {",
    "where N is total count of this object.' + langSuffix;\n      } else {"
)

code = code.replace(
    "'List ALL distinct objects visible and count each. Reply ONLY as JSON: {\"objects\":[{\"name\":\"object\",\"count\":N}]}';",
    "'List ALL distinct objects visible and count each. Reply ONLY as JSON: {\"objects\":[{\"name\":\"object\",\"count\":N}]}' + langSuffix;"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
