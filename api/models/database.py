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
