with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Find the Stack and rewrite the gesture layers
old_block = """          _buildFullScreenPreview(),
          // Tap-to-identify layer sits directly above the preview and BELOW the
          // controls, so buttons get their own taps while empty-area taps fall here.
          Positioned.fill(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onScaleStart: (d) {
                if (d.pointerCount == 1 && d.focalPointDelta == Offset.zero) {
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

new_block = """          _buildFullScreenPreview(),
          // Layer 2: Scale detector for drawing rect (1 finger) + zoom (2 fingers)
          Positioned.fill(
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onScaleStart: (d) {
                if (d.pointerCount == 1) {
                  setState(() {
                    _rectStart = d.localFocalPoint;
                    _selectionRect = Rect.fromPoints(d.localFocalPoint, d.localFocalPoint);
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
              onScaleEnd: (_) {
                // If rect is tiny (just a tap), clear it
                if (_selectionRect != null && _selectionRect!.width.abs() < 30 && _selectionRect!.height.abs() < 30) {
                  setState(() { _selectionRect = null; _rectStart = null; });
                } else {
                  setState(() => _rectStart = null);
                }
              },
            ),
          ),
          // Layer 3: Rect + Dot overlay (visual)
          if (_selectionRect != null) _buildSelectionRect(),
          if (_dotPosition != null) _buildDot(),
          // Layer 4: Tap-inside-rect detector — ACTIVE ONLY when rect exists
          if (_selectionRect != null)
            Positioned(
              left: _selectionRect!.left,
              top: _selectionRect!.top,
              width: _selectionRect!.width.abs(),
              height: _selectionRect!.height.abs(),
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTapDown: (d) {
                  final absPos = Offset(
                    _selectionRect!.left + d.localPosition.dx,
                    _selectionRect!.top + d.localPosition.dy,
                  );
                  setState(() => _dotPosition = absPos);
                  _onTap(absPos);
                },
              ),
            ),"""

code = code.replace(old_block, new_block)

# Remove duplicate rect/dot overlays from Stack (they're now in their own positioned block)
code = code.replace(
    "          if (_selectionRect != null) _buildSelectionRect(),\n          if (_dotPosition != null) _buildDot(),\n          _buildZoomSlider(),\n          if (_tapPosition != null) _buildRipple(),",
    "          _buildZoomSlider(),\n          if (_tapPosition != null) _buildRipple(),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
