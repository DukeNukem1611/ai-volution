import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/category.dart';
import '../models/file.dart';
import 'package:dio/dio.dart';
import '../models/news_article.dart';

class ApiService {
  static const String baseUrl = 'https://3p4ldmwd-8000.inc1.devtunnels.ms';
  // 'http://localhost:8000';
  String? _token;
  static const String tokenKey = 'jwt_token';
  late Dio _dio;

  // Add constructor to load token
  ApiService() {
    _loadToken().then((_) {
      if (_token != null) {
        print('Token loaded: $_token');
      }
    });
    _dio = Dio();
  }

  // Add method to load token from SharedPreferences
  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(tokenKey);
  }

  Future<bool> checkLoggedIn() async {
    await _loadToken();
    if (_token != null) {
      print('Token loaded: $_token');
      return true;
    }
    return false;
  }

  // Add method to save token
  Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(tokenKey, token);
    _token = token;
  }

  // Add method to clear token
  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(tokenKey);
    _token = null;
  }

  Future<Map<String, dynamic>> register(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users/register'),
      body: json.encode({'email': email, 'password': password}),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to register');
  }

  Future<String> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users/login'),
      body: json.encode({'email': email, 'password': password}),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final token = data['access_token'];
      await _saveToken(token);
      return token;
    }
    throw Exception('Failed to login');
  }

  Future<List<Category>> getCategories() async {
    final response = await http.get(
      Uri.parse('$baseUrl/categories/'),
      headers: {'Authorization': 'Bearer $_token'},
    );

    if (response.statusCode == 200) {
      List<dynamic> data = json.decode(response.body);
      return data.map((json) => Category.fromJson(json)).toList();
    }
    throw Exception('Failed to load categories');
  }

  Future<Category> createCategory(String name) async {
    final response = await http.post(
      Uri.parse('$baseUrl/categories/'),
      headers: {
        'Authorization': 'Bearer $_token',
        'Content-Type': 'application/json',
      },
      body: json.encode({'name': name}),
    );

    if (response.statusCode == 200) {
      return Category.fromJson(json.decode(response.body));
    }
    throw Exception('Failed to create category');
  }

  Future<FileModel> uploadFile(String filePath, String categoryId) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/files/'),
    );

    request.headers['Authorization'] = 'Bearer $_token';
    request.files.add(await http.MultipartFile.fromPath('file', filePath));

    var response = await request.send();
    var responseData = await response.stream.bytesToString();

    if (response.statusCode == 200) {
      return FileModel.fromJson(json.decode(responseData));
    }
    throw Exception('Failed to upload file');
  }

  Future<List<FileModel>> getFiles() async {
    final response = await http.get(
      Uri.parse('$baseUrl/files/'),
      headers: {'Authorization': 'Bearer $_token'},
    );

    if (response.statusCode == 200) {
      List<dynamic> data = json.decode(response.body);
      return data.map((json) => FileModel.fromJson(json)).toList();
    }
    // throw Exception('Failed to load files');
    return [];
  }

  Future<List<int>> downloadHighlightedFile(String fileId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/files/$fileId/highlighted'),
      headers: {'Authorization': 'Bearer $_token'},
    );

    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      throw Exception('Failed to download file');
    }
  }

  Future<void> uploadFiles(List<String> filePaths) async {
    // Implement your file upload logic here
    // Example:
    for (var path in filePaths) {
      // Add your API call to upload each file
      await uploadFile(path, 'processing');
    }
  }

  // Add method to check if user is logged in
  bool get isLoggedIn => _token != null;

  Future<NewsResponse> getNews({int page = 1}) async {
    // final response = await _dio.get('/news/', queryParameters: {'page': page});
    final test_categories = ["Politics", "Technology", "Health"];

    final response = await http.get(
      Uri.parse('$baseUrl/news/?categories=${test_categories.join(',')}'),
      headers: {'Authorization': 'Bearer $_token'},
    );
    print(response.body);
    if (response.statusCode == 200) {
      return NewsResponse.fromJson(json.decode(response.body));
    }
    throw Exception('Failed to load news');
  }

  Future<void> resetNewsHistory() async {
    // await _dio.post('/news/reset-history');
    final response = await http.post(
      Uri.parse('$baseUrl/news/reset-history'),
      headers: {'Authorization': 'Bearer $_token'},
    );
    if (response.statusCode == 200) {
      return;
    }
    throw Exception('Failed to reset news history');
  }
}
