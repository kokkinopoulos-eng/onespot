with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "  void _onPointerUp(PointerUpEvent e) {\n    final upPos = _pointers[e.pointer] ?? e.localPosition;\n    final wasTap = _pointers.length == 1 && !_moved && !_isPinch;",
    "  void _onPointerUp(PointerUpEvent e) {\n    final upPos = _pointers[e.pointer] ?? e.localPosition;\n    final wasTap = _pointers.length == 1 && !_moved && !_isPinch;\n    debugPrint('ONESPOT TAP: pos=$upPos moved=$_moved pinch=$_isPinch wasTap=$wasTap rect=$_selectionRect contains=${_selectionRect?.contains(upPos)}');"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
