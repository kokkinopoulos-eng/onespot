with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    lines = f.readlines()

# Find Positioned.fill with Listener
listener_start = None
listener_end = None
for i, line in enumerate(lines):
    if "Positioned.fill" in line and listener_start is None:
        # Check if next lines contain Listener
        for j in range(i, min(i+5, len(lines))):
            if "Listener(" in lines[j]:
                listener_start = i
                break
    if listener_start is not None and listener_end is None:
        if i > listener_start and "),\n" == lines[i] and lines[i-1].strip() == "),":
            listener_end = i
            break

print(f"Listener block: {listener_start} to {listener_end}")

if listener_start and listener_end:
    listener_block = lines[listener_start:listener_end+1]
    # Remove from current position
    del lines[listener_start:listener_end+1]
    # Find _buildErrorCard and insert after it
    for i, line in enumerate(lines):
        if "_buildErrorCard" in line:
            lines.insert(i+1, "".join(listener_block))
            break
    with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("Done")
else:
    print("Not found")
