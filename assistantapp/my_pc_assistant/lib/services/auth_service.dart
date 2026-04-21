import 'package:flutter/foundation.dart';
import '../models/user_model.dart';

class AuthService extends ChangeNotifier {
  UserModel? _currentUser;
  bool _isAuthenticated = false;

  UserModel? get currentUser => _currentUser;
  bool get isAuthenticated => _isAuthenticated;

  Future<bool> signIn(String email, String password) async {
    // Giả lập gọi API
    await Future.delayed(const Duration(seconds: 2));
    
    if (email == 'test@gmail.com' && password == '12345678') {
      _currentUser = UserModel(
        id: '1',
        name: 'John Smith',
        email: email,
        profileImageUrl: 'https://i.pravatar.cc/150?u=john',
      );
      _isAuthenticated = true;
      notifyListeners();
      return true;
    }
    return false;
  }

  Future<void> signUp(String name, String phone, String password) async {
    // Giả lập gọi API
    await Future.delayed(const Duration(seconds: 2));
    _currentUser = UserModel(
      id: '2',
      name: name,
      email: 'newuser@gmail.com',
      phoneNumber: phone,
      profileImageUrl: 'https://i.pravatar.cc/150?u=new',
    );
    _isAuthenticated = true;
    notifyListeners();
  }

  void signOut() {
    _currentUser = null;
    _isAuthenticated = false;
    notifyListeners();
  }
}
