import sys
import os
import hashlib
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from qdrant_client import QdrantClient
from utils.embedder import Embedder
from langchain_qdrant import QdrantVectorStore
import logging
from langchain_core.tools import Tool


logger = logging.getLogger(__name__)


class Indexer:
    """Simple document indexer using Qdrant"""

    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.client = QdrantClient(url=os.getenv("QDRANT_URL"))
        self.embedder = Embedder()

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embedder,
        )
        # Ensure collection exists
        self._create_collection()

    def _create_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "size": self.embedder.get_sentence_embedding_dimension(),
                    "distance": "Cosine",
                },
            )
        except Exception as e:
            logger.info(f"Collection may already exist: {e}")

    async def index_document(self, text: str, metadata: Dict) -> None:
        """Index a document's text with metadata"""
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)

            # Create documents with metadata
            documents = [
                Document(page_content=chunk, metadata=metadata) for chunk in chunks
            ]
            # Get embeddings
            embeddings = self.embedder.embed_documents(
                [d.page_content for d in documents]
            )
            print(len(documents))
            print(len(embeddings))

            # Generate unique IDs using hash of content and metadata
            def generate_id(content: str, metadata: Dict) -> int:
                combined = f"{content}{json.dumps(metadata, sort_keys=True)}"
                return int(hashlib.sha256(combined.encode()).hexdigest()[:16], 16)

            # Upload to Qdrant
            self.vector_store.add_documents(documents)

        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            raise

    def search(self, query: str, limit: int = 3) -> List[Dict]:
        """Search for relevant document chunks"""
        try:
            query_vector = self.embedder.embed_query(query)

            results = self.vector_store.similarity_search(
                query=query,
                k=limit,
            )
            # print(results)

            return [
                {
                    "content": r.page_content,
                    "metadata": r.metadata,
                }
                for r in results
            ]

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    def as_tool(self) -> Tool:
        """Convert the indexer into a LangChain tool."""
        return Tool(
            name="document_search",
            description="Search through indexed documents for relevant information. Input should be a search query string.",
            func=self.search,
        )
