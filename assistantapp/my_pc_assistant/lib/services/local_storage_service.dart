import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';

class LocalStorageService extends ChangeNotifier {
  static late SharedPreferences _prefs;

  // Keys
  static const String _themeKey = 'theme_mode';
  static const String _userDisplayNameKey = 'user_display_name';
  static const String _notificationsEnabledKey = 'notifications_enabled';

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // Theme preference
  String get themeMode => _prefs.getString(_themeKey) ?? 'system';
  
  Future<void> setThemeMode(String mode) async {
    await _prefs.setString(_themeKey, mode);
    notifyListeners();
  }

  // User display name
  String get userDisplayName => _prefs.getString(_userDisplayNameKey) ?? '';
  
  Future<void> setUserDisplayName(String name) async {
    await _prefs.setString(_userDisplayNameKey, name);
    notifyListeners();
  }

  // Notifications toggle
  bool get notificationsEnabled => _prefs.getBool(_notificationsEnabledKey) ?? true;
  
  Future<void> setNotificationsEnabled(bool enabled) async {
    await _prefs.setBool(_notificationsEnabledKey, enabled);
    notifyListeners();
  }

  // Generic data persistence for "non-important" data
  Future<void> saveData(String key, String value) async {
    await _prefs.setString(key, value);
  }

  String? getData(String key) {
    return _prefs.getString(key);
  }
}
