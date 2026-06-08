with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()
code = code.replace(
    "          ],\n        ),\n      ),\n    );\n  }\n  Widget _buildTopBar",
    "          ],\n        ),\n    );\n  }\n  Widget _buildTopBar"
)
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
