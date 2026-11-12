import 'package:flutter/material.dart';

import 'api.dart';

const navy = Color(0xFF1E2A5A);
const teal = Color(0xFF1597AB);
const danger = Color(0xFFC62828);
const safe = Color(0xFF2E7D32);

ThemeData phishGuardTheme() => ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: teal, primary: teal),
      useMaterial3: true,
    );

class ResultCard extends StatelessWidget {
  final Prediction result;
  const ResultCard({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final color = result.isPhishing ? danger : safe;
    final pct = (result.confidence * 100).toStringAsFixed(1);
    return Container(
      key: const Key('resultCard'),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        border: Border.all(color: color, width: 1.5),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Icon(result.isPhishing ? Icons.gpp_bad_outlined : Icons.verified_user_outlined, color: color, size: 40),
          const SizedBox(height: 8),
          Text(result.isPhishing ? 'PHISHING' : 'AMAN',
              style: TextStyle(color: color, fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 1)),
          const SizedBox(height: 4),
          Text('Keyakinan: $pct%', style: const TextStyle(color: navy, fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: result.confidence,
              minHeight: 8,
              color: color,
              backgroundColor: color.withValues(alpha: 0.15),
            ),
          ),
          if (result.reasons.isNotEmpty) ...[
            const SizedBox(height: 10),
            Align(
              alignment: Alignment.centerLeft,
              child: Column(
                key: const Key('reasons'),
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Tanda bahaya terdeteksi:', style: TextStyle(fontWeight: FontWeight.bold, color: navy)),
                  for (final r in result.reasons)
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(Icons.warning_amber_rounded, size: 18, color: color),
                          const SizedBox(width: 6),
                          Expanded(child: Text(r)),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 8),
          Text(
            result.isPhishing
                ? 'Jangan klik tautan, jangan bagikan OTP/PIN, dan jangan transfer uang.'
                : 'Tidak terdeteksi tanda phishing. Tetap waspada terhadap permintaan data pribadi.',
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.black87),
          ),
          const SizedBox(height: 6),
          Text('model ${result.modelVersion} · ${result.latencyMs.toStringAsFixed(1)} ms',
              style: const TextStyle(color: Colors.black45, fontSize: 11)),
        ],
      ),
    );
  }
}

class ErrorCard extends StatelessWidget {
  final String message;
  const ErrorCard({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      key: const Key('errorCard'),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF4E5),
        border: Border.all(color: const Color(0xFFE65100)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          const Icon(Icons.wifi_off, color: Color(0xFFE65100)),
          const SizedBox(width: 10),
          Expanded(child: Text(message)),
        ],
      ),
    );
  }
}

