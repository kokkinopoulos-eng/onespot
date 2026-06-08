with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

old = """                _buildFullScreenPreview(),
                // Tap-to-identify layer sits directly above the preview and BELOW
                // the controls. We use a raw Listener and derive every gesture
                // from pointer events ourselves — no GestureDetector / arena, so
                // taps are never swallowed.
                //   • 1 finger, no movement  → tap (identify inside rect)
                //   • 1 finger, dragged       → draw selection rect
                //   • 2 fingers               → pinch-zoom
                Positioned.fill(
                  child: Listener(
                    behavior: HitTestBehavior.opaque,
                    onPointerDown: _onPointerDown,
                    onPointerMove: _onPointerMove,
                    onPointerUp: _onPointerUp,
                    onPointerCancel: _onPointerCancel,
                  ),
                ),
                _buildTopBar(),
                _buildModeSelector(),
                _buildCounterPanel(),
                if (_selectionRect != null) _buildSelectionRect(),
                if (_dotPosition != null) _buildDot(),
                _buildZoomSlider(),
                if (_tapPosition != null) _buildRipple(),
                // Popup is the TOP-most child so it is always visible above everything.
                if (_isIdentifying) _buildIdentifyingIndicator(),
                if (_showingToast) _buildToast(),
                if (_lastError != null) _buildErrorCard(),"""

new = """                _buildFullScreenPreview(),
                _buildTopBar(),
                _buildModeSelector(),
                _buildCounterPanel(),
                if (_selectionRect != null) _buildSelectionRect(),
                if (_dotPosition != null) _buildDot(),
                _buildZoomSlider(),
                if (_tapPosition != null) _buildRipple(),
                if (_isIdentifying) _buildIdentifyingIndicator(),
                if (_showingToast) _buildToast(),
                if (_lastError != null) _buildErrorCard(),
                // Listener is TOPMOST so it receives all pointer events first
                Positioned.fill(
                  child: Listener(
                    behavior: HitTestBehavior.translucent,
                    onPointerDown: _onPointerDown,
                    onPointerMove: _onPointerMove,
                    onPointerUp: _onPointerUp,
                    onPointerCancel: _onPointerCancel,
                  ),
                ),"""

code = code.replace(old, new)
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done" if old in open("lib/features/camera/camera_screen.dart", encoding="utf-8").read() == False else "Not found")
