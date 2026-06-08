with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "if (mounted) setState(() { _identifyResult = null; _tapPosition = null; _isPaused = false; });",
    "if (mounted) setState(() { _tapPosition = null; _isPaused = false; });"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
