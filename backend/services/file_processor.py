import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from typing import List, Dict
from pathlib import Path
from utils.parser import UnstructuredParser
from services.indexer import Indexer

logger = logging.getLogger(__name__)


class FileProcessor:
    """Service to process and index uploaded files"""

    def __init__(self):
        self.parser = UnstructuredParser()
        self.indexer = Indexer(collection_name="documents")

    async def process_file(self, file_path: str) -> Dict:
        """Process and index a file"""
        try:
            # Extract text using Unstructured
            text = await self.parser.extract_text_async(file_path)

            # Index the content
            metadata = {
                "filename": Path(file_path).name,
                "file_path": file_path,
            }

            await self.indexer.index_document(text, metadata)

            return {
                "status": "success",
                "message": f"File {Path(file_path).name} processed and indexed successfully",
            }

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {"status": "error", "message": f"Error processing file: {str(e)}"}


if __name__ == "__main__":
    import asyncio

    asyncio.run(FileProcessor().process_file("test.pdf"))
