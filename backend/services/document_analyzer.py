import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
from typing import List, Dict, Union
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from models.highlight_models import Highlight, DocumentAnalysis
from utils.parser import UnstructuredParser
from utils.pdf_highlighter import add_highlights as add_pdf_highlights
from utils.docx_highlighter import add_highlights as add_docx_highlights
from utils.ppt_highlighter import add_highlights as add_ppt_highlights

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DocumentAnalyzer:
    """Agent that analyzes documents to identify and highlight important information"""

    def __init__(self, api_key: str = None, openai_api_key: str = None):
        """Initialize the document analyzer

        Args:
            api_key: Unstructured API key for parsing documents
            openai_api_key: OpenAI API key for content analysis
        """
        self.parser = UnstructuredParser()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            length_function=len,
        )

    async def analyze_chunk(self, chunk: str) -> List[Highlight]:
        """Analyze a single chunk of text"""
        prompt = f"""Analyze the following text chunk and identify important sections that should be highlighted.
        For each highlight, assign one of these color categories:
        - GREEN: Main ideas and big takeaways
        - YELLOW: Important vocabulary and definitions
        - PINK: Questions or areas needing clarification
        - BLUE: Supporting details and sub-ideas
        
        Only include truly significant information.
        
        Text chunk:
        {chunk}
        """

        response = await self.llm.with_structured_output(DocumentAnalysis).ainvoke(
            prompt
        )
        highlights = response.highlights
        return highlights

    async def analyze_document(self, file_path: Union[str, Path]) -> Dict:
        """Analyze a document using chunking and structured output"""
        try:
            # Extract text and metadata from document
            text = await self.parser.extract_text_async(file_path)

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)

            # Analyze each chunk
            all_highlights = []
            for i, chunk in enumerate(chunks):
                chunk_highlights = await self.analyze_chunk(chunk)
                all_highlights.extend(chunk_highlights)

            # Create structured output
            analysis = DocumentAnalysis(
                highlights=all_highlights,
                total_pages=len(chunks),
                document_title=Path(file_path).name,
            )

            # Add highlights based on file type
            file_extension = Path(file_path).suffix.lower()
            highlight_data = [h.dict() for h in analysis.highlights]

            if file_extension == ".pdf":
                highlighted_path = add_pdf_highlights(highlight_data, str(file_path))
            elif file_extension == ".docx":
                highlighted_path = add_docx_highlights(highlight_data, str(file_path))
            elif file_extension in [".ppt", ".pptx"]:
                highlighted_path = add_ppt_highlights(highlight_data, str(file_path))
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            return {
                "message": f"Document analyzed and highlights added. Output at: {highlighted_path}",
                "analysis": analysis.dict(),
                "highlighted_path": highlighted_path,
            }

        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {"message": f"Error analyzing document: {str(e)}"}

    def analyze_document_sync(self, file_path: Union[str, Path]) -> Dict:
        """Synchronous version of analyze_document"""
        import asyncio

        return asyncio.run(self.analyze_document(file_path))


if __name__ == "__main__":
    analyzer = DocumentAnalyzer()
    result = analyzer.analyze_document_sync("new.pptx")
    print(result)
