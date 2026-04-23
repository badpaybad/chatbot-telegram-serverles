package com.mypcassistant.my_pc_assistant

import io.flutter.embedding.android.FlutterFragmentActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import android.os.Build

class MainActivity : FlutterFragmentActivity() {
    private val CHANNEL = "com.mypcassistant/device"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            if (call.method == "getAndroidVersion") {
                result.success("Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})")
            } else {
                result.notImplemented()
            }
        }
    }
}
