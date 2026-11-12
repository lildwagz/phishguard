import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:phishguard/api.dart';
import 'package:phishguard/main.dart';
import 'package:shared_preferences/shared_preferences.dart';

PhishGuardApi Function(String) fakeApi(http.Response Function(http.Request) handler, {List<String>? sent}) =>
    (url) => PhishGuardApi(url, client: MockClient((req) async {
          sent?.add(req.body);
          return handler(req);
        }));

http.Response ok(String label, double conf) => http.Response(
    jsonEncode({'label': label, 'confidence': conf, 'model_version': 'test-1', 'latency_ms': 3.2}), 200);

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));

  testWidgets('empty input shows validation error and does not call the API (FR-02)', (tester) async {
    final sent = <String>[];
    await tester.pumpWidget(PhishGuardApp(apiFactory: fakeApi((_) => ok('aman', 0.9), sent: sent)));
    await tester.enterText(find.byKey(const Key('messageField')), '   ');
    await tester.tap(find.byKey(const Key('analyzeButton')));
    await tester.pumpAndSettle();
    expect(find.text('Teks pesan tidak boleh kosong'), findsOneWidget);
    expect(sent, isEmpty);
  });

  testWidgets('phishing result shows label, confidence and is added to history (FR-01, FR-03)', (tester) async {
    final sent = <String>[];
    await tester.pumpWidget(PhishGuardApp(apiFactory: fakeApi((_) => ok('phishing', 0.973), sent: sent)));
    await tester.enterText(find.byKey(const Key('messageField')), 'Selamat anda menang, klik bit.ly/x');
    await tester.tap(find.byKey(const Key('analyzeButton')));
    await tester.pumpAndSettle();

    expect(jsonDecode(sent.single), {'text': 'Selamat anda menang, klik bit.ly/x'});
    expect(find.text('PHISHING'), findsOneWidget);
    expect(find.text('Keyakinan: 97.3%'), findsOneWidget);
    // history list sits below the result card; scroll so the lazily-built ListView creates it
    await tester.scrollUntilVisible(find.textContaining('Phishing · 97%'), 200,
        scrollable: find.byType(Scrollable).first); // .first = page ListView (the TextField has its own)
    expect(find.textContaining('Phishing · 97%'), findsOneWidget);

    final saved = (await SharedPreferences.getInstance()).getStringList('history')!;
    expect(saved, hasLength(1));
  });

  testWidgets('rule reasons from the API are listed on the result card', (tester) async {
    await tester.pumpWidget(PhishGuardApp(
        apiFactory: fakeApi((_) => http.Response(
            jsonEncode({
              'label': 'phishing',
              'confidence': 0.95,
              'model_version': 'test-1',
              'latency_ms': 2.0,
              'reasons': ['Meminta membuka/menginstal file .apk'],
            }),
            200))));
    await tester.enterText(find.byKey(const Key('messageField')), 'LIHAT_FOTO_PAKET.apk');
    await tester.tap(find.byKey(const Key('analyzeButton')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('reasons')), findsOneWidget);
    expect(find.text('Meminta membuka/menginstal file .apk'), findsOneWidget);
  });

  testWidgets('safe result shows AMAN', (tester) async {
    await tester.pumpWidget(PhishGuardApp(apiFactory: fakeApi((_) => ok('aman', 0.88))));
    await tester.enterText(find.byKey(const Key('messageField')), 'Besok kumpul jam 4 ya');
    await tester.tap(find.byKey(const Key('analyzeButton')));
    await tester.pumpAndSettle();
    expect(find.text('AMAN'), findsOneWidget);
  });

  testWidgets('server down shows a friendly error', (tester) async {
    await tester.pumpWidget(PhishGuardApp(
        apiFactory: (url) => PhishGuardApi(url, client: MockClient((_) async => throw Exception('refused')))));
    await tester.enterText(find.byKey(const Key('messageField')), 'halo');
    await tester.tap(find.byKey(const Key('analyzeButton')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('errorCard')), findsOneWidget);
    expect(find.textContaining('Tidak bisa terhubung'), findsOneWidget);
  });

  testWidgets('rate limited (429) shows a wait message', (tester) async {
    await tester.pumpWidget(PhishGuardApp(apiFactory: fakeApi((_) => http.Response('{"detail":"x"}', 429))));
    await tester.enterText(find.byKey(const Key('messageField')), 'halo');
    await tester.tap(find.byKey(const Key('analyzeButton')));
    await tester.pumpAndSettle();
    expect(find.textContaining('Terlalu banyak permintaan'), findsOneWidget);
  });
}
