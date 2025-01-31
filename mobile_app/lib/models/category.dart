import 'package:mobile_app/models/file.dart';

class Category {
  final String id;
  final String name;
  List<FileModel> files = [];

  Category({required this.id, required this.name});

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      name: json['name'],
    );
  }
}
