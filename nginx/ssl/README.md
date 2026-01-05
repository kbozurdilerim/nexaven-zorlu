# SSL Sertifika Placeholder

Bu dizine SSL sertifikaları eklenecek.

## Let's Encrypt ile SSL Kurulumu

```bash
# 1. Certbot kurulumu
sudo apt install certbot

# 2. Sertifika oluşturma
sudo certbot certonly --standalone -d nexaven.com.tr -d www.nexaven.com.tr

# 3. Sertifikaları buraya kopyalama
sudo cp /etc/letsencrypt/live/nexaven.com.tr/fullchain.pem ./
sudo cp /etc/letsencrypt/live/nexaven.com.tr/privkey.pem ./

# 4. Nginx'i yeniden başlatma
docker-compose restart nginx
```

## Geçici Self-Signed Sertifika (Test için)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout privkey.pem \
  -out fullchain.pem \
  -subj "/C=TR/ST=Turkey/L=Istanbul/O=ZorluForce/CN=nexaven.com.tr"
```

**Not:** Production ortamında mutlaka Let's Encrypt sertifikası kullanın!
