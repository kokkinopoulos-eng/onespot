with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "    final upPos = _pointers[e.pointer] ?? e.localPosition;\n    final wasTap = _pointers.length == 1 && !_moved && !_isPinch;\n    _pointers.remove(e.pointer);",
    "    final upPos = _pointers[e.pointer] ?? e.localPosition;\n    final wasOnlyPointer = _pointers.length == 1;\n    _pointers.remove(e.pointer);\n    final wasTap = wasOnlyPointer && !_moved && !_isPinch;"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
