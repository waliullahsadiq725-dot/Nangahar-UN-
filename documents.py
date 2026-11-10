from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Document, Download, Favorite
from app.schemas import DocumentOut

router = APIRouter(prefix="/api/documents", tags=["Documents"])
UPLOAD_DIR = Path(settings.upload_dir).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_BYTES = settings.max_upload_mb * 1024 * 1024

def ensure_document_file(doc: Document) -> Path:
    path = (UPLOAD_DIR / doc.stored_filename).resolve()
    if path.parent != UPLOAD_DIR or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return path

@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    title: str = Form(...), description: str | None = Form(None),
    department: str | None = Form(None), subject: str | None = Form(None),
    semester: str | None = Form(None), academic_year: str | None = Form(None),
    file: UploadFile = File(...), user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf" and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    content = await file.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"Maximum file size is {settings.max_upload_mb} MB")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF")
    stored = f"{uuid4().hex}.pdf"
    (UPLOAD_DIR / stored).write_bytes(content)
    status_value = "approved" if user.role in ("admin", "superadmin") else "pending"
    doc = Document(
        title=title.strip(), description=description, original_filename=(file.filename or "document.pdf")[:255],
        stored_filename=stored, file_size=len(content), department=department or user.department,
        subject=subject, semester=semester, academic_year=academic_year,
        uploader_id=user.id, status=status_value
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("", response_model=list[DocumentOut])
def list_documents(
    search: str | None = None, department: str | None = None,
    subject: str | None = None, skip: int = 0, limit: int = 30,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    limit = min(max(limit, 1), 100)
    query = db.query(Document)
    if user.role in ("admin", "superadmin"):
        pass
    else:
        query = query.filter(or_(Document.status == "approved", Document.uploader_id == user.id))
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(Document.title.ilike(term), Document.description.ilike(term), Document.subject.ilike(term)))
    if department:
        query = query.filter(Document.department == department)
    if subject:
        query = query.filter(Document.subject == subject)
    return query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{document_id}/preview")
def preview_document(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc or (doc.status != "approved" and doc.uploader_id != user.id and user.role not in ("admin", "superadmin")):
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(ensure_document_file(doc), media_type="application/pdf", content_disposition_type="inline")

@router.get("/{document_id}/download")
def download_document(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc or (doc.status != "approved" and doc.uploader_id != user.id and user.role not in ("admin", "superadmin")):
        raise HTTPException(status_code=404, detail="Document not found")
    doc.download_count += 1
    db.add(Download(user_id=user.id, document_id=doc.id))
    db.commit()
    return FileResponse(ensure_document_file(doc), media_type="application/pdf",
                        filename=doc.original_filename, content_disposition_type="attachment")

@router.post("/{document_id}/favorite")
def toggle_favorite(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc or doc.status != "approved":
        raise HTTPException(status_code=404, detail="Document not found")
    fav = db.query(Favorite).filter_by(user_id=user.id, document_id=doc.id).first()
    if fav:
        db.delete(fav)
        db.commit()
        return {"favorited": False}
    db.add(Favorite(user_id=user.id, document_id=doc.id))
    db.commit()
    return {"favorited": True}

@router.get("/my/favorites", response_model=list[DocumentOut])
def my_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (db.query(Document).join(Favorite, Favorite.document_id == Document.id)
            .filter(Favorite.user_id == user.id).order_by(Favorite.created_at.desc()).all())

@router.get("/my/uploads", response_model=list[DocumentOut])
def my_uploads(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.uploader_id == user.id).order_by(Document.created_at.desc()).all()
