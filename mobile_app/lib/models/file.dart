class FileModel {
  final String id;
  final String filename;
  final String categoryId;
  final String? summary;
  final String? highlightedFilename;
  final String userId;
  final DateTime createdAt;

  FileModel({
    required this.id,
    required this.filename,
    required this.categoryId,
    this.summary,
    this.highlightedFilename,
    required this.userId,
    required this.createdAt,
  });

  factory FileModel.fromJson(Map<String, dynamic> json) {
    return FileModel(
      id: json['id'],
      filename: json['original_filename'] ?? '',
      categoryId: json['category_id'] ?? '',
      summary: json['summary'] ?? '',
      highlightedFilename: json['highlighted_filename'] ?? '',
      userId: json['user_id'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
