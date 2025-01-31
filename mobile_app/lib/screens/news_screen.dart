import 'dart:developer';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/news_article.dart';
import '../services/api_service.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

class NewsScreen extends StatefulWidget {
  const NewsScreen({super.key});

  @override
  State<NewsScreen> createState() => _NewsScreenState();
}

class _NewsScreenState extends State<NewsScreen> {
  late PageController _pageController;
  List<NewsArticle> articles = [];
  int currentPage = 1;
  bool isLoading = false;
  bool hasMore = true;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
    _loadInitialArticles();
  }

  Future<void> _loadInitialArticles() async {
    if (isLoading) return;
    if (!mounted) return;
    setState(() => isLoading = true);

    try {
      final response = await Provider.of<ApiService>(context, listen: false)
          .getNews(page: currentPage);
      if (!mounted) return;
      setState(() {
        articles = response.articles;
        hasMore = response.hasMore;
        isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => isLoading = false);
      // Handle error
    }
  }

  Future<void> _loadMoreArticles() async {
    if (isLoading || !hasMore) return;
    if (!mounted) return;
    setState(() => isLoading = true);

    try {
      final response = await Provider.of<ApiService>(context, listen: false)
          .getNews(page: currentPage + 1);
      if (!mounted) return;
      setState(() {
        articles.addAll(response.articles);
        currentPage++;
        hasMore = response.hasMore;
        isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => isLoading = false);
      // Handle error
    }
  }

  Future<void> _launchURL(String url) async {
    log('Launching URL: $url');
    await launchUrl(Uri.parse(url));
    // if (await canLaunchUrl(Uri.parse(url))) {
    // } else {
    //   // throw Exception('Failed to launch URL');
    // }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading && articles.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    return PageView.builder(
      controller: _pageController,
      scrollDirection: Axis.vertical,
      onPageChanged: (index) {
        if (index >= articles.length - 2) {
          _loadMoreArticles();
        }
      },
      itemBuilder: (context, index) {
        if (index >= articles.length) {
          return const Center(child: CircularProgressIndicator());
        }

        final article = articles[index];
        return Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 16),
              if (article.urlToImage != null)
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Image.network(
                    article.urlToImage!,
                    height: 200,
                    width: double.infinity,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) =>
                        const SizedBox.shrink(),
                  ),
                ),
              const SizedBox(height: 16),
              Text(
                article.title,
                style: GoogleFonts.poppins(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              if (article.description != null)
                Text(
                  article.description!.length > 400
                      ? article.description!.substring(0, 400) + '...'
                      : article.description!,
                  style: GoogleFonts.poppins(fontSize: 16),
                ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => _launchURL(article.url),
                child: Text(
                  'Read Full Article',
                  style: GoogleFonts.poppins(),
                ),
              ),
              const Spacer(),
              Center(
                child: Text(
                  'Swipe up for next article',
                  style: GoogleFonts.poppins(
                    color: Colors.grey,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }
}
