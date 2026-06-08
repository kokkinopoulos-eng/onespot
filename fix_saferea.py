with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "      body: SafeArea(\n        child: Column(",
    "      body: Column("
)
code = code.replace(
    "          _buildTopBar(),\n          _buildModeSelector(),",
    "          SafeArea(bottom: false, child: _buildTopBar()),\n          _buildModeSelector(),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
