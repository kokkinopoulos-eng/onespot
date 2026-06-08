with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "  Map<String, dynamic>? _identifyResult;\n",
    ""
)
code = code.replace(
    "_identifyResult = result;\n        _isIdentifying = false;",
    "_isIdentifying = false;"
)
code = code.replace(
    "_identifyResult = null; _isPaused = true;",
    "_isPaused = true;"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
