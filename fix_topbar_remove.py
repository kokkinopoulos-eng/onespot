with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Remove top bar from Column
code = code.replace(
    "            // ── Top bar (outside camera, always above the Expanded area) ──\n            _buildTopBar(),\n",
    ""
)

# Add torch and flip to bottom bar
code = code.replace(
    "        _barBtn('ABOUT', Icons.info_outline, () => Navigator.pushNamed(context, '/about')),",
    "        _barBtn('TORCH', _torchOn ? Icons.flashlight_on : Icons.flashlight_off, _toggleTorch),\n        _barBtn('FLIP', Icons.flip_camera_android, _flipCamera),\n        _barBtn('ABOUT', Icons.info_outline, () => Navigator.pushNamed(context, '/about')),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
