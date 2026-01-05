#!/bin/bash

# ZorluForce VPS Deployment Script
# For nexaven.com.tr/zorlu.ecu

set -e

echo "🚀 ZorluForce VPS Deployment"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="nexaven.com.tr"
APP_DIR="/opt/zorluforce"
REPO_URL="git@github.com:yourusername/zorluforce.git" # Git repo'nuzu buraya ekleyin

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Bu script root olarak çalıştırılmalıdır${NC}"
    echo "Kullanım: sudo ./deploy.sh"
    exit 1
fi

echo -e "${BLUE}📋 Sistem gereksinimleri kontrol ediliyor...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker bulunamadı, kuruluyor...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $SUDO_USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker kuruldu${NC}"
else
    echo -e "${GREEN}✅ Docker mevcut${NC}"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose bulunamadı, kuruluyor...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose kuruldu${NC}"
else
    echo -e "${GREEN}✅ Docker Compose mevcut${NC}"
fi

# Create application directory
echo -e "${BLUE}📁 Uygulama dizini oluşturuluyor...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env dosyası bulunamadı${NC}"
    echo -e "${BLUE}📝 Örnek .env dosyası oluşturuluyor...${NC}"
    
    # Generate random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    cat > .env << EOF
# ZorluForce Production Environment
SECRET_KEY=$SECRET_KEY
DOMAIN=$DOMAIN
MONGO_URL=mongodb://mongodb:27017/zorluforce
DB_NAME=zorluforce

# Optional: AI API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

# Optional: Email Configuration
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EOF

    echo -e "${GREEN}✅ .env dosyası oluşturuldu${NC}"
    echo -e "${YELLOW}⚠️  .env dosyasını düzenleyip gerekli ayarları yapın${NC}"
fi

# Pull latest changes (if git repo is configured)
if [ -d ".git" ]; then
    echo -e "${BLUE}📥 En son değişiklikler çekiliyor...${NC}"
    git pull
else
    echo -e "${YELLOW}⚠️  Git repository bulunamadı${NC}"
    echo -e "${BLUE}📦 Dosyaları manuel olarak yükleyin veya git clone yapın${NC}"
fi

# Create necessary directories
echo -e "${BLUE}📂 Gerekli dizinler oluşturuluyor...${NC}"
mkdir -p uploads/ai_analysis uploads/ai_training uploads/backups
mkdir -p ai-models
mkdir -p nginx/ssl

# Set permissions
chmod -R 755 uploads
chmod -R 755 ai-models

# Build and start containers
echo -e "${BLUE}🐳 Docker containers oluşturuluyor ve başlatılıyor...${NC}"
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
echo -e "${BLUE}⏳ Servisler başlatılıyor...${NC}"
sleep 10

# Check container status
echo -e "${BLUE}📊 Container durumları:${NC}"
docker-compose ps

# Show logs
echo ""
echo -e "${BLUE}📋 Son loglar:${NC}"
docker-compose logs --tail=50

echo ""
echo -e "${GREEN}✅ Deployment tamamlandı!${NC}"
echo ""
echo -e "${YELLOW}📝 Önemli Notlar:${NC}"
echo "================================"
echo -e "1. Uygulama ana adresi: ${BLUE}http://$DOMAIN:8888/zorlu.ecu${NC}"
echo -e "2. Alternatif adres: ${BLUE}http://$DOMAIN:9000/zorlu.ecu${NC}"
echo -e "3. API endpoint: ${BLUE}http://$DOMAIN:8888/zorlu.ecu/api${NC}"
echo ""
echo -e "${YELLOW}🔌 Kullanılan Portlar:${NC}"
echo "   3001 - Backend API (FastAPI/Python)"
echo "   8888 - HTTP Ana Port (Nginx)"
echo "   9000 - HTTP Alternatif Port (Nginx)"
echo "   443  - HTTPS (SSL sonrası)"
echo ""
echo -e "${YELLOW}🔒 SSL Sertifikası (HTTPS) için:${NC}"
echo "   1. Let's Encrypt kurulumu:"
echo "      sudo apt install certbot"
echo "      sudo certbot certonly --standalone -d $DOMAIN"
echo ""
echo "   2. Sertifika dosyalarını kopyalayın:"
echo "      sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $APP_DIR/nginx/ssl/"
echo "      sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $APP_DIR/nginx/ssl/"
echo ""
echo "   3. Nginx'i yeniden başlatın:"
echo "      docker-compose restart nginx"
echo ""
echo -e "${YELLOW}📊 Yönetim Komutları:${NC}"
echo "   Durumu kontrol et:    docker-compose ps"
echo "   Logları görüntüle:    docker-compose logs -f"
echo "   Durdur:               docker-compose stop"
echo "   Başlat:               docker-compose start"
echo "   Yeniden başlat:       docker-compose restart"
echo "   Kaldır:               docker-compose down"
echo ""
echo -e "${GREEN}🎉 Kurulum başarıyla tamamlandı!${NC}"
