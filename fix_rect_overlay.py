with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Add rect overlay and zoom slider to Stack
code = code.replace(
    "            if (_tapPosition != null) _buildRipple(),",
    """            if (_selectionRect != null) _buildSelectionRect(),
            if (_dotPosition != null) _buildDot(),
            _buildZoomSlider(),
            if (_tapPosition != null) _buildRipple(),"""
)

# Add _buildSelectionRect, _buildDot, _buildZoomSlider methods before _buildRipple
code = code.replace(
    "  Widget _buildRipple() {",
    """  Widget _buildSelectionRect() {
    return Positioned(
      left: _selectionRect!.left,
      top: _selectionRect!.top,
      child: Container(
        width: _selectionRect!.width.abs(),
        height: _selectionRect!.height.abs(),
        decoration: BoxDecoration(
          border: Border.all(color: const Color(0xFF00FF88), width: 2),
          color: const Color(0xFF00FF88).withOpacity(0.08),
        ),
        child: _selectionRect!.width.abs() > 60 && _selectionRect!.height.abs() > 30
          ? const Align(
              alignment: Alignment.topCenter,
              child: Padding(
                padding: EdgeInsets.only(top: 4),
                child: Text('Tap inside to identify', style: TextStyle(color: Color(0xFF00FF88), fontSize: 10, letterSpacing: 1)),
              ),
            )
          : null,
      ),
    );
  }

  Widget _buildDot() {
    return Positioned(
      left: _dotPosition!.dx - 8,
      top: _dotPosition!.dy - 8,
      child: Container(
        width: 16, height: 16,
        decoration: const BoxDecoration(
          color: Color(0xFFFFD600),
          shape: BoxShape.circle,
          boxShadow: [BoxShadow(color: Color(0xFFFFD600), blurRadius: 6, spreadRadius: 2)],
        ),
      ),
    );
  }

  Widget _buildZoomSlider() {
    if (_maxZoom <= 1.0) return const SizedBox.shrink();
    return Positioned(
      right: 16,
      top: 160,
      bottom: 120,
      child: RotatedBox(
        quarterTurns: 3,
        child: Slider(
          value: _zoomLevel,
          min: _minZoom,
          max: _maxZoom,
          activeColor: const Color(0xFF00FF88),
          inactiveColor: Colors.white24,
          onChanged: (v) {
            setState(() => _zoomLevel = v);
            _controller?.setZoomLevel(v);
          },
        ),
      ),
    );
  }

  Widget _buildRipple() {"""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
