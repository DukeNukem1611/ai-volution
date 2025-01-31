import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from typing import List, Dict, Union
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from utils.parser import UnstructuredParser
from models.summary_models import DocumentSummary, ChunkSummary, DocumentClassification
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Static categories for document classification
DOCUMENT_CATEGORIES = [
    "Technical Documentation",
    "Business Strategy",
    "Research Paper",
    "Educational Material",
    "Project Planning",
]


class DocumentSummarizer:
    """Service that provides comprehensive document summaries and category classification using CoT"""

    def __init__(self):
        self.parser = UnstructuredParser()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=300,
            length_function=len,
        )

    async def _generate_chunk_summary(self, chunk: str) -> ChunkSummary:
        """Generate summary for a single chunk using Chain of Thought prompting"""
        prompt = f"""Analyze this text chunk step by step to create a structured summary:

        Text chunk: {chunk}

        Follow these steps:
        1) First, identify the main topics (provide as a list)
        2) Extract key points (provide as a list)
        3) Synthesize a coherent summary

        Provide your analysis in a structured format that includes:
        - A list of main topics
        - A list of key points
        - A synthesized summary
        """

        response = await self.llm.with_structured_output(ChunkSummary).ainvoke(prompt)
        return response

    async def _classify_document(
        self, full_summary: str, categories: List[str]
    ) -> DocumentClassification:
        """Classify document into categories using Chain of Thought prompting"""
        categories_str = "\n".join(f"- {cat}" for cat in categories)

        prompt = f"""Determine the most suitable category for this document through careful reasoning.

        Available categories:
        {categories_str}

        Document summary:
        {full_summary}

        Think through this step by step:
        1) First, identify key characteristics of this document
        2) Analyze how these characteristics align with each category
        3) Compare the strength of alignment with each category
        4) Select the most appropriate category and explain why

        Provide a structured response with:
        - The best matching category (must be one from the list above)
        - A confidence score (0-100)
        - A detailed explanation of why this category was chosen
        """

        response = await self.llm.with_structured_output(
            DocumentClassification
        ).ainvoke(prompt)
        return response

    async def analyze_document(
        self, file_path: Union[str, Path], categories: List[str]
    ) -> Union[DocumentSummary, Dict[str, str]]:
        """Analyze document to provide summary and classification"""
        try:
            # Extract text from document
            text = await self.parser.extract_text_async(file_path)

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)

            # Generate summaries for each chunk
            chunk_summaries: List[ChunkSummary] = []
            for chunk in chunks:
                summary = await self._generate_chunk_summary(chunk)
                chunk_summaries.append(summary)

            # Combine chunk summaries into a full summary
            combined_summaries = "\n".join(cs.summary for cs in chunk_summaries)
            combined_summary_prompt = f"""Synthesize these separate summaries into one coherent summary:

            Individual summaries:
            {combined_summaries}

            Create a comprehensive yet concise summary that:
            1) Captures the overarching themes
            2) Maintains logical flow
            3) Includes key insights from all chunks
            """

            full_summary_response = await self.llm.ainvoke(combined_summary_prompt)
            full_summary = full_summary_response.content

            # Classify the document
            classification = await self._classify_document(full_summary, categories)

            # Create final structured output
            document_summary = DocumentSummary(
                document_title=Path(file_path).name,
                chunk_summaries=chunk_summaries,
                full_summary=full_summary,
                classification=classification,
                available_categories=categories,
            )

            return document_summary

        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {"error": f"Error analyzing document: {str(e)}"}

    def analyze_document_sync(
        self, file_path: Union[str, Path]
    ) -> Union[DocumentSummary, Dict[str, str]]:
        """Synchronous version of analyze_document"""
        import asyncio

        return asyncio.run(self.analyze_document(file_path))


if __name__ == "__main__":
    summarizer = DocumentSummarizer()
    result = summarizer.analyze_document_sync("test.pdf")
    if isinstance(result, DocumentSummary):
        print(f"Summary: {result.full_summary}")
        print(f"Classification: {result.classification}")
    else:
        print(f"Error: {result['error']}")
