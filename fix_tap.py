with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()
code = code.replace(
    "body: GestureDetector(\n        onTapDown: _onTap,\n        child: Stack(\n          fit: StackFit.expand,\n          children: [",
    "body: Stack(\n          fit: StackFit.expand,\n          children: ["
)
code = code.replace(
    "if (_tapPosition != null) _buildRipple(),",
    "if (_tapPosition != null) _buildRipple(),\n            GestureDetector(onTapDown: _onTap, child: Container(color: Colors.transparent)),"
)
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
