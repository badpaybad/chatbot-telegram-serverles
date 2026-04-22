import 'package:flutter/foundation.dart';
import 'package:nfc_manager/nfc_manager.dart';

class NfcService extends ChangeNotifier {
  bool _isAvailable = false;
  String _nfcData = "";

  bool get isAvailable => _isAvailable;
  String get nfcData => _nfcData;

  Future<void> checkAvailability() async {
    _isAvailable = await NfcManager.instance.isAvailable();
    notifyListeners();
  }

  Future<void> startNfcSession() async {
    if (!await NfcManager.instance.isAvailable()) {
      if (kDebugMode) print("NFC is not available on this device");
      return;
    }

    NfcManager.instance.startSession(onDiscovered: (NfcTag tag) async {
      _nfcData = tag.data.toString();
      notifyListeners();
      await NfcManager.instance.stopSession();
    });
  }

  Future<void> stopNfcSession() async {
    await NfcManager.instance.stopSession();
  }
}
