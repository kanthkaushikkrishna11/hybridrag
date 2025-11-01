# 🐳 Docker Deployment Files Overview

This directory contains all necessary files for deploying HybridRAG using Docker on AWS EC2.

## 📁 Files Included

### Docker Configuration Files

| File | Purpose |
|------|---------|
| `Dockerfile.backend` | Builds the FastAPI backend container |
| `Dockerfile.frontend` | Builds the React frontend with Nginx |
| `docker-compose.yml` | Orchestrates both containers |
| `nginx.conf` | Nginx configuration for serving React app |
| `.dockerignore` | Excludes unnecessary files from Docker build |

### Deployment Files

| File | Purpose |
|------|---------|
| `deploy-aws.sh` | Automated deployment script for AWS |
| `env.template` | Template for environment variables |

### Documentation

| File | Purpose |
|------|---------|
| `docs/AWS_DOCKER_DEPLOYMENT.md` | Complete deployment guide |
| `docs/DEPLOYMENT.md` | General deployment options |

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# On your AWS EC2 Ubuntu instance
git clone https://github.com/kanthkaushikkrishna11/hybridrag.git
cd hybridrag
cp env.template .env
nano .env  # Configure your credentials
chmod +x deploy-aws.sh
./deploy-aws.sh
```

### Option 2: Manual Deployment

```bash
# 1. Configure environment
cp env.template .env
nano .env

# 2. Build images
docker compose build

# 3. Start containers
docker compose up -d

# 4. Check status
docker compose ps
docker compose logs -f
```

## 🔧 Architecture

```
┌─────────────────────────────────────────────┐
│           AWS EC2 Instance                  │
│                                              │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │   Frontend   │      │    Backend      │ │
│  │  (Nginx:80)  │─────▶│  (FastAPI:8010) │ │
│  └──────────────┘      └─────────────────┘ │
│         │                       │           │
└─────────┼───────────────────────┼───────────┘
          │                       │
          ▼                       ▼
   [Users Browser]      [External Services]
                        • Supabase (Database)
                        • Pinecone (Vector DB)
                        • Google Gemini (AI)
```

## 📋 Prerequisites

### AWS Setup
- EC2 instance (Ubuntu 20.04+)
- Security Group with ports: 22 (SSH), 80 (HTTP), 8010 (API)
- Elastic IP (recommended)

### External Services
- Supabase account (PostgreSQL database)
- Pinecone account (vector database)
- Google Gemini API key

## 🔐 Environment Variables

Required in `.env` file:

```bash
# Database (Supabase)
DATABASE_USER=postgres.xxxxx
DATABASE_PASSWORD=xxxxx
DATABASE_HOST=db.xxxxx.supabase.co
DATABASE_PORT=5432
DATABASE_NAME=postgres

# Pinecone
PINECONE_API_KEY=xxxxx
PINECONE_INDEX=pdf-assistant-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Google Gemini
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXX

# Frontend (replace with your EC2 public IP)
VITE_API_URL=http://YOUR_AWS_PUBLIC_IP:8010
```

## 🐛 Common Issues

### Port Already in Use
```bash
sudo netstat -tlnp | grep -E '80|8010'
sudo kill -9 <PID>
```

### Container Won't Start
```bash
docker compose logs backend
docker compose logs frontend
```

### Frontend Can't Connect to Backend
1. Check `VITE_API_URL` in `.env`
2. Rebuild frontend: `docker compose build frontend --no-cache`
3. Verify AWS Security Group allows port 8010

### Database Connection Failed
```bash
docker compose exec backend python -c "from src.backend.config import config; print(config.database_url)"
```

## 🔄 Maintenance Commands

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop services
docker compose down

# Update and redeploy
git pull origin main
docker compose down
docker compose build
docker compose up -d

# Clean up
docker system prune -a
```

## 📊 Monitoring

```bash
# Check container status
docker compose ps

# Resource usage
docker stats

# Health checks
curl http://localhost:8010/health
curl http://localhost/health
```

## 🌐 Access Your Application

After successful deployment:

- **Frontend:** `http://YOUR_AWS_PUBLIC_IP`
- **Backend API:** `http://YOUR_AWS_PUBLIC_IP:8010`
- **Health Check:** `http://YOUR_AWS_PUBLIC_IP:8010/health`

## 📚 Full Documentation

For complete step-by-step instructions, troubleshooting, and best practices:

👉 **[AWS Docker Deployment Guide](docs/AWS_DOCKER_DEPLOYMENT.md)**

## 💡 Tips

1. **Use Elastic IP** for consistent public IP address
2. **Enable HTTPS** using Let's Encrypt for production
3. **Monitor logs** regularly: `docker compose logs -f`
4. **Backup `.env`** file securely
5. **Update regularly** with `git pull && docker compose up -d --build`

## 🆘 Need Help?

1. Check [AWS_DOCKER_DEPLOYMENT.md](docs/AWS_DOCKER_DEPLOYMENT.md) troubleshooting section
2. Review container logs: `docker compose logs`
3. Verify all environment variables in `.env`
4. Test external services connectivity
5. Check AWS Security Group rules

---

**Happy Deploying! 🚀**

