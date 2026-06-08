with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Remove counter panel from Column
code = code.replace(
    "            // ── Counter panel (outside camera) ──\n            if (_counts.isNotEmpty) _buildCounterPanel(),",
    ""
)

# Add counter panel as overlay inside Stack (above bounding boxes, below toast)
code = code.replace(
    "                    if (_isIdentifying) _buildIdentifyingIndicator(),",
    "                    if (_counts.isNotEmpty) _buildCounterOverlay(),\n                    if (_isIdentifying) _buildIdentifyingIndicator(),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
