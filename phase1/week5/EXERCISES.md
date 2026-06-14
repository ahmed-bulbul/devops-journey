# Week 5 — Docker Compose Full Stack

Working directory: ~/workspace/aws-learn/phase1/week5/

This week you wire everything together: 3 Spring Boot services + MySQL + Redis + nginx.
By the end you'll have a production-like local environment running with one command.

---

## SECTION 1 — Multi-Service Compose Stack

Study: `compose/docker-compose.yml`

### 1.1 Stack Overview
```
Internet
    │
  port 80
    ▼
 [nginx]  ─────────────────────────────────── frontend network
    │           │                 │
    ▼           ▼                 ▼
[user-svc:8081] [order-svc:8082] [product-svc:8083]
    │           │                 │
    └───────────┴─────────────────┘
                │                          backend network (internal)
          ┌─────┴──────┐
          ▼            ▼
       [MySQL]      [Redis]
```

**Key design decisions in this compose file:**
- Two networks: `frontend` (nginx + services) and `backend` (services + DB/Redis)
- `backend` is `internal: true` — DB/Redis cannot be reached from outside Docker
- `depends_on` with `condition: service_healthy` — services only start after DB is ready
- Resource limits on every service (`memory`, `cpus`)
- Logging driver with rotation (`json-file`, max-size)

### 1.2 Start the Stack
```bash
cd compose/

# Create secrets file
cp ../secrets/app.env.example ../secrets/app.env
nano ../secrets/app.env    # set real passwords

# Build service images (if not built yet)
docker compose build

# Start everything
docker compose up -d

# Watch startup
docker compose ps
docker compose logs -f

# Wait for all services to be "healthy"
watch docker compose ps
```

### 1.3 Verify Everything Works
```bash
# nginx health
curl http://localhost/health

# Each service via nginx
curl http://localhost/users/actuator/health
curl http://localhost/orders/actuator/health
curl http://localhost/products/actuator/health

# Check MySQL has all 3 databases
docker compose exec mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} \
    -e "SHOW DATABASES;"

# Check Redis is responding
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} ping
```

**Challenge 1:** Start the full stack and verify all 6 services are healthy using `docker compose ps`.

---

## SECTION 2 — Override Files

### 2.1 How Override Files Work
```bash
# Docker Compose merges files in order:
docker compose up                                           # uses docker-compose.yml + docker-compose.override.yml (auto)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up   # explicit

# Merge strategy:
# - Single values: override file WINS
# - Lists (ports, volumes, env): MERGED (both apply)
# - Map (environment): MERGED (override adds/replaces keys)
```

### 2.2 Using Override for Local Dev
```bash
# docker-compose.override.yml is auto-loaded — adds debug ports, adminer
docker compose up -d

# Access adminer (DB GUI) at:
# http://localhost:8888
# Server: mysql, Username: appuser, Password: from .env, Database: users_db

# Connect IntelliJ remote debugger to user-service
# Host: localhost, Port: 5001
```

### 2.3 Production Mode (no override)
```bash
# Explicitly choose files — skips override.yml, uses prod.yml instead
docker compose -f compose/docker-compose.yml -f compose/docker-compose.prod.yml up -d

# Difference: no debug ports, syslog logging, pulls from registry (not local build)
```

**Challenge 2:** Run the stack in "production mode" using the prod compose file. Verify debug ports are NOT exposed.
```bash
docker compose -f compose/docker-compose.yml -f compose/docker-compose.prod.yml up -d
docker compose ps
# Confirm 5001, 5002, 5003 are NOT in the ports column
```

---

## SECTION 3 — Secrets Management in Compose

### 3.1 File-Based Secrets (what we use)
```bash
# .env file approach (simple, good for local dev)
# docker-compose.yml references: env_file: - ../secrets/app.env

cat secrets/app.env.example
# Copy and fill in
cp secrets/app.env.example secrets/app.env

# Verify env vars are loaded in a service
docker compose exec user-service env | grep DB_PASSWORD
```

### 3.2 Docker Secrets (Swarm mode — reference)
```yaml
# In docker-compose.yml (Swarm only):
services:
  app:
    secrets:
      - db_password
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password   # app reads from file, not env

secrets:
  db_password:
    file: ./secrets/db_password.txt    # or external: true for Swarm secrets
```

```bash
# At runtime, secret is mounted as a file at /run/secrets/db_password
# Spring Boot can read it with: @Value("${DB_PASSWORD_FILE:#{null}}")
# Better: use AWS Secrets Manager (Phase 3)
```

### 3.3 What NOT to do
```bash
# BAD: hardcoded in docker-compose.yml
environment:
  DB_PASSWORD: mysecretpassword123    # visible in git, docker inspect

# BAD: .env committed to git
# Make sure .gitignore has:
echo "secrets/app.env" >> ../.gitignore
echo ".env" >> ../.gitignore
```

---

## SECTION 4 — Resource Limits

### 4.1 Setting Limits in Compose
```yaml
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 512m      # container OOM-killed if it exceeds this
      cpus: '0.5'       # max 50% of one CPU core
    reservations:
      memory: 256m      # guaranteed minimum
```

