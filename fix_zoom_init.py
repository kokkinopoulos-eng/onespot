with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Init zoom after camera starts
code = code.replace(
    "    if (mounted) setState(() => _isInitialized = true);",
    """    if (mounted) setState(() => _isInitialized = true);
    final zoomLevels = await _controller!.getMaxZoomLevel();
    final minZoom = await _controller!.getMinZoomLevel();
    setState(() { _maxZoom = zoomLevels; _minZoom = minZoom; });"""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
