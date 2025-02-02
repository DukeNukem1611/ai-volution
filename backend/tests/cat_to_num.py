import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import List, Set, Dict
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

    def get_categories_to_num(self):
        info = {}
        for article in self.articles:
            for category in [cat[0] for cat in article.category]:
                if category not in info:
                    info[category] = 0
                info[category] += 1
        return info


if __name__ == "__main__":
    news_service = NewsService()
    info = news_service.get_categories_to_num()
    print(info)
    print(info.keys())
