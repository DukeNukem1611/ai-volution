class NewsArticle {
  final String title;
  final String? description;
  final String url;
  final String? urlToImage;
  final DateTime publishedAt;
  final String? content;

  NewsArticle({
    required this.title,
    this.description,
    required this.url,
    this.urlToImage,
    required this.publishedAt,
    this.content,
  });

  factory NewsArticle.fromJson(Map<String, dynamic> json) {
    return NewsArticle(
      title: json['title'],
      description: json['description'],
      url: json['url'],
      urlToImage: json['urlToImage'],
      publishedAt: DateTime.parse(json['publishedAt']),
      content: json['content'],
    );
  }
}

class NewsResponse {
  final List<NewsArticle> articles;
  final int page;
  final int totalPages;
  final bool hasMore;

  NewsResponse({
    required this.articles,
    required this.page,
    required this.totalPages,
    required this.hasMore,
  });

  factory NewsResponse.fromJson(Map<String, dynamic> json) {
    return NewsResponse(
      articles: (json['articles'] as List)
          .map((article) => NewsArticle.fromJson(article))
          .toList(),
      page: json['page'],
      totalPages: json['total_pages'],
      hasMore: json['has_more'],
    );
  }
} 