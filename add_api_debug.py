with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "      debugPrint('BOXES: ${rects.length}  previewSize=$_previewRenderSize  offset=$_previewOffset');",
    "      debugPrint('BOXES: ${rects.length}  previewSize=$_previewRenderSize  offset=$_previewOffset');\n      if (boxes.isNotEmpty) debugPrint('BOX_RAW: ${boxes[0]}');"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
