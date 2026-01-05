# 🚀 ZorluForce VPS Deployment Guide

nexaven.com.tr/zorlu.ecu üzerinde çalışacak şekilde yapılandırılmış Docker Compose deployment.

## 📋 Gereksinimler

- VPS Sunucu (Ubuntu 20.04+ / Debian 11+ önerilir)
- Docker & Docker Compose
- SSH erişimi
- En az 2GB RAM, 20GB disk alanı
- Domain: nexaven.com.tr

## 🔧 Hızlı Kurulum

### 1. Dosyaları VPS'e Yükleme

```bash
# Yerel bilgisayarınızdan VPS'e dosyaları kopyalayın
scp -r cartechub/ user@your-vps-ip:/opt/zorluforce

# Veya git kullanarak
ssh user@your-vps-ip
cd /opt
git clone your-repo-url zorluforce
```

### 2. Deployment Script'ini Çalıştırma

```bash
# VPS'e bağlanın
ssh user@your-vps-ip

# Deployment dizinine gidin
cd /opt/zorluforce

# Script'i çalıştırılabilir yapın
chmod +x deploy.sh

# Deployment'ı başlatın
sudo ./deploy.sh
```

Script otomatik olarak:
- ✅ Docker ve Docker Compose'u kurar (yoksa)
- ✅ Gerekli dizinleri oluşturur
- ✅ .env dosyası oluşturur
- ✅ Tüm container'ları build eder ve başlatır

### 3. Environment Ayarları

`.env` dosyasını düzenleyin:

```bash
nano .env
```

**Önemli:** SECRET_KEY'i mutlaka değiştirin!

```env
SECRET_KEY=your-super-secret-key-here-min-32-chars
DOMAIN=nexaven.com.tr

# Opsiyonel: AI servisleri için API anahtarları
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Opsiyonel: Email ayarları
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Sonra container'ları yeniden başlatın:

```bash
docker-compose restart
```

## 🌐 Domain ve DNS Ayarları

### nexaven.com.tr DNS Kaydı

Domain sağlayıcınızda (GoDaddy, Namecheap, vs.) aşağıdaki A kaydını ekleyin:

```
Type: A
Host: @
Value: VPS_IP_ADRESINIZ
TTL: 3600
```

Alternatif olarak subdomain kullanmak isterseniz:

```
Type: A
Host: app (veya istediğiniz subdomain)
Value: VPS_IP_ADRESINIZ
TTL: 3600
```

## 🔒 SSL Sertifikası (HTTPS) Kurulumu

### Let's Encrypt ile Ücretsiz SSL

```bash
# Certbot kurulumu
sudo apt update
sudo apt install certbot -y

# SSL sertifikası oluşturma
sudo certbot certonly --standalone -d nexaven.com.tr -d www.nexaven.com.tr

# Sertifikaları nginx dizinine kopyalama
sudo cp /etc/letsencrypt/live/nexaven.com.tr/fullchain.pem /opt/zorluforce/nginx/ssl/
sudo cp /etc/letsencrypt/live/nexaven.com.tr/privkey.pem /opt/zorluforce/nginx/ssl/

# Nginx'i yeniden başlatma
cd /opt/zorluforce
docker-compose restart nginx
```

### Otomatik Sertifika Yenileme

```bash
# Crontab'a ekleyin
sudo crontab -e

