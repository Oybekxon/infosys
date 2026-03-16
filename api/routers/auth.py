from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
import os

from models.database import get_db, Admin

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


# ─── Schemalar ────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
    admin: dict


class AdminCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None


# ─── Yordamchi funksiyalar ────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati tugagan",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.execute(select(Admin).where(Admin.username == username))
    admin = result.scalar_one_or_none()
    if admin is None or not admin.is_active:
        raise credentials_exception
    return admin


# ─── Endpointlar ──────────────────────────────────────

@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Admin).where(Admin.username == form.username))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(form.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri login yoki parol",
        )

    # So'nggi kirish vaqtini yangilash
    admin.last_login = datetime.utcnow()
    await db.commit()

    token = create_token({"sub": admin.username, "id": admin.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "full_name": admin.full_name,
            "is_superuser": admin.is_superuser,
        }
    }


@router.post("/register", status_code=201)
async def register_first_admin(
    data: AdminCreate,
    db: AsyncSession = Depends(get_db)
):
    """Birinchi adminni yaratish (faqat hech admin yo'q bo'lganda ishlaydi)"""
    result = await db.execute(select(Admin))
    if result.first():
        raise HTTPException(status_code=403, detail="Admin allaqachon mavjud")

    admin = Admin(
        username=data.username,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        is_superuser=True,
    )
    db.add(admin)
    await db.commit()
    return {"message": "Admin muvaffaqiyatli yaratildi"}


@router.get("/me")
async def get_me(current_admin: Admin = Depends(get_current_admin)):
    return {
        "id": current_admin.id,
        "username": current_admin.username,
        "full_name": current_admin.full_name,
        "is_superuser": current_admin.is_superuser,
        "last_login": current_admin.last_login,
    }
