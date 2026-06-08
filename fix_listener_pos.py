with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Remove listener from bottom of stack
code = code.replace(
    """                // Listener is TOPMOST so it receives all pointer events first
                Positioned.fill(
                  child: Listener(
                    behavior: HitTestBehavior.opaque,
                    onPointerDown: _onPointerDown,
                    onPointerMove: _onPointerMove,
                    onPointerUp: _onPointerUp,
                    onPointerCancel: _onPointerCancel,
                  ),
                ),""",
    ""
)

# Add listener right after _buildFullScreenPreview
code = code.replace(
    "                _buildFullScreenPreview(),\n                _buildTopBar(),",
    """                _buildFullScreenPreview(),
                Positioned.fill(
                  child: Listener(
                    behavior: HitTestBehavior.opaque,
                    onPointerDown: _onPointerDown,
                    onPointerMove: _onPointerMove,
                    onPointerUp: _onPointerUp,
                    onPointerCancel: _onPointerCancel,
                  ),
                ),
                _buildTopBar(),"""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
