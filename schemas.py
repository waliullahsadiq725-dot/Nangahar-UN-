from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(pattern="^(student|teacher)$")
    department: str | None = Field(default=None, max_length=160)
    student_id: str | None = Field(default=None, max_length=80)
    staff_id: str | None = Field(default=None, max_length=80)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    department: str | None
    student_id: str | None
    staff_id: str | None
    is_approved: bool
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class DocumentOut(BaseModel):
    id: int
    title: str
    description: str | None
    original_filename: str
    file_size: int
    department: str | None
    subject: str | None
    semester: str | None
    academic_year: str | None
    uploader_id: int
    status: str
    rejection_reason: str | None
    download_count: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserStatusIn(BaseModel):
    is_approved: bool | None = None
    is_active: bool | None = None

class DocumentReviewIn(BaseModel):
    status: str = Field(pattern="^(approved|rejected)$")
    rejection_reason: str | None = None
