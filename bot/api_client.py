import httpx
import os

API_URL    = os.getenv("API_URL", "http://api:8000")
API_SECRET = os.getenv("API_SECRET", "")

HEADERS = {"X-Internal-Secret": API_SECRET}


async def upsert_user(telegram_id: int, username: str | None,
                      first_name: str, last_name: str | None = None,
                      language_code: str = "uz") -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_URL}/api/users/upsert",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "language_code": language_code,
            },
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()


async def save_message(user_id: int, text: str,
                       direction: str = "in",
                       telegram_msg_id: int | None = None) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_URL}/api/messages/",
            json={
                "user_id": user_id,
                "text": text,
                "direction": direction,
                "telegram_msg_id": telegram_msg_id,
            },
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
