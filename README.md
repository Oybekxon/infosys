# InfoSys — Telegram Bot va Veb-Panel Axborot Tizimi

Zamonaviy axborot tizimi: Telegram bot + React admin panel + FastAPI backend + PostgreSQL.

---

## Tizim tarkibi

```
infosys/
├── api/                  ← FastAPI backend
│   ├── main.py           ← Asosiy ilova
│   ├── models/           ← Ma'lumotlar bazasi modellari
│   ├── routers/          ← API endpointlar
│   ├── requirements.txt
│   └── Dockerfile
├── bot/                  ← Telegram bot (aiogram 3)
│   ├── main.py           ← Bot entry point
│   ├── handlers/         ← Xabar handlerlari
│   ├── keyboards/        ← Tugmalar
│   ├── api_client.py     ← Backend bilan muloqot
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/             ← React admin panel (Vite)
│   ├── src/
│   │   ├── App.jsx       ← Asosiy komponent
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── nginx/
│   └── nginx.conf        ← Reverse proxy
├── docker-compose.yml    ← Barcha servislar
├── .env.example          ← O'zgaruvchilar shabloni
└── deploy.sh             ← Bir buyruqli o'rnatish
```

---

## Tezkor o'rnatish (serverda)

### 1-qadam: Serverga kirish

```bash
ssh root@SIZNING_SERVER_IP
```

### 2-qadam: Loyihani yuklab olish

```bash
git clone https://github.com/sizning/infosys.git
cd infosys
```

**Yoki arxivdan:**
```bash
unzip infosys.zip
cd infosys
```

### 3-qadam: Docker o'rnatish (agar yo'q bo'lsa)

```bash
# Ubuntu / Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Docker Compose plugin
sudo apt-get install docker-compose-plugin
```

### 4-qadam: Bir buyruq bilan ishga tushirish

```bash
chmod +x deploy.sh
bash deploy.sh
```

Skript sizdan quyidagilarni so'raydi:
- **BOT_TOKEN** — Telegram botingiz tokeni (@BotFather dan)
- **Admin login va parol**

Shundan keyin hamma narsa avtomatik sozlanadi.

---

## Qo'lda sozlash

### .env faylini tahrirlash

```bash
cp .env.example .env
nano .env
```

```env
BOT_TOKEN=1234567890:AABBccDDeeFF...   # @BotFather dan oling
DB_PASSWORD=kuchli_parol_kiriting
REDIS_PASSWORD=redis_paroli
SECRET_KEY=64_belgili_tasodifiy_kalit
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin_paroli
```

### Ishga tushirish

```bash
docker compose up -d --build
```

### Birinchi adminni yaratish

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"parolingiz","full_name":"Admin"}'
```

---

## Telegram Bot sozlash

### 1. Bot yaratish

1. Telegram'da **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: `InfoSys Bot`)
4. Bot username kiriting (masalan: `infosys_uz_bot`)
5. Olingan tokenni `.env` fayliga saqlang:
   ```
   BOT_TOKEN=1234567890:AAABBB...
   ```

### 2. Bot komandalarini sozlash

@BotFather ga quyidagini yuboring:
```
/setcommands
```
Botingizni tanlang va yuboring:
```
start - Boshlash
help - Yordam
```

---

## Admin panel ishlatish

Panel `http://SERVERINGIZ_IP` manzilida ochiladi.

### Sahifalar:

| Sahifa | Maqsad |
|--------|--------|
| **Boshqaruv** | Umumiy statistika, grafiklar |
| **Foydalanuvchilar** | Botga yozgan foydalanuvchilar ro'yxati, bloklash |
| **Xabarlar** | Barcha xabarlar tarixi |
| **Bildirishnomalar** | Barcha foydalanuvchilarga xabar yuborish |

---

## Foydali buyruqlar

```bash
# Loglarni ko'rish
docker compose logs -f api
docker compose logs -f bot
docker compose logs -f nginx

# Servislar holati
docker compose ps

# Qayta ishga tushirish
docker compose restart api
docker compose restart bot

# To'liq to'xtatish
docker compose down

# Ma'lumotlar bilan to'liq o'chirish (ehtiyot bo'ling!)
docker compose down -v

# Bot konteyneriga kirish
docker compose exec bot bash

# API konteyneriga kirish
docker compose exec api bash

# PostgreSQL ga kirish
docker compose exec postgres psql -U admin -d infosys
```

---

## API hujjatlari

Server ishga tushgandan so'ng:
- **Swagger UI:** `http://SERVERINGIZ_IP/docs`
- **ReDoc:** `http://SERVERINGIZ_IP/redoc`

---

## Yangi handler qo'shish (botga)

`bot/handlers/__init__.py` faylida yangi Router qo'shing:

```python
from aiogram import Router, F
from aiogram.types import Message

my_handler = Router()

@my_handler.message(F.text == "🆕 Yangi bo'lim")
async def my_section(msg: Message):
    await msg.answer("Yangi bo'lim javobi!")
```

Keyin `bot/main.py` da ro'yxatdan o'tkazing:
```python
from handlers import my_handler
dp.include_router(my_handler)
```

---

## Muammolarni hal qilish

### Bot ishlamaydi
```bash
docker compose logs bot
# BOT_TOKEN to'g'riligini tekshiring
```

### API ulanmaydi
```bash
docker compose logs api
# PostgreSQL va Redis tayyor bo'lishini kuting
docker compose logs postgres
```

### Port band
```bash
# 80-port kimga tegishli
sudo lsof -i :80
sudo systemctl stop nginx  # Agar system nginx bo'lsa
```

### Ma'lumotlar bazasi muammosi
```bash
# Bazani qayta yaratish
docker compose down -v
docker compose up -d
```
