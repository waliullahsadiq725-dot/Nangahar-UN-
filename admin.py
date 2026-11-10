from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.dependencies import require_roles
from app.models import User, Document, Download
from app.schemas import UserOut, UserStatusIn, DocumentOut, DocumentReviewIn

router = APIRouter(prefix="/api/admin", tags=["Administration"])

@router.get("/stats")
def stats(db: Session = Depends(get_db), admin: User = Depends(require_roles("admin", "superadmin"))):
    return {
        "total_users": db.query(User).count(),
        "students": db.query(User).filter(User.role == "student").count(),
        "teachers": db.query(User).filter(User.role == "teacher").count(),
        "admins": db.query(User).filter(User.role.in_(["admin", "superadmin"])).count(),
        "total_documents": db.query(Document).count(),
        "pending_documents": db.query(Document).filter(Document.status == "pending").count(),
        "total_downloads": db.query(Download).count(),
        "pending_users": db.query(User).filter(User.is_approved == False, User.role.in_(["student", "teacher"])).count()
    }

@router.get("/users", response_model=list[UserOut])
def users(role: str | None = None, pending_only: bool = False, skip: int = 0, limit: int = 50,
          db: Session = Depends(get_db), admin: User = Depends(require_roles("admin", "superadmin"))):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if pending_only:
        q = q.filter(User.is_approved == False, User.role.in_(["student", "teacher"]))
    return q.order_by(User.created_at.desc()).offset(skip).limit(min(max(limit, 1), 100)).all()

@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserStatusIn, db: Session = Depends(get_db),
                admin: User = Depends(require_roles("admin", "superadmin"))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "superadmin":
        raise HTTPException(status_code=403, detail="Super admin account cannot be changed here")
    if data.is_approved is not None:
        user.is_approved = data.is_approved
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user

@router.get("/documents/pending", response_model=list[DocumentOut])
def pending_documents(db: Session = Depends(get_db), admin: User = Depends(require_roles("admin", "superadmin"))):
    return db.query(Document).filter(Document.status == "pending").order_by(Document.created_at.asc()).all()

@router.patch("/documents/{document_id}/review", response_model=DocumentOut)
def review_document(document_id: int, data: DocumentReviewIn, db: Session = Depends(get_db),
                    admin: User = Depends(require_roles("admin", "superadmin"))):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.status = data.status
    doc.rejection_reason = data.rejection_reason if data.status == "rejected" else None
    db.commit()
    db.refresh(doc)
    return doc
