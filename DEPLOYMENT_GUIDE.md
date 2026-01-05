# 🚀 ZorluForce Deployment Guide

## Overview

ZorluForce Automotive ECU Management System can be deployed in multiple configurations:

1. **Web Application** (Development)
2. **Desktop Application** (Windows, Linux, macOS)
3. **Mobile Application** (Android, iOS)
4. **Hybrid Deployment** (All platforms)

---

## 📦 Available Backends

### Python Backend (Port 8001)
- **Status:** ✅ Production Ready
- **Features:** All features implemented
- **Location:** `/app/backend/`

### C# Backend (Port 5193)
- **Status:** ✅ Production Ready  
- **Features:** Full feature parity with Python
- **Location:** `/app/backend-csharp/ZorluForce.API/`

---

## 🖥️ Desktop Deployment

### Prerequisites
- Node.js 18+
- Python 3.8+ (for Python backend) OR .NET 8.0 (for C# backend)
- MongoDB 5.0+

### Option 1: Electron + Python Backend

```bash
# 1. Build frontend
cd /app/frontend
yarn install
yarn build

# 2. Copy to Electron
cp -r build ../desktop-electron/

# 3. Package Electron app
cd ../desktop-electron
yarn install
yarn build:linux   # For Linux
# OR
yarn build:win     # For Windows (on Windows machine)
```

**Output:**
- Linux: `dist/ZorluForce-1.0.0.AppImage`, `dist/zorluforce_1.0.0_amd64.deb`
- Windows: `dist/ZorluForce Setup 1.0.0.exe`

### Option 2: Electron + C# Backend

```bash
# 1. Build C# backend
cd /app/backend-csharp/ZorluForce.API
dotnet publish -c Release -o ../../desktop-electron/resources/backend-csharp

# 2. Package with Electron (same as Option 1)
```

---

## 📱 Mobile Deployment

### Android

```bash
cd /app/mobile

# 1. Install dependencies
yarn install

# 2. Update backend URL in App.js
# Change BACKEND_URL to your server IP

# 3. Build APK
yarn build:android

# Output: android/app/build/outputs/apk/release/app-release.apk
```

### iOS

```bash
cd /app/mobile

# 1. Install dependencies  
yarn install
cd ios && pod install && cd ..

# 2. Update backend URL in App.js

# 3. Build (requires macOS + Xcode)
yarn build:ios

# Or open in Xcode:
# open ios/ZorluForce.xcworkspace
```

---

## 🌐 Web Deployment (Cloud)

### Using Docker

```dockerfile
# Dockerfile
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install
COPY frontend/ ./
RUN yarn build

FROM python:3.11-slim
WORKDIR /app

# Install MongoDB
RUN apt-get update && apt-get install -y mongodb

# Copy backend
COPY backend/ ./backend/
RUN pip install -r backend/requirements.txt

# Copy frontend build
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Expose ports
EXPOSE 8001 3000 27017

# Start services
CMD mongod --fork --logpath /var/log/mongodb.log && \
    cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 & \
    cd frontend && serve -s build -l 3000
```

Build and run:
```bash
docker build -t zorluforce .
docker run -p 8001:8001 -p 3000:3000 zorluforce
```

---

## 🔧 Installation Scripts

### Linux Installer

**Location:** `/app/installers/start-zorluforce.sh`

Features:
- Auto-checks MongoDB
- Starts backend automatically
- Creates log files
- System service integration

Usage:
```bash
./start-zorluforce.sh
```

### Windows Installer

**Location:** `/app/installers/start-zorluforce.bat`

Features:
- Checks MongoDB service
- Starts backend in background
- Creates desktop shortcuts
- Auto-updates

Usage:
```cmd
start-zorluforce.bat
```

---

## 📊 Backend Selection

### When to use Python Backend:
- ✅ Rapid development
- ✅ Easier AI/ML integration
- ✅ Larger ecosystem

### When to use C# Backend:
- ✅ Better Windows integration
- ✅ Higher performance
- ✅ Enterprise environments
- ✅ Native .NET applications

---

## 🔐 Environment Configuration

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=zorluforce_production
SECRET_KEY=your-super-secret-key-change-this
CORS_ORIGINS=*
```

### Frontend (.env.production)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
# OR for C#
REACT_APP_BACKEND_URL=http://localhost:5193
```

---

## 📦 Distribution Packages

### Windows
- **Installer:** `ZorluForce-Setup-1.0.0.exe`
- **Portable:** `ZorluForce-1.0.0-win.zip`
- **Size:** ~150MB

### Linux
- **AppImage:** `ZorluForce-1.0.0.AppImage`
- **DEB:** `zorluforce_1.0.0_amd64.deb`
- **RPM:** `zorluforce-1.0.0.x86_64.rpm`
- **Size:** ~120MB

### macOS
- **DMG:** `ZorluForce-1.0.0.dmg`
- **Size:** ~140MB

### Android
- **APK:** `zorluforce-1.0.0.apk`
- **Bundle:** `zorluforce-1.0.0.aab` (for Play Store)
- **Size:** ~25MB

### iOS
- **IPA:** `ZorluForce-1.0.0.ipa` (requires Apple Developer)
- **Size:** ~30MB

---

## 🧪 Testing Deployments

### Test Desktop App
```bash
# Linux
./ZorluForce-1.0.0.AppImage

# Windows
ZorluForce.exe

# macOS
open /Applications/ZorluForce.app
```

### Test Mobile App
```bash
# Android (via ADB)
adb install zorluforce-1.0.0.apk

# iOS (via Xcode)
xcrun simctl install booted ZorluForce.app
```

---

## 📝 Post-Deployment Checklist

- [ ] MongoDB configured and running
- [ ] Backend API accessible
- [ ] Frontend loads correctly
- [ ] User authentication works
- [ ] File upload functional
- [ ] AI features operational
- [ ] Database backups configured
- [ ] SSL certificates installed (production)
- [ ] Monitoring setup
- [ ] Error logging configured

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check logs
tail -f /app/logs/backend.log

# Verify MongoDB
sudo systemctl status mongod

# Check port availability
netstat -tulpn | grep 8001
```

### Frontend blank screen
```bash
# Check browser console
# Verify REACT_APP_BACKEND_URL
# Clear browser cache
```

### Mobile app connection issues
```bash
# Verify backend URL in App.js
# Check firewall rules
# Ensure backend accessible from mobile network
```

---

## 📞 Support

- **Email:** support@zorluforce.com
- **Documentation:** https://docs.zorluforce.com
- **Issues:** https://github.com/zorluforce/issues

---

## 📄 License

© 2024 ZorluForce Automotive Systems. All rights reserved.

This is proprietary software. See LICENSE file for details.
