# 📝 AWS Deployment Commands Cheat Sheet

**Quick reference for your AWS Ubuntu terminal**

---

## 🚀 INITIAL DEPLOYMENT

```bash
# Clone repository
git clone https://github.com/kanthkaushikkrishna11/hybridrag.git
cd hybridrag

# Configure environment
cp env.template .env
nano .env  # Edit with your credentials

# Deploy automatically
chmod +x deploy-aws.sh
./deploy-aws.sh
```

---

## 🔧 DOCKER COMMANDS

### Container Management
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend
```

### View Status
```bash
# Check container status
docker compose ps

# Resource usage (real-time)
docker stats

# Check container health
docker ps
```

### View Logs
```bash
# All logs (follow mode)
docker compose logs -f

# Backend only
docker compose logs backend -f

# Frontend only
docker compose logs frontend -f

# Last 100 lines
docker compose logs --tail=100

# Specific time range
docker compose logs --since 30m
```

### Build and Update
```bash
# Rebuild all images
docker compose build

# Rebuild without cache
docker compose build --no-cache

# Rebuild specific service
docker compose build backend

# Pull latest code and redeploy
git pull origin main
docker compose down
docker compose build
docker compose up -d
```

### Shell Access
```bash
# Enter backend container
docker compose exec backend bash

# Enter frontend container
docker compose exec frontend sh

# Run command in backend
docker compose exec backend python -c "print('Hello')"
```

---

## 🔍 DEBUGGING

### Check Backend Health
```bash
curl http://localhost:8010/health
curl http://YOUR_PUBLIC_IP:8010/health
```

### Check Frontend
```bash
curl http://localhost/
curl http://YOUR_PUBLIC_IP/
```

### Test Database Connection
```bash
docker compose exec backend python -c "
from src.backend.config import config
print(config.database_url)
"
```

### Check Environment Variables
```bash
# View all env vars in backend
docker compose exec backend printenv

# Specific variables
docker compose exec backend printenv | grep DATABASE
docker compose exec backend printenv | grep PINECONE
docker compose exec backend printenv | grep GEMINI
```

### Port Checks
```bash
# Check what's using ports
sudo netstat -tlnp | grep 80
sudo netstat -tlnp | grep 8010

# Kill process on port
sudo kill -9 <PID>

# Check all listening ports
sudo netstat -tlnp
```

---

## 🧹 CLEANUP

### Remove Stopped Containers
```bash
docker container prune -f
```

### Remove Unused Images
```bash
docker image prune -f

# Remove all unused images
docker image prune -a -f
```

### Remove Unused Volumes
```bash
docker volume prune -f
```

### Full Cleanup (CAUTION!)
```bash
# Remove everything unused
docker system prune -a -f

# Remove everything including volumes
docker system prune -a -f --volumes
```

### Check Disk Usage
```bash
# Docker disk usage
docker system df

# System disk usage
df -h
```

---

## 📊 MONITORING

### Watch Logs Live
```bash
# Watch all logs
watch -n 2 'docker compose logs --tail=20'

# Watch resource usage
watch -n 2 'docker stats --no-stream'
```

### Container Inspection
```bash
# Detailed container info
docker inspect hybridrag-backend
docker inspect hybridrag-frontend

# Get container IP
docker inspect hybridrag-backend | grep IPAddress
```

### Check Networks
```bash
# List networks
docker network ls

# Inspect hybridrag network
docker network inspect hybridrag_hybridrag-network
```

---

## 🔄 UPDATE & MAINTENANCE

### Update Application
```bash
cd ~/hybridrag
git pull origin main
docker compose down
docker compose build
docker compose up -d
docker compose logs -f
```

### Backup Logs
```bash
mkdir -p ~/backups
sudo cp -r ~/hybridrag/logs ~/backups/logs-$(date +%Y%m%d-%H%M%S)
```

### Backup Environment
```bash
cp ~/hybridrag/.env ~/backups/.env-$(date +%Y%m%d)
```

---

## 🆘 TROUBLESHOOTING

### Container Won't Start
```bash
# Check logs
docker compose logs backend
docker compose logs frontend

# Try clean restart
docker compose down
docker compose up -d
docker compose logs -f
```

### Port Already in Use
```bash
# Find and kill process
sudo netstat -tlnp | grep -E '80|8010'
sudo kill -9 <PID>

# Restart containers
docker compose restart
```

### Out of Memory
```bash
# Check memory usage
free -h
docker stats --no-stream

# Restart with memory cleanup
docker compose down
docker system prune -f
docker compose up -d
```

### Frontend Can't Connect to Backend
```bash
# Check VITE_API_URL
grep VITE_API_URL .env

# Rebuild frontend
docker compose build frontend --no-cache
docker compose up -d frontend
```

### Reset Everything
```bash
# Nuclear option - complete reset
docker compose down -v
docker system prune -a -f
rm -rf logs/*
docker compose build --no-cache
docker compose up -d
```

---

## 🔐 SECURITY

### Update Ubuntu
```bash
sudo apt update
sudo apt upgrade -y
```

### Check Security Group
```bash
# From AWS Console or CLI
aws ec2 describe-security-groups --group-ids <sg-id>
```

### View Active Connections
```bash
sudo netstat -an | grep :80
sudo netstat -an | grep :8010
```

---

## 📈 PERFORMANCE

### Check CPU/Memory
```bash
# System resources
top
htop  # If installed

# Docker resources
docker stats
```

### Optimize Images
```bash
# Remove unused images
docker image prune -a -f

# Check image sizes
docker images
```

---

## 🎯 QUICK TESTS

### Full Health Check
```bash
# Backend
curl -f http://localhost:8010/health && echo "✅ Backend OK" || echo "❌ Backend Failed"

# Frontend
curl -f http://localhost/ && echo "✅ Frontend OK" || echo "❌ Frontend Failed"

# Container status
docker compose ps | grep Up && echo "✅ Containers Running" || echo "❌ Containers Down"
```

### Upload Test
```bash
# From local machine (replace with your IP and PDF)
curl -X POST -F "file=@test.pdf" http://YOUR_AWS_IP:8010/uploadpdf
```

---

## 📱 ACCESS URLS

```bash
# Get your public IP
curl http://checkip.amazonaws.com

# Your URLs will be:
# Frontend:    http://YOUR_PUBLIC_IP
# Backend:     http://YOUR_PUBLIC_IP:8010
# Health:      http://YOUR_PUBLIC_IP:8010/health
```

---

## 💡 USEFUL ALIASES

Add to `~/.bashrc` for shortcuts:

```bash
# Add these to ~/.bashrc
echo "
# Docker shortcuts
alias dps='docker compose ps'
alias dlogs='docker compose logs -f'
alias dup='docker compose up -d'
alias ddown='docker compose down'
alias drestart='docker compose restart'
alias dstats='docker stats'
alias dclean='docker system prune -f'
" >> ~/.bashrc

# Apply changes
source ~/.bashrc
```

---

## 📞 GETTING HELP

If issues persist:

1. Check logs: `docker compose logs -f`
2. Review documentation: `docs/AWS_DOCKER_DEPLOYMENT.md`
3. Check container status: `docker compose ps`
4. Verify environment variables: `docker compose exec backend printenv`
5. Test external services (Supabase, Pinecone, Gemini)

---

**Save this file for quick reference!**

Print it: `cat AWS_COMMANDS_CHEATSHEET.md | less`

