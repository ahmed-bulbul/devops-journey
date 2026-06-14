# Week 4 — Docker + Spring Boot Docker

Working directory: ~/workspace/aws-learn/phase1/week4/

---

## SECTION 1 — Docker Architecture

```
Docker Architecture:

  Your Terminal
      │
      ▼
  Docker CLI (client)  ──── REST API ────►  Docker Daemon (dockerd)
                                                    │
                                          ┌─────────┼─────────┐
                                          ▼         ▼         ▼
                                       Images  Containers  Networks/Volumes
                                          │
                                          ▼
                                    Registry (Docker Hub / ECR)
```

**Key concepts:**
```
Image      = blueprint (read-only, built from Dockerfile)
Container  = running instance of an image (writable layer on top)
Layer      = each Dockerfile instruction creates a cached layer
Registry   = remote storage for images (Docker Hub, AWS ECR)
Daemon     = background service that manages everything
Client     = the 'docker' CLI you type commands into
```

```bash
# Check Docker is running
docker version
docker info

# Docker info shows: containers running, images, storage driver, etc.
docker info | grep -E "Containers|Images|Server Version"
```

---

## SECTION 2 — Dockerfile Instructions

Study all 4 Dockerfiles in `dockerfiles/` folder.

### 2.1 Core Instructions
```dockerfile
FROM eclipse-temurin:17-jre          # base image
WORKDIR /app                         # set working directory (creates it)
COPY src/ ./src/                     # copy files from host to image
ADD file.tar.gz /app/                # like COPY but also extracts archives
RUN ./mvnw package -DskipTests       # execute command during BUILD
ENV APP_PORT=8080                    # set environment variable
EXPOSE 8080                          # document the port (doesn't actually open it)
VOLUME /app/logs                     # create a mount point
USER appuser                         # switch to non-root user
ARG BUILD_VERSION=latest             # build-time variable (not in final image)
LABEL maintainer="bulbul@devops"     # metadata
```

### 2.2 CMD vs ENTRYPOINT
```dockerfile
# CMD — default command, can be overridden at runtime
CMD ["java", "-jar", "app.jar"]
# docker run myimage → runs java -jar app.jar
# docker run myimage bash → overrides CMD, runs bash instead

# ENTRYPOINT — always runs, CMD becomes arguments
ENTRYPOINT ["java"]
CMD ["-jar", "app.jar"]
# docker run myimage → java -jar app.jar
# docker run myimage -version → java -version  (CMD overridden, ENTRYPOINT fixed)

# Shell form vs exec form
CMD java -jar app.jar          # shell form (runs via /bin/sh -c, PID 1 is sh)
CMD ["java", "-jar", "app.jar"]  # exec form (PID 1 is java — preferred for signals)
```

### 2.3 Build the basic image
```bash
# Build (from week4 folder)
docker build -t order-service:basic -f dockerfiles/Dockerfile.basic .

# Build multi-stage
docker build -t order-service:multistage -f dockerfiles/Dockerfile.multistage .

# Compare image sizes
docker images | grep order-service

# Build with build args
docker build --build-arg BUILD_VERSION=1.0.0 -t order-service:1.0.0 .

# Build with no cache
docker build --no-cache -t order-service:fresh .
```

**Challenge 1:** Build both `Dockerfile.basic` and `Dockerfile.multistage`. Compare sizes with `docker images`.

---

## SECTION 3 — Docker Commands

### 3.1 Images
```bash
# List images
docker images
docker images | grep order-service

# Pull an image
docker pull eclipse-temurin:17-jre
docker pull postgres:15-alpine

# Inspect image layers
docker history order-service:multistage
docker history --no-trunc order-service:multistage

# Inspect full image metadata
docker inspect order-service:multistage

# Remove image
docker rmi order-service:basic
docker rmi $(docker images -q -f dangling=true)   # remove untagged (dangling) images
```

