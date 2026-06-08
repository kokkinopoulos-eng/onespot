import os

history_model = """import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class HistoryEntry {
  final String id;
  final DateTime timestamp;
  final String mode;
  final Map<String, dynamic> result;

  HistoryEntry({
    required this.id,
    required this.timestamp,
    required this.mode,
    required this.result,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'timestamp': timestamp.toIso8601String(),
    'mode': mode,
    'result': result,
  };

  factory HistoryEntry.fromJson(Map<String, dynamic> json) => HistoryEntry(
    id: json['id'],
    timestamp: DateTime.parse(json['timestamp']),
    mode: json['mode'],
    result: Map<String, dynamic>.from(json['result']),
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

  Future<void> add(String mode, Map<String, dynamic> result) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getStringList(_key) ?? [];
    final entry = HistoryEntry(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      timestamp: DateTime.now(),
      mode: mode,
      result: result,
    );
    raw.insert(0, jsonEncode(entry.toJson()));
    if (raw.length > 200) raw.removeLast();
    await prefs.setStringList(_key, raw);
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}
"""

os.makedirs("lib/core/models", exist_ok=True)
os.makedirs("lib/core/services", exist_ok=True)
with open("lib/core/models/history_entry.dart", "w", encoding="utf-8") as f:
    f.write(history_model)
print("Done")
