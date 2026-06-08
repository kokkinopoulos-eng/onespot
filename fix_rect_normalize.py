with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Fix _buildSelectionRect to use normalized coordinates
code = code.replace(
    """  Widget _buildSelectionRect() {
    return Positioned(
      left: _selectionRect!.left,
      top: _selectionRect!.top,
      child: Container(
        width: _selectionRect!.width.abs(),
        height: _selectionRect!.height.abs(),""",
    """  Widget _buildSelectionRect() {
    // Normalize so left/top are always smaller than right/bottom
    final normalized = Rect.fromLTRB(
      _selectionRect!.left < _selectionRect!.right ? _selectionRect!.left : _selectionRect!.right,
      _selectionRect!.top < _selectionRect!.bottom ? _selectionRect!.top : _selectionRect!.bottom,
      _selectionRect!.left > _selectionRect!.right ? _selectionRect!.left : _selectionRect!.right,
      _selectionRect!.top > _selectionRect!.bottom ? _selectionRect!.top : _selectionRect!.bottom,
    );
    return Positioned(
      left: normalized.left,
      top: normalized.top,
      child: Container(
        width: normalized.width,
        height: normalized.height,"""
)

# Also normalize the contains check in _onPointerUp
code = code.replace(
    "      if (_selectionRect != null && _selectionRect!.contains(upPos)) {",
    """      Rect? normRect;
      if (_selectionRect != null) {
        normRect = Rect.fromLTRB(
          _selectionRect!.left < _selectionRect!.right ? _selectionRect!.left : _selectionRect!.right,
          _selectionRect!.top < _selectionRect!.bottom ? _selectionRect!.top : _selectionRect!.bottom,
          _selectionRect!.left > _selectionRect!.right ? _selectionRect!.left : _selectionRect!.right,
          _selectionRect!.top > _selectionRect!.bottom ? _selectionRect!.top : _selectionRect!.bottom,
        );
      }
      if (normRect != null && normRect.contains(upPos)) {"""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
