from typing import List
from pydantic import BaseModel, Field


class DocumentClassification(BaseModel):
    category: str = Field(
        ..., description="The best matching category for the document"
    )
    confidence: int = Field(..., description="Confidence score from 0-100")
    explanation: str = Field(..., description="Explanation for the category selection")


class ChunkSummary(BaseModel):
    main_topics: List[str] = Field(
        ..., description="Main topics identified in the chunk"
    )
    key_points: List[str] = Field(..., description="Key points from the chunk")
    summary: str = Field(..., description="Synthesized summary of the chunk")


class DocumentSummary(BaseModel):
    document_title: str = Field(..., description="Title of the analyzed document")
    chunk_summaries: List[ChunkSummary] = Field(
        ..., description="Summaries of individual chunks"
    )
    full_summary: str = Field(..., description="Complete document summary")
    classification: DocumentClassification = Field(
        ..., description="Document classification details"
    )
    available_categories: List[str] = Field(
        ..., description="List of available classification categories"
    )
