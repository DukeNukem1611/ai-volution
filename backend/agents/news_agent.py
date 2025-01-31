import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from models.news_agent_models import (
    UserTopics,
    TopicQuery,
    NewsSearchResult,
    AgentResponse,
)
from utils.news_api import get_news


class NewsAgent:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        # Initialize Tavily Search
        self.search_tool = TavilySearchResults(
            max_results=6, search_depth="advanced", api_key=os.getenv("TAVILY_API_KEY")
        )

        # Define tools
        @tool
        def search_news(query: str) -> List[dict]:
            """Search for news articles using the news API"""
            return get_news(query=query, page_size=5)

        self.tools = [self.search_tool, search_news]

        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert news researcher and analyst. Your task is to:
            1. For each user topic, use Tavily to find the latest trending aspects
            2. Generate relevant search queries based on the findings
            3. Use these queries to search for news articles
            4. Ensure diverse coverage while maintaining relevance
            
            Be precise and focus on current events.""",
                ),
                ("user", "{input}"),
                ("user", "Topics to research: {topics}"),
                ("assistant", "{agent_scratchpad}"),
            ]
        )

        # Create the agent
        self.agent = create_openai_functions_agent(
            llm=self.llm, prompt=self.prompt, tools=self.tools
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent, tools=self.tools, verbose=True
        )

    async def process_topic(self, topic: str) -> NewsSearchResult:
        """Process a single topic to get relevant news"""
        # First use Tavily to get context about the topic
        search_result = await self.search_tool.ainvoke(
            f"latest news and developments about {topic}"
        )

        # Generate keywords based on the search results
        keywords_response = await self.llm.ainvoke(
            f"""Based on these search results about {topic}, generate 5 specific keyword combinations for news search.
            Use the following format:
            - Use + for must-include terms
            - Use quotes for exact phrases
            - Use OR between alternatives
            - Keep each combination under 5 keywords
            
            Search results:
            {search_result}
            
            Return only the keyword combinations, one per line."""
        )

        keywords = [
            k.strip() for k in keywords_response.content.split("\n") if k.strip()
        ]
        print("Search keywords: ", keywords)

        # Get news for each keyword combination concurrently
        async def fetch_news(keyword):
            return await get_news(query=keyword, page_size=3)

        all_articles = []
        news_tasks = [fetch_news(keyword) for keyword in keywords]
        articles_lists = await asyncio.gather(*news_tasks)
        for articles in articles_lists:
            all_articles.extend(articles)

        return NewsSearchResult(topic=topic, articles=all_articles)

    async def get_news_for_topics(self, user_topics: UserTopics) -> AgentResponse:
        """Process multiple topics concurrently and return aggregated results"""
        tasks = [self.process_topic(topic) for topic in user_topics.topics]
        results = await asyncio.gather(*tasks)

        return AgentResponse(results=results)


if __name__ == "__main__":
    import asyncio
    import json

    agent = NewsAgent()

    news = asyncio.run(
        agent.get_news_for_topics(
            UserTopics(
                topics=[
                    "Politics",
                    "Bollywood",
                    "Economy",
                    "Sports",
                    "Technology",
                    "Health",
                    "Education",
                    "Science",
                    "Environment",
                    "Entertainment",
                    "Business",
                    "Art",
                    "Travel",
                    "Food",
                    "Fashion",
                    "Music",
                    "Crime",
                    "Automobiles",
                    "Real Estate",
                    "Gaming",
                    "Weather",
                    # "Astrology",
                    # "Religion",
                    # "Culture",
                    # "Literature",
                    # "Philosophy",
                    # "Psychology",
                ]
                # topics=["Bollywood"]
            )
        )
    )

    all_articles = []
    for result in news.results:
        all_articles.extend([article.model_dump() for article in result.articles])
    with open("all_articles_2.json", "w") as f:
        json.dump(all_articles, f)
    print(len(all_articles))

    # for result in news.results:
    #     print(f"\n=== {result.topic} ===")
    #     for article in result.articles:
    #         print(f"\nTitle: {article.title}")
    #         print(f"URL: {article.url}")
    #         if article.urlToImage:
    #             print(f"Image: {article.urlToImage}")
    #         print(f"Published: {article.publishedAt}")
    #         print("-" * 50)
