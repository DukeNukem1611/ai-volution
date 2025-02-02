from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from typing import List


class Embedder(Embeddings):
    """
    Embedder class that implements LangChain's Embeddings interface.
    Implements Singleton pattern to ensure only one instance is created.
    """

    _instance = None

    def __new__(cls, model_name: str = "all-MiniLM-L6-v2"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = SentenceTransformer(model_name)
        return cls._instance

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Skip initialization if instance already exists
        if hasattr(self, "model"):
            return
        else:
            self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a query."""
        embedding = self.model.encode([text])[0]
        return embedding.tolist()

    def get_sentence_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self.model.get_sentence_embedding_dimension()
