# ZorluForce Quick Start Scripts

# Linux/Mac'te çalıştırma izni ver:
# chmod +x *.sh

# 1. İlk Kurulum
echo "Deployment başlatılıyor..."
sudo ./deploy.sh

# 2. Servisleri Başlat
docker-compose up -d

# 3. Servisleri Durdur
docker-compose stop

# 4. Servisleri Yeniden Başlat
docker-compose restart

# 5. Logları Görüntüle
docker-compose logs -f

# 6. Container Durumlarını Kontrol Et
docker-compose ps

# 7. Güncelleme (Yeni kod deploy)
git pull
docker-compose build --no-cache
docker-compose up -d

# 8. Temizlik (Container'ları ve volume'ları sil)
docker-compose down -v

# 9. MongoDB Backup
docker exec zorluforce-mongodb mongodump --out=/data/backup --db=zorluforce
docker cp zorluforce-mongodb:/data/backup ./backup-$(date +%Y%m%d)

# 10. SSL Sertifikası Kurma
sudo certbot certonly --standalone -d nexaven.com.tr
sudo cp /etc/letsencrypt/live/nexaven.com.tr/*.pem nginx/ssl/
docker-compose restart nginx
