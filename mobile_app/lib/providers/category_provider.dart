import 'package:flutter/foundation.dart';
import '../models/category.dart' as category_model;
import '../services/api_service.dart';
import './file_provider.dart';

class CategoryProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final FileProvider _fileProvider;
  List<category_model.Category> _categories = [];
  List<category_model.Category> get categories => _categories;

  CategoryProvider(this._fileProvider) {
    _fileProvider.addListener(_updateCategoryFiles);
  }

  @override
  void dispose() {
    _fileProvider.removeListener(_updateCategoryFiles);
    super.dispose();
  }

  Future<void> loadCategories() async {
    _categories = await _apiService.getCategories();
    _updateCategoryFiles();
    notifyListeners();
  }

  void _updateCategoryFiles() {
    final filesByCategory = _fileProvider.getFilesByCategory;
    for (var category in _categories) {
      category.files = filesByCategory[category.id] ?? [];
    }
  }

  Future<void> createCategory(String name) async {
    await _apiService.createCategory(name);
    await loadCategories();
  }
}
