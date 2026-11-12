import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:phishguard/api.dart';
import 'package:phishguard/scan.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));

  PhishGuardApi Function(String) fake(List<String> sent) => (url) => PhishGuardApi(url,
      client: MockClient((req) async {
        sent.add((jsonDecode(req.body) as Map)['text'] as String);
        return http.Response(
            jsonEncode({
              'label': 'phishing',
              'confidence': 0.95,
              'model_version': 't',
              'latency_ms': 1.0,
              'reasons': ['Meminta membuka/menginstal file .apk'],
            }),
            200);
      }));

  testWidgets('selected text is scanned and result shown with reasons', (tester) async {
    final sent = <String>[];
    var closed = false;
    await tester.pumpWidget(ScanApp(
      loadText: () async => '  Ini foto paket kakak: LIHAT_FOTO_PAKET.apk ',
      close: () async => closed = true,
      apiFactory: fake(sent),
    ));
    await tester.pumpAndSettle();
    expect(sent, ['Ini foto paket kakak: LIHAT_FOTO_PAKET.apk']);
    expect(find.text('PHISHING'), findsOneWidget);
    expect(find.text('Meminta membuka/menginstal file .apk'), findsOneWidget);
    expect((await SharedPreferences.getInstance()).getStringList('history'), hasLength(1));

    await tester.tap(find.byKey(const Key('closeButton')));
    expect(closed, isTrue);
  });

  testWidgets('long selection is truncated to 2000 chars before calling the API', (tester) async {
    final sent = <String>[];
    await tester.pumpWidget(ScanApp(loadText: () async => 'a' * 2500, close: () async {}, apiFactory: fake(sent)));
    await tester.pumpAndSettle();
    expect(sent.single.length, 2000);
    expect(find.text('Teks dipotong ke 2000 karakter pertama.'), findsOneWidget);
  });

  testWidgets('empty selection shows a message and never calls the API', (tester) async {
    final sent = <String>[];
    await tester.pumpWidget(ScanApp(loadText: () async => null, close: () async {}, apiFactory: fake(sent)));
    await tester.pumpAndSettle();
    expect(sent, isEmpty);
    expect(find.text('Tidak ada teks yang dipilih.'), findsOneWidget);
  });
}
