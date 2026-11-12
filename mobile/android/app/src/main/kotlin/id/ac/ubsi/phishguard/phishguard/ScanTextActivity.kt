package id.ac.ubsi.phishguard.phishguard

import android.content.Intent
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.android.FlutterActivityLaunchConfigs.BackgroundMode
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

/**
 * "Scan dengan PhishGuard" in the text-selection menu of any app (Intent.ACTION_PROCESS_TEXT),
 * and as a Share target (Intent.ACTION_SEND, text/plain) for SMS/chat apps where text cannot be selected.
 * Runs the Dart entrypoint `scanMain` (lib/main.dart) in a transparent window and hands it the selected text.
 * No permissions needed: the user explicitly picks this action for text they selected.
 */
class ScanTextActivity : FlutterActivity() {
    override fun getDartEntrypointFunctionName(): String = "scanMain"

    override fun getBackgroundMode(): BackgroundMode = BackgroundMode.transparent

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "phishguard/process_text")
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "getText" -> result.success(
                        (intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT)
                            ?: intent.getCharSequenceExtra(Intent.EXTRA_TEXT))?.toString()
                    )
                    "close" -> {
                        result.success(null)
                        finish()
                    }
                    else -> result.notImplemented()
                }
            }
    }
}
