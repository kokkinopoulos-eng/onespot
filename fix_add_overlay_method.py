with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

new_method = """  Widget _buildCounterOverlay() {
    return Positioned(
      left: 12,
      bottom: 12,
      child: Container(
        constraints: const BoxConstraints(minWidth: 120, maxWidth: 180, maxHeight: 180),
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.75),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFF00FF88).withOpacity(0.4)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('DETECTED', style: TextStyle(color: Color(0xFF00FF88), fontSize: 9, letterSpacing: 2)),
            const SizedBox(height: 6),
            ..._counts.entries.map((e) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 1),
              child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                Expanded(child: Text(e.key, style: const TextStyle(color: Colors.white, fontSize: 11), overflow: TextOverflow.ellipsis)),
                const SizedBox(width: 8),
                Text(e.value.toString(), style: const TextStyle(color: Color(0xFF00FF88), fontSize: 13, fontWeight: FontWeight.bold)),
              ]),
            )),
            const Divider(color: Color(0xFF00FF88), height: 10, thickness: 0.3),
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              const Text('TOTAL', style: TextStyle(color: Colors.white38, fontSize: 9)),
              Text(_counts.values.fold(0, (a, b) => a + b).toString(),
                style: const TextStyle(color: Color(0xFF00FF88), fontWeight: FontWeight.bold, fontSize: 12)),
            ]),
          ],
        ),
      ),
    );
  }

"""

# Insert before _buildBoundingBoxes
code = code.replace(
    "  Widget _buildBoundingBoxes() {",
    new_method + "  Widget _buildBoundingBoxes() {"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
