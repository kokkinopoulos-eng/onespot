with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()
code = code.replace(
    "CameraPreview(_controller!),",
    "SizedBox.expand(child: FittedBox(fit: BoxFit.cover, child: SizedBox(width: _controller!.value.previewSize!.height, height: _controller!.value.previewSize!.width, child: CameraPreview(_controller!)))),"
)
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
