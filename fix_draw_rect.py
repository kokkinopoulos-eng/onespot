with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Add new state variables
code = code.replace(
    "  bool _isIdentifying = false;\n  bool _showingToast = false;\n  String _toastMsg = '';",
    """  bool _isIdentifying = false;
  bool _showingToast = false;
  String _toastMsg = '';
  Rect? _selectionRect;
  Offset? _dragStart;
  Offset? _dotPosition;
  bool _isDrawing = false;
  double _zoomLevel = 1.0;
  double _maxZoom = 1.0;
  double _minZoom = 1.0;"""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
