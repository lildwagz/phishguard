import 'package:flutter/material.dart';

import 'api.dart';
import 'history.dart';
import 'scan.dart';
import 'widgets.dart';

void main() => runApp(const PhishGuardApp());

/// Entry point used by Android's "Scan dengan PhishGuard" text-selection action
/// (ScanTextActivity → ACTION_PROCESS_TEXT). Shows a small result dialog instead of the full app.
@pragma('vm:entry-point')
void scanMain() => runApp(const ScanApp());

class PhishGuardApp extends StatelessWidget {
  final HistoryStore? store;
  final PhishGuardApi Function(String baseUrl)? apiFactory;

  const PhishGuardApp({super.key, this.store, this.apiFactory});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PhishGuard',
      debugShowCheckedModeBanner: false,
      theme: phishGuardTheme(),
      home: HomePage(store: store ?? HistoryStore(), apiFactory: apiFactory ?? PhishGuardApi.new),
    );
  }
}

class HomePage extends StatefulWidget {
  final HistoryStore store;
  final PhishGuardApi Function(String baseUrl) apiFactory;

  const HomePage({super.key, required this.store, required this.apiFactory});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _text = TextEditingController();
  String _baseUrl = defaultBaseUrl();
  bool _loading = false;
  String? _inputError;
  String? _error;
  Prediction? _result;
  List<HistoryEntry> _history = [];

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    final url = await widget.store.loadApiUrl();
    final history = await widget.store.load();
    if (!mounted) return;
    setState(() {
      if (url != null && url.isNotEmpty) _baseUrl = url;
      _history = history;
    });
  }

  Future<void> _analyze() async {
    final text = _text.text;
    if (text.trim().isEmpty) {
      // FR-02: validate before calling the API
      setState(() {
        _inputError = 'Teks pesan tidak boleh kosong';
        _result = null;
        _error = null;
      });
      return;
    }
    setState(() {
      _loading = true;
      _inputError = null;
      _error = null;
      _result = null;
    });
    try {
      final p = await widget.apiFactory(_baseUrl).predict(text);
      final oneLine = text.trim().replaceAll(RegExp(r'\s+'), ' ');
      final history = await widget.store.add(HistoryEntry(
        preview: oneLine.length > 80 ? '${oneLine.substring(0, 80)}…' : oneLine,
        label: p.label,
        confidence: p.confidence,
        time: DateTime.now(),
      ));
      if (!mounted) return;
      setState(() {
        _result = p;
        _history = history;
      });
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _editApiUrl() async {
    final c = TextEditingController(text: _baseUrl);
    final url = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Alamat server API'),
        content: TextField(
          controller: c,
          decoration: const InputDecoration(hintText: 'http://10.0.2.2:8000'),
          keyboardType: TextInputType.url,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Batal')),
          FilledButton(onPressed: () => Navigator.pop(ctx, c.text.trim()), child: const Text('Simpan')),
        ],
      ),
    );
    if (url == null || url.isEmpty) return;
    final clean = url.endsWith('/') ? url.substring(0, url.length - 1) : url;
    await widget.store.saveApiUrl(clean);
    setState(() => _baseUrl = clean);
  }

  Future<void> _clearHistory() async {
    await widget.store.clear();
    setState(() => _history = []);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PhishGuard', style: TextStyle(color: navy, fontWeight: FontWeight.bold)),
        centerTitle: true,
        actions: [
          IconButton(
            tooltip: 'Pengaturan server',
            icon: const Icon(Icons.settings_outlined),
            onPressed: _editApiUrl,
          ),
        ],
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(2),
          child: ColoredBox(color: teal, child: SizedBox(height: 2, width: double.infinity)),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 560),
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                const Text('Teks pesan (SMS/Email)',
                    style: TextStyle(fontWeight: FontWeight.bold, color: navy, fontSize: 16)),
                const SizedBox(height: 8),
                TextField(
                  key: const Key('messageField'),
                  controller: _text,
                  minLines: 5,
                  maxLines: 10,
                  maxLength: 2000,
                  decoration: InputDecoration(
                    hintText: 'Tempel atau ketik pesan di sini...',
                    errorText: _inputError,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                    filled: true,
                    fillColor: const Color(0xFFF9FAFB),
                  ),
                  onChanged: (_) {
                    if (_inputError != null) setState(() => _inputError = null);
                  },
                ),
                const SizedBox(height: 8),
                SizedBox(
                  height: 52,
                  child: FilledButton(
                    key: const Key('analyzeButton'),
                    style: FilledButton.styleFrom(
                      backgroundColor: teal,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: _loading ? null : _analyze,
                    child: _loading
                        ? const SizedBox(
                            width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white))
                        : const Text('Analisis', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  ),
                ),
                const SizedBox(height: 16),
                if (_result != null) ResultCard(result: _result!),
                if (_error != null) ErrorCard(message: _error!),
                const SizedBox(height: 24),
                Row(
                  children: [
                    const Expanded(
                      child: Text('Riwayat (di perangkat ini)',
                          style: TextStyle(fontWeight: FontWeight.bold, color: navy, fontSize: 16)),
                    ),
                    if (_history.isNotEmpty)
                      TextButton.icon(
                        onPressed: _clearHistory,
                        icon: const Icon(Icons.delete_outline, size: 18),
                        label: const Text('Hapus'),
                      ),
                  ],
                ),
                if (_history.isEmpty)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 8),
                    child: Text('Belum ada analisis.', style: TextStyle(color: Colors.black54)),
                  ),
                for (final h in _history) HistoryTile(entry: h),
                const SizedBox(height: 16),
                Text('Server: $_baseUrl',
                    textAlign: TextAlign.center, style: const TextStyle(color: Colors.black45, fontSize: 12)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class HistoryTile extends StatelessWidget {
  final HistoryEntry entry;
  const HistoryTile({super.key, required this.entry});

  @override
  Widget build(BuildContext context) {
    final phishing = entry.label == 'phishing';
    final t = entry.time;
    String two(int n) => n.toString().padLeft(2, '0');
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(phishing ? Icons.gpp_bad_outlined : Icons.verified_user_outlined, color: phishing ? danger : safe),
      title: Text(entry.preview, maxLines: 2, overflow: TextOverflow.ellipsis),
      subtitle: Text(
          '${phishing ? 'Phishing' : 'Aman'} · ${(entry.confidence * 100).toStringAsFixed(0)}% · '
          '${two(t.day)}/${two(t.month)} ${two(t.hour)}:${two(t.minute)}'),
    );
  }
}
