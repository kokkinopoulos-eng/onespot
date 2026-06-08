with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    content = f.read()
content = content.replace("'\\${obj['count']}'", "'${obj[\"count\"]}'")
content = content.replace("'\\${obj['count']}'", "'${obj[\"count\"]}'")
content = content.replace("Similar visible: \\${_identifyResult!['similar']}", "Similar visible: ${_identifyResult!['similar']}")
content = content.replace("'\\${_counts.values.fold(0, (a, b) => a + b)}'", "'${_counts.values.fold(0, (a, b) => a + b)}'")
content = content.replace("'\\${e.value}'", "'${e.value}'")
content = content.replace("'\\${e.key}: \\${e.value}'", "'${e.key}: ${e.value}'")
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
