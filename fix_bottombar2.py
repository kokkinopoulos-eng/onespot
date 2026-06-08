with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Find and replace _buildBottomBar and _barBtn
start = code.find("  Widget _buildBottomBar()")
end = code.find("\n  Widget _", start + 1)
if end == -1:
    end = code.find("\n  // ──", start + 1)

new = """  Widget _buildBottomBar() {
    return Container(
      color: Colors.black,
      padding: const EdgeInsets.fromLTRB(12, 12, 12, 24),
      child: Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [
        _barBtn('CLEAR', Icons.clear, () => setState(() {
          _counts.clear();
          _boundingBoxes.clear();
          _selectionRect = null;
          _dotPosition = null;
          _tapPosition = null;
        })),
        _barBtn('HISTORY', Icons.history, () => Navigator.pushNamed(context, '/history')),
        GestureDetector(
          onTap: () async {
            if (_isPaused) {
              await _controller?.resumePreview();
            } else {
              await _controller?.pausePreview();
            }
            setState(() => _isPaused = !_isPaused);
          },
          child: Container(
            width: 52, height: 52,
            decoration: BoxDecoration(shape: BoxShape.circle,
              color: _isPaused ? const Color(0xFF00FF88) : Colors.transparent,
              border: Border.all(color: const Color(0xFF00FF88), width: 2)),
            child: Center(child: Text(_isPaused ? '▶' : '⏸',
              style: TextStyle(color: _isPaused ? Colors.black : const Color(0xFF00FF88), fontSize: 20))),
          ),
        ),
        _barBtn('SETTINGS', Icons.settings, () => Navigator.pushNamed(context, '/settings')),
        _barBtn('ABOUT', Icons.info_outline, () => Navigator.pushNamed(context, '/about')),
      ]),
    );
  }

  Widget _barBtn(String label, IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        Icon(icon, color: Colors.white54, size: 22),
        const SizedBox(height: 3),
        Text(label, style: const TextStyle(color: Colors.white38, fontSize: 9, letterSpacing: 0.5)),
      ]),
    );
  }
"""

code = code[:start] + new + code[end:]
with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
