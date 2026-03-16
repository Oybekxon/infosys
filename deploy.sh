#!/bin/bash
# ══════════════════════════════════════════════════════
#  InfoSys — To'liq o'rnatish skripti
#  Ishlatish: bash deploy.sh
# ══════════════════════════════════════════════════════
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; exit 1; }
info() { echo -e "${BLUE}[→]${NC} $1"; }

echo ""
echo "══════════════════════════════════════════════"
echo "   InfoSys — Axborot tizimi o'rnatilmoqda"
echo "══════════════════════════════════════════════"
echo ""

# ─── 1. Muhit tekshirish ──────────────────────────────
info "Docker tekshirilmoqda..."
command -v docker      >/dev/null 2>&1 || err "Docker o'rnatilmagan! https://docs.docker.com/get-docker/"
command -v docker compose >/dev/null 2>&1 || err "Docker Compose o'rnatilmagan!"
log "Docker tayyor: $(docker --version)"

# ─── 2. .env fayl ────────────────────────────────────
if [ ! -f ".env" ]; then
    warn ".env fayli topilmadi — .env.example dan nusxa olinmoqda..."
    cp .env.example .env

    # Tasodifiy kalitlar generatsiya qilish
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    DB_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))" 2>/dev/null || openssl rand -base64 12)
    REDIS_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(12))" 2>/dev/null || openssl rand -base64 10)

    sed -i "s/your_strong_password_here/$DB_PASS/g"    .env
    sed -i "s/your_redis_password_here/$REDIS_PASS/g"  .env
    sed -i "s/your_very_long_random_secret_key_minimum_32_chars/$SECRET/g" .env

    echo ""
    echo "════════════════════════════════════════════"
    warn "Muhim: .env faylini oching va BOT_TOKEN ni kiriting!"
    echo ""
    echo "  nano .env"
    echo ""
    echo "  BOT_TOKEN=sizning_bot_tokeningiz"
    echo "════════════════════════════════════════════"
    echo ""

    read -p "BOT_TOKEN ni kiriting (yoki Enter bosib keyinroq qo'shing): " BOT_TOKEN_INPUT
    if [ ! -z "$BOT_TOKEN_INPUT" ]; then
        sed -i "s/1234567890:AABBccDDeeFFggHHiiJJkkLLmmNNoopp/$BOT_TOKEN_INPUT/g" .env
        log "BOT_TOKEN saqlandi"
    fi
fi

# ─── 3. SSL papkasini yaratish ────────────────────────
mkdir -p nginx/ssl
log "Nginx SSL papkasi tayyor"

# ─── 4. Eski konteynerlarni to'xtatish ───────────────
info "Eski konteynerlar to'xtatilmoqda..."
docker compose down --remove-orphans 2>/dev/null || true

# ─── 5. Imaglarni build qilish ────────────────────────
info "Docker imaglar build qilinmoqda (bir necha daqiqa ketishi mumkin)..."
docker compose build --no-cache
log "Build muvaffaqiyatli!"

# ─── 6. Ishga tushirish ───────────────────────────────
info "Servislar ishga tushirilmoqda..."
docker compose up -d
log "Barcha servislar ishga tushdi!"

# ─── 7. Ma'lumotlar bazasini kutish ──────────────────
info "PostgreSQL tayyor bo'lishini kutilmoqda..."
sleep 8

# ─── 8. Birinchi adminni yaratish ─────────────────────
echo ""
echo "════════════════════════════════════════════"
info "Birinchi adminni yaratish..."
echo ""
read -p "  Admin login (default: admin): " ADMIN_USER
ADMIN_USER=${ADMIN_USER:-admin}
read -s -p "  Admin parol: " ADMIN_PASS
echo ""

RESPONSE=$(curl -s -X POST "http://localhost:8000/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$ADMIN_USER\",\"password\":\"$ADMIN_PASS\",\"full_name\":\"Super Admin\"}" 2>&1)

if echo "$RESPONSE" | grep -q "muvaffaqiyatli\|created"; then
    log "Admin yaratildi: $ADMIN_USER"
else
    warn "Admin yaratishda muammo (balki allaqachon mavjud): $RESPONSE"
fi

# ─── 9. Holat tekshirish ──────────────────────────────
echo ""
echo "════════════════════════════════════════════"
info "Servislar holati:"
docker compose ps
echo ""

# ─── 10. Natija ──────────────────────────────────────
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo ""
echo "══════════════════════════════════════════════"
echo -e "${GREEN}  InfoSys muvaffaqiyatli o'rnatildi!${NC}"
echo "══════════════════════════════════════════════"
echo ""
echo "  🌐 Admin panel:  http://$SERVER_IP"
echo "  📡 API docs:     http://$SERVER_IP/docs"
echo "  🤖 Bot:          Telegram'da botingizni toping"
echo ""
echo "  Login:  $ADMIN_USER"
echo ""
echo "  Loglarni ko'rish:"
echo "    docker compose logs -f api"
echo "    docker compose logs -f bot"
echo ""
echo "  To'xtatish:   docker compose down"
echo "  Qayta start:  docker compose up -d"
echo "══════════════════════════════════════════════"
