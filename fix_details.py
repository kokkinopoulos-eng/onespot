with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "    setState(() { _tapPosition = details.localPosition; _lastError = null; });",
    "    setState(() { _tapPosition = position; _lastError = null; });"
)
code = code.replace(
    "    debugPrint('ONESPOT: tap at ${details.localPosition}');",
    "    debugPrint('ONESPOT: tap at $position');"
)

# Fix onTapDown signature in GestureDetector
code = code.replace(
    "        onTapDown: (d) {\n          // Tap inside rect = place dot\n          if (_selectionRect != null && _selectionRect!.contains(d.localPosition)) {\n            setState(() => _dotPosition = d.localPosition);\n            _onTap(d.localPosition);\n          } else {\n            // Tap outside = clear rect\n            setState(() { _selectionRect = null; _dotPosition = null; });\n          }\n        },",
    "        onTapDown: (TapDownDetails d) {\n          if (_selectionRect != null && _selectionRect!.contains(d.localPosition)) {\n            setState(() => _dotPosition = d.localPosition);\n            _onTap(d.localPosition);\n          } else {\n            setState(() { _selectionRect = null; _dotPosition = null; });\n          }\n        },"
)

# Fix Stack references
code = code.replace(
    "            if (_selectionRect != null) _buildSelectionRect(),\n            if (_dotPosition != null) _buildDot(),\n            _buildZoomSlider(),",
    "            if (_selectionRect != null) _buildSelectionRect(),\n            if (_dotPosition != null) _buildDot(),\n            _buildZoomSlider(),"
)

# Remove unused fields warnings - use them
code = code.replace(
    "  Rect? _selectionRect;\n  Offset? _dragStart;\n  Offset? _dotPosition;\n  bool _isDrawing = false;",
    "  Rect? _selectionRect;\n  Offset? _dragStart;\n  Offset? _dotPosition;\n  bool _isDrawing = false;\n  // ignore: unused_field"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
