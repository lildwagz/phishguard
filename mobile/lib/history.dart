import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

/// FR-03: analysis history stored only on this device (never sent to the server).
class HistoryEntry {
  final String preview; // first 80 characters of the message
  final String label;
  final double confidence;
  final DateTime time;

  const HistoryEntry({required this.preview, required this.label, required this.confidence, required this.time});

  Map<String, dynamic> toJson() =>
      {'preview': preview, 'label': label, 'confidence': confidence, 'time': time.toIso8601String()};

  factory HistoryEntry.fromJson(Map<String, dynamic> j) => HistoryEntry(
        preview: j['preview'] as String,
        label: j['label'] as String,
        confidence: (j['confidence'] as num).toDouble(),
        time: DateTime.parse(j['time'] as String),
      );
}

class HistoryStore {
  static const _key = 'history';
  static const _apiKey = 'api_base_url';
  static const maxEntries = 50;

  Future<List<HistoryEntry>> load() async {
    final prefs = await SharedPreferences.getInstance();
    return (prefs.getStringList(_key) ?? [])
        .map((s) => HistoryEntry.fromJson(jsonDecode(s) as Map<String, dynamic>))
        .toList();
  }

  Future<List<HistoryEntry>> add(HistoryEntry e) async {
    final items = [e, ...await load()].take(maxEntries).toList();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_key, items.map((x) => jsonEncode(x.toJson())).toList());
    return items;
  }

  Future<void> clear() async => (await SharedPreferences.getInstance()).remove(_key);

  Future<String?> loadApiUrl() async => (await SharedPreferences.getInstance()).getString(_apiKey);

  Future<void> saveApiUrl(String url) async => (await SharedPreferences.getInstance()).setString(_apiKey, url);
}
