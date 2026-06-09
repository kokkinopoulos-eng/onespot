with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Update mapping from boxes to points
code = code.replace(
    """      final rects = boxes.map<Rect>((b) {
        final fx = (b['x'] as num).toDouble();
        final fy = (b['y'] as num).toDouble();
        final fw = (b['w'] as num).toDouble();
        final fh = (b['h'] as num).toDouble();
        return Rect.fromLTWH(fx * pw + ox, fy * ph + oy, fw * pw, fh * ph);
      }).toList();""",
    """      final rects = boxes.map<Rect>((b) {
        final cx = b.containsKey('cx') ? (b['cx'] as num).toDouble() : (b['x'] as num).toDouble() + (b['w'] as num).toDouble() / 2;
        final cy = b.containsKey('cy') ? (b['cy'] as num).toDouble() : (b['y'] as num).toDouble() + (b['h'] as num).toDouble() / 2;
        final sx = cx * pw + ox;
        final sy = cy * ph + oy;
        return Rect.fromLTWH(sx - 16, sy - 16, 32, 32);
      }).toList();"""
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