### 3.2 Containers
```bash
# Run a container
docker run order-service:multistage

# Run in background (detached)
docker run -d order-service:multistage

# Run with port mapping (host:container)
docker run -d -p 8080:8080 order-service:multistage

# Run with name
docker run -d --name my-order-service -p 8080:8080 order-service:multistage

# Run with environment variables
docker run -d \
  -e SPRING_PROFILES_ACTIVE=docker \
  -e DB_PASSWORD=secret \
  -p 8080:8080 \
  order-service:multistage

# Run interactively (great for debugging)
docker run -it eclipse-temurin:17-jre bash
docker run -it --rm alpine sh           # --rm removes container after exit

# List running containers
docker ps
docker ps -a    # all including stopped

# Stop / start / restart
docker stop my-order-service
docker start my-order-service
docker restart my-order-service

# Remove container
docker rm my-order-service
docker rm -f my-order-service           # force remove even if running

# Remove all stopped containers
docker container prune
```

### 3.3 Logs, Exec, Stats, Inspect
```bash
# View logs
docker logs my-order-service
docker logs -f my-order-service          # follow (like tail -f)
docker logs --tail 50 my-order-service   # last 50 lines
docker logs --since 10m my-order-service # logs from last 10 minutes

# Execute command inside running container
docker exec my-order-service ls /app
docker exec -it my-order-service bash    # interactive shell inside container
docker exec my-order-service env         # see environment variables

# Resource usage (like htop for containers)
docker stats
docker stats my-order-service
docker stats --no-stream                  # one snapshot, not live

# Inspect container metadata
docker inspect my-order-service
docker inspect my-order-service | grep IPAddress
```

**Challenge 2:** Run a postgres:15-alpine container with a name, map port 5432, set POSTGRES_PASSWORD env var. Then exec into it and run `psql`.
```bash
docker run -d --name practice-postgres \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  postgres:15-alpine

docker exec -it practice-postgres psql -U postgres -d testdb
# Inside psql: \l (list DBs), \q (quit)
```

---

## SECTION 4 — Docker Networking

### 4.1 Network Types
```
bridge  — default network. Containers can talk to each other by name.
          Containers are isolated from host network.
          Use for: most applications.

host    — container shares host's network stack. No isolation.
          Use for: performance-sensitive apps (reduces NAT overhead).
          Not recommended for production.

overlay — for Docker Swarm / multi-host networking.
          Use for: distributed systems across multiple hosts.

none    — no networking at all.
          Use for: batch jobs that don't need network.
```

### 4.2 Bridge Network (most common)
```bash
# Create a custom network
docker network create my-backend

# List networks
docker network ls

# Run containers on same network (they can reach each other by container name)
docker run -d --name postgres --network my-backend \
  -e POSTGRES_PASSWORD=secret postgres:15-alpine

docker run -d --name app --network my-backend \
  -e DB_URL=jdbc:postgresql://postgres:5432/mydb \    # 'postgres' resolves by name
  order-service:multistage

# Inspect network
docker network inspect my-backend

# Remove network
docker network rm my-backend
```

### 4.3 Container-to-Container Communication
```bash
# From inside app container, ping postgres by name
docker exec app ping postgres

# Check if app can reach postgres port
docker exec app nc -zv postgres 5432
```

**Challenge 3:** Create a custom bridge network. Run postgres and redis on it. Then run a temp alpine container on the same network and verify both are reachable by name.
```bash
docker network create practice-net
docker run -d --name pg --network practice-net -e POSTGRES_PASSWORD=x postgres:15-alpine
docker run -d --name rd --network practice-net redis:7-alpine
docker run --rm --network practice-net alpine sh -c "ping -c 2 pg && ping -c 2 rd"
```

---

## SECTION 5 — Docker Volumes

### 5.1 Named Volumes vs Bind Mounts
```
Named Volume   — Docker manages the storage location
                 Best for: databases, persistent app data
                 docker run -v postgres_data:/var/lib/postgresql/data

Bind Mount     — maps a host path directly into container
                 Best for: development (hot reload, sharing configs)
                 docker run -v /home/bulbul/app:/app

tmpfs Mount    — stored in host memory, never written to disk
                 Best for: secrets, temp files
                 docker run --tmpfs /tmp
```

