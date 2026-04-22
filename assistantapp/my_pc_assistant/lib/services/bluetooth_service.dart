import 'package:flutter/foundation.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';

class BluetoothService extends ChangeNotifier {
  List<ScanResult> _scanResults = [];
  bool _isScanning = false;

  List<ScanResult> get scanResults => _scanResults;
  bool get isScanning => _isScanning;

  Future<void> startScan() async {
    if (await FlutterBluePlus.isSupported == false) {
      if (kDebugMode) print("Bluetooth not supported");
      return;
    }

    _isScanning = true;
    _scanResults = [];
    notifyListeners();

    // Lắng nghe kết quả quét
    var subscription = FlutterBluePlus.onScanResults.listen((results) {
      _scanResults = results;
      notifyListeners();
    }, onError: (e) {
      if (kDebugMode) print(e);
    });

    // Bắt đầu quét
    await FlutterBluePlus.startScan(timeout: const Duration(seconds: 15));

    _isScanning = false;
    notifyListeners();
  }

  Future<void> stopScan() async {
    await FlutterBluePlus.stopScan();
    _isScanning = false;
    notifyListeners();
  }

  Future<void> connectToDevice(BluetoothDevice device) async {
    await device.connect(license: License.free);
    if (kDebugMode) print("Connected to ${device.platformName}");
  }

  Future<void> disconnectDevice(BluetoothDevice device) async {
    await device.disconnect();
    if (kDebugMode) print("Disconnected from ${device.platformName}");
  }
}
