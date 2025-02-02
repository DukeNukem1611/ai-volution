import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import TypedDict, Annotated, Dict, Any
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import (
    AnyMessage,
    SystemMessage,
    HumanMessage,
    ToolMessage,
    AIMessage,
)
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from services.indexer import Indexer
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the document agent."""

    messages: Annotated[list[AnyMessage], operator.add]


class DocumentAgent:
    """ReAct agent for document retrieval and querying using LangGraph"""

    def __init__(self):
        # Initialize tools
        self.indexer = Indexer(collection_name="documents")
        print(os.getenv("TAVILY_API_KEY"))
        self.tools_dict = {
            "document_search": self.indexer.as_tool(),
            # "web_search": TavilySearchResults(
            #     # tavily_api_key=os.getenv("TAVILY_API_KEY"),
            #     max_results=3,
            #     description="Use for finding supplementary information from the web when documents don't contain enough context.",
            # ),
        }

        # Initialize model
        self.model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

        # 2. For additional context:
        #            - Use web_search to supplement document information
        #            - Clearly distinguish between document and web sources
        # System prompt
        self.system_prompt = """You are a helpful assistant that helps users find information in their documents and the web.
        
        
        Follow these guidelines:
        1. For document queries:
           - First use document_search to find relevant information
           - Cite specific documents when providing information
           
        
           
        2. Response format:
           - Keep responses clear and concise
           - Always cite sources with their origins
           - If no relevant information is found, clearly state that
        """

        # Build graph
        self.graph = self.build_graph()

    def exists_action(self, state: AgentState) -> bool:
        """Check if there are any tool calls to make."""
        result = state["messages"][-1]
        return hasattr(result, "tool_calls") and len(result.tool_calls) > 0

    def call_llm(self, state: AgentState) -> AgentState:
        """Call the LLM with the current state."""
        messages = state["messages"][-10:]  # Limit context window

        if self.system_prompt:
            messages = [SystemMessage(content=self.system_prompt)] + messages

        try:
            message = self.model.bind_tools(self.tools_dict.values()).invoke(messages)
            print(message)
            return {"messages": state["messages"] + [message]}
        except Exception as e:
            logger.error(f"Error in call_llm: {type(e).__name__} - {str(e)}")
            return {
                "messages": state["messages"]
                + [AIMessage(content=f"Sorry, I encountered an error: {str(e)}")]
            }

    def take_action(self, state: AgentState) -> AgentState:
        """Execute tool calls from the LLM."""
        tool_calls = state["messages"][-1].tool_calls
        if not tool_calls:
            return {"messages": state["messages"]}

        results = []
        for tool_call in tool_calls:
            tool_name = (
                tool_call.function.name
                if hasattr(tool_call, "function")
                else tool_call.get("name")
            )
            if tool_name == "tavily_search_results_json":
                tool_name = "web_search"

            if not tool_name or tool_name not in self.tools_dict:
                logger.error(f"Invalid tool call: {tool_call}")
                results.append(
                    ToolMessage(
                        tool_call_id=tool_call.get("id", ""),
                        name=tool_name or "unknown",
                        content="Error: Invalid tool call",
                    )
                )
                continue

            try:
                tool = self.tools_dict[tool_name]
                arguments = (
                    tool_call.function.arguments
                    if hasattr(tool_call, "function")
                    else tool_call.get("arguments", "")
                )
                result = tool.invoke(arguments)
                print(result)
                results.append(
                    ToolMessage(
                        tool_call_id=tool_call.get("id", ""),
                        name=tool_name,
                        content=str(result),
                    )
                )
            except Exception as e:
                logger.error(f"Error invoking tool {tool_name}: {e}")
                results.append(
                    ToolMessage(
                        tool_call_id=tool_call.get("id", ""),
                        name=tool_name,
                        content=f"Error: {str(e)}",
                    )
                )

        return {"messages": results}

    def build_graph(self) -> StateGraph:
        """Build the agent's workflow graph."""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("llm", self.call_llm)
        graph.add_node("action", self.take_action)

        # Add edges
        graph.add_conditional_edges(
            "llm", self.exists_action, {True: "action", False: END}
        )
        graph.add_edge("action", "llm")

        # Set entry point
        graph.set_entry_point("llm")

        return graph.compile()

    def stream(self, query: str):
        """Stream the agent's response."""
        messages = [HumanMessage(content=query)]
        return self.graph.stream({"messages": messages})

    async def query(self, user_query: str) -> str:
        """Query documents and generate a response"""
        try:
            messages = [HumanMessage(content=user_query)]
            result = self.graph.invoke({"messages": messages})
            return result["messages"][-1].content
        except Exception as e:
            logger.error(f"Error in document query: {e}")
            return f"Sorry, I encountered an error: {str(e)}"


if __name__ == "__main__":
    import asyncio

    async def test_agent():
        agent = DocumentAgent()
        query = " Best Path Decision Framework Best Path Analysis Prune In e Analysis Tree Publishability Assessment Review Needed Generate Reasoning Paths i — Multi-perspective Analysis Tree Visualization Publication Decision"
        print("\nStreaming Query:")
        for event in agent.stream(query):
            for v in event.values():
                print(v["messages"][-1].content)

    asyncio.run(test_agent())
