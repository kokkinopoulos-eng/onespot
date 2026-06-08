with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Freeze offset at tap time — save snapshot before API call
code = code.replace(
    "      final pw = _previewRenderSize.width;\n      final ph = _previewRenderSize.height;\n      final ox = _previewOffset.dx;\n      final oy = _previewOffset.dy;",
    "      // Snapshot the preview geometry at tap time — it may change as panels appear/disappear\n      final pw = _previewRenderSize.width;\n      final ph = _previewRenderSize.height;\n      final ox = _previewOffset.dx;\n      final oy = _previewOffset.dy;\n      if (pw == 0 || ph == 0) { setState(() => _lastError = 'Preview not ready — try again'); return; }"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
