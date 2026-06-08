with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "      body: GestureDetector(\n        onPanStart: _onDragStart,\n        onPanUpdate: _onDragUpdate,\n        onPanEnd: _onDragEnd,\n        onTapDown: _onTapInRect,",
    """      body: GestureDetector(
        onScaleStart: (d) {
          if (d.pointerCount == 1) {
            // Single finger — start drawing rect
            setState(() {
              _dragStart = d.localFocalPoint;
              _selectionRect = null;
              _dotPosition = null;
              _isDrawing = true;
            });
          }
        },
        onScaleUpdate: (d) {
          if (d.pointerCount == 2) {
            // Two fingers — zoom
            final newZoom = (_zoomLevel * d.scale).clamp(_minZoom, _maxZoom);
            _controller?.setZoomLevel(newZoom);
            setState(() => _zoomLevel = newZoom);
          } else if (d.pointerCount == 1 && _isDrawing && _dragStart != null) {
            // Single finger — update rect
            final cur = d.localFocalPoint;
            setState(() {
              _selectionRect = Rect.fromPoints(_dragStart!, cur);
            });
          }
        },
        onScaleEnd: (d) {
          setState(() => _isDrawing = false);
        },
        onTapDown: (d) {
          // Tap inside rect = place dot
          if (_selectionRect != null && _selectionRect!.contains(d.localPosition)) {
            setState(() => _dotPosition = d.localPosition);
            _onTap(d.localPosition);
          } else {
            // Tap outside = clear rect
            setState(() { _selectionRect = null; _dotPosition = null; });
          }
        },"""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
