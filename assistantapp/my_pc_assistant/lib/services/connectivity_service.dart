import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';

class ConnectivityService extends ChangeNotifier {
  List<ConnectivityResult> _connectionStatus = [ConnectivityResult.none];
  final Connectivity _connectivity = Connectivity();

  List<ConnectivityResult> get connectionStatus => _connectionStatus;

  ConnectivityService() {
    _connectivity.onConnectivityChanged.listen((List<ConnectivityResult> result) {
      _connectionStatus = result;
      notifyListeners();
    });
  }

  Future<void> checkConnectivity() async {
    _connectionStatus = await _connectivity.checkConnectivity();
    notifyListeners();
  }

  bool get isWifi => _connectionStatus.contains(ConnectivityResult.wifi);
  bool get isMobile => _connectionStatus.contains(ConnectivityResult.mobile);
  bool get isConnected => !_connectionStatus.contains(ConnectivityResult.none);
}
