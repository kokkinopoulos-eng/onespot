with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "  Rect? _selectionRect;\n  Offset? _dotPosition;",
    "  Rect? _selectionRect;\n  Offset? _dotPosition;\n  Offset? _rectStart;"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
