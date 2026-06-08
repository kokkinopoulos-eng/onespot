# Fix camera_screen.dart
with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "        if (_mode == SpotMode.identify) {\n          prompt = 'What is the main object? Reply ONLY as JSON: {\"name\":\"object name\",\"description\":\"one sentence\",\"similar\":N} where N is count of similar objects visible.';\n        } else if (_mode == SpotMode.countOne) {\n          prompt = 'What is the most prominent object? Count all similar ones visible. Reply ONLY as JSON: {\"name\":\"object name\",\"description\":\"one sentence\",\"similar\":N} where N is total count of this object.';\n        } else {\n          prompt = 'List ALL distinct objects visible and count each. Reply ONLY as JSON: {\"objects\":[{\"name\":\"object\",\"count\":N}]}' + langSuffix;\n        }",
    "        final langSuffix = ' Reply in $language.';\n        if (_mode == SpotMode.identify) {\n          prompt = 'What is the main object? Reply ONLY as JSON: {\"name\":\"object name\",\"description\":\"one sentence\",\"similar\":N} where N is count of similar objects visible.' + langSuffix;\n        } else if (_mode == SpotMode.countOne) {\n          prompt = 'What is the most prominent object? Count all similar ones visible. Reply ONLY as JSON: {\"name\":\"object name\",\"description\":\"one sentence\",\"similar\":N} where N is total count of this object.' + langSuffix;\n        } else {\n          prompt = 'List ALL distinct objects visible and count each. Reply ONLY as JSON: {\"objects\":[{\"name\":\"object\",\"count\":N}]}' + langSuffix;\n        }"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Camera done")

# Fix settings_screen.dart - remove duplicate _languageController
with open("lib/features/settings/settings_screen.dart", encoding="utf-8") as f:
    lines = f.readlines()

seen = False
new_lines = []
for line in lines:
    if "final TextEditingController _languageController = TextEditingController();" in line:
        if not seen:
            seen = True
            new_lines.append(line)
        # skip duplicate
    else:
        new_lines.append(line)

with open("lib/features/settings/settings_screen.dart", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Settings done")
