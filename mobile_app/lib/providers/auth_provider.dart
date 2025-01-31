import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService;
  bool _isAuthenticated = false;

  AuthProvider(this._apiService);

  bool get isAuthenticated => _isAuthenticated;

  Future<void> login(String email, String password) async {
    final token = await _apiService.login(email, password);
    if (token != null) {
      _isAuthenticated = true;
      notifyListeners();
    }
  }

  Future<void> register(String email, String password) async {
    await _apiService.register(email, password);
  }

  Future<void> logout() async {
    await _apiService.clearToken();
    _isAuthenticated = false;
    notifyListeners();
  }

  Future<bool> tryAutoLogin() async {
    if (await _apiService.checkLoggedIn()) {
      _isAuthenticated = true;
      notifyListeners();
      return true;
    }
    return false;
  }
}