```bash
# Verify limits are applied
docker stats --no-stream

# Check if a container hit OOM (Out Of Memory)
docker inspect user-service | grep -A5 OOMKilled
docker events --filter container=user-service --filter event=oom
```

### 4.2 JVM in Containers
```bash
# Without container awareness, JVM uses host memory for heap sizing
# BAD: -Xmx4g on a container limited to 512m = OOM kill

# GOOD: use container-aware flags
export JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
# JVM sees container limit (512m), sets heap to 75% = 384m

# Check what JVM sees inside container
docker exec user-service java -XX:+PrintFlagsFinal -version 2>/dev/null | grep MaxHeapSize
```

---

## SECTION 5 — Logging Drivers

### 5.1 json-file (default)
```bash
# Logs stored in: /var/lib/docker/containers/<id>/<id>-json.log
docker logs user-service                # read via Docker API
docker logs -f user-service             # follow
docker logs --since 5m user-service    # last 5 minutes

# With rotation configured in compose:
# max-size: "10m"   → rotate when log reaches 10MB
# max-file: "3"     → keep 3 rotated files max
```

### 5.2 syslog (production)
```bash
# Sends logs to syslog daemon or remote aggregator
# Configured in docker-compose.prod.yml

# View syslog logs
sudo journalctl -u docker --since "10 minutes ago"
sudo tail -f /var/log/syslog | grep user-service
```

### 5.3 Structured Logging (Spring Boot → ELK)
```bash
# Add to Spring Boot application.yml:
# logging.pattern.console: '{"time":"%d","level":"%p","service":"user-service","msg":"%m"}%n'

# Or use logback with JSON encoder:
# <dependency>
#   <groupId>net.logstash.logback</groupId>
#   <artifactId>logstash-logback-encoder</artifactId>
# </dependency>

# Then pipe to Logstash/ELK (Phase 6 — Monitoring)
```

**Challenge 3:** Check the logs of all 3 services at once. Find which service took the longest to start.
```bash
docker compose logs --timestamps user-service order-service product-service \
    | grep -E "Started|startup" | sort
```

---

## REAL-WORLD CHALLENGES

### Challenge A — Stack Restart Test
Stop just the user-service container. Verify nginx returns 502. Restart it. Verify nginx recovers.
```bash
docker compose stop user-service
curl http://localhost/users/actuator/health    # should 502
docker compose start user-service
# Wait for health check
watch 'docker compose ps user-service'
curl http://localhost/users/actuator/health    # should 200
```

### Challenge B — Database Persistence
Insert data into MySQL. Bring down the stack with `docker compose down` (without -v). Bring it back up. Verify data is still there.
```bash
docker compose exec mysql mysql -u appuser -p${DB_PASSWORD} users_db \
    -e "CREATE TABLE test_persist (id INT); INSERT INTO test_persist VALUES (42);"
docker compose down
docker compose up -d
docker compose exec mysql mysql -u appuser -p${DB_PASSWORD} users_db \
    -e "SELECT * FROM test_persist;"
```

### Challenge C — Resource Monitoring
Run the full stack. In a separate terminal, monitor all container resource usage live.
```bash
watch -n 2 'docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"'
```

### Challenge D — Network Isolation Verify
Prove that MySQL is NOT reachable from outside Docker (backend network is internal).
```bash
# Should fail — MySQL is not exposed to host
nc -zv localhost 3306    # (unless override.yml exposes it)

# Should succeed — from order-service (on backend network)
docker compose exec order-service nc -zv mysql 3306
```

---

## QUICK REFERENCE CARD

| Command | What it does |
|---------|-------------|
| `docker compose up -d` | Start full stack |
| `docker compose up --build -d` | Rebuild images and start |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop + remove volumes (data loss!) |
| `docker compose ps` | Status of all services |
| `docker compose logs -f svc` | Follow logs for one service |
| `docker compose exec svc cmd` | Run command in service |
| `docker compose stop svc` | Stop one service |
| `docker compose start svc` | Start one service |
| `docker compose restart svc` | Restart one service |
| `docker compose scale svc=3` | Run 3 instances of service |
| `docker stats --no-stream` | One-shot resource usage |
| `docker compose -f a.yml -f b.yml up` | Merge compose files |

---

## DONE? Checklist

- [ ] I started the full 6-service stack with one command and all services reached healthy
- [ ] I understand the two-network design (frontend vs backend) and why backend is internal
- [ ] I know how docker-compose.override.yml auto-merges with the base file
- [ ] I ran the stack in "production mode" using explicit file selection
- [ ] I managed secrets with env_file and know why .env must be in .gitignore
- [ ] I set memory and CPU limits and verified them with docker stats
- [ ] I understand -XX:+UseContainerSupport and why it matters for Java
- [ ] I used json-file logging with rotation and read logs with docker logs
- [ ] I understand syslog as an alternative for production
- [ ] I completed all 4 real-world challenges

Next: Phase 1 Project — Containerised Spring Boot Microservices
