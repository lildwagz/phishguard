import 'package:flutter_test/flutter_test.dart';
import 'package:phishguard/api.dart';

void main() {
  group('baseUrlFor', () {
    test('Android memakai alamat host emulator', () {
      expect(baseUrlFor(isWeb: false, page: null), 'http://10.0.2.2:8000');
    });

    test('web lewat Funnel memakai origin halaman (satu origin dengan nginx)', () {
      expect(baseUrlFor(isWeb: true, page: Uri.parse('https://zam.taile0ea7c.ts.net/')),
          'https://zam.taile0ea7c.ts.net');
    });

    test('web dari container lokal :8080 memakai origin halaman', () {
      expect(baseUrlFor(isWeb: true, page: Uri.parse('http://localhost:8080/#/')),
          'http://localhost:8080');
    });

    test('web dari IP LAN memakai origin halaman', () {
      expect(baseUrlFor(isWeb: true, page: Uri.parse('http://192.168.100.14:8080/')),
          'http://192.168.100.14:8080');
    });

    test('flutter run (dev server localhost port acak) tetap ke API :8000', () {
      expect(baseUrlFor(isWeb: true, page: Uri.parse('http://localhost:53211/')),
          'http://localhost:8000');
    });
  });
}
