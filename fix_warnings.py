with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "Offset? _rectStart;" in line:
        continue
    if "final previewSize = _controller!.value.previewSize!;" in line:
        continue
    new_lines.append(line)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Done")
