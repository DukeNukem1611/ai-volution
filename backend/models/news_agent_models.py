import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pydantic import BaseModel, Field
from typing import List, Optional
from models.news_models import NewsArticle


class UserTopics(BaseModel):
    topics: List[str] = Field(
        ..., description="List of news topics the user is interested in"
    )


class TopicQuery(BaseModel):
    topic: str = Field(..., description="Original topic of interest")
    search_queries: List[str] = Field(
        ..., description="Generated search queries for this topic"
    )


class NewsSearchResult(BaseModel):
    topic: str = Field(..., description="Original topic")
    articles: List[NewsArticle] = Field(..., description="List of news articles found")


class AgentResponse(BaseModel):
    results: List[NewsSearchResult] = Field(
        ..., description="Search results grouped by topic"
    )
