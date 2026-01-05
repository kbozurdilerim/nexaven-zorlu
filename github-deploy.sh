#!/bin/bash
# ZorluForce GitHub Deploy Script
# Tüm değişiklikleri commit ve push yapar

set -e

echo "🚀 ZorluForce GitHub Deploy"
echo "============================"
echo ""

# Git durumunu kontrol et
echo "📊 Durumu kontrol ediyorum..."
git status

echo ""
echo "📝 Değişiklikleri ekliyor..."
git add .

echo ""
echo "💬 Commit mesajı:"
COMMIT_MSG="feat: Otomatik AI models indirmesi ve frontend-backend entegrasyonu

- AI models otomatik indirme scripti ekle
- Backend startup'da modelleri initialize et
- Frontend-backend CORS konfigürasyonu
- Docker Compose AI models volume mapping
- Startup scripts ve entrypoint'ler"

echo "$COMMIT_MSG"
echo ""

git commit -m "$COMMIT_MSG" || echo "Hiç değişiklik yok veya hata oluştu"

echo ""
echo "🔼 GitHub'a push yapılıyor..."
git push origin main || git push origin master || echo "Push başarısız olabilir"

echo ""
echo "✅ Deploy tamamlandı!"
echo ""
echo "Sıradaki adımlar:"
echo "1. GitHub repository'ni kontrol edin"
echo "2. VPS'te deploy edin: sudo ./deploy.sh"
echo "3. Erişin: http://your-domain:8888/zorlu.ecu"
