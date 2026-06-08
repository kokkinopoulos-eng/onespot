with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Fix the inner GestureDetector onTapDown
code = code.replace(
    "              behavior: HitTestBehavior.opaque,\n              onTapDown: _onTap,",
    "              behavior: HitTestBehavior.opaque,\n              onTapDown: (TapDownDetails d) {\n                if (_selectionRect != null && _selectionRect!.contains(d.localPosition)) {\n                  setState(() => _dotPosition = d.localPosition);\n                  _onTap(d.localPosition);\n                } else {\n                  setState(() { _selectionRect = null; _dotPosition = null; });\n                }\n              },"
)

# Add rect overlays to Stack
code = code.replace(
    "          if (_tapPosition != null) _buildRipple(),",
    "          if (_selectionRect != null) _buildSelectionRect(),\n          if (_dotPosition != null) _buildDot(),\n          _buildZoomSlider(),\n          if (_tapPosition != null) _buildRipple(),"
)

# Remove unused _dragStart and _isDrawing
code = code.replace(
    "  Offset? _dragStart;\n  bool _isDrawing = false;\n  // ignore: unused_field\n",
    ""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
