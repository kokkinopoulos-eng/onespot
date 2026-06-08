with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    """          Positioned.fill(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTapDown: (TapDownDetails d) {
                if (_selectionRect != null && _selectionRect!.contains(d.localPosition)) {
                  setState(() => _dotPosition = d.localPosition);
                  _onTap(d.localPosition);
                } else {
                  setState(() { _selectionRect = null; _dotPosition = null; });
                }
              },
            ),
          ),""",
    """          Positioned.fill(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onScaleStart: (d) {
                if (d.pointerCount == 1) {
                  setState(() {
                    _rectStart = d.localFocalPoint;
                    _selectionRect = null;
                    _dotPosition = null;
                  });
                }
              },
              onScaleUpdate: (d) {
                if (d.pointerCount == 2) {
                  final newZoom = (_zoomLevel * d.scale).clamp(_minZoom, _maxZoom);
                  _controller?.setZoomLevel(newZoom);
                  setState(() => _zoomLevel = newZoom);
                } else if (d.pointerCount == 1 && _rectStart != null) {
                  setState(() {
                    _selectionRect = Rect.fromPoints(_rectStart!, d.localFocalPoint);
                  });
                }
              },
              onScaleEnd: (_) => setState(() => _rectStart = null),
              onTapDown: (TapDownDetails d) {
                if (_selectionRect != null && _selectionRect!.contains(d.localPosition)) {
                  setState(() => _dotPosition = d.localPosition);
                  _onTap(d.localPosition);
                } else {
                  setState(() { _selectionRect = null; _dotPosition = null; });
                }
              },
            ),
          ),"""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
