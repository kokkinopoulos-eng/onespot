code = """import 'package:flutter/material.dart';
import '../../core/models/history_entry.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});
  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final HistoryService _service = HistoryService();
  List<HistoryEntry> _entries = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final entries = await _service.getAll();
    setState(() { _entries = entries; _loading = false; });
  }

  Future<void> _clear() async {
    await _service.clear();
    setState(() => _entries.clear());
  }

  String _formatTime(DateTime dt) {
    return '\${dt.day}/\${dt.month}/\${dt.year} \${dt.hour.toString().padLeft(2,'0')}:\${dt.minute.toString().padLeft(2,'0')}';
  }

  String _modeIcon(String mode) {
    switch (mode) {
      case 'identify': return '🔍';
      case 'countOne': return '🎯';
      case 'freeCount': return '📊';
      default: return '📌';
    }
  }

  Widget _buildResult(Map<String, dynamic> result) {
    if (result['objects'] != null) {
      final objects = result['objects'] as List;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: objects.map((obj) => Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(obj['name'] ?? '', style: const TextStyle(color: Colors.white70, fontSize: 13)),
            Text('\${obj['count']}', style: const TextStyle(color: Color(0xFF00FF88), fontSize: 13, fontWeight: FontWeight.bold)),
          ],
        )).toList(),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(result['name'] ?? '', style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.bold)),
        if (result['description'] != null)
          Text(result['description'], style: const TextStyle(color: Colors.white54, fontSize: 12)),
        if ((result['similar'] ?? 0) > 0)
          Text('Similar: \${result['similar']}', style: const TextStyle(color: Color(0xFF00FF88), fontSize: 12)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF080810),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F0F1A),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: RichText(text: const TextSpan(
          style: TextStyle(fontFamily: 'BebasNeue', fontSize: 22, letterSpacing: 2),
          children: [
            TextSpan(text: 'ONE', style: TextStyle(color: Colors.white)),
            TextSpan(text: 'SPOT', style: TextStyle(color: Color(0xFF00FF88))),
            TextSpan(text: ' History', style: TextStyle(color: Colors.white)),
          ],
        )),
        actions: [
          if (_entries.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_outline, color: Colors.white54),
              onPressed: () async {
                final confirm = await showDialog<bool>(
                  context: context,
                  builder: (_) => AlertDialog(
                    backgroundColor: const Color(0xFF0F0F1A),
                    title: const Text('Clear History', style: TextStyle(color: Colors.white)),
                    content: const Text('Delete all entries?', style: TextStyle(color: Colors.white54)),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                      TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Clear', style: TextStyle(color: Color(0xFFFF3C6E)))),
                    ],
                  ),
                );
                if (confirm == true) _clear();
              },
            ),
        ],
      ),
      body: _loading
        ? const Center(child: CircularProgressIndicator(color: Color(0xFF00FF88)))
        : _entries.isEmpty
          ? const Center(child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('📋', style: TextStyle(fontSize: 48)),
                SizedBox(height: 12),
                Text('No history yet', style: TextStyle(color: Colors.white38, fontSize: 16)),
                SizedBox(height: 4),
                Text('Tap to identify objects', style: TextStyle(color: Colors.white24, fontSize: 13)),
              ],
            ))
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: _entries.length,
              separatorBuilder: (_, __) => const Divider(color: Color(0xFF1E1E32), height: 1),
              itemBuilder: (_, i) {
                final e = _entries[i];
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(_modeIcon(e.mode), style: const TextStyle(fontSize: 20)),
                      const SizedBox(width: 12),
                      Expanded(child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildResult(e.result),
                          const SizedBox(height: 4),
                          Text(_formatTime(e.timestamp), style: const TextStyle(color: Colors.white24, fontSize: 11)),
                        ],
                      )),
                    ],
                  ),
                );
              },
            ),
    );
  }
}
"""
with open("lib/features/history/history_screen.dart", "w", encoding="utf-8") as f:
    import os
    os.makedirs("lib/features/history", exist_ok=True)
    f.write(code)
print("Done")
