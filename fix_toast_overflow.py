with open("lib/features/camera/camera_screen.dart", encoding="utf-8") as f:
    code = f.read()

# Add _showResultToast method before _showToast
code = code.replace(
    "  void _showToast(String msg) {",
    """  void _showResultToast(Map<String, dynamic> result) {
    String msg;
    if (result['objects'] != null) {
      final count = (result['objects'] as List).length;
      final total = (result['objects'] as List).fold<int>(0, (sum, obj) => sum + (obj['count'] as int? ?? 1));
      msg = 'Found $count types, $total objects total → History';
    } else {
      final name = result['name'] ?? 'Unknown';
      final similar = result['similar'] ?? 0;
      msg = similar > 1 ? 'Found $name x$similar → History' : 'Found $name → History';
    }
    setState(() { _toastMsg = msg; _showingToast = true; });
    Future.delayed(const Duration(seconds: 5), () {
      if (mounted) setState(() { _showingToast = false; });
    });
  }

  void _showToast(String msg) {"""
)

# Add toast state variables after _isIdentifying
code = code.replace(
    "  bool _isIdentifying = false;",
    "  bool _isIdentifying = false;\n  bool _showingToast = false;\n  String _toastMsg = '';"
)

# Replace identify popup in stack with toast
code = code.replace(
    "if (_isIdentifying) _buildIdentifyingIndicator(),",
    "if (_isIdentifying) _buildIdentifyingIndicator(),\n            if (_showingToast) _buildToast(),"
)

# Add _buildToast and _buildIdentifyingIndicator methods before _buildRipple
code = code.replace(
    "  Widget _buildRipple() {",
    """  Widget _buildToast() {
    return Positioned(
      top: 80, left: 24, right: 24,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.75),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFF00FF88).withOpacity(0.5)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('✅ ', style: TextStyle(fontSize: 14)),
            Flexible(child: Text(_toastMsg, style: const TextStyle(color: Colors.white, fontSize: 13), textAlign: TextAlign.center)),
          ],
        ),
      ),
    );
  }

  Widget _buildIdentifyingIndicator() {
    return Positioned(
      top: 80, left: 24, right: 24,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.75),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFF00FF88).withOpacity(0.5)),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF00FF88))),
            SizedBox(width: 10),
            Text('Identifying...', style: TextStyle(color: Colors.white70, fontSize: 13)),
          ],
        ),
      ),
    );
  }

  Widget _buildRipple() {"""
)

# Call _showResultToast after saving to history - replace old setState block
code = code.replace(
    "await _historyService.add(_mode.name, result);",
    "await _historyService.add(_mode.name, result);\n      _showResultToast(result);"
)

# Fix counter panel overflow - top right, constrained
code = code.replace(
    "return Positioned(\n      top: 160, right: 16,",
    "return Positioned(\n      top: 160, right: 16,"
)

# Fix counter panel max width
code = code.replace(
    "constraints: BoxConstraints(minWidth: 160, maxWidth: MediaQuery.of(context).size.width * 0.55, maxHeight: MediaQuery.of(context).size.height * 0.4),",
    "constraints: BoxConstraints(minWidth: 140, maxWidth: MediaQuery.of(context).size.width * 0.45, maxHeight: MediaQuery.of(context).size.height * 0.35),"
)

with open("lib/features/camera/camera_screen.dart", "w", encoding="utf-8") as f:
    f.write(code)
print("Done")
