from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NewsSource(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


class NewsArticle(BaseModel):
    source: NewsSource
    author: Optional[str] = None
    title: str
    description: Optional[str] = None
    url: str
    urlToImage: Optional[str] = None
    publishedAt: datetime
    content: Optional[str] = None
    category: Optional[List[List[str | float]]] = None
    keywords: Optional[List[str]] = None
    country: Optional[List[str]] = None

    @classmethod
    def from_tavily(cls, tavily_result: dict) -> "NewsArticle":
        return cls(
            title=tavily_result.get("title", ""),
            description=tavily_result.get("content", ""),
            url=tavily_result.get("url", ""),
            urlToImage=tavily_result.get("image_url", None),
            publishedAt=tavily_result.get("published_date", datetime.now()),
            content=tavily_result.get("content", None),
        )


class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    page: int
    total_pages: int
    has_more: bool
