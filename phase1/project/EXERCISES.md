# Phase 1 Project — Containerised Spring Boot Microservices

## What You'll Build

3 Spring Boot microservices wired together with Docker Compose:

```
nginx (port 80)
  ├── /users/*    → user-service:8081    (MySQL users_db + Redis)
  ├── /orders/*   → order-service:8082   (MySQL orders_db + Redis + calls user/product)
  └── /products/* → product-service:8083 (MySQL products_db + Redis)
          │
    [MySQL:3306]  [Redis:6379]
```

---

## STEP 1 — Create Your Spring Boot Services

You need 3 real Spring Boot projects. Create each using Spring Initializr.

```bash
# Option A: Spring Initializr CLI
curl https://start.spring.io/starter.zip \
  -d dependencies=web,data-jpa,actuator,mysql,data-redis,lombok \
  -d type=maven-project \
  -d language=java \
  -d bootVersion=3.2.5 \
  -d baseDir=user-service \
  -d groupId=com.bulbul \
  -d artifactId=user-service \
  -d name=user-service \
  -o user-service.zip
unzip user-service.zip
rm user-service.zip

# Repeat for order-service and product-service (change artifactId and baseDir)
```

**User Service minimum endpoints:**
```java
GET  /users              → list all users
GET  /users/{id}         → get user by ID
POST /users              → create user
GET  /actuator/health    → health check (required for compose healthcheck)
```

**Order Service minimum endpoints:**
```java
GET  /orders             → list all orders
POST /orders             → create order (validates user via user-service)
GET  /actuator/health
```

**Product Service minimum endpoints:**
```java
GET  /products           → list all products (cached in Redis)
GET  /products/{id}      → get product
POST /products           → create product
GET  /actuator/health
```

---

## STEP 2 — Configure application.yml

Replace `src/main/resources/application.yml` in each service with the one provided in this folder.

The provided configs use environment variables so the same JAR works locally AND in Docker:
```yaml
spring:
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:mysql://localhost:3306/users_db}
    # Default (local dev) ↑        Docker override ↑ (set via compose env)
```

---

## STEP 3 — Write Dockerfiles

Dockerfiles are already prepared in each service folder.

Key things to verify:
```bash
# Each Dockerfile uses multi-stage build
grep "AS builder" user-service/Dockerfile    # should match
grep "AS runtime" user-service/Dockerfile    # should match

# Non-root user
grep "USER appuser" user-service/Dockerfile  # should match

# Health check
grep "HEALTHCHECK" user-service/Dockerfile   # should match
```

---

## STEP 4 — Build and Test Each Service Individually

```bash
# Build user-service image
docker build -t user-service:latest ./user-service/

# Test it standalone (connects to local MySQL if running)
docker run -d --name test-user \
  -e SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/users_db \
  -e SPRING_DATASOURCE_USERNAME=root \
  -e SPRING_DATASOURCE_PASSWORD=password \
  -p 8081:8081 \
  user-service:latest

docker logs -f test-user
curl http://localhost:8081/actuator/health

docker rm -f test-user

# Repeat for order-service and product-service
```

---

## STEP 5 — Start the Full Stack

```bash
cd phase1/project/

# Set up secrets
cp secrets.env.example secrets.env
nano secrets.env    # set strong passwords

# Build all images and start
docker compose up -d --build

# Watch startup progress
watch 'docker compose ps'

# Follow logs
docker compose logs -f
```

---

## STEP 6 — Verify the Full Stack

```bash
# Infrastructure
docker compose ps                           # all 6 services healthy
docker network ls | grep project            # frontend + backend networks
docker volume ls | grep project             # mysql_data + redis_data

# nginx routing
curl http://localhost/health                # nginx
curl http://localhost/users/actuator/health
curl http://localhost/orders/actuator/health
curl http://localhost/products/actuator/health

# Create and read data
curl -X POST http://localhost/users \
     -H "Content-Type: application/json" \
     -d '{"name":"Bulbul","email":"bulbul@test.com"}'

curl http://localhost/users

curl -X POST http://localhost/products \
     -H "Content-Type: application/json" \
     -d '{"name":"Laptop","price":999.99}'

curl http://localhost/products

# Verify databases
docker compose exec mysql mysql -u appuser -p${DB_PASSWORD} \
    -e "SHOW DATABASES; USE users_db; SHOW TABLES;"

# Verify Redis
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} keys "*"
```

---

## STEP 7 — Push Images to Docker Hub

```bash
# Login
docker login

# Tag images with your Docker Hub username
export DOCKERHUB_USERNAME=your_username

docker tag user-service:latest    $DOCKERHUB_USERNAME/user-service:1.0.0
docker tag order-service:latest   $DOCKERHUB_USERNAME/order-service:1.0.0
docker tag product-service:latest $DOCKERHUB_USERNAME/product-service:1.0.0

# Push
docker push $DOCKERHUB_USERNAME/user-service:1.0.0
docker push $DOCKERHUB_USERNAME/order-service:1.0.0
docker push $DOCKERHUB_USERNAME/product-service:1.0.0

# Also tag as latest
docker tag user-service:latest $DOCKERHUB_USERNAME/user-service:latest
docker push $DOCKERHUB_USERNAME/user-service:latest
```

---

## STEP 8 — Test Image Pull (verify Docker Hub works)

```bash
# Remove local images
docker rmi user-service:latest $DOCKERHUB_USERNAME/user-service:1.0.0

# Pull from Docker Hub
docker pull $DOCKERHUB_USERNAME/user-service:1.0.0

# Run from pulled image
docker run -d -p 8081:8081 \
  -e SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/users_db \
  -e SPRING_DATASOURCE_USERNAME=root \
  -e SPRING_DATASOURCE_PASSWORD=password \
  $DOCKERHUB_USERNAME/user-service:1.0.0

curl http://localhost:8081/actuator/health
docker rm -f $(docker ps -q --filter ancestor=$DOCKERHUB_USERNAME/user-service:1.0.0)
```

---

## PROJECT CHECKLIST

- [ ] Created 3 Spring Boot services (User, Order, Product) with proper REST endpoints
- [ ] Each service has `GET /actuator/health` working
- [ ] Wrote optimised multi-stage Dockerfiles (builder + runtime stages) for all 3 services
- [ ] All Dockerfiles use non-root user
- [ ] All Dockerfiles have HEALTHCHECK instruction
- [ ] docker compose up -d --build starts all 6 services
- [ ] All 6 services show "healthy" in docker compose ps
- [ ] nginx routes /users/, /orders/, /products/ correctly
- [ ] Can create and read data via each service through nginx
- [ ] MySQL has 3 separate databases
- [ ] Redis caching is configured for product-service
- [ ] Secrets are in secrets.env (not hardcoded in compose file)
- [ ] Resource limits (memory, cpus) are set for all services
- [ ] All 3 images pushed to Docker Hub
- [ ] Pulled image from Docker Hub and verified it runs

## PHASE 1 COMPLETE!

You now have:
- Advanced Git workflow skills (branching, rebase, hooks, GPG)
- Docker expertise (multi-stage builds, networking, volumes, security)
- Docker Compose for full-stack local development
- 3 containerised Spring Boot microservices on Docker Hub

Next: Phase 2 — CI/CD Pipelines (Week 6: GitHub Actions)
