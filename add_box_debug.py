with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    "      debugPrint('BOXES: ${rects.length}  previewSize=$_previewRenderSize  offset=$_previewOffset');",
    "      debugPrint('BOXES: ${rects.length}  previewSize=$_previewRenderSize  offset=$_previewOffset');\n      if (rects.isNotEmpty) debugPrint('BOX0: fraction=(${boxes[0]['x']},${boxes[0]['y']},${boxes[0]['w']},${boxes[0]['h']}) screen=${rects[0]}');"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
