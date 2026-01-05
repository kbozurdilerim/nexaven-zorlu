@echo off
REM ZorluForce VPS Deployment Script - Windows Version
REM For nexaven.com.tr/zorlu.ecu

echo ================================
echo  ZorluForce VPS Deployment
echo ================================
echo.

set DOMAIN=nexaven.com.tr
set APP_DIR=C:\zorluforce

REM Check if Docker is installed
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker bulunamadi! Lutfen Docker Desktop'i yukleyin:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [OK] Docker mevcut
echo.

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker Compose bulunamadi!
    pause
    exit /b 1
)

echo [OK] Docker Compose mevcut
echo.

REM Navigate to project directory
if not exist "%APP_DIR%" (
    echo [INFO] Uygulama dizini olusturuluyor: %APP_DIR%
    mkdir "%APP_DIR%"
)

cd /d "%APP_DIR%"

REM Check for .env file
if not exist ".env" (
    echo [WARNING] .env dosyasi bulunamadi
    echo [INFO] .env.example dosyasindan kopyalayin ve duzenleyin
    if exist ".env.example" (
        copy .env.example .env
        echo [OK] .env dosyasi olusturuldu
    )
)

REM Create necessary directories
echo [INFO] Gerekli dizinler olusturuluyor...
if not exist "uploads\ai_analysis" mkdir uploads\ai_analysis
if not exist "uploads\ai_training" mkdir uploads\ai_training
if not exist "uploads\backups" mkdir uploads\backups
if not exist "ai-models" mkdir ai-models
if not exist "nginx\ssl" mkdir nginx\ssl

echo [OK] Dizinler olusturuldu
echo.

REM Build and start containers
echo [INFO] Docker containers olusturuluyor ve baslatiliyor...
docker-compose down
docker-compose build --no-cache
docker-compose up -d

REM Wait for services
echo [INFO] Servisler baslatiliyor...
timeout /t 10 /nobreak >nul

REM Check container status
echo.
echo [INFO] Container durumlari:
docker-compose ps

echo.
echo ================================
echo  Deployment Tamamlandi!
echo ================================
echo.
echo Ana adres: http://%DOMAIN%:8888/zorlu.ecu
echo Alternatif: http://%DOMAIN%:9000/zorlu.ecu
echo API endpoint: http://%DOMAIN%:8888/zorlu.ecu/api
echo.
echo Kullanilan Portlar:
echo   3001 - Backend API (FastAPI/Python)
echo   8888 - HTTP Ana Port (Nginx)
echo   9000 - HTTP Alternatif Port (Nginx)
echo   443  - HTTPS (SSL sonrasi)
echo.
echo Yonetim Komutlari:
echo   Durumu kontrol et:    docker-compose ps
echo   Loglari goruntule:    docker-compose logs -f
echo   Durdur:               docker-compose stop
echo   Baslat:               docker-compose start
echo   Yeniden baslat:       docker-compose restart
echo.
pause
