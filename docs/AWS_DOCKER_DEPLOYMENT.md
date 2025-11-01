# 🚀 AWS Docker Deployment Guide for HybridRAG

This comprehensive guide will help you deploy the HybridRAG application to AWS using Docker and Docker Compose.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## 🎯 Prerequisites

Before you begin, ensure you have:

### ✅ AWS Setup
- [x] AWS EC2 instance running (Ubuntu 20.04 or later recommended)
- [x] Security Group configured with the following inbound rules:
  - SSH (22) - For terminal access
  - HTTP (80) - For frontend access
  - Custom TCP (8010) - For backend API access
- [x] Elastic IP attached to your EC2 instance (recommended for production)
- [x] SSH key pair for connecting to your instance

### ✅ External Services
- [x] **Supabase Account** with PostgreSQL database configured
  - Get credentials from: Supabase Dashboard → Project Settings → Database
- [x] **Pinecone Account** with an index created
  - Get API key from: https://app.pinecone.io/
- [x] **Google Gemini API Key**
  - Get from: https://makersuite.google.com/app/apikey

### ✅ Local Requirements (for pushing code)
- [x] Git installed and repository access
- [x] Your AWS EC2 instance IP address

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS EC2 Instance                      │
│                                                               │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │   Nginx (Port 80)│              │  Backend API     │    │
│  │   Frontend       │─────────────▶│  (Port 8010)     │    │
│  │   (React/Vite)   │              │  FastAPI + Gunicorn│   │
│  └──────────────────┘              └──────────────────┘    │
│           │                                  │               │
│           │                                  │               │
│           ▼                                  ▼               │
│    Docker Container 1              Docker Container 2       │
└───────────────────────────────────────────────────────────┘
                        │                      │
                        ▼                      ▼
        ┌───────────────────────────────────────────┐
        │        External Services                   │
        │  • Supabase (PostgreSQL Database)         │
        │  • Pinecone (Vector Database)             │
        │  • Google Gemini AI (LLM)                 │
        └───────────────────────────────────────────┘
```

---

## 🚀 Step-by-Step Deployment

### Step 1: Connect to Your AWS EC2 Instance

```bash
# Connect via SSH (replace with your key and IP)
ssh -i /path/to/your-key.pem ubuntu@YOUR_AWS_PUBLIC_IP
```

### Step 2: Install Docker and Docker Compose

```bash
# Update package index
sudo apt-get update

# Install prerequisite packages
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to the docker group (to run docker without sudo)
sudo usermod -aG docker $USER

# Apply the new group membership (logout and login, or run:)
newgrp docker

# Verify Docker installation
docker --version
docker compose version
```

Expected output:
```
Docker version 24.x.x, build xxxxx
Docker Compose version v2.x.x
```

### Step 3: Clone Your Repository

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/kanthkaushikkrishna11/hybridrag.git

# Navigate to the project directory
cd hybridrag

# Verify you're on the main branch
git branch
```

### Step 4: Configure Environment Variables

```bash
# Create .env file from template
cp env.template .env

# Edit the .env file with your actual credentials
nano .env
```

**Important:** Fill in ALL the following values in your `.env` file:

```bash
# Database Configuration (from Supabase)
DATABASE_USER=postgres.xyzabcdefgh
DATABASE_PASSWORD=your_actual_password_here
DATABASE_HOST=db.xyzabcdefgh.supabase.co
DATABASE_PORT=5432
DATABASE_NAME=postgres

# Pinecone Configuration
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX=pdf-assistant-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Google Gemini Configuration
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Frontend Configuration - IMPORTANT!
# Replace YOUR_AWS_PUBLIC_IP with your actual EC2 instance public IP
VITE_API_URL=http://YOUR_AWS_PUBLIC_IP:8010

# Application Configuration
MAX_FILE_SIZE=10485760
LOG_LEVEL=INFO
DEBUG=False
```

**To save and exit nano:**
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter`

### Step 5: Verify All Files Are Present

```bash
# Check if all Docker files exist
ls -la | grep -E 'Dockerfile|docker-compose|nginx.conf'
```

You should see:
- `Dockerfile.backend`
- `Dockerfile.frontend`
- `docker-compose.yml`
- `nginx.conf`

### Step 6: Build Docker Images

This step will take 5-10 minutes depending on your instance size.

```bash
# Build both frontend and backend images
docker compose build

