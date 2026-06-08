with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "Offset? _dragStart;" in line or "bool _isDrawing = false;" in line:
        continue
    new_lines.append(line)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Done")
