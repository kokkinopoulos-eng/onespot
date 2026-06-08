with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Add dart:ui import if not present
if "import 'dart:ui'" not in code:
    code = code.replace(
        "import 'package:flutter/material.dart';",
        "import 'dart:ui' as ui;\nimport 'package:flutter/material.dart';"
    )

# Replace takePicture with crop version
old = """      final image = await _controller!.takePicture();
      final bytes = await image.readAsBytes();"""

new = """      final image = await _controller!.takePicture();
      final fullBytes = await image.readAsBytes();
      // Crop around tap point for better identification
      Uint8List bytes = fullBytes;
      if (_tapPosition != null) {
        try {
          final codec = await ui.instantiateImageCodec(fullBytes);
          final frame = await codec.getNextFrame();
          final img = frame.image;
          final screenSize = MediaQuery.of(context).size;
          final scaleX = img.width / screenSize.width;
          final scaleY = img.height / screenSize.height;
          final cropSize = 400.0;
          final cx = (_tapPosition!.dx * scaleX).clamp(cropSize/2, img.width - cropSize/2);
          final cy = (_tapPosition!.dy * scaleY).clamp(cropSize/2, img.height - cropSize/2);
          final recorder = ui.PictureRecorder();
          final canvas = Canvas(recorder);
          final src = Rect.fromLTWH(cx - cropSize/2, cy - cropSize/2, cropSize, cropSize);
          final dst = Rect.fromLTWH(0, 0, cropSize, cropSize);
          canvas.drawImageRect(img, src, dst, Paint());
          final cropped = await recorder.endRecording().toImage(cropSize.toInt(), cropSize.toInt());
          final byteData = await cropped.toByteData(format: ui.ImageByteFormat.png);
          if (byteData != null) bytes = byteData.buffer.asUint8List();
        } catch (e) {
          debugPrint('ONESPOT: crop failed, using full image');
        }
      }"""

code = code.replace(old, new)

# Add Uint8List import if not present
if "dart:typed_data" not in code:
    code = code.replace(
        "import 'dart:ui' as ui;",
        "import 'dart:typed_data';\nimport 'dart:ui' as ui;"
    )

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