### 5.2 Volume Commands
```bash
# Create named volume
docker volume create postgres_data

# List volumes
docker volume ls

# Inspect volume (see where it's stored on host)
docker volume inspect postgres_data

# Use named volume
docker run -d \
  -v postgres_data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:15-alpine

# Use bind mount (host path:container path)
docker run -d \
  -v $(pwd)/config:/app/config:ro \     # :ro = read-only
  order-service:multistage

# Remove volume
docker volume rm postgres_data
docker volume prune    # remove all unused volumes
```

---

## SECTION 6 — Docker Hub: Push and Pull

### 6.1 Login and Tag
```bash
# Login to Docker Hub
docker login
# Enter your Docker Hub username and password

# Tag your image with your username
docker tag order-service:multistage YOUR_DOCKERHUB_USERNAME/order-service:1.0.0
docker tag order-service:multistage YOUR_DOCKERHUB_USERNAME/order-service:latest

# Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/order-service:1.0.0
docker push YOUR_DOCKERHUB_USERNAME/order-service:latest

# Pull from Docker Hub
docker pull YOUR_DOCKERHUB_USERNAME/order-service:1.0.0
```

### 6.2 Tagging Strategy
```bash
# Semantic versioning
myapp:1.2.3          # specific version (immutable — never overwrite)
myapp:1.2            # minor version (updated when patch releases)
myapp:1              # major version
myapp:latest         # latest (always the newest — use for dev only)

# Git commit SHA (best for CI/CD traceability)
myapp:abc1234        # exact commit that built this image
myapp:main-abc1234   # branch + commit

# Environment tags
myapp:staging
myapp:production
```

---

## SECTION 7 — Docker Compose

Study: `compose/docker-compose.yml` and `compose/docker-compose.override.yml`

### 7.1 Core Commands
```bash
cd compose/

# Start all services (builds if needed)
docker compose up

# Start in background
docker compose up -d

# Build images first, then start
docker compose up --build -d

# View logs
docker compose logs
docker compose logs -f app           # follow logs for app service only

# Status
docker compose ps

# Execute command in a service
docker compose exec app bash
docker compose exec postgres psql -U appuser -d orders

# Stop (keeps containers)
docker compose stop

# Stop and remove containers (keeps volumes)
docker compose down

# Stop and remove containers + volumes (DESTROYS DATA)
docker compose down -v

# Scale a service
docker compose up -d --scale app=3
```

### 7.2 Key Concepts from the Compose File
```yaml
depends_on:           # start order + health check dependency
  postgres:
    condition: service_healthy    # wait until healthcheck passes

healthcheck:          # Docker monitors this — restarts if fails
  test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 60s   # grace period before health checks start

env_file:             # load vars from a file
  - .env

networks:             # isolated network for services
  backend:
    driver: bridge
```

### 7.3 Environment Variables and Secrets
```bash
# Create .env file (never commit this)
cat > compose/.env << 'EOF'
DB_PASSWORD=supersecret
REDIS_PASSWORD=redispass
EOF

# Compose auto-loads .env from same directory
docker compose up -d

# Override for different environments
docker compose --env-file .env.production up -d
```

**Challenge 4:** Start the full compose stack. Verify all 3 services are healthy.
```bash
cd compose
echo "DB_PASSWORD=secret" > .env
docker compose up -d
docker compose ps
docker compose logs -f
# Wait for all to show "healthy"
curl http://localhost:8080/actuator/health
```

---

## SECTION 8 — Docker Security

