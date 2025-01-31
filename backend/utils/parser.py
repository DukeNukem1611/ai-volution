import os
import asyncio
from typing import List, Dict, Union, Optional
from pathlib import Path
from dotenv import load_dotenv
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared, operations
from diskcache import Cache
import hashlib

load_dotenv()


class UnstructuredParser:
    """Parser class that uses Unstructured.io API to extract text from various document types"""

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """Initialize the parser with API key

        Args:
            api_key: Unstructured API key. If not provided, will look for UNSTRUCTURED_API_KEY env variable
            cache_dir: Directory to store cached results. If None, uses '.cache' in current directory
        """
        self.api_key = api_key or os.getenv("UNSTRUCTURED_API_KEY")
        print(self.api_key)
        if not self.api_key:
            raise ValueError(
                "API key must be provided either directly or via UNSTRUCTURED_API_KEY environment variable"
            )

        self.client = UnstructuredClient(
            api_key_auth=self.api_key,
            server_url="https://api.unstructuredapp.io/general/v0/general",
        )
        self.supported_extensions = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
        self.cache = Cache(cache_dir or ".cache")

    def _validate_file(self, file_path: Union[str, Path]) -> Path:
        """Validate that the file exists and is a supported type

        Args:
            file_path: Path to the file to validate

        Returns:
            Path object of validated file

        Raises:
            ValueError: If file doesn't exist or is unsupported type
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File not found: {file_path}")

        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file type: {path.suffix}. Supported types: {self.supported_extensions}"
            )

        return path

    def _get_file_hash(self, file_path: Path) -> str:
        """Generate a hash of the file contents for caching

        Args:
            file_path: Path to the file

        Returns:
            SHA-256 hash of the file contents
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def parse_file_async(
        self, file_path: Union[str, Path], chunking_strategy: Optional[str] = None
    ) -> List[Dict]:
        """Parse a document file using Unstructured API asynchronously

        Args:
            file_path: Path to file to parse
            chunking_strategy: Optional chunking strategy (e.g. "by_title")

        Returns:
            List of dictionaries containing extracted elements
        """
        file_path = self._validate_file(file_path)

        # Generate cache key from file hash and chunking strategy
        file_hash = self._get_file_hash(file_path)
        cache_key = f"{file_hash}_{chunking_strategy}"

        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # If not in cache, process the file
        with open(file_path, "rb") as f:
            files = shared.Files(content=f.read(), file_name=file_path.name)

        params = shared.PartitionParameters(
            files=files,
            split_pdf_page=True,  # Enable PDF page splitting for better performance
            split_pdf_concurrency_level=15,  # Max concurrent requests
        )

        if chunking_strategy:
            params.chunking_strategy = chunking_strategy

        request = operations.PartitionRequest(partition_parameters=params)

        response = await self.client.general.partition_async(request=request)
        result = response.elements if response.elements else []

        # Cache the result before returning
        self.cache.set(cache_key, result)
        return result

    async def extract_text_async(
        self, file_path: Union[str, Path], chunking_strategy: Optional[str] = None
    ) -> str:
        """Extract plain text from a document file asynchronously

        Args:
            file_path: Path to file to parse
            chunking_strategy: Optional chunking strategy

        Returns:
            Extracted text as a single string
        """
        elements = await self.parse_file_async(file_path, chunking_strategy)
        return "\n".join(element["text"] for element in elements if "text" in element)

    # Add sync versions that wrap the async methods
    def parse_file(
        self, file_path: Union[str, Path], chunking_strategy: Optional[str] = None
    ) -> List[Dict]:
        """Synchronous version of parse_file_async"""
        return asyncio.run(self.parse_file_async(file_path, chunking_strategy))

    def extract_text(
        self, file_path: Union[str, Path], chunking_strategy: Optional[str] = None
    ) -> str:
        """Synchronous version of extract_text_async"""
        return asyncio.run(self.extract_text_async(file_path, chunking_strategy))


if __name__ == "__main__":
    parser = UnstructuredParser()
    text = parser.extract_text("test.docx")
    print(text)
