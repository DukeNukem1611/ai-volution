import 'package:flutter/material.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:open_file/open_file.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/file.dart';
import '../services/api_service.dart';
import '../main.dart';

class FileViewerScreen extends StatefulWidget {
  final FileModel file;

  const FileViewerScreen({super.key, required this.file});

  @override
  State<FileViewerScreen> createState() => _FileViewerScreenState();
}

class _FileViewerScreenState extends State<FileViewerScreen> {
  final ApiService _apiService = ApiService();
  String? _downloadedFilePath;
  bool _isDownloading = false;

  Future<void> _downloadFile(BuildContext context) async {
    try {
      setState(() {
        _isDownloading = true;
      });

      // Get the downloads directory
      final directory = await getApplicationDocumentsDirectory();
      final filePath = '${directory.path}/${widget.file.filename}';

      // Download the file
      final fileBytes =
          await _apiService.downloadHighlightedFile(widget.file.id);

      // Save the file
      final file = File(filePath);
      await file.writeAsBytes(fileBytes);

      setState(() {
        _downloadedFilePath = filePath;
        _isDownloading = false;
      });

      // Show success message with option to open
      if (mounted) {
        _showDownloadCompleteDialog(context);
      }
    } catch (e) {
      setState(() {
        _isDownloading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error downloading file: ${e.toString()}')),
        );
      }
    }
  }

  Future<void> _openFile() async {
    if (_downloadedFilePath != null) {
      final result = await OpenFile.open(_downloadedFilePath!);
      if (result.type != ResultType.done) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error opening file: ${result.message}')),
          );
        }
      }
    }
  }

  void _showDownloadCompleteDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Download Complete'),
          content: const Text('Would you like to open the file?'),
          actions: <Widget>[
            TextButton(
              child: const Text('Cancel'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
            TextButton(
              child: const Text('Open'),
              onPressed: () {
                Navigator.of(context).pop();
                _openFile();
              },
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    String fileExtension = widget.file.filename.split('.').last;
    String fileType = fileExtension == 'pdf'
        ? 'PDF Document'
        : fileExtension == 'docx'
            ? 'Word Document'
            : (fileExtension == 'pptx' || fileExtension == 'ppt')
                ? 'PowerPoint Document'
                : 'Unknown Document';
    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        leading: IconButton(
          icon: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: surfaceColor,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.arrow_back_ios_new, size: 20),
          ),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          widget.file.filename,
          style: GoogleFonts.poppins(
            fontWeight: FontWeight.w600,
            fontSize: 20,
          ),
        ),
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              backgroundColor,
              backgroundColor.withOpacity(0.8),
            ],
          ),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // File Icon and Type
              Center(
                child: Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: primaryColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(24),
                      ),
                      child: const Icon(
                        Icons.description_outlined,
                        size: 64,
                        color: primaryColor,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Document Details',
                      style: GoogleFonts.poppins(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),

              // File Information Card
              Container(
                decoration: BoxDecoration(
                  color: surfaceColor,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (widget.file.summary != null) ...[
                        Text(
                          'Summary',
                          style: GoogleFonts.poppins(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: primaryColor,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          widget.file.summary!,
                          style: GoogleFonts.poppins(
                            fontSize: 16,
                            color: Colors.white70,
                            height: 1.6,
                          ),
                        ),
                        const SizedBox(height: 24),
                      ],

                      // Download Section
                      if (_isDownloading)
                        Center(
                          child: Column(
                            children: [
                              const CircularProgressIndicator(
                                color: primaryColor,
                                strokeWidth: 3,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'Downloading...',
                                style: GoogleFonts.poppins(
                                  color: Colors.white70,
                                ),
                              ),
                            ],
                          ),
                        )
                      else
                        Center(
                          child: ElevatedButton.icon(
                            onPressed: () => _downloadFile(context),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: primaryColor,
                              padding: const EdgeInsets.symmetric(
                                horizontal: 24,
                                vertical: 16,
                              ),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                            ),
                            icon: const Icon(Icons.download_rounded),
                            label: Text(
                              'Download Highlighted Version',
                              style: GoogleFonts.poppins(
                                fontWeight: FontWeight.w600,
                                fontSize: 16,
                              ),
                            ),
                          ),
                        ),

                      if (_downloadedFilePath != null) ...[
                        const SizedBox(height: 16),
                        Center(
                          child: TextButton.icon(
                            onPressed: _openFile,
                            style: TextButton.styleFrom(
                              foregroundColor: primaryColor,
                            ),
                            icon: const Icon(Icons.open_in_new_rounded),
                            label: Text(
                              'Open File',
                              style: GoogleFonts.poppins(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              // Additional File Details
              const SizedBox(height: 24),
              Container(
                decoration: BoxDecoration(
                  color: surfaceColor,
                  borderRadius: BorderRadius.circular(24),
                ),
                padding: const EdgeInsets.all(24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'File Details',
                      style: GoogleFonts.poppins(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: primaryColor,
                      ),
                    ),
                    const SizedBox(height: 16),
                    _buildDetailRow('File Name', widget.file.filename),
                    _buildDetailRow('File Type', fileType),
                    _buildDetailRow(
                        'Date Added',
                        widget.file.createdAt
                            .toLocal()
                            .toString()
                            .split(' ')[0]),

                    // _buildDetailRow('Size',
                    //     '${(widget.file.size / 1024 / 1024).toStringAsFixed(2)} MB'),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: GoogleFonts.poppins(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
          Text(
            value,
            style: GoogleFonts.poppins(
              color: Colors.white,
              fontWeight: FontWeight.w500,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
