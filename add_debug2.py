with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "  void _onPointerDown(PointerDownEvent e) {",
    "  void _onPointerDown(PointerDownEvent e) {\n    debugPrint('ONESPOT: pointer down \${e.pointer} pos=\${e.localPosition}');"
)
code = code.replace(
    "  void _onPointerUp(PointerUpEvent e) {",
    "  void _onPointerUp(PointerUpEvent e) {\n    debugPrint('ONESPOT: pointer up \${e.pointer} moved=\$_moved');"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
