import json
from typing import List, Set, Dict
import os
from models.news_models import NewsArticle, NewsResponse
from datetime import datetime
from models.database_models import User
from config.database import get_db


class NewsService:
    def __init__(self):
        self.articles: List[NewsArticle] = []
        self.served_articles: Dict[str, Set[str]] = (
            {}
        )  # user_id -> set of served article URLs
        self.page_size = 10
        self._load_articles()
        self.db = next(get_db())

    def _load_articles(self):
        """Load articles from JSON file"""
        try:
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "updated_articles.json"
            )
            with open(file_path, "r") as f:
                articles_data = json.load(f)

            # Convert datetime strings to datetime objects
            for article in articles_data:
                if "publishedAt" in article:
                    article["publishedAt"] = datetime.fromisoformat(
                        article["publishedAt"].replace("Z", "+00:00")
                    )

            self.articles = [NewsArticle(**article) for article in articles_data]
        except Exception as e:
            print(f"Error loading articles: {e}")
            self.articles = []

    def _filter_by_categories(
        self, articles: List[NewsArticle], preferred_categories: List[str]
    ) -> List[NewsArticle]:
        """Filter articles based on user's preferred categories"""
        if not preferred_categories:
            return articles

        filtered_articles = []
        for article in articles:
            if not article.category:
                continue

            # Extract category names from the nested structure
            article_categories = [cat[0].lower() for cat in article.category]

            # Check if any of the preferred categories match
            if any(
                preferred_cat.lower() in article_categories
                for preferred_cat in preferred_categories
            ):
                filtered_articles.append(article)

        return filtered_articles

    def _get_unserved_articles(
        self, user_id: str, articles: List[NewsArticle]
    ) -> List[NewsArticle]:
        """Filter out articles that have already been served to the user"""
        if user_id not in self.served_articles:
            self.served_articles[user_id] = set()

        unserved = []
        for article in articles:
            if article.url not in self.served_articles[user_id]:
                unserved.append(article)

        return unserved

    def get_articles(
        self, user_id: str, page: int = 1, preferred_categories: List[str] = None
    ) -> NewsResponse:
        """Get paginated articles based on user preferences"""
        # Filter articles by categories

        db_user = self.db.query(User).filter(User.id == user_id).first()
        preferred_categories = db_user.newcategories
        print(f"Preferred categories: {preferred_categories}")
        filtered_articles = self._filter_by_categories(
            self.articles, preferred_categories
        )
        print(f"Filtered articles: {len(filtered_articles)}")

        # Get unserved articles
        # available_articles = self._get_unserved_articles(user_id, filtered_articles)
        # print(f"Available articles: {len(available_articles)}")

        available_articles = filtered_articles

        # Calculate pagination
        start_idx = (page - 1) * self.page_size
        end_idx = start_idx + self.page_size

        # Get articles for current page
        current_articles = available_articles[start_idx:end_idx]

        # # Mark articles as served
        # for article in current_articles:
        #     self.served_articles[user_id].add(article.url)

        # Calculate total pages
        total_pages = (len(available_articles) + self.page_size - 1) // self.page_size

        return NewsResponse(
            articles=current_articles,
            page=page,
            total_pages=total_pages,
            has_more=page < total_pages,
        )

    def reset_user_history(self, user_id: str):
        """Reset the served articles history for a user"""
        self.served_articles[user_id] = set()
