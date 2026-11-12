import 'dart:convert';

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;

/// Default API address: the web build runs on the same machine as the API;
/// the Android emulator reaches the host machine through 10.0.2.2.
String defaultBaseUrl() => kIsWeb ? 'http://localhost:8000' : 'http://10.0.2.2:8000';

class Prediction {
  final String label; // "phishing" | "aman"
  final double confidence; // 0..1
  final String modelVersion;
  final double latencyMs;
  final List<String> reasons; // rule hits explaining a phishing verdict (may be empty)

  const Prediction({
    required this.label,
    required this.confidence,
    required this.modelVersion,
    required this.latencyMs,
    this.reasons = const [],
  });

  bool get isPhishing => label == 'phishing';

  factory Prediction.fromJson(Map<String, dynamic> j) => Prediction(
        label: j['label'] as String,
        confidence: (j['confidence'] as num).toDouble(),
        modelVersion: j['model_version'] as String,
        latencyMs: (j['latency_ms'] as num).toDouble(),
        reasons: [for (final r in (j['reasons'] as List?) ?? const []) r as String],
      );
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

class PhishGuardApi {
  final String baseUrl;
  final http.Client _client;

  PhishGuardApi(this.baseUrl, {http.Client? client}) : _client = client ?? http.Client();

  Future<Prediction> predict(String text) async {
    final http.Response res;
    try {
      res = await _client
          .post(
            Uri.parse('$baseUrl/v1/predict'),
            headers: {'content-type': 'application/json'},
            body: jsonEncode({'text': text}),
          )
          .timeout(const Duration(seconds: 10));
    } catch (_) {
      throw ApiException('Tidak bisa terhubung ke server ($baseUrl). Pastikan API berjalan.');
    }
    if (res.statusCode == 200) {
      return Prediction.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
    }
    if (res.statusCode == 422) {
      throw ApiException('Pesan tidak valid: harus diisi dan maksimal 2000 karakter.');
    }
    if (res.statusCode == 429) {
      throw ApiException('Terlalu banyak permintaan. Tunggu sebentar lalu coba lagi.');
    }
    if (res.statusCode == 413) {
      throw ApiException('Pesan terlalu besar untuk dikirim ke server.');
    }
    throw ApiException('Server error (${res.statusCode}). Coba lagi nanti.');
  }
}
