with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "if (_identifyResult != null || _isIdentifying) _buildIdentifyPopup(),",
    "if (_isIdentifying) _buildIdentifyingIndicator(),\n            if (_showingToast) _buildToast(),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
