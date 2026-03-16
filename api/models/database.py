from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean,
    DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import async_sessionmaker
import enum
import os
import ssl

_raw = os.getenv("DATABASE_URL", "postgresql://admin:secret123@localhost:5432/infosys")
_raw = _raw.split("?")[0]
DATABASE_URL = (
    _raw
    .replace("postgres://", "postgresql+asyncpg://")
    .replace("postgresql://", "postgresql+asyncpg://")
)

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"ssl": ssl_ctx},
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class UserStatus(str, enum.Enum):
    active  = "active"
    blocked = "blocked"
    pending = "pending"


class BroadcastStatus(str, enum.Enum):
    draft     = "draft"
    scheduled = "scheduled"
    sent      = "sent"
    failed    = "failed"


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id            = Column(Integer,    primary_key=True, index=True)
    telegram_id   = Column(BigInteger, unique=True, nullable=False, index=True)
    username      = Column(String(64), nullable=True)
    first_name    = Column(String(128),nullable=False)
    last_name     = Column(String(128),nullable=True)
    language_code = Column(String(8),  default="uz")
    status        = Column(SAEnum(UserStatus), default=UserStatus.active)
    is_bot        = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    messages   = relationship("Message",  back_populates="user")
    activities = relationship("Activity", back_populates="user")


class Message(Base):
    __tablename__ = "messages"

    id              = Column(Integer,    primary_key=True, index=True)
    user_id         = Column(Integer,    ForeignKey("telegram_users.id"), nullable=False)
    telegram_msg_id = Column(BigInteger, nullable=True)
    direction       = Column(String(8),  default="in")
    text            = Column(Text,       nullable=True)
    media_type      = Column(String(32), nullable=True)
    media_url       = Column(String(512),nullable=True)
    is_read         = Column(Boolean,    default=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("TelegramUser", back_populates="messages")


class Broadcast(Base):
    __tablename__ = "broadcasts"

    id           = Column(Integer,     primary_key=True, index=True)
    title        = Column(String(256), nullable=False)
    text         = Column(Text,        nullable=False)
    media_url    = Column(String(512), nullable=True)
    media_type   = Column(String(32),  nullable=True)
    status       = Column(SAEnum(BroadcastStatus), default=BroadcastStatus.draft)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at      = Column(DateTime(timezone=True), nullable=True)
    sent_count   = Column(Integer, default=0)
    fail_count   = Column(Integer, default=0)
    created_by   = Column(Integer, ForeignKey("admins.id"), nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    admin = relationship("Admin", back_populates="broadcasts")


class Admin(Base):
    __tablename__ = "admins"

    id              = Column(Integer,     primary_key=True, index=True)
    username        = Column(String(64),  unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name       = Column(String(128), nullable=True)
    is_superuser    = Column(Boolean, default=False)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    last_login      = Column(DateTime(timezone=True), nullable=True)

    broadcasts = relationship("Broadcast", back_populates="admin")


class Activity(Base):
    __tablename__ = "activities"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("telegram_users.id"), nullable=False)
    action     = Column(String(64), nullable=False)
    data       = Column(Text,       nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("TelegramUser", back_populates="activities")
