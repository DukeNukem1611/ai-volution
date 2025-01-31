import os
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from config.database import get_db, engine
from models.database_models import Category, File as DBFile
from schemas.file import KFileResponse
from utils.auth import verify_token
from services.file_processor import process_file

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/", response_model=KFileResponse)
async def upload_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token),
):
    categories = (
        db.query(Category).filter(Category.user_id == current_user["user_id"]).all()
    )
    categories = [
        {"id": cat.id, "name": cat.name, "user_id": cat.user_id} for cat in categories
    ]

    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    stored_filename = f"{datetime.utcnow().timestamp()}_{file.filename}"
    file_path = os.path.join(upload_dir, stored_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_file = DBFile(
        original_filename=file.filename,
        stored_filename=stored_filename,
        user_id=current_user["user_id"],
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    background_tasks.add_task(process_file, file_path, db_file.id, db, categories)
    return db_file


@router.get("/", response_model=List[KFileResponse])
async def get_files(
    db: Session = Depends(get_db), current_user: dict = Depends(verify_token)
):
    files = db.query(DBFile).filter(DBFile.user_id == current_user["user_id"]).all()

    return files


@router.get("/{file_id}")
async def get_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token),
):
    file = (
        db.query(DBFile)
        .filter(DBFile.id == file_id, DBFile.user_id == current_user["user_id"])
        .first()
    )
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join("uploads", file.stored_filename)
    return FileResponse(file_path, filename=file.original_filename)


@router.get("/{file_id}/highlighted")
async def get_highlighted_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token),
):
    file = (
        db.query(DBFile)
        .filter(DBFile.id == file_id, DBFile.user_id == current_user["user_id"])
        .first()
    )
    if not file or not file.highlighted_filename:
        raise HTTPException(status_code=404, detail="Highlighted file not found")

    file_path = os.path.join("files", file.highlighted_filename)
    return FileResponse(file_path, filename=f"highlighted_{file.original_filename}")


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token),
):
    file = (
        db.query(DBFile)
        .filter(DBFile.id == file_id, DBFile.user_id == current_user["user_id"])
        .first()
    )
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete physical files
    try:
        os.remove(os.path.join("uploads", file.stored_filename))
        if file.highlighted_filename:
            os.remove(os.path.join("uploads", file.highlighted_filename))
    except OSError:
        pass

    db.delete(file)
    db.commit()
    return {"message": "File deleted"}
