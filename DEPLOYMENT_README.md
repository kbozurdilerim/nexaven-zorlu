# ZorluForce - nexaven.com.tr/zorlu.ecu Deployment

## 🎯 Kurulum Yapıldı

✅ Docker Compose yapılandırması
✅ Backend Dockerfile (Python + FastAPI)
✅ Frontend Dockerfile (React + Nginx)
✅ Nginx reverse proxy (/zorlu.ecu alt dizini için)
✅ Environment dosyaları (.env.example, .env.production)
✅ Deployment scriptleri (deploy.sh, deploy.bat)
✅ Detaylı dokümantasyon (VPS_DEPLOYMENT.md)

## 🚀 VPS'e Nasıl Deploy Edilir?

### Adım 1: Dosyaları VPS'e Yükleyin

```bash
# SSH ile bağlanın
ssh kullanici@vps-ip-adresi

# Uygulama dizini oluşturun
sudo mkdir -p /opt/zorluforce

# Dosyaları yükleyin (yerel bilgisayarınızdan)
scp -r C:\Users\zorlu\Desktop\cartechub/* kullanici@vps-ip:/opt/zorluforce/
```

### Adım 2: Deployment Script'ini Çalıştırın

```bash
# VPS'te
cd /opt/zorluforce
chmod +x deploy.sh
sudo ./deploy.sh
```

Script otomatik olarak:
- Docker ve Docker Compose kurar
- .env dosyası oluşturur
- Tüm container'ları build edip başlatır

### Adım 3: Domain DNS Ayarları

nexaven.com.tr domain sağlayıcınızda (GoDaddy, Namecheap, vs.):

```
Type: A
Host: @
Value: VPS_IP_ADRESINIZ
TTL: 3600
```

### Adım 4: SSL Sertifikası (HTTPS)

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d nexaven.com.tr
sudo cp /etc/letsencrypt/live/nexaven.com.tr/*.pem /opt/zorluforce/nginx/ssl/
docker-compose restart nginx
```

## 📍 Erişim Adresleri

- Frontend: `https://nexaven.com.tr/zorlu.ecu`
- API: `https://nexaven.com.tr/zorlu.ecu/api`
- Health Check: `https://nexaven.com.tr/zorlu.ecu/api/health`
- Ana Port: `http://nexaven.com.tr:8888/zorlu.ecu`
- Alternatif Port: `http://nexaven.com.tr:9000/zorlu.ecu`

## 🔌 Kullanılan Portlar

- **3001**: Backend API (FastAPI/Python)
- **8888**: HTTP Ana Port (Nginx)
- **9000**: HTTP Alternatif Port (Nginx)
- **443**: HTTPS (SSL sertifikası sonrası)

## 📊 Yönetim Komutları

```bash
# Container durumunu kontrol et
docker-compose ps

# Logları görüntüle
docker-compose logs -f

# Servisleri yeniden başlat
docker-compose restart

# Güncellemeler için
git pull  # veya dosyaları yeniden yükle
docker-compose build --no-cache
docker-compose up -d
```

## 🔧 Önemli Ayarlar

### .env Dosyası

```env
SECRET_KEY=güvenli-rastgele-32-karakter-değiştir
DOMAIN=nexaven.com.tr
MONGO_URL=mongodb://mongodb:27017/zorluforce
DB_NAME=zorluforce
```

### Firewall

```bash
sudo ufw allow ssh
sudo ufw allow 3001/tcp  # Backend API
sudo ufw allow 8888/tcp  # HTTP Ana
sudo ufw allow 9000/tcp  # HTTP Alternatif
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## 📚 Detaylı Dokümantasyon

Tüm detaylar için: `VPS_DEPLOYMENT.md` dosyasına bakın.

## 🐛 Sorun Giderme

### Container başlamıyor?
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Port kullanımda?
```bash
sudo lsof -i :80
sudo lsof -i :443
```

### Backend'e erişilemiyor?
```bash
curl http://localhost:8001/api/health
docker-compose logs backend
```

## 🔒 Güvenlik

1. ✅ `.env` dosyasındaki SECRET_KEY'i değiştirin
2. ✅ HTTPS kullanın (Let's Encrypt)
3. ✅ Firewall aktif edin
4. ✅ Düzenli backup yapın

## 📦 Dosya Yapısı

```
cartechub/
├── docker-compose.yml          # Ana orchestration
├── .env.example                # Environment şablonu
├── deploy.sh                   # Linux deployment
├── deploy.bat                  # Windows deployment
├── VPS_DEPLOYMENT.md           # Detaylı kılavuz
├── backend/
│   ├── Dockerfile             # Python backend image
│   └── ...
├── frontend/
│   ├── Dockerfile             # React frontend image
│   ├── nginx.conf             # Frontend nginx config
│   └── ...
└── nginx/
    ├── nginx.conf             # Ana reverse proxy
    └── ssl/                   # SSL sertifikaları
```

## 🎉 Başarılı Deployment!

Uygulama nexaven.com.tr/zorlu.ecu adresinde çalışacak!

Her şey hazır - sadece VPS'e yükleyip deploy.sh scriptini çalıştırın! 🚀
