import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

class DeviceService extends ChangeNotifier {
  static const platform = MethodChannel('com.mypcassistant/device');
  
  String _androidVersion = "Unknown";
  String get androidVersion => _androidVersion;

  Future<void> fetchAndroidVersion() async {
    try {
      final String result = await platform.invokeMethod('getAndroidVersion');
      _androidVersion = result;
    } on PlatformException catch (e) {
      _androidVersion = "Failed to get version: '${e.message}'.";
    }
    notifyListeners();
  }
}