# Verify images are created
docker images
```

You should see:
```
REPOSITORY              TAG       IMAGE ID       CREATED          SIZE
hybridrag-backend      latest    xxxxx          X minutes ago    XXX MB
hybridrag-frontend     latest    xxxxx          X minutes ago    XXX MB
```

### Step 7: Start the Application

```bash
# Start all services in detached mode
docker compose up -d

# Verify containers are running
docker compose ps
```

Expected output:
```
NAME                   STATUS              PORTS
hybridrag-backend      Up X seconds       0.0.0.0:8010->8010/tcp
hybridrag-frontend     Up X seconds       0.0.0.0:80->80/tcp
```

### Step 8: Verify Deployment

```bash
# Check backend health
curl http://localhost:8010/health

# Check frontend (should return HTML)
curl http://localhost/

# View backend logs
docker compose logs backend

# View frontend logs
docker compose logs frontend

# Follow logs in real-time (Ctrl+C to exit)
docker compose logs -f
```

### Step 9: Test External Access

Open your web browser and navigate to:

**Frontend:** `http://YOUR_AWS_PUBLIC_IP`

**Backend API:** `http://YOUR_AWS_PUBLIC_IP:8010/health`

You should see the HybridRAG application interface.

---

## 🔧 Environment Configuration

### Required Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_USER` | Supabase PostgreSQL user | `postgres.abcdefghijk` |
| `DATABASE_PASSWORD` | Database password | `your_secure_password` |
| `DATABASE_HOST` | Supabase database host | `db.abcdefghijk.supabase.co` |
| `DATABASE_PORT` | PostgreSQL port | `5432` |
| `DATABASE_NAME` | Database name | `postgres` |
| `PINECONE_API_KEY` | Pinecone API key | `12345678-abcd-1234-efgh-123456789abc` |
| `PINECONE_INDEX` | Pinecone index name | `pdf-assistant-index` |
| `PINECONE_CLOUD` | Cloud provider | `aws` |
| `PINECONE_REGION` | AWS region | `us-east-1` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSyXXXXXXXXXXXXXXXXXX` |
| `VITE_API_URL` | Backend API URL for frontend | `http://13.58.123.45:8010` |

### Getting Your Credentials

#### Supabase Database
1. Go to https://supabase.com/dashboard
2. Select your project
3. Navigate to **Settings** → **Database**
4. Find the connection string and extract:
   - Host (e.g., `db.abcdefghijk.supabase.co`)
   - User (e.g., `postgres.abcdefghijk`)
   - Password (your project password)

#### Pinecone
1. Go to https://app.pinecone.io/
2. Click on **API Keys** in the sidebar
3. Copy your API key
4. Note your index name (or create a new index with dimension 768)

#### Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Click **Create API Key**
3. Copy the generated key (starts with `AIza`)

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs for errors
docker compose logs backend
docker compose logs frontend

# Check if ports are already in use
sudo netstat -tlnp | grep -E '80|8010'

# If ports are in use, kill the process
sudo kill -9 <PID>
```

### Backend health check fails

```bash
# Check backend logs
docker compose logs backend

# Enter the backend container
docker compose exec backend bash

# Test inside container
python -c "import requests; print(requests.get('http://localhost:8010/health').text)"
```

### Frontend can't connect to backend

1. **Check VITE_API_URL:** Ensure it points to your public IP
   ```bash
   grep VITE_API_URL .env
   ```

2. **Rebuild frontend with correct URL:**
   ```bash
   docker compose down
   docker compose build frontend --no-cache
   docker compose up -d
   ```

3. **Check AWS Security Group:** Ensure port 8010 is open

### Database connection issues

```bash
# Test database connection from backend container
docker compose exec backend bash
python -c "
from src.backend.config import config
print(config.database_url)
"

# Test with psql
docker compose exec backend bash
apt-get update && apt-get install -y postgresql-client
psql "postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require"
```

### Pinecone connection issues

```bash
# Test Pinecone from backend container
docker compose exec backend python -c "
from pinecone import Pinecone
import os
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
print(pc.list_indexes())
"
```

### View all container logs

```bash
# All logs
docker compose logs