# Şu satırı ekleyin (her ay 1'inde sertifikayı yeniler)
0 0 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/nexaven.com.tr/*.pem /opt/zorluforce/nginx/ssl/ && cd /opt/zorluforce && docker-compose restart nginx
```

## 📊 Yönetim Komutları

```bash
# Container durumlarını görüntüleme
docker-compose ps

# Logları görüntüleme (canlı)
docker-compose logs -f

# Belirli bir servisin loglarını görüntüleme
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# Servisleri durdurma
docker-compose stop

# Servisleri başlatma
docker-compose start

# Servisleri yeniden başlatma
docker-compose restart

# Tüm servisleri kaldırma (veriler korunur)
docker-compose down

# Tüm servisleri ve verileri kaldırma
docker-compose down -v

# Yeni deployment (güncellemeler için)
git pull  # veya dosyaları tekrar yükleyin
docker-compose build --no-cache
docker-compose up -d
```

## 🔍 Container'lara Erişim

```bash
# Backend container'a giriş
docker exec -it zorluforce-backend bash

# Frontend container'a giriş
docker exec -it zorluforce-frontend sh

# MongoDB container'a giriş
docker exec -it zorluforce-mongodb mongosh

# Nginx container'a giriş
docker exec -it zorluforce-nginx sh
```

## 📁 Yapı

```
nexaven.com.tr/zorlu.ecu          → Frontend uygulaması
nexaven.com.tr/zorlu.ecu/api      → Backend API
```

## 🔥 Firewall Ayarları

```bash
# UFW firewall kurulumu (Ubuntu/Debian)
sudo apt install ufw

# Temel portları açma
sudo ufw allow ssh
sudo ufw allow 3001/tcp  # Backend API
sudo ufw allow 8888/tcp  # HTTP Ana
sudo ufw allow 9000/tcp  # HTTP Alternatif
sudo ufw allow 443/tcp   # HTTPS

# Firewall'ı aktifleştirme
sudo ufw enable

# Durumu kontrol etme
sudo ufw status
```

## 🐛 Sorun Giderme

### Container başlamıyor

```bash
# Logları kontrol edin
docker-compose logs

# Container'ı yeniden build edin
docker-compose build --no-cache backend
docker-compose up -d
```

### Port kullanımda hatası

```bash
# Hangi process portu kullanıyor kontrol edin
sudo lsof -i :80
sudo lsof -i :443

# Process'i durdurun veya farklı port kullanın
```

### MongoDB bağlantı hatası

```bash
# MongoDB container'ının çalıştığını kontrol edin
docker-compose ps mongodb

# MongoDB loglarını kontrol edin
docker-compose logs mongodb

# MongoDB'yi yeniden başlatın
docker-compose restart mongodb
```

### Frontend backend'e bağlanamıyor

```bash
# Network ayarlarını kontrol edin
docker network ls
docker network inspect zorluforce_zorluforce-network

# Backend'in çalıştığını kontrol edin
curl http://localhost:3001/api/health
```

## 📈 Performans İyileştirmeleri

### 1. MongoDB Index'leri

```bash
docker exec -it zorluforce-mongodb mongosh zorluforce

# Index'leri oluşturun
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "username": 1 }, { unique: true })
db.uploads.createIndex({ "created_at": -1 })
```

### 2. Nginx Cache

nginx.conf'a cache ayarları eklenmiş durumda (static files için 1 yıl cache).

### 3. Container Resource Limitleri

docker-compose.yml'ye ekleyin:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M
```

## 🔄 Yedekleme

### MongoDB Yedekleme

```bash
# Yedek alma
docker exec zorluforce-mongodb mongodump --out=/data/backup --db=zorluforce

# Yedeği dışarı kopyalama
docker cp zorluforce-mongodb:/data/backup ./backup-$(date +%Y%m%d)

# Yedeği geri yükleme
docker exec zorluforce-mongodb mongorestore /data/backup
```

### Uploads Yedekleme

```bash
# Uploads klasörünü yedekleme
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz uploads/

# Uzak sunucuya yedekleme
rsync -avz uploads/ user@backup-server:/backups/zorluforce/
```

## 📞 Destek

Sorun yaşarsanız:
1. Logları kontrol edin: `docker-compose logs`
2. Container durumlarını kontrol edin: `docker-compose ps`
3. Sistem kaynaklarını kontrol edin: `htop` veya `docker stats`

## 🎉 Test

Deployment sonrası test edin:

```bash
# Frontend (Port 8888)
curl http://nexaven.com.tr:8888/zorlu.ecu

# Backend API
curl http://nexaven.com.tr:8888/zorlu.ecu/api/health

# Backend direkt erişim
curl http://localhost:3001/api/health

# 9000 portu (alternatif)
curl http://nexaven.com.tr:9000/zorlu.ecu

# SSL (HTTPS kurulduysa)
curl https://nexaven.com.tr/zorlu.ecu
```

Tarayıcıda: 
- `http://nexaven.com.tr:8888/zorlu.ecu`
- `http://nexaven.com.tr:9000/zorlu.ecu`
- `https://nexaven.com.tr/zorlu.ecu` (SSL sonrası)

## 🔐 Güvenlik Önerileri

1. ✅ `.env` dosyasındaki SECRET_KEY'i güçlü yapın
2. ✅ HTTPS kullanın (Let's Encrypt)
3. ✅ Firewall aktif edin (sadece 80, 443, SSH)
4. ✅ Düzenli yedekleme yapın
5. ✅ MongoDB'ye dışarıdan erişimi kapatın
6. ✅ SSH key-based authentication kullanın
7. ✅ Fail2ban kurun

```bash
# Fail2ban kurulumu
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

**Başarılı deployment'lar! 🚀**
