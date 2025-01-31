import os
import logging
import asyncio
from sqlalchemy.orm import Session
from typing import List
from models.database_models import File as DBFile
from services.document_analyzer import DocumentAnalyzer
from services.document_summarizer import DocumentSummarizer

logger = logging.getLogger(__name__)

document_analyzer = DocumentAnalyzer()
document_summarizer = DocumentSummarizer()


async def process_file(
    file_path: str, file_id: str, db: Session, categories: List[dict]
):
    logger.info(f"Processing file {file_id}")
    try:
        analyzer_task = asyncio.create_task(
            document_analyzer.analyze_document(file_path)
        )
        summarizer_task = asyncio.create_task(
            document_summarizer.analyze_document(
                file_path, [c["name"] for c in categories]
            )
        )

        analyzer_result, summarizer_result = await asyncio.gather(
            analyzer_task, summarizer_task
        )

        file = db.query(DBFile).filter(DBFile.id == file_id).first()
        if file:
            file.highlighted_filename = os.path.basename(
                analyzer_result["highlighted_path"]
            )
            file.summary = (
                summarizer_result.full_summary
                if hasattr(summarizer_result, "full_summary")
                else str(summarizer_result)
            )
            category_name = (
                summarizer_result.classification.category
                if hasattr(summarizer_result, "classification")
                else None
            )

            for cat in categories:
                if cat["name"] == category_name:
                    file.category_id = cat["id"]
                    logger.info(f"Category id: {cat['id']}")
                    break

            db.commit()

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
    finally:
        db.close()
