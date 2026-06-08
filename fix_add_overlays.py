with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Add overlays before zoom slider
code = code.replace(
    "          _buildZoomSlider(),\n          if (_tapPosition != null) _buildRipple(),",
    "          if (_selectionRect != null) _buildSelectionRect(),\n          if (_dotPosition != null) _buildDot(),\n          _buildZoomSlider(),\n          if (_tapPosition != null) _buildRipple(),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
