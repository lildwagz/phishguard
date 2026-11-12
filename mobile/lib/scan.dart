import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'api.dart';
import 'history.dart';
import 'widgets.dart';

/// Native side: ScanTextActivity.kt (receives ACTION_PROCESS_TEXT from any app's text-selection menu).
const _channel = MethodChannel('phishguard/process_text');

Future<String?> _nativeText() => _channel.invokeMethod<String>('getText');
Future<void> _nativeClose() => _channel.invokeMethod<void>('close');

/// Small dialog app shown on top of the app the user selected text in.
class ScanApp extends StatelessWidget {
  final Future<String?> Function() loadText;
  final Future<void> Function() close;
  final HistoryStore? store;
  final PhishGuardApi Function(String baseUrl)? apiFactory;

  const ScanApp({
    super.key,
    this.loadText = _nativeText,
    this.close = _nativeClose,
    this.store,
    this.apiFactory,
  });

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PhishGuard',
      debugShowCheckedModeBanner: false,
      theme: phishGuardTheme(),
      home: ScanDialog(
        loadText: loadText,
        close: close,
        store: store ?? HistoryStore(),
        apiFactory: apiFactory ?? PhishGuardApi.new,
      ),
    );
  }
}

class ScanDialog extends StatefulWidget {
  static const maxChars = 2000; // same limit as the API (FR-02)

  final Future<String?> Function() loadText;
  final Future<void> Function() close;
  final HistoryStore store;
  final PhishGuardApi Function(String baseUrl) apiFactory;

  const ScanDialog({
    super.key,
    required this.loadText,
    required this.close,
    required this.store,
    required this.apiFactory,
  });

  @override
  State<ScanDialog> createState() => _ScanDialogState();
}

class _ScanDialogState extends State<ScanDialog> {
  String? _text;
  bool _truncated = false;
  Prediction? _result;
  String? _error;

  @override
  void initState() {
    super.initState();
    _run();
  }

  Future<void> _run() async {
    final raw = (await widget.loadText())?.trim() ?? '';
    if (raw.isEmpty) {
      setState(() => _error = 'Tidak ada teks yang dipilih.');
      return;
    }
    final text = raw.length > ScanDialog.maxChars ? raw.substring(0, ScanDialog.maxChars) : raw;
    setState(() {
      _text = text;
      _truncated = raw.length > ScanDialog.maxChars;
    });
    try {
      final baseUrl = await widget.store.loadApiUrl() ?? defaultBaseUrl();
      final p = await widget.apiFactory(baseUrl).predict(text);
      final oneLine = text.replaceAll(RegExp(r'\s+'), ' ');
      await widget.store.add(HistoryEntry(
        preview: oneLine.length > 80 ? '${oneLine.substring(0, 80)}…' : oneLine,
        label: p.label,
        confidence: p.confidence,
        time: DateTime.now(),
      ));
      if (mounted) setState(() => _result = p);
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black38, // dims the app underneath; window itself is transparent
      body: GestureDetector(
        onTap: widget.close, // tap outside the card closes the popup
        child: Center(
          child: GestureDetector(
            onTap: () {}, // swallow taps on the card itself
            child: Container(
              key: const Key('scanCard'),
              margin: const EdgeInsets.all(20),
              constraints: const BoxConstraints(maxWidth: 480),
              decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
              padding: const EdgeInsets.all(16),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.shield_outlined, color: teal),
                        SizedBox(width: 8),
                        Text('PhishGuard', style: TextStyle(fontWeight: FontWeight.bold, color: navy, fontSize: 18)),
                      ],
                    ),
                    const SizedBox(height: 10),
                    if (_text != null)
                      Text('"${_text!.length > 160 ? '${_text!.substring(0, 160)}…' : _text}"',
                          style: const TextStyle(color: Colors.black54, fontStyle: FontStyle.italic)),
                    if (_truncated)
                      const Padding(
                        padding: EdgeInsets.only(top: 4),
                        child: Text('Teks dipotong ke 2000 karakter pertama.',
                            style: TextStyle(color: Colors.black45, fontSize: 12)),
                      ),
                    const SizedBox(height: 12),
                    if (_result == null && _error == null)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 16),
                        child: Center(child: CircularProgressIndicator()),
                      ),
                    if (_result != null) ResultCard(result: _result!),
                    if (_error != null) ErrorCard(message: _error!),
                    const SizedBox(height: 12),
                    FilledButton(
                      key: const Key('closeButton'),
                      style: FilledButton.styleFrom(backgroundColor: teal),
                      onPressed: widget.close,
                      child: const Text('Tutup'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
