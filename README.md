# NUDL Backend — Nangarhar University Digital Library

FastAPI backend starter for a university digital library.

## Included
- Student and teacher self-registration (accounts wait for admin approval)
- JWT login and `/api/auth/me`
- Separate roles: student, teacher, admin, superadmin
- PDF upload with size and PDF-signature validation
- Admin approval queue for uploaded PDFs
- Approved document listing, inline preview and download
- Favorites and personal upload list
- Admin user approval/disable, document review and dashboard statistics
- Swagger API documentation at `/docs`

## 1. Requirements
Python 3.10+ (recommended 3.11 or 3.12).

## 2. Install locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set a strong `SECRET_KEY`.
For local testing, SQLite is configured by default.

## 3. Create the first Super Admin
Set environment variables in the same terminal.

Windows PowerShell:
```powershell
$env:ADMIN_EMAIL="your-admin-email@example.com"
$env:ADMIN_PASSWORD="Use-A-Unique-Password-At-Least-12-Chars"
$env:ADMIN_NAME="NU Digital Library Super Admin"
python create_admin.py
```

macOS/Linux:
```bash
export ADMIN_EMAIL="your-admin-email@example.com"
export ADMIN_PASSWORD="Use-A-Unique-Password-At-Least-12-Chars"
export ADMIN_NAME="NU Digital Library Super Admin"
python create_admin.py
```

Do not add a public admin-registration endpoint. Create administrators only through a trusted server-side process.

## 4. Run
```bash
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs`.

## 5. Main API routes
- `POST /api/auth/register` — student/teacher registration
- `POST /api/auth/login` — login; returns bearer token
- `GET /api/auth/me` — current user
- `POST /api/documents/upload` — upload PDF (multipart form)
- `GET /api/documents` — search/list documents
- `GET /api/documents/{id}/preview` — preview PDF
- `GET /api/documents/{id}/download` — download PDF
- `POST /api/documents/{id}/favorite` — toggle favorite
- `GET /api/documents/my/favorites` — favorites
- `GET /api/documents/my/uploads` — current user's uploads
- `GET /api/admin/stats` — admin dashboard counters
- `GET /api/admin/users` — user list
- `PATCH /api/admin/users/{id}` — approve/disable account
- `GET /api/admin/documents/pending` — pending PDFs
- `PATCH /api/admin/documents/{id}/review` — approve/reject PDF

## 6. Frontend connection
Send `Authorization: Bearer <access_token>` for protected routes.
For file upload, send `multipart/form-data` with `title`, optional metadata fields, and `file`.
Set `CORS_ORIGINS` to the exact deployed frontend origin(s), comma-separated.

## 7. Deploy notes
- Use PostgreSQL in production, not SQLite.
- Set `DATABASE_URL`, `SECRET_KEY`, `UPLOAD_DIR`, `MAX_UPLOAD_MB`, and `CORS_ORIGINS` in hosting environment variables.
- Persistent disk/object storage is required for uploaded PDFs. Ephemeral hosting storage can be lost during redeploys.
- Back up the database and uploaded files.
- For production schema changes, add Alembic migrations before changing models.
- Before public launch, add email verification, password reset, audit logs, rate limiting, malware scanning, pagination metadata, and institutional account verification.
