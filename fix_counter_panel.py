with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Hide counter panel when empty
code = code.replace(
    "            // ── Counter panel (outside camera) ──\n            _buildCounterPanel(),",
    "            // ── Counter panel (outside camera) ──\n            if (_counts.isNotEmpty) _buildCounterPanel(),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
