# 🚀 Healthcare Voice AI - Deployment Guide

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring Setup](#monitoring-setup)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This guide covers the complete deployment process for the Healthcare Voice AI application, including development, staging, and production environments.

## 🔧 Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended

### Software Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Node.js**: 18+ (for frontend development)
- **Python**: 3.11+ (for backend development)

### External Services

- **Database**: Supabase (PostgreSQL)
- **Cache**: Redis
- **Voice AI**: VAPI
- **Calendar**: Google Calendar API
- **SSL**: Let's Encrypt (production)

## 🌍 Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/healthcare-voice-ai.git
cd healthcare-voice-ai
```

### 2. Environment Variables

Create environment files for different environments:

#### Development (.env.development)
```bash
# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# External APIs
VAPI_API_KEY=your_vapi_key
GOOGLE_CALENDAR_ID=your_calendar_id

# Security
JWT_SECRET=your_jwt_secret
REDIS_PASSWORD=your_redis_password

# Monitoring
GRAFANA_PASSWORD=your_grafana_password
```

#### Production (.env.production)
```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Database
SUPABASE_URL=your_production_supabase_url
SUPABASE_KEY=your_production_supabase_key

# External APIs
VAPI_API_KEY=your_production_vapi_key
GOOGLE_CALENDAR_ID=your_production_calendar_id

# Security
JWT_SECRET=your_strong_jwt_secret
REDIS_PASSWORD=your_strong_redis_password

# SSL
DOMAIN=your-domain.com
EMAIL=admin@your-domain.com

# Monitoring
GRAFANA_PASSWORD=your_strong_grafana_password
```

## 🐳 Docker Deployment

### Development Environment

```bash
# Start development environment
docker-compose --profile dev up -d

# View logs
docker-compose logs -f app

# Stop environment
docker-compose --profile dev down
```

### Production Environment

```bash
# Start production environment
docker-compose --profile prod up -d

# Start with SSL
docker-compose --profile ssl up -d

# Start with monitoring
docker-compose --profile monitoring up -d
```

### Available Profiles

- **dev**: Development environment with hot reload
- **prod**: Production environment without SSL
- **ssl**: Production environment with SSL/TLS
- **monitoring**: Monitoring stack (Prometheus, Grafana)
- **test**: Testing environment

## 🏭 Production Deployment

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application user
sudo useradd -m -s /bin/bash healthcare-ai
sudo usermod -aG docker healthcare-ai
```

### 2. Application Deployment

```bash
# Switch to application user
sudo su - healthcare-ai

# Clone repository
git clone https://github.com/your-org/healthcare-voice-ai.git
cd healthcare-voice-ai

# Copy environment file
cp .env.production .env

# Start production environment
docker-compose --profile ssl --profile monitoring up -d
```

### 3. System Service Setup

Create systemd service for automatic startup:

```bash
sudo tee /etc/systemd/system/healthcare-voice-ai.service > /dev/null <<EOF
[Unit]
Description=Healthcare Voice AI
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/healthcare-ai/healthcare-voice-ai
ExecStart=/usr/local/bin/docker-compose --profile ssl --profile monitoring up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=healthcare-ai

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable healthcare-voice-ai
sudo systemctl start healthcare-voice-ai
```

## 🔒 SSL/TLS Configuration

### Automatic SSL with Let's Encrypt

The application automatically handles SSL certificate generation and renewal using Let's Encrypt.

### Manual SSL Configuration

If you need to configure SSL manually:

```bash
# Generate SSL certificates
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to application
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./ssl/
```

### SSL Renewal

SSL certificates are automatically renewed by the `ssl-renewal` service in Docker Compose.

## 📊 Monitoring Setup

### Prometheus Metrics

Access Prometheus at: `http://your-domain.com:9090`

### Grafana Dashboards

Access Grafana at: `http://your-domain.com:3000`
- Username: `admin`
- Password: Set in `GRAFANA_PASSWORD` environment variable

### Key Metrics

- **Application Health**: `/system/health`
- **System Metrics**: `/system/metrics`
- **Prometheus Metrics**: `/metrics`

## 💾 Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec app-prod pg_dump -h your_supabase_host -U your_user -d your_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec app-prod psql -h your_supabase_host -U your_user -d your_db < backup_file.sql
```

### Application Data Backup

```bash
# Backup uploads and logs
tar -czf healthcare-ai-backup-$(date +%Y%m%d_%H%M%S).tar.gz uploads/ logs/ quarantine/

# Restore backup
tar -xzf healthcare-ai-backup-file.tar.gz
```

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/healthcare-voice-ai"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T app-prod pg_dump -h your_supabase_host -U your_user -d your_db > $BACKUP_DIR/db_backup_$DATE.sql

# Application data backup
tar -czf $BACKUP_DIR/app_data_$DATE.tar.gz uploads/ logs/ quarantine/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Application Won't Start

```bash
# Check logs
docker-compose logs app

# Check environment variables
docker-compose config

# Restart services
docker-compose restart
```

#### 2. Database Connection Issues

```bash
# Test database connection
docker-compose exec app python -c "from healthcare_voice_ai.core.database import db_manager; print(db_manager.health_check())"

# Check database logs
docker-compose logs postgres
```

#### 3. SSL Certificate Issues

```bash
# Check SSL status
docker-compose exec nginx-ssl certbot certificates

# Renew certificates manually
docker-compose exec nginx-ssl certbot renew
```

#### 4. Performance Issues

```bash
# Check system resources
docker stats

# Check application metrics
curl http://localhost:8000/system/metrics

# Check logs for errors
docker-compose logs app | grep ERROR
```

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# System status
curl http://localhost:8000/system/status

# Database status
curl http://localhost:8000/system/database/performance
```

### Log Locations

- **Application Logs**: `logs/healthcare_voice_ai.log`
- **Error Logs**: `logs/healthcare_voice_ai_errors.log`
- **Audit Logs**: `logs/healthcare_voice_ai_audit.log`
- **Nginx Logs**: `logs/nginx/`

## 🔄 Updates and Maintenance

### Application Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose --profile ssl --profile monitoring up -d --build

# Run database migrations
docker-compose exec app-prod alembic upgrade head
```

### System Maintenance

```bash
# Clean up unused Docker resources
docker system prune -a

# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart services
sudo systemctl restart healthcare-voice-ai
```

## 📞 Support

For deployment issues:

1. Check the logs first
2. Review this documentation
3. Check the GitHub issues
4. Contact the development team

## 🔐 Security Considerations

- Always use strong passwords
- Keep SSL certificates updated
- Regularly update dependencies
- Monitor security logs
- Implement proper firewall rules
- Use environment variables for secrets
- Enable audit logging
- Regular security scans
