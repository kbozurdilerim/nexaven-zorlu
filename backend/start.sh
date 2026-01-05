#!/bin/bash
# ZorluForce Backend Startup Script
# AI models'i initialize et ve uvicorn'u başlat

set -e

echo "🚀 ZorluForce Backend Başlatılıyor..."
echo ""

# AI models'i kontrol et ve indir
echo "📦 AI Models kontrol ediliyor..."
python /app/init_ai_models.py || echo "⚠️  AI Models initializasyonu atlanıyor..."

echo ""
echo "🔌 Backend API başlatılıyor... (Port 3001)"
echo ""

# Backend'i başlat
exec python -m uvicorn server:app --host 0.0.0.0 --port 3001 --workers 2
