import 'package:flutter/material.dart';
import 'package:mobile_app/main.dart';
import 'package:mobile_app/models/category.dart';
import 'package:provider/provider.dart';
import '../providers/category_provider.dart';
import '../providers/file_provider.dart';
import 'category_screen.dart';
import 'upload_screen.dart';
import 'package:google_fonts/google_fonts.dart';

class DocumentScreen extends StatefulWidget {
  const DocumentScreen({super.key});

  @override
  State<DocumentScreen> createState() => _DocumentScreenState();
}

class _DocumentScreenState extends State<DocumentScreen> {
  late FileProvider _fileProvider;
  final List<List<Color>> gradients = [
    [const Color(0xFF4F46E5), const Color(0xFF3730A3)], // Indigo gradient
    [const Color(0xFF7C3AED), const Color(0xFF5B21B6)], // Purple gradient
    [const Color(0xFFEA580C), const Color(0xFFC2410C)], // Orange gradient
    [const Color(0xFF0891B2), const Color(0xFF0E7490)], // Cyan gradient
    [const Color(0xFF059669), const Color(0xFF047857)], // Emerald gradient
    [const Color(0xFFDB2777), const Color(0xFFBE185D)], // Pink gradient
  ];

  @override
  void initState() {
    super.initState();
    _fileProvider = Provider.of<FileProvider>(context, listen: false);
    _loadData();
    _fileProvider.startPolling();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _fileProvider = Provider.of<FileProvider>(context, listen: false);
    _loadData();
  }

  @override
  void dispose() {
    _fileProvider.stopPolling();
    super.dispose();
  }

  Future<void> _loadData() async {
    if (!mounted) return;

    // Load files first
    await _fileProvider.loadFiles();

    // Then load categories, which will use the files data
    if (!mounted) return;
    await Provider.of<CategoryProvider>(context, listen: false)
        .loadCategories();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: primaryColor.withOpacity(0.15),
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Icon(
                Icons.folder_special,
                color: primaryColor,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Text(
              'Document Manager',
              style: GoogleFonts.poppins(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            child: IconButton(
              icon: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: surfaceColor,
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: const Icon(Icons.upload_rounded, size: 24),
              ),
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const UploadScreen()),
                );
              },
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          Consumer<FileProvider>(
            builder: (context, fileProvider, _) {
              if (fileProvider.processingFiles.isEmpty) {
                return const SizedBox.shrink();
              }
              return Container(
                margin: const EdgeInsets.all(16),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: surfaceColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Processing Files',
                      style: GoogleFonts.poppins(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...fileProvider.processingFiles.map((file) => ListTile(
                          leading: const CircularProgressIndicator(),
                          title: Text(
                            file.filename,
                            style: GoogleFonts.poppins(color: Colors.white70),
                          ),
                          subtitle: Text(
                            'Processing...',
                            style: GoogleFonts.poppins(color: Colors.white54),
                          ),
                        )),
                  ],
                ),
              );
            },
          ),
          Expanded(
            child: Consumer<CategoryProvider>(
              builder: (context, categoryProvider, _) {
                final categories = categoryProvider.categories;
                return categories.isEmpty
                    ? _buildEmptyState()
                    : Container(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                            colors: [
                              backgroundColor,
                              backgroundColor.withOpacity(0.9),
                            ],
                          ),
                        ),
                        child: GridView.builder(
                          padding: const EdgeInsets.all(24),
                          gridDelegate:
                              SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount:
                                MediaQuery.of(context).size.width > 600 ? 3 : 2,
                            childAspectRatio: 1.1,
                            crossAxisSpacing: 20,
                            mainAxisSpacing: 20,
                          ),
                          itemCount: categories.length,
                          itemBuilder: (context, index) =>
                              _buildCategoryCard(categories[index], index),
                        ),
                      );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddCategoryDialog(context),
        icon: const Icon(Icons.add_rounded, color: Colors.white),
        label: Text(
          'Add Category',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.w500,
            color: Colors.white,
            fontSize: 16,
          ),
        ),
        backgroundColor: primaryColor,
        elevation: 4,
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.folder_open_rounded,
            size: 80,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No Categories Yet',
            style: GoogleFonts.poppins(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Colors.grey[700],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Create a category to get started',
            style: GoogleFonts.poppins(
              fontSize: 16,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryCard(Category category, int index) {
    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => CategoryScreen(category: category),
            ),
          );
        },
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: gradients[index % gradients.length],
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: gradients[index % gradients.length][0].withOpacity(0.3),
                blurRadius: 12,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: Stack(
              children: [
                Positioned(
                  right: -20,
                  bottom: -20,
                  child: Icon(
                    Icons.folder,
                    size: 120,
                    color: Colors.white.withOpacity(0.1),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        category.name,
                        style: GoogleFonts.poppins(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${category.files.length} files',
                        // '0 files',
                        style: GoogleFonts.poppins(
                          fontSize: 14,
                          color: Colors.white.withOpacity(0.8),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _showAddCategoryDialog(BuildContext context) async {
    final textController = TextEditingController();
    return showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: Text(
          'Add Category',
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.w600,
            fontSize: 20,
          ),
        ),
        content: TextField(
          controller: textController,
          decoration: InputDecoration(
            labelText: 'Category Name',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: primaryColor, width: 2),
            ),
          ),
          style: GoogleFonts.poppins(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(
              'Cancel',
              style: GoogleFonts.poppins(
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          ElevatedButton(
            onPressed: () async {
              if (textController.text.isNotEmpty) {
                await Provider.of<CategoryProvider>(context, listen: false)
                    .createCategory(textController.text);
                Navigator.pop(context);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: primaryColor,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: Text(
              'Add',
              style: GoogleFonts.poppins(
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
