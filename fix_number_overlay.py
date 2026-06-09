with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

old = """  Widget _buildBoundingBoxes() {
    return Stack(
      children: _boundingBoxes.asMap().entries.map((entry) {
        final r = entry.value;
        final idx = entry.key;
        // Cycle through distinct hues so overlapping boxes are distinguishable.
        final color = HSVColor.fromAHSV(1, (idx * 47.0) % 360, 1, 1).toColor();
        return Positioned(
          left: r.left,
          top: r.top,
          child: Container(
            width: r.width,
            height: r.height,
            decoration: BoxDecoration(
              border: Border.all(color: color, width: 2),
              color: color.withOpacity(0.08),
            ),
            child: r.height > 20
              ? Align(
                  alignment: Alignment.topLeft,
                  child: Container(
                    color: color.withOpacity(0.7),
                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                    child: Text('${idx + 1}',
                        style: const TextStyle(color: Colors.black, fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                )
              : null,
          ),
        );"""

new = """  Widget _buildBoundingBoxes() {
    return Stack(
      children: _boundingBoxes.asMap().entries.map((entry) {
        final r = entry.value;
        final idx = entry.key;
        final cx = r.left + r.width / 2;
        final cy = r.top + r.height / 2;
        return Positioned(
          left: cx - 14,
          top: cy - 14,
          child: Container(
            width: 28, height: 28,
            decoration: BoxDecoration(
              color: const Color(0xFF00FF88),
              shape: BoxShape.circle,
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.5), blurRadius: 4)],
            ),
            child: Center(
              child: Text('${idx + 1}',
                style: const TextStyle(color: Colors.black, fontSize: 13, fontWeight: FontWeight.bold)),
            ),
          ),
        );"""

code = code.replace(old, new)
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done" if old not in open("lib/features/camera/camera_screen.dart", encoding="utf-8").read() else "Not found")
