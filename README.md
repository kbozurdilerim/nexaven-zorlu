# 🚀 ZorluForce - Automotive ECU Management System

Professional ECU file management, tuning, and AI-powered diagnostic system for automotive workshops and tuning companies.

## 📋 Overview

ZorluForce is a comprehensive automotive ECU (Engine Control Unit) management platform that provides:

- 🔧 **ECU File Management** - Upload, analyze, and manage ECU files
- 🤖 **AI-Powered Analysis** - Automatic ECU file analysis and optimization
- ⚡ **Advanced Tuning** - Professional ECU tuning and calibration
- 📊 **Performance Monitoring** - Track and analyze vehicle performance
- 👥 **Multi-User Support** - Role-based access control (Admin, Tuner, Franchise)
- 💰 **Billing System** - Credit-based subscription management
- 🔔 **Real-time Notifications** - WebSocket-based notification system

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.11 with FastAPI
- MongoDB for data storage
- WebSocket for real-time features
- Docker containerization

**Frontend:**
- React 18
- Modern responsive UI
- Real-time dashboard

**Infrastructure:**
- Nginx reverse proxy
- Docker Compose orchestration
- SSL/HTTPS support

## 🚀 Quick Deployment

### Prerequisites

- VPS/Server with Ubuntu 20.04+ or Debian 11+
- Docker & Docker Compose
- Domain name (e.g., nexaven.com.tr)
- At least 2GB RAM, 20GB disk space

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/zorluforce.git
cd zorluforce
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Important:** Change the `SECRET_KEY` to a secure random string!

### 3. Deploy with Script

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
sudo ./deploy.sh
```

The script will automatically:
- ✅ Install Docker and Docker Compose if needed
- ✅ Create necessary directories
- ✅ Build and start all containers
- ✅ Set up the database

### 4. Configure Domain

Add DNS A record pointing to your server IP:

```
Type: A
Host: @
Value: YOUR_SERVER_IP
TTL: 3600
```

### 5. Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d nexaven.com.tr

# Copy certificates
sudo cp /etc/letsencrypt/live/nexaven.com.tr/*.pem ./nginx/ssl/

# Restart Nginx
docker-compose restart nginx
```

## 🌐 Access

After deployment, access the application at:

- **Main Application**: `http://your-domain:8888/zorlu.ecu`
- **Alternative Port**: `http://your-domain:9000/zorlu.ecu`
- **API**: `http://your-domain:8888/zorlu.ecu/api`
- **HTTPS** (after SSL): `https://your-domain/zorlu.ecu`

## 🔌 Port Configuration

- **3001** - Backend API (FastAPI/Python)
- **8888** - HTTP Main Port (Nginx)
- **9000** - HTTP Alternative Port (Nginx)
- **443** - HTTPS (after SSL setup)

### Firewall Configuration

```bash
sudo ufw allow ssh
sudo ufw allow 3001/tcp
sudo ufw allow 8888/tcp
sudo ufw allow 9000/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📊 Management Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# Restart services
docker-compose restart

# Stop services
docker-compose stop

# Start services
docker-compose start

# Update deployment
git pull
docker-compose build --no-cache
docker-compose up -d

# Remove everything (including data)
docker-compose down -v
```

## 🔐 Default Users

After deployment, create an admin user:

```bash
docker exec -it zorluforce-backend python create_admin_user.py
```

## 🛠️ Configuration

### Environment Variables (.env)

```env
# Security (REQUIRED - Change this!)
SECRET_KEY=your-super-secure-random-key-here

# Domain
DOMAIN=nexaven.com.tr

# Database (usually no need to change)
MONGO_URL=mongodb://mongodb:27017/zorluforce
DB_NAME=zorluforce

# Optional: AI Services
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

# Optional: Email Configuration
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

## 📚 Documentation

- **[VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md)** - Detailed deployment guide
- **[DEPLOYMENT_README.md](DEPLOYMENT_README.md)** - Quick start guide
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Comprehensive deployment info

## 🔄 Backup & Restore

### MongoDB Backup

```bash
# Create backup
docker exec zorluforce-mongodb mongodump --out=/data/backup --db=zorluforce

# Copy backup to host
docker cp zorluforce-mongodb:/data/backup ./backup-$(date +%Y%m%d)

# Restore from backup
docker exec zorluforce-mongodb mongorestore /data/backup
```

### Uploads Backup

```bash
# Backup uploads directory
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz uploads/
```

## 🐛 Troubleshooting

### Containers not starting?

```bash
docker-compose logs
docker-compose ps
```

### Port already in use?

```bash
sudo lsof -i :8888
sudo lsof -i :3001
```

### Backend connection issues?

```bash
# Check backend health
curl http://localhost:3001/api/health

# Check network
docker network inspect zorluforce_zorluforce-network
```

## 🔒 Security Recommendations

1. ✅ Use strong `SECRET_KEY` in `.env`
2. ✅ Enable HTTPS with Let's Encrypt
3. ✅ Configure firewall (only necessary ports)
4. ✅ Regular backups
5. ✅ Keep Docker images updated
6. ✅ Use SSH key authentication
7. ✅ Install fail2ban for SSH protection

## 📈 Performance Optimization

### MongoDB Indexes

```bash
docker exec -it zorluforce-mongodb mongosh zorluforce

# Create indexes
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "username": 1 }, { unique: true })
db.uploads.createIndex({ "created_at": -1 })
```

## 🤝 Contributing

This is a proprietary system for automotive ECU management. For support or inquiries, please contact the development team.

## 📄 License

Proprietary - All rights reserved

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review documentation in `VPS_DEPLOYMENT.md`
3. Contact system administrator

---

**Made with ❤️ for Automotive Professionals**

🚗 Professional ECU Management | 🔧 Advanced Tuning | 🤖 AI-Powered Analysis
