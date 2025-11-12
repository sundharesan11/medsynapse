# Docker Deployment Guide

Complete guide for running MedSynapse in Docker containers.

---

## Quick Start

### Prerequisites

- Docker Desktop (Mac/Windows) or Docker Engine (Linux)
- Docker Compose v2.0+
- At least 4GB RAM available
- 2GB free disk space

### 3-Step Setup

**Step 1: Clone and Configure**

```bash
cd /path/to/medsynapse

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required: GROQ_API_KEY
# Optional: LANGSMITH_API_KEY (for tracing)
```

**Step 2: Start Services**

```bash
# Start all services in detached mode
docker-compose up -d

# Or start with logs visible
docker-compose up
```

**Step 3: Access Application**

```bash
# Wait 30-60 seconds for all services to start
# Then open in browser:
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## Services Overview

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 5173 | React app with Vite dev server |
| **Backend** | 8000 | FastAPI application |
| **Qdrant** | 6333 | Vector database REST API + Dashboard |
| **Qdrant gRPC** | 6334 | gRPC interface (optional) |

### Service Dependencies

```
Frontend → Backend → Qdrant
```

- Frontend depends on Backend
- Backend depends on Qdrant
- Services start in correct order automatically

---

## Docker Compose Commands

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Start with build (after code changes)
docker-compose up -d --build

# View startup logs
docker-compose up
```

### Stopping Services

```bash
# Stop all services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (deletes data!)
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f qdrant

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Restarting Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend
```

---

## Development Workflow

### Hot Reload Features

Both frontend and backend support hot-reload for rapid development:

**Backend (FastAPI + Uvicorn):**
- Edit Python files in `backend/`
- Server automatically reloads
- API immediately reflects changes
- No manual restart needed

**Frontend (React + Vite):**
- Edit files in `frontend/src/`
- Browser auto-refreshes
- Changes appear instantly
- Preserves React state when possible

### Making Changes

**1. Edit Code Locally**

Just edit files in your local `backend/` or `frontend/` directories. Changes are immediately synced to containers via volume mounts.

**2. Changes Reflect Automatically**

- Backend: Uvicorn detects changes and reloads
- Frontend: Vite hot-reloads the browser
- No manual rebuild needed

**3. When to Rebuild**

Rebuild only when dependencies change:

```bash
# Backend dependencies changed (requirements.txt)
docker-compose up -d --build backend

# Frontend dependencies changed (package.json)
docker-compose up -d --build frontend
```

---

## Container Management

### Accessing Container Shell

```bash
# Backend (Python/bash)
docker exec -it medsynapse-backend bash

# Frontend (Node/sh)
docker exec -it medsynapse-frontend sh

# Qdrant (Alpine/sh)
docker exec -it medsynapse-qdrant sh
```

### Running Commands Inside Containers

```bash
# Run backend tests
docker exec -it medsynapse-backend python tests/test_graph.py

# Install new Python package
docker exec -it medsynapse-backend pip install package-name

# Install new npm package
docker exec -it medsynapse-frontend npm install package-name
```

### Viewing Container Stats

```bash
# Resource usage
docker stats

# Specific container
docker stats medsynapse-backend

# Container details
docker inspect medsynapse-backend
```

---

## Persistent Data

### Qdrant Storage

Vector database data is persisted in `./qdrant_storage/`:

```bash
# Check storage size
du -sh qdrant_storage/

# Backup data
tar -czf qdrant_backup_$(date +%Y%m%d).tar.gz qdrant_storage/

# Restore from backup
tar -xzf qdrant_backup_20241112.tar.gz
```

### Logs Directory

Backend logs (when configured) are in `backend/logs/`:

```bash
# View JSON logs
cat backend/logs/medsynapse.log | jq '.'

# Monitor logs in real-time
tail -f backend/logs/medsynapse.log | jq '.'
```

---

## Networking

### Internal Communication

Services communicate via Docker network `medsynapse-network`:

- Frontend → Backend: `http://backend:8000`
- Backend → Qdrant: `http://qdrant:6333`

### External Access

From host machine:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Qdrant: `http://localhost:6333`

### CORS Configuration

Backend allows requests from:
- `http://localhost:5173` (frontend dev server)
- `http://localhost:3000` (alternative frontend port)

Update in `backend/main.py` if needed.

---

## Environment Variables

### Loading from .env

Docker Compose automatically loads variables from `.env`:

```env
GROQ_API_KEY=gsk_your_key_here
LANGSMITH_API_KEY=ls__your_key_here
QDRANT_URL=http://qdrant:6333
```

### Service-Specific Variables

