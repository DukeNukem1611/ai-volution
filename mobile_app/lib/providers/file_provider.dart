import 'package:flutter/foundation.dart';
import '../models/file.dart';
import '../services/api_service.dart';
import 'dart:async';

class FileProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  List<FileModel> _files = [];
  List<FileModel> get files => _files;
  Timer? _pollingTimer;

  // Add a list to track files being processed
  List<FileModel> _processingFiles = [];
  List<FileModel> get processingFiles => _processingFiles;

  Map<String, List<FileModel>> get getFilesByCategory {
    Map<String, List<FileModel>> filesByCategory = {};
    for (var file in _files) {
      if (!filesByCategory.containsKey(file.categoryId)) {
        filesByCategory[file.categoryId] = [];
      }
      filesByCategory[file.categoryId]!.add(file);
    }
    return filesByCategory;
  }

  void startPolling() {
    // Poll every 5 seconds
    _pollingTimer =
        Timer.periodic(const Duration(seconds: 10), (_) => loadFiles());
  }

  void stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
  }

  @override
  void dispose() {
    stopPolling();
    super.dispose();
  }

  Future<void> loadFiles() async {
    _files = await _apiService.getFiles();
    notifyListeners();
  }

  Future<void> uploadFiles(List<String> filePaths) async {
    // Add files to processing list first
    for (var path in filePaths) {
      _processingFiles.add(FileModel(
        id: DateTime.now().toString(), // Temporary ID
        filename: path.split('/').last,
        categoryId: 'processing',
        userId: 'processing',
        createdAt: DateTime.now(),
      ));
    }
    notifyListeners();

    // Start upload
    await _apiService.uploadFiles(filePaths);

    // Remove from processing list and refresh files
    _processingFiles.clear();
    await loadFiles();
  }

  Future<void> downloadHighlightedFile(String fileId, String savePath) async {
    await _apiService.downloadHighlightedFile(fileId);
  }
}
