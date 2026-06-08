with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Increase move threshold from 8 to 20px
code = code.replace(
    "      if ((e.localPosition - _gestureStart!).distance > 8) _moved = true;",
    "      if ((e.localPosition - _gestureStart!).distance > 20) _moved = true;"
)

# Fix wasTap - also allow small movement taps inside rect
code = code.replace(
    "    final wasTap = _pointers.length == 1 && !_moved && !_isPinch;",
    "    final smallMove = _pointers.length == 1 && !_isPinch && (_gestureStart != null && (upPos - _gestureStart!).distance < 30);\n    final wasTap = ((_pointers.length == 1 && !_moved && !_isPinch) || smallMove);"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
