import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Optional
import aiohttp
from models.news_models import NewsArticle
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"


async def get_news(
    query: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    language: Optional[str] = "en",
    sort_by: Optional[str] = "relevancy",
    page_size: Optional[int] = 10,
    page: Optional[int] = 1,
) -> List[NewsArticle]:
    params = {
        "apiKey": api_key,
        "q": query,
        "language": language,
        "sortBy": sort_by,
        "pageSize": page_size,
        "page": page,
    }

    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL, params=params) as response:
            data = await response.json()
            if response.status != 200:
                raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
            return [NewsArticle(**article) for article in data["articles"]]


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(get_news(query="Sajid Nadiadwala")))
