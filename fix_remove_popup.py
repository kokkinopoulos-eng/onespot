with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Find and remove _buildIdentifyPopup method
start = code.find("  Widget _buildIdentifyPopup()")
if start != -1:
    # Find the next method after it
    next_method = code.find("\n  Widget ", start + 1)
    if next_method == -1:
        next_method = code.find("\n  void ", start + 1)
    if next_method != -1:
        code = code[:start] + code[next_method+1:]

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
