import os
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
import shutil
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

from config.database import get_db, engine
from models.database_models import Base, Category, File as DBFile, User
from services.document_analyzer import DocumentAnalyzer
from services.document_summarizer import DocumentSummarizer
from utils.auth import (
    verify_token,
    create_access_token,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from pydantic import BaseModel
from typing import Optional
import logging
from routers import users, categories, files
from services.news_service import NewsService
from models.news_models import NewsResponse

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize services
document_analyzer = DocumentAnalyzer()
document_summarizer = DocumentSummarizer()
news_service = NewsService()

# Include routers
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(files.router)


# Pydantic models
class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True


class KFileResponse(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    highlighted_filename: Optional[str]
    summary: Optional[str]
    category_id: Optional[str]
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Additional Pydantic models for user operations
class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


async def process_file(
    file_path: str, file_id: str, db: Session, categories: List[dict]
):
    logger.info(f"Processing file {file_id}")
    # db = Session(engine)
    try:

        # Get fresh categories from database
        # categories = (
        #     db.query(Category).filter(Category.id.in_([c.id for c in categories])).all()
        # )

        # Run analyzer and summarizer concurrently
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

        # Update database with results
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
            logger.info(f"Categories: {categories}")
            logger.info(f"Category name: {category_name}")
            for cat in categories:

                if cat["name"] == category_name:
                    file.category_id = cat["id"]
                    logger.info(f"Category id: {cat['id']}")
                    break

            print(file.summary)
            db.commit()

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
    finally:
        db.close()


@app.get("/news/", response_model=NewsResponse)
async def get_news(
    page: int = 1,
    categories: Optional[List[str]] = None,
    current_user: User = Depends(verify_token),
):
    """Get paginated news articles based on user preferences"""
    return news_service.get_articles(
        user_id=current_user["user_id"], page=page, preferred_categories=categories
    )


@app.post("/news/reset-history")
async def reset_news_history(current_user: User = Depends(verify_token)):
    """Reset the news history for the current user"""
    news_service.reset_user_history(current_user.id)
    return {"message": "News history reset successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
