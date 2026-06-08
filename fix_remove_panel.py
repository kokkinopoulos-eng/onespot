with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    lines = f.readlines()

# Find and remove _buildCounterPanel method
start = None
depth = 0
end = None
for i, line in enumerate(lines):
    if "_buildCounterPanel()" in line and "Widget" in line:
        start = i
    if start is not None:
        depth += line.count("{") - line.count("}")
        if depth == 0 and i > start:
            end = i
            break

if start is not None and end is not None:
    del lines[start:end+1]
    with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Done")
else:
    print("Not found")
