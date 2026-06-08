with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "Text('\\${_counts.values.fold(0, (a, b) => a + b)}'",
    "Text(_counts.values.fold(0, (a, b) => a + b).toString()"
)
code = code.replace(
    "Text('\\${e.key}: \\${e.value}'",
    "Text('${e.key}: ${e.value}'"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