# Specific service
docker compose logs backend -f

# Last 100 lines
docker compose logs --tail=100
```

### Restart services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend

# Stop all services
docker compose down

# Start all services
docker compose up -d
```

---

## 🔄 Maintenance

### Updating the Application

```bash
# Navigate to project directory
cd ~/hybridrag

# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker compose down
docker compose build
docker compose up -d

# Verify
docker compose ps
```

### Viewing Logs

```bash
# Real-time logs
docker compose logs -f

# Backend only
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100
```

### Backup Data

```bash
# Create backup directory
mkdir -p ~/backups

# Backup logs
sudo cp -r ~/hybridrag/logs ~/backups/logs-$(date +%Y%m%d)

# Backup .env file
cp ~/hybridrag/.env ~/backups/.env-$(date +%Y%m%d)
```

### Monitoring Container Health

```bash
# Check container status
docker compose ps

# Check resource usage
docker stats

# Check specific container
docker inspect hybridrag-backend
```

### Cleaning Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything (CAUTION!)
docker system prune -a
```

### SSL/HTTPS Setup (Optional but Recommended)

For production, you should set up HTTPS using Let's Encrypt:

1. **Install Certbot:**
   ```bash
   sudo apt-get install -y certbot python3-certbot-nginx
   ```

2. **Get SSL Certificate:**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

3. **Update docker-compose.yml to mount certificates:**
   ```yaml
   frontend:
     volumes:
       - /etc/letsencrypt:/etc/letsencrypt:ro
   ```

4. **Update nginx.conf with SSL configuration**

---

## 📊 Performance Tuning

### Adjusting Worker Processes

Edit `Dockerfile.backend` to change number of workers based on your instance size:

```dockerfile
# For t2.small (1 vCPU): 2 workers
# For t2.medium (2 vCPU): 4 workers  
# For t2.large (2 vCPU): 4 workers
# Formula: (2 × CPU cores) + 1

CMD ["gunicorn", "app:app", \
     "--workers", "4", \
     ...
]
```

### Memory Optimization

For smaller instances (< 2GB RAM):

```yaml
# Add to docker-compose.yml under each service
services:
  backend:
    mem_limit: 1g
    mem_reservation: 512m
```

---

## 🎯 Quick Command Reference

```bash
# Start application
docker compose up -d

# Stop application
docker compose down

# View logs
docker compose logs -f

# Restart application
docker compose restart

# Rebuild and restart
docker compose down && docker compose build && docker compose up -d

# Check status
docker compose ps

# View resource usage
docker stats

# Access backend shell
docker compose exec backend bash

# Access frontend shell
docker compose exec frontend sh
```

---

## ✅ Deployment Checklist

Before going live, verify:

- [ ] All environment variables are set correctly in `.env`
- [ ] AWS Security Group allows ports 80, 8010, and 22
- [ ] Supabase database is accessible
- [ ] Pinecone index exists and is accessible
- [ ] Gemini API key is valid
- [ ] Frontend can access backend API
- [ ] Health endpoints return 200 OK
- [ ] Can upload a PDF and get responses
- [ ] Logs show no critical errors
- [ ] SSL certificate installed (for production)
- [ ] Monitoring and alerts configured
- [ ] Backup strategy in place

---

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review container logs: `docker compose logs`
3. Check AWS Security Group settings
4. Verify all environment variables
5. Test external services (Supabase, Pinecone, Gemini) individually

---

## 📝 Additional Notes

- **Persistence:** Logs are stored in `./logs` directory and persist across container restarts
- **Updates:** To update, pull latest code, rebuild images, and restart containers
- **Scaling:** For high traffic, consider using AWS ECS or EKS for container orchestration
- **Monitoring:** Consider adding tools like Prometheus, Grafana, or AWS CloudWatch
- **Backups:** Regularly backup your `.env` file and database

---

**🎉 Congratulations!** Your HybridRAG application is now live and accessible to the world!

Access your application at: `http://YOUR_AWS_PUBLIC_IP`

