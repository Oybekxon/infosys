from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from routers import auth, users, messages, broadcasts, stats
from models.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: jadvallarni yaratish
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="InfoSys API",
    description="Telegram bot va veb-panel axborot tizimi",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da domenni ko'rsating
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routerlar
app.include_router(auth.router,       prefix="/api/auth",       tags=["Auth"])
app.include_router(users.router,      prefix="/api/users",      tags=["Users"])
app.include_router(messages.router,   prefix="/api/messages",   tags=["Messages"])
app.include_router(broadcasts.router, prefix="/api/broadcasts", tags=["Broadcasts"])
app.include_router(stats.router,      prefix="/api/stats",      tags=["Stats"])

# Media fayllar
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "InfoSys API"}