```bash
# 1. Run as non-root (already in Dockerfile.multistage and Dockerfile.secure)
docker inspect my-container | grep User

# 2. Read-only filesystem
docker run --read-only \
  --tmpfs /tmp \                    # allow writes only to /tmp
  order-service:multistage

# 3. Limit resources
docker run -d \
  --memory="512m" \                 # max 512MB RAM
  --cpus="0.5" \                    # max 50% of one CPU
  order-service:multistage

# 4. Scan for vulnerabilities with Trivy
sudo apt install -y wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" \
    | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt update && sudo apt install -y trivy

# Scan an image
trivy image order-service:multistage
trivy image --severity HIGH,CRITICAL order-service:multistage

# 5. Don't run privileged containers
docker run --privileged ...    # NEVER in production — gives root on host

# 6. Drop capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE order-service:multistage
```

---

## REAL-WORLD CHALLENGES

### Challenge A — Image Size Optimization
Build all 4 Dockerfiles. Compare sizes. Explain why multistage is smaller.
```bash
docker images | grep -E "order-service|REPOSITORY"
docker history order-service:multistage
```

### Challenge B — Debug a Container
Run an order-service container. Exec into it. Check: running process, env vars, open ports, disk usage.
```bash
docker exec -it my-order-service sh
# Inside:
ps aux
env | grep SPRING
ss -tlnp
df -h
```

### Challenge C — Volume Persistence
Start postgres with a named volume. Insert data. Stop and remove the container. Start a NEW postgres container with the SAME volume. Verify data is still there.
```bash
docker run -d --name pg1 -v mydata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=x postgres:15-alpine
docker exec pg1 psql -U postgres -c "CREATE TABLE test (id int); INSERT INTO test VALUES (1);"
docker rm -f pg1
docker run -d --name pg2 -v mydata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=x postgres:15-alpine
docker exec pg2 psql -U postgres -c "SELECT * FROM test;"
```

### Challenge D — Push to Docker Hub
Build the multistage Dockerfile, tag it with your Docker Hub username, push it, then pull it on the same machine to verify.
```bash
docker build -t YOUR_USERNAME/order-service:week4 -f dockerfiles/Dockerfile.multistage .
docker push YOUR_USERNAME/order-service:week4
docker rmi YOUR_USERNAME/order-service:week4
docker pull YOUR_USERNAME/order-service:week4
```

---

## QUICK REFERENCE CARD

| Command | What it does |
|---------|-------------|
| `docker build -t name:tag .` | Build image from Dockerfile |
| `docker build -f Dockerfile.x` | Use specific Dockerfile |
| `docker images` | List images |
| `docker run -d -p 8080:8080 img` | Run container detached |
| `docker run -it img bash` | Run interactive shell |
| `docker ps` | List running containers |
| `docker ps -a` | All containers |
| `docker logs -f name` | Follow container logs |
| `docker exec -it name bash` | Shell into container |
| `docker stats` | Live resource usage |
| `docker inspect name` | Full metadata |
| `docker stop/rm name` | Stop/remove container |
| `docker volume create name` | Create named volume |
| `docker network create name` | Create network |
| `docker compose up -d` | Start compose stack |
| `docker compose down -v` | Stop + remove volumes |
| `docker compose exec svc cmd` | Run in service |
| `trivy image name` | Scan for CVEs |

---

## DONE? Checklist

- [ ] I understand Docker architecture (daemon, client, image, container, layer)
- [ ] I can write a Dockerfile using FROM, COPY, RUN, ENV, EXPOSE, CMD, ENTRYPOINT
- [ ] I built a multi-stage Dockerfile and can explain why it's smaller
- [ ] I understand layered JARs and how they improve CI/CD cache efficiency
- [ ] I can use docker run, exec, logs, inspect, stats, rm, rmi
- [ ] I know the difference between bridge, host, and overlay networks
- [ ] I created a custom network and ran containers that communicate by name
- [ ] I know the difference between named volumes and bind mounts
- [ ] I pushed an image to Docker Hub with proper tagging
- [ ] I ran the full compose stack (app + postgres + redis) and verified health
- [ ] I understand docker compose depends_on with health checks
- [ ] I ran a container with non-root user, resource limits, and read-only filesystem
- [ ] I scanned an image with Trivy

Next: Week 5 — Docker Compose Full Stack
