#!/bin/bash

# HybridRAG AWS Deployment Script
# This script automates the deployment process on AWS EC2

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}   HybridRAG AWS Docker Deployment Script${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if running on Ubuntu/Debian
if [ ! -f /etc/debian_version ]; then
    print_error "This script is designed for Ubuntu/Debian systems"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed. Installing Docker..."
    
    # Update package index
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed successfully"
    print_warning "You may need to log out and back in for Docker group permissions to take effect"
else
    print_success "Docker is already installed"
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available"
    exit 1
else
    print_success "Docker Compose is available"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found"
    
    if [ -f env.template ]; then
        print_info "Copying env.template to .env"
        cp env.template .env
        print_warning "Please edit .env file with your actual credentials before continuing"
        print_info "Run: nano .env"
        exit 0
    else
        print_error "env.template file not found"
        exit 1
    fi
else
    print_success ".env file found"
fi

# Verify required files exist
print_info "Checking required files..."

REQUIRED_FILES=(
    "Dockerfile.backend"
    "Dockerfile.frontend"
    "docker-compose.yml"
    "nginx.conf"
    "app.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file not found: $file"
        exit 1
    fi
done
print_success "All required files present"

# Check if containers are already running
if docker compose ps | grep -q "Up"; then
    print_warning "Containers are already running"
    read -p "Do you want to rebuild and restart? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Stopping existing containers..."
        docker compose down
    else
        print_info "Exiting without changes"
        exit 0
    fi
fi

# Build Docker images
print_info "Building Docker images (this may take 5-10 minutes)..."
if docker compose build; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    exit 1
fi

# Start containers
print_info "Starting containers..."
if docker compose up -d; then
    print_success "Containers started successfully"
else
    print_error "Failed to start containers"
    exit 1
fi

# Wait for services to be healthy
print_info "Waiting for services to be healthy (30 seconds)..."
sleep 30

# Check container status
print_info "Checking container status..."
docker compose ps

# Test backend health
print_info "Testing backend health endpoint..."
if curl -f http://localhost:8010/health &> /dev/null; then
    print_success "Backend is healthy"
else
    print_error "Backend health check failed"
    print_info "Check logs with: docker compose logs backend"
fi

# Test frontend
print_info "Testing frontend..."
if curl -f http://localhost/ &> /dev/null; then
    print_success "Frontend is accessible"
else
    print_error "Frontend is not accessible"
    print_info "Check logs with: docker compose logs frontend"
fi

# Get public IP
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || echo "Unable to fetch")

echo ""
echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}   Deployment Complete!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""
echo -e "Frontend URL: ${GREEN}http://$PUBLIC_IP${NC}"
echo -e "Backend API:  ${GREEN}http://$PUBLIC_IP:8010${NC}"
echo -e "Health Check: ${GREEN}http://$PUBLIC_IP:8010/health${NC}"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs:           docker compose logs -f"
echo "  Stop application:    docker compose down"
echo "  Restart:             docker compose restart"
echo "  Check status:        docker compose ps"
echo ""
echo -e "${YELLOW}Security Reminders:${NC}"
echo "  1. Ensure AWS Security Group allows ports 80 and 8010"
echo "  2. Consider setting up SSL/HTTPS for production"
echo "  3. Regularly backup your .env file and data"
echo ""

