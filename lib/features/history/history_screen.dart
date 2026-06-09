import 'dart:io';
import 'package:flutter/material.dart';
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

  String _formatDate(DateTime dt) {
    final months = ['Ιαν','Φεβ','Μαρ','Απρ','Μαΐ','Ιουν','Ιουλ','Αυγ','Σεπ','Οκτ','Νοε','Δεκ'];
    return '${dt.day} ${months[dt.month - 1]} ${dt.year}';
  }

  String _formatTime(DateTime dt) =>
      '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';

  Widget _buildThumbnail(String? path) {
    if (path != null && File(path).existsSync()) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(8),
        child: Image.file(
          File(path),
          width: 64,
          height: 64,
          fit: BoxFit.cover,
          cacheWidth: 128,
          errorBuilder: (_, __, ___) => _placeholderThumb(),
        ),
      );
    }
    return _placeholderThumb();
  }

  Widget _placeholderThumb() => Container(
    width: 64,
    height: 64,
    decoration: BoxDecoration(
      color: const Color(0xFF1E1E32),
      borderRadius: BorderRadius.circular(8),
    ),
    child: const Icon(Icons.image_not_supported_outlined, color: Colors.white24, size: 28),
  );

  Widget _buildCountBadge(Map<String, dynamic> result) {
    final String label;
    if (result.containsKey('name') && result.containsKey('count')) {
      label = '${result['count']} ${result['name']}';
    } else {
      // Legacy format: sum all int values
      final total = result.values.whereType<int>().fold(0, (a, b) => a + b);
      label = '$total αντικείμενα';
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: const Color(0xFF00FF88).withAlpha(26),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF00FF88).withAlpha(77)),
      ),
      child: Text(label,
        style: const TextStyle(color: Color(0xFF00FF88), fontSize: 12, fontWeight: FontWeight.bold)),
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
                    title: const Text('Διαγραφή ιστορικού', style: TextStyle(color: Colors.white)),
                    content: const Text('Να διαγραφούν όλες οι εγγραφές;', style: TextStyle(color: Colors.white54)),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Άκυρο')),
                      TextButton(onPressed: () => Navigator.pop(context, true),
                        child: const Text('Διαγραφή', style: TextStyle(color: Color(0xFFFF3C6E)))),
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
                    Text('Δεν υπάρχει ιστορικό', style: TextStyle(color: Colors.white38, fontSize: 16)),
                    SizedBox(height: 4),
                    Text('Κάντε αναγνώριση για να ξεκινήσει', style: TextStyle(color: Colors.white24, fontSize: 13)),
                  ],
                ))
              : ListView.separated(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: _entries.length,
                  separatorBuilder: (_, __) => const Divider(color: Color(0xFF1A1A2E), height: 1),
                  itemBuilder: (_, i) {
                    final e = _entries[i];
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          _buildThumbnail(e.thumbnailPath),
                          const SizedBox(width: 14),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                _buildCountBadge(e.result),
                                const SizedBox(height: 6),
                                Row(
                                  children: [
                                    const Icon(Icons.calendar_today_outlined, size: 12, color: Colors.white38),
                                    const SizedBox(width: 4),
                                    Text(_formatDate(e.timestamp),
                                        style: const TextStyle(color: Colors.white54, fontSize: 12)),
                                    const SizedBox(width: 10),
                                    const Icon(Icons.access_time, size: 12, color: Colors.white24),
                                    const SizedBox(width: 4),
                                    Text(_formatTime(e.timestamp),
                                        style: const TextStyle(color: Colors.white38, fontSize: 12)),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}
