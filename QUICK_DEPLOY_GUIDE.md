# ⚡ Quick Deploy Guide - AWS EC2 with Docker

**Deploy HybridRAG to AWS in under 15 minutes!**

## 📋 What You Need

- ✅ AWS EC2 instance (Ubuntu) with public IP
- ✅ SSH access to your instance
- ✅ Supabase database credentials
- ✅ Pinecone API key
- ✅ Google Gemini API key

## 🚀 Deployment Steps

### 1️⃣ Connect to Your AWS Instance

```bash
ssh -i your-key.pem ubuntu@YOUR_AWS_PUBLIC_IP
```

### 2️⃣ Install Docker (First Time Only)

```bash
# Update system
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

### 3️⃣ Clone Repository

```bash
cd ~
git clone https://github.com/kanthkaushikkrishna11/hybridrag.git
cd hybridrag
```

### 4️⃣ Configure Environment

```bash
# Copy template
cp env.template .env

# Edit configuration
nano .env
```

**Fill in these values:**

```bash
# Supabase Database
DATABASE_USER=postgres.your_ref
DATABASE_PASSWORD=your_password
DATABASE_HOST=db.your_ref.supabase.co
DATABASE_PORT=5432
DATABASE_NAME=postgres

# Pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=pdf-assistant-index
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1

# Google Gemini
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXX

# Frontend (IMPORTANT: Use your EC2 public IP)
VITE_API_URL=http://YOUR_AWS_PUBLIC_IP:8010
```

**Save:** `Ctrl+X`, then `Y`, then `Enter`

### 5️⃣ Run Deployment Script

```bash
chmod +x deploy-aws.sh
./deploy-aws.sh
```

**OR manually:**

```bash
docker compose build
docker compose up -d
```

### 6️⃣ Verify Deployment

```bash
# Check containers
docker compose ps

# Check logs
docker compose logs -f

# Test backend
curl http://localhost:8010/health

# Test frontend
curl http://localhost/
```

### 7️⃣ Configure AWS Security Group

**Required Inbound Rules:**

| Type | Port | Source | Description |
|------|------|--------|-------------|
| SSH | 22 | Your IP | SSH access |
| HTTP | 80 | 0.0.0.0/0 | Frontend |
| Custom TCP | 8010 | 0.0.0.0/0 | Backend API |

### 8️⃣ Access Your App

🎉 **Your app is live at:**

- **Frontend:** `http://YOUR_AWS_PUBLIC_IP`
- **Backend:** `http://YOUR_AWS_PUBLIC_IP:8010`
- **Health:** `http://YOUR_AWS_PUBLIC_IP:8010/health`

## 🔧 Useful Commands

```bash
# View logs (real-time)
docker compose logs -f

# View specific service logs
docker compose logs backend -f
docker compose logs frontend -f

# Restart services
docker compose restart

# Stop services
docker compose down

# Check status
docker compose ps

# View resource usage
docker stats

# Update and redeploy
git pull origin main
docker compose down
docker compose build
docker compose up -d
```

## 🐛 Troubleshooting

### Backend Not Starting

```bash
# Check logs
docker compose logs backend

# Check environment variables
docker compose exec backend printenv | grep -E 'DATABASE|PINECONE|GEMINI'

# Test database connection
docker compose exec backend python -c "from src.backend.config import config; print(config.database_url)"
```

### Frontend Can't Connect to Backend

```bash
# Verify VITE_API_URL
grep VITE_API_URL .env

# Rebuild frontend with correct URL
docker compose down
docker compose build frontend --no-cache
docker compose up -d
```

### Port Already in Use

```bash
# Find process using port
sudo netstat -tlnp | grep -E '80|8010'

# Kill process
sudo kill -9 <PID>
```

### Container Health Check Failing

```bash
# Wait 30 seconds for startup
sleep 30

# Check again
docker compose ps

# View detailed logs
docker compose logs --tail=100
```

## 🔄 Updating Your App

```bash
cd ~/hybridrag
git pull origin main
docker compose down
docker compose build
docker compose up -d
docker compose logs -f
```

## 📊 Monitoring

```bash
# Container status
docker compose ps

# Resource usage
docker stats

# Disk usage
docker system df

# Network status
docker network ls
```

## 🆘 Quick Fixes

### Containers Won't Start
```bash
docker compose down
docker system prune -a -f
docker compose build --no-cache
docker compose up -d
```

### Out of Disk Space
```bash
docker system prune -a -f
docker volume prune -f
```

### Reset Everything
```bash
docker compose down -v
docker system prune -a -f
# Then rebuild and restart
docker compose build
docker compose up -d
```

## ✅ Deployment Checklist

- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] `.env` file configured with all credentials
- [ ] AWS Security Group allows ports 80, 8010, and 22
- [ ] Containers running: `docker compose ps`
- [ ] Backend health check passes: `curl http://localhost:8010/health`
- [ ] Frontend accessible: `curl http://localhost/`
- [ ] External access works from browser
- [ ] Can upload PDF and get responses

## 📚 Full Documentation

For detailed information:
- **Complete Guide:** [docs/AWS_DOCKER_DEPLOYMENT.md](docs/AWS_DOCKER_DEPLOYMENT.md)
- **Deployment Options:** [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Docker Files Info:** [DOCKER_DEPLOYMENT_README.md](DOCKER_DEPLOYMENT_README.md)

## 💡 Pro Tips

1. **Use Elastic IP** to avoid IP changes on restart
2. **Enable HTTPS** with Let's Encrypt for production
3. **Monitor logs** regularly: `docker compose logs -f`
4. **Backup `.env`** securely (never commit to git!)
5. **Set up CloudWatch** for production monitoring
6. **Use t2.medium** or larger for better performance
7. **Enable auto-updates** for security patches

## 🎯 Performance Tuning

### For t2.small (1 vCPU, 2GB RAM)
```yaml
# In docker-compose.yml
backend:
  mem_limit: 1g
```

### For t2.medium (2 vCPU, 4GB RAM)
```dockerfile
# In Dockerfile.backend
--workers 4  # Already configured
```

### For t2.large or bigger
```dockerfile
# In Dockerfile.backend
--workers 8  # Edit the Dockerfile
```

---

**🎉 You're All Set!**

Your HybridRAG application is now live and accessible worldwide!

For issues, check [docs/AWS_DOCKER_DEPLOYMENT.md](docs/AWS_DOCKER_DEPLOYMENT.md) troubleshooting section.