**Backend:**
```env
QDRANT_URL=http://qdrant:6333  # Use service name
GROQ_API_KEY=${GROQ_API_KEY}   # From .env
PYTHONUNBUFFERED=1             # Immediate output
```

**Frontend:**
```env
VITE_API_URL=http://localhost:8000  # External URL
NODE_ENV=development
```

### Overriding Variables

```bash
# Override for single run
GROQ_API_KEY=new_key docker-compose up -d

# Override in docker-compose.yml
services:
  backend:
    environment:
      - GROQ_API_KEY=hardcoded_key  # Not recommended!
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill the process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Map to different host port
```

#### 2. Backend Can't Connect to Qdrant

**Error:** `ConnectionError: Cannot connect to Qdrant at http://qdrant:6333`

**Solution:**
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Check Qdrant health
docker exec medsynapse-qdrant curl -f http://localhost:6333/

# Restart Qdrant
docker-compose restart qdrant

# Check network
docker network inspect medsynapse-network
```

#### 3. Frontend Can't Reach Backend

**Error:** `Network error` or `Failed to fetch` in browser console

**Solution:**
```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check CORS settings in backend/main.py
# 3. Verify VITE_API_URL in frontend/.env
# 4. Check browser console for specific error

# 5. Restart frontend
docker-compose restart frontend
```

#### 4. Hot Reload Not Working

**Backend:**
```bash
# Check if volume is mounted
docker inspect medsynapse-backend | grep -A 10 Mounts

# Check Uvicorn logs
docker-compose logs -f backend | grep -i reload

# Restart with rebuild
docker-compose up -d --build backend
```

**Frontend:**
```bash
# Check Vite logs
docker-compose logs -f frontend

# Clear browser cache
# Restart frontend
docker-compose restart frontend
```

#### 5. Permission Denied Errors

**Error:** `Permission denied` when accessing volumes

**Solution (Linux):**
```bash
# Fix ownership
sudo chown -R $USER:$USER qdrant_storage/
sudo chown -R $USER:$USER backend/
sudo chown -R $USER:$USER frontend/
```

#### 6. Out of Memory

**Error:** Container killed or service crashes

**Solution:**
```bash
# Check Docker resource limits
docker info | grep -i memory

# Increase in Docker Desktop:
# Settings → Resources → Memory → Set to 4GB+

# Check container memory usage
docker stats
```

---

## Advanced Configuration

### Custom Docker Compose

Create `docker-compose.override.yml` for local customizations:

```yaml
services:
  backend:
    environment:
      - LOG_LEVEL=DEBUG
    ports:
      - "8001:8000"  # Custom port

  frontend:
    ports:
      - "3000:5173"  # Custom port
```

This file is automatically merged with `docker-compose.yml` and git-ignored.

### Production Deployment

For production, create separate Dockerfiles:

**backend/Dockerfile.prod:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**frontend/Dockerfile.prod:**
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Health Checks

### Built-in Health Checks

All services have health checks configured:

```bash
# Check service health
docker-compose ps

# Should show (healthy) status
```

### Manual Health Checks

**Backend:**
```bash
curl http://localhost:8000/health
# {"status": "healthy", "cache_stats": {...}}
```

**Qdrant:**
```bash
curl http://localhost:6333/
# {"title": "qdrant - vector search engine", ...}
```

**Frontend:**
```bash
curl -I http://localhost:5173
# HTTP/1.1 200 OK
```

---

## Performance Tuning

### Resource Limits

Add resource limits in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Multi-stage Builds

Reduce image size with multi-stage builds (production):

```dockerfile
# Build stage
FROM python:3.11 AS builder
RUN pip install --user package

# Runtime stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```

---

## Cleanup

### Remove Containers

```bash
# Stop and remove all containers
docker-compose down

# Also remove volumes (DELETES DATA!)
docker-compose down -v

# Also remove images
docker-compose down --rmi all
```

### Remove Unused Resources

```bash
# Remove dangling images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a
```

### Free Disk Space

```bash
# Check disk usage
docker system df

# Clean build cache
docker builder prune
```

---

## Next Steps

- **Modify code** and see hot-reload in action
- **Run tests** inside containers
- **Monitor logs** during development
- **Deploy to production** with optimized Dockerfiles

For Phase 4 features, see [PHASE4_GUIDE.md](PHASE4_GUIDE.md).

---

## Support

**Issues?**
1. Check this guide's troubleshooting section
2. View logs: `docker-compose logs -f`
3. Inspect containers: `docker inspect container_name`
4. Check GitHub issues

**Clean slate:**
```bash
docker-compose down -v
docker-compose up -d --build
```
