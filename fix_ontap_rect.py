with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Replace old _onTap signature
code = code.replace(
    "  Future<void> _onTap(TapDownDetails details) async {",
    "  Future<void> _onTap(Offset position) async {"
)

code = code.replace(
    "    if (_isIdentifying) return;\n    setState(() { _tapPosition = details.localPosition; });",
    "    if (_isIdentifying) return;\n    setState(() { _tapPosition = position; });"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
