with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Find and replace _buildCameraPreview with simple version
old_start = code.find("  Widget _buildCameraPreview()")
old_end = code.find("\n  Widget _", old_start + 1)
if old_start == -1 or old_end == -1:
    old_start = code.find("  Widget _buildFullScreenPreview()")
    old_end = code.find("\n  Widget _", old_start + 1)

new_method = """  Widget _buildCameraPreview() {
    return SizedBox.expand(
      child: FittedBox(
        fit: BoxFit.cover,
        child: SizedBox(
          width: _controller!.value.previewSize!.height,
          height: _controller!.value.previewSize!.width,
          child: CameraPreview(_controller!),
        ),
      ),
    );
  }
"""

code = code[:old_start] + new_method + code[old_end+1:]
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
