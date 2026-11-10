import os
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models import User
from app.core.security import hash_password

def main():
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    name = os.getenv("ADMIN_NAME", "NU Digital Library Administrator")
    if not email or not password:
        raise SystemExit("Set ADMIN_EMAIL and ADMIN_PASSWORD environment variables first.")
    if len(password) < 12:
        raise SystemExit("ADMIN_PASSWORD must be at least 12 characters.")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email.lower()).first()
        if existing:
            raise SystemExit("An account with this email already exists.")
        admin = User(full_name=name, email=email.lower(), password_hash=hash_password(password),
                     role="superadmin", is_approved=True, is_active=True)
        db.add(admin)
        db.commit()
        print(f"Super admin created: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
