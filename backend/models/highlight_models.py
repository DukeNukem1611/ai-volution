from pydantic import BaseModel, Field
from typing import List, Literal


class HighlightType(BaseModel):
    """Represents the type and color of a highlight"""
    color: Literal["green", "yellow", "pink", "blue"] = Field(
        description="Color of the highlight (green=main ideas, yellow=vocabulary, pink=questions, blue=sub-ideas)"
    )
    description: str = Field(description="Description of what this highlight type represents")


class Highlight(BaseModel):
    """Represents a single highlight in a document"""

    content: str = Field(description="The exact text to be highlighted")
    explanation: str = Field(description="Explanation of why this section is important")
    highlight_type: HighlightType = Field(description="Type and color of the highlight")


class DocumentAnalysis(BaseModel):
    """Represents the complete analysis of a document"""

    highlights: List[Highlight] = Field(
        description="List of highlights found in the document"
    )
    total_pages: int = Field(description="Total number of pages in the document")
    document_title: str = Field(description="Title or filename of the document")
