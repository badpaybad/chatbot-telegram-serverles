import 'package:flutter/material.dart';
import 'local_storage_service.dart';

class ThemeService extends ChangeNotifier {
  final LocalStorageService _storageService;
  ThemeMode _themeMode = ThemeMode.system;

  ThemeService(this._storageService) {
    _loadTheme();
  }

  void _loadTheme() {
    final savedMode = _storageService.themeMode;
    if (savedMode == 'light') {
      _themeMode = ThemeMode.light;
    } else if (savedMode == 'dark') {
      _themeMode = ThemeMode.dark;
    } else {
      _themeMode = ThemeMode.system;
    }
    notifyListeners();
  }

  ThemeMode get themeMode => _themeMode;

  bool get isDarkMode => _themeMode == ThemeMode.dark;

  void toggleTheme() {
    if (_themeMode == ThemeMode.light) {
      setThemeMode(ThemeMode.dark);
    } else {
      setThemeMode(ThemeMode.light);
    }
  }

  void setThemeMode(ThemeMode mode) {
    _themeMode = mode;
    _storageService.setThemeMode(mode.toString().split('.').last);
    notifyListeners();
  }
}
