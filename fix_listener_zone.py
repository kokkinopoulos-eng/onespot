with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Replace Positioned.fill with specific zone listener
code = code.replace(
    """                Positioned.fill(
                  child: Listener(
                    behavior: HitTestBehavior.opaque,
                    onPointerDown: _onPointerDown,
                    onPointerMove: _onPointerMove,
                    onPointerUp: _onPointerUp,
                    onPointerCancel: _onPointerCancel,
                  ),
                ),""",
    """                Positioned(
                  top: 170,
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: Listener(
                    behavior: HitTestBehavior.opaque,
                    onPointerDown: _onPointerDown,
                    onPointerMove: _onPointerMove,
                    onPointerUp: _onPointerUp,
                    onPointerCancel: _onPointerCancel,
                  ),
                ),"""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
