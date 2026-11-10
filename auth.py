from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="This email is already registered")
    user = User(
        full_name=data.full_name.strip(), email=email,
        password_hash=hash_password(data.password), role=data.role,
        department=data.department, student_id=data.student_id,
        staff_id=data.staff_id, is_approved=False, is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account is disabled")
    if user.role in ("student", "teacher") and not user.is_approved:
        raise HTTPException(status_code=403, detail="Your account is waiting for admin approval")
    return TokenOut(access_token=create_access_token(str(user.id)), user=user)

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(__import__("app.dependencies", fromlist=["get_current_user"]).get_current_user)):
    return user
