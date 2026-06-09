import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:convert';

class HistoryEntry {
  final String id;
  final DateTime timestamp;
  final String mode;
  final Map<String, dynamic> result;
  final String? thumbnailPath;

  HistoryEntry({
    required this.id,
    required this.timestamp,
    required this.mode,
    required this.result,
    this.thumbnailPath,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'timestamp': timestamp.toIso8601String(),
    'mode': mode,
    'result': result,
    if (thumbnailPath != null) 'thumbnailPath': thumbnailPath,
  };

  factory HistoryEntry.fromJson(Map<String, dynamic> json) => HistoryEntry(
    id: json['id'],
    timestamp: DateTime.parse(json['timestamp']),
    mode: json['mode'],
    result: Map<String, dynamic>.from(json['result']),
    thumbnailPath: json['thumbnailPath'] as String?,
  );
}

class HistoryService {
  static const _key = 'onespot_history';

  Future<List<HistoryEntry>> getAll() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_key) ?? [];
    return raw.map((e) => HistoryEntry.fromJson(jsonDecode(e))).toList()
      ..sort((a, b) => b.timestamp.compareTo(a.timestamp));
  }

  /// Saves a history entry. [imageBytes] is the full JPEG frame — stored as a
  /// thumbnail file in the app documents dir.
  Future<void> add(String mode, Map<String, dynamic> result,
      {List<int>? imageBytes}) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_key) ?? [];
    final id = DateTime.now().millisecondsSinceEpoch.toString();

    String? thumbPath;
    if (imageBytes != null) {
      try {
        final dir = await getApplicationDocumentsDirectory();
        final isPng = imageBytes.length >= 4 &&
            imageBytes[0] == 0x89 && imageBytes[1] == 0x50;
        final ext = isPng ? 'png' : 'jpg';
        final file = File('${dir.path}/onespot_thumb_$id.$ext');
        await file.writeAsBytes(imageBytes);
        thumbPath = file.path;
      } catch (e) {
        debugPrint('Thumbnail save failed: $e');
      }
    }

    final entry = HistoryEntry(
      id: id,
      timestamp: DateTime.now(),
      mode: mode,
      result: result,
      thumbnailPath: thumbPath,
    );
    raw.insert(0, jsonEncode(entry.toJson()));
    // Keep at most 100 entries; delete orphaned thumbnail files for removed ones.
    while (raw.length > 100) {
      final removed = HistoryEntry.fromJson(jsonDecode(raw.removeLast()));
      if (removed.thumbnailPath != null) {
        try { File(removed.thumbnailPath!).deleteSync(); } catch (_) {}
      }
    }
    await prefs.setStringList(_key, raw);
  }

  Future<void> clear() async {
    final entries = await getAll();
    for (final e in entries) {
      if (e.thumbnailPath != null) {
        try { File(e.thumbnailPath!).deleteSync(); } catch (_) {}
      }
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
