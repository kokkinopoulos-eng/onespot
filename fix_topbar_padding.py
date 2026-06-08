with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "  Widget _buildTopBar() {\n    return Container(\n      color: Colors.black,\n      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),",
    "  Widget _buildTopBar() {\n    final topPad = MediaQuery.of(context).padding.top;\n    return Container(\n      color: Colors.black,\n      padding: EdgeInsets.fromLTRB(16, topPad + 8, 16, 8),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
