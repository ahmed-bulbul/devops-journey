# Week 2 — Networking & SSH

Working directory: ~/workspace/aws-learn/phase0/week2/

Run all commands from this directory unless told otherwise.

---

## SECTION 1 — Networking Fundamentals

### 1.1 OSI Model — DevOps Relevance

| Layer | Name | What DevOps cares about |
|-------|------|------------------------|
| 7 | Application | HTTP, HTTPS, DNS, SSH — your app lives here |
| 6 | Presentation | TLS/SSL encryption, encoding |
| 5 | Session | SSH sessions, persistent connections |
| 4 | Transport | TCP (reliable) vs UDP (fast) — ports live here |
| 3 | Network | IP addresses, routing, subnets — VPC lives here |
| 2 | Data Link | MAC addresses, switches |
| 1 | Physical | Cables, NICs |

**DevOps rule of thumb:**
- Layers 3–4 → firewall rules (IP, port, TCP/UDP)
- Layer 7 → nginx, load balancers, application health checks
- Layer 4 → `ss`, `netstat`, port scanning
- Layer 3 → `ping`, `traceroute`, VPC routing tables

### 1.2 IP Addressing and CIDR Notation
```bash
# View your machine's IP addresses
ip addr show
ip addr show eth0       # specific interface
hostname -I             # quick — just the IPs

# CIDR examples:
# 10.0.0.0/16   = 65536 addresses (VPC range)
# 10.0.1.0/24   = 256 addresses   (subnet)
# 10.0.1.0/28   = 16 addresses    (small subnet)
# 10.0.1.5/32   = 1 address       (single host)

# Calculate subnet info
ipcalc 10.0.1.0/24      # install: sudo apt install ipcalc
ipcalc 192.168.1.0/28
```

**Common private IP ranges (memorize these):**
```
10.0.0.0/8       — AWS VPCs, large private networks
172.16.0.0/12    — Docker default bridge network
192.168.0.0/16   — home/office routers
127.0.0.0/8      — loopback (localhost)
```

### 1.3 Ports and Protocols
```bash
# Common ports every DevOps engineer must know:
# 22    SSH
# 80    HTTP
# 443   HTTPS
# 3306  MySQL
# 5432  PostgreSQL
# 6379  Redis
# 8080  Spring Boot (default)
# 8081  Second app / Docker registry
# 9090  Prometheus
# 3000  Grafana
# 5601  Kibana
# 9200  Elasticsearch

# TCP vs UDP:
# TCP — reliable, ordered, connection-based (HTTP, SSH, database)
# UDP — fast, no guarantee, connectionless (DNS queries, video streaming)

# Check what is listening on your machine
sudo ss -tlnp             # TCP, listening, numeric, with process
sudo ss -tlnp | grep 8080
sudo netstat -tlnp        # older alternative (install: sudo apt install net-tools)

# Check a specific port
sudo ss -tlnp | grep ':22'
```

**Challenge 1:** Find what process is listening on port 22 on your machine.
```bash
sudo ss -tlnp | grep ':22'
```

---

## SECTION 2 — Networking Diagnostic Tools

### 2.1 ping — check reachability
```bash
# Ping a host
ping google.com
ping 8.8.8.8

# Limit to 4 packets
ping -c 4 google.com

# Ping with interval (every 0.2s — faster)
ping -i 0.2 -c 10 google.com

# Ping a local IP to test LAN connectivity
ping 192.168.1.1
```

### 2.2 traceroute — trace the network path
```bash
# Install if needed
sudo apt install traceroute

# Trace route to a host
traceroute google.com

# Use ICMP instead of UDP (often unblocked by firewalls)
traceroute -I google.com

# Trace route and show IPs (no DNS lookup — faster)
traceroute -n google.com

# Alternative: mtr (combines ping + traceroute, live updating)
sudo apt install mtr
mtr google.com
mtr --report google.com     # one-shot report
```

### 2.3 ss and netstat — socket statistics
```bash
# Show all listening TCP ports with process names
sudo ss -tlnp

# Show all connections (established + listening)
sudo ss -tanp

# Show UDP ports
sudo ss -ulnp

# Show all sockets for a specific process
sudo ss -tlnp | grep java
sudo ss -tlnp | grep nginx

# Show connections to a specific port
ss -tn dst :443

# netstat (older, same purpose)
sudo netstat -tlnp
sudo netstat -an | grep ESTABLISHED | wc -l    # count active connections
```

### 2.4 curl and wget — HTTP from command line
```bash
# Basic GET request
curl http://localhost
curl https://httpbin.org/get

# Show response headers only
curl -I http://localhost

# Show both headers and body
curl -v http://localhost

# POST with JSON body
curl -X POST http://localhost/api/users \
     -H "Content-Type: application/json" \
     -d '{"name": "Bulbul", "email": "test@test.com"}'

# Follow redirects
curl -L http://localhost

# Save response to file
curl -o response.json http://localhost/api/users

# Set timeout
curl --max-time 5 http://localhost

# Pass auth token
curl -H "Authorization: Bearer TOKEN" http://localhost/api/orders

# wget — download files
wget http://example.com/file.tar.gz
wget -O myfile.tar.gz http://example.com/file.tar.gz

# wget — mirror a site
wget -r --no-parent http://example.com/docs/
```

### 2.5 nc (netcat) — raw TCP/UDP testing
```bash
# Install
sudo apt install netcat-openbsd

# Test if a port is open (connection test)
nc -zv 127.0.0.1 8080
nc -zv google.com 443

# Test multiple ports
nc -zv 127.0.0.1 8080-8085

# Quick TCP server (useful for testing)
nc -l 9999                            # listen on port 9999
nc 127.0.0.1 9999                     # connect to it (in another terminal)

# Send a string to a port
echo "hello" | nc 127.0.0.1 9999

# Test if SSH port is open on a remote server
nc -zv SERVER_IP 22
```

**Challenge 2:** Test if port 80 is open on localhost and port 443 is open on google.com.
```bash
nc -zv 127.0.0.1 80
nc -zv google.com 443
```

---

## SECTION 3 — DNS

### 3.1 DNS Record Types
```
A      → hostname to IPv4 address       (api.example.com → 1.2.3.4)
AAAA   → hostname to IPv6 address
CNAME  → alias to another hostname      (www → example.com)
MX     → mail server for a domain
TXT    → arbitrary text (used for SPF, DKIM, domain verification)
NS     → nameservers for a domain
PTR    → reverse DNS (IP → hostname)
```

### 3.2 dig — query DNS
```bash
# Install
sudo apt install dnsutils

# Basic A record lookup
dig google.com

# Short output (just the answer)
dig +short google.com

# Look up a specific record type
dig google.com A
dig google.com MX
dig google.com NS
dig google.com TXT
dig google.com CNAME

# Query a specific DNS server
dig @8.8.8.8 google.com          # use Google's DNS
dig @1.1.1.1 google.com          # use Cloudflare's DNS

# Reverse DNS (IP to hostname)
dig -x 8.8.8.8

# Trace the full DNS resolution path
dig +trace google.com
```

### 3.3 nslookup — simpler DNS tool
```bash
# Basic lookup
nslookup google.com

# Look up specific record type
nslookup -type=MX gmail.com
nslookup -type=A github.com

# Use a specific DNS server
nslookup google.com 8.8.8.8

# Reverse lookup
nslookup 8.8.8.8
```

**Challenge 3:** Find the mail servers (MX records) for gmail.com.
```bash
dig gmail.com MX +short
# or
nslookup -type=MX gmail.com
```

**Challenge 4:** What IP does github.com resolve to? Use both dig and nslookup.
```bash
dig +short github.com
nslookup github.com
```

---

## SECTION 4 — SSH Key Authentication

### 4.1 Generate a Key Pair
```bash
# Generate ed25519 key (modern — preferred)
ssh-keygen -t ed25519 -C "bulbul@devops" -f ~/.ssh/id_ed25519

# Generate rsa key (older, still widely used)
ssh-keygen -t rsa -b 4096 -C "bulbul@devops" -f ~/.ssh/id_rsa

# List your keys
ls -lh ~/.ssh/

# View your PUBLIC key (safe to share)
cat ~/.ssh/id_ed25519.pub

# NEVER share your private key
```

### 4.2 Copy Key to Server and Connect
```bash
# Copy public key to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@SERVER_IP

# Manual copy (if ssh-copy-id not available)
cat ~/.ssh/id_ed25519.pub | ssh user@SERVER_IP \
  'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'

# Connect using key
ssh -i ~/.ssh/id_ed25519 user@SERVER_IP

# Verbose (debug connection issues)
ssh -vvv user@SERVER_IP

# Run command without opening shell
ssh user@SERVER_IP 'uptime && df -h'
```

### 4.3 SSH Permissions — Must Be Exact
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519         # private key
chmod 644 ~/.ssh/id_ed25519.pub     # public key
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/config

# Verify
ls -la ~/.ssh/
```

### 4.4 SSH Config File (~/.ssh/config)
Study the example: `ssh/ssh_config_example`
```bash
# Create/edit config
nano ~/.ssh/config
chmod 600 ~/.ssh/config

# Example entry:
# Host myserver
#     HostName 192.168.1.100
#     User ubuntu
#     IdentityFile ~/.ssh/id_ed25519

# Now connect with just:
ssh myserver

# Test config without connecting
ssh -G myserver | grep -E "hostname|user|identityfile"
```

**Challenge 5:** Generate an ed25519 key, create a config alias `Host practice` pointing to 127.0.0.1 with your username, verify with `ssh -G practice`.
```bash
ssh-keygen -t ed25519 -C "week2" -f ~/.ssh/id_ed25519 -N ""
chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_ed25519
# Add to ~/.ssh/config:
# Host practice
#     HostName 127.0.0.1
#     User YOUR_USERNAME
#     IdentityFile ~/.ssh/id_ed25519
ssh -G practice | grep -E "hostname|user|identityfile"
```

---

## SECTION 5 — SSH Advanced: sftp, scp, Port Forwarding

### 5.1 scp — secure copy
Practice files are in the `data/` folder: `servers.txt`, `app.properties`, `deploy_notes.txt`

```bash
# Copy a local file to /tmp (simulates copying to a server — use localhost)
scp data/deploy_notes.txt localhost:/tmp/

# Copy it back
scp localhost:/tmp/deploy_notes.txt /tmp/deploy_notes_copy.txt

# Copy with a config alias (after setting up 'Host practice' in Section 4)
scp data/app.properties practice:/tmp/

# Copy entire data/ directory recursively
scp -r data/ localhost:/tmp/week2-data/

# Preserve timestamps and permissions
scp -p data/servers.txt localhost:/tmp/
```

### 5.2 sftp — interactive file transfer
```bash
# Open sftp session
sftp user@SERVER_IP
sftp myserver           # using config alias

# Inside sftp session:
sftp> ls                # list remote files
sftp> lls               # list LOCAL files
sftp> pwd               # remote current directory
sftp> lpwd              # local current directory
sftp> cd /var/log       # change remote directory
sftp> lcd /tmp          # change local directory
sftp> get app.log       # download file
sftp> get -r logs/      # download directory
sftp> put app.jar       # upload file
sftp> put -r dist/      # upload directory
sftp> mkdir /opt/myapp  # create remote directory
sftp> rm old.jar        # delete remote file
sftp> exit              # close session

# Non-interactive — batch download
sftp user@SERVER_IP:/var/log/app.log ./app.log
```

### 5.3 rsync — efficient sync
```bash
# Sync local → remote (only sends changed files)
rsync -avz ./myapp/ user@SERVER_IP:/opt/myapp/

# Sync and delete files on remote not in local
rsync -avz --delete ./myapp/ user@SERVER_IP:/opt/myapp/

# Dry run (see what WOULD change)
rsync -avzn ./myapp/ user@SERVER_IP:/opt/myapp/

# Sync FROM server
rsync -avz user@SERVER_IP:/var/log/ ./remote-logs/

# rsync flags:
#  -a  archive (preserves permissions, timestamps, symlinks)
#  -v  verbose
#  -z  compress
#  -n  dry run
#  --progress  show per-file progress
```

### 5.4 Port Forwarding (Tunneling)
```bash
# LOCAL (-L): access remote resource as if it's local
# Forward localhost:5432 → remote server → remote DB:5432
ssh -L 5432:localhost:5432 user@SERVER_IP
# Now connect: psql -h localhost -p 5432

# LOCAL with explicit remote target:
# Forward localhost:3306 → remote server → db.internal:3306
ssh -L 3306:db.internal:3306 user@SERVER_IP

# REMOTE (-R): expose your local port to remote server
# Anyone on server hitting :8080 reaches your local :8080
ssh -R 8080:localhost:8080 user@SERVER_IP

# DYNAMIC (-D): SOCKS proxy
# Route all browser traffic through the server
ssh -D 1080 user@SERVER_IP

# Background tunnel (keep alive)
ssh -f -N -L 5432:localhost:5432 user@SERVER_IP
#   -f  go to background
#   -N  no shell, just the tunnel
```

**Challenge 6:** Use rsync dry run to preview syncing the `data/` folder to `/tmp/week2-data/`. Then do the real sync.
```bash
# Dry run first
rsync -avzn data/ /tmp/week2-data/

# Real sync
rsync -avz data/ /tmp/week2-data/

# Verify
ls -lh /tmp/week2-data/
```

---

## SECTION 6 — ufw and iptables Basics

### 6.1 ufw — Uncomplicated Firewall
Study the reference: `ufw/rules_reference.txt`

```bash
# Status
sudo ufw status verbose
sudo ufw status numbered

# First-time setup (ORDER MATTERS)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp          # SSH first — before enable!
sudo ufw limit 22/tcp          # rate limit SSH (brute force protection)
sudo ufw allow 80/tcp          # HTTP
sudo ufw allow 443/tcp         # HTTPS
sudo ufw allow from 127.0.0.1 to any port 8080  # app ports local only
sudo ufw allow from 127.0.0.1 to any port 8081
sudo ufw enable

# Block specific IP
sudo ufw deny from 203.0.113.5

# Delete rules
sudo ufw delete allow 8080/tcp
sudo ufw status numbered       # then:
sudo ufw delete 3              # delete by number

# Reload
sudo ufw reload
```

### 6.2 iptables Basics (what ufw wraps)
```bash
# View current rules (what ufw actually creates)
sudo iptables -L -n -v
sudo iptables -L INPUT -n -v    # just inbound rules

# The three main chains:
# INPUT   — traffic coming TO this machine
# OUTPUT  — traffic leaving FROM this machine
# FORWARD — traffic passing THROUGH (router mode)

# Add a rule manually (append to INPUT chain)
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# Block an IP
sudo iptables -A INPUT -s 203.0.113.5 -j DROP

# Allow established connections (needed for outbound responses)
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Delete a rule
sudo iptables -D INPUT -p tcp --dport 8080 -j ACCEPT

# Flush all rules (DANGEROUS — wipes firewall)
# sudo iptables -F

# Save rules (survives reboot)
sudo apt install iptables-persistent
sudo netfilter-persistent save

# NOTE: In real DevOps work, use ufw or cloud Security Groups
# iptables is useful to understand what's happening underneath
```

**Challenge 7:** From `logs/nginx_access.log`, find the suspicious IP, then write the ufw and iptables commands to block it.
```bash
# Find it
awk '$9 >= 400 {print $1}' logs/nginx_access.log | sort | uniq -c | sort -rn

# Block with ufw
sudo ufw deny from 203.0.113.5 comment 'Scanner'

# Block with iptables (alternative)
sudo iptables -A INPUT -s 203.0.113.5 -j DROP
```

---

## SECTION 7 — nginx: Static Site + Reverse Proxy

### 7.1 Install and Service Management
```bash
sudo apt update && sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx       # start on boot
sudo systemctl status nginx
sudo systemctl reload nginx       # reload config (no downtime)
sudo systemctl restart nginx      # full restart

# Check what ports nginx listens on
sudo ss -tlnp | grep nginx

# Test config (ALWAYS before reload)
sudo nginx -t

# Dump full effective config
sudo nginx -T
```

### 7.2 Serve a Static Site
```bash
# Web root
ls /var/www/html/

# Deploy the practice HTML page
sudo cp nginx/html/index.html /var/www/html/index.html
sudo chown www-data:www-data /var/www/html/index.html

# Test
sudo nginx -t && sudo systemctl reload nginx
curl http://localhost
curl -I http://localhost          # headers only
```

### 7.3 Multi-Service Reverse Proxy (Week 2 Project config)
Study: `nginx/sites-available/multi-service-proxy`

```bash
# Enable the multi-service proxy
sudo cp nginx/sites-available/multi-service-proxy /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/multi-service-proxy \
           /etc/nginx/sites-enabled/multi-service-proxy
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t && sudo systemctl reload nginx

# Test routing
curl http://localhost/health
curl http://localhost/app1/api/users    # → port 8080
curl http://localhost/app2/api/users    # → port 8081
```

### 7.4 Load Balancing Concepts
nginx supports multiple upstream algorithms — no code change needed, just config:

```nginx
# Round-robin (default) — each request goes to next server in order
upstream myapp {
    server 127.0.0.1:8080;
    server 127.0.0.1:8082;
}

# Least connections — send to server with fewest active connections
upstream myapp {
    least_conn;
    server 127.0.0.1:8080;
    server 127.0.0.1:8082;
}

# IP hash — same client always goes to same server (sticky sessions)
upstream myapp {
    ip_hash;
    server 127.0.0.1:8080;
    server 127.0.0.1:8082;
}

# Weight — send 70% to :8080, 30% to :8082
upstream myapp {
    server 127.0.0.1:8080 weight=7;
    server 127.0.0.1:8082 weight=3;
}
```

```bash
# Real-world DevOps note:
# nginx load balancing = Layer 7 (HTTP-aware, can route by URL)
# AWS ALB            = Layer 7 (path-based routing, host-based routing)
# AWS NLB            = Layer 4 (TCP-level, ultra-low latency)
```

### 7.5 nginx Log Analysis
```bash
# Practice with the sample logs in this repo
cat logs/nginx_access.log
cat logs/nginx_error.log

# Real logs (after nginx is installed)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Filter to only errors
grep '" [45]' logs/nginx_access.log

# Count requests per endpoint
awk '{print $7}' logs/nginx_access.log | sort | uniq -c | sort -rn

# Count requests per HTTP method
awk '{print $6}' logs/nginx_access.log | tr -d '"' | sort | uniq -c | sort -rn
```

---

## SECTION 8 — TLS/SSL Basics

### 8.1 How TLS Works (concepts)
```
1. Client connects to server on port 443
2. Server sends its certificate (contains public key + domain + CA signature)
3. Client verifies certificate was signed by a trusted CA
4. Both sides negotiate a symmetric session key (using public/private key crypto)
5. All traffic is encrypted with the session key

Key terms:
  Certificate    — proof of identity, signed by a CA
  CA             — Certificate Authority (Let's Encrypt, DigiCert, etc.)
  Private key    — stays on your server, NEVER shared
  Public key     — inside the certificate, shared with everyone
  CSR            — Certificate Signing Request (what you send to the CA)
  SNI            — Server Name Indication (how one IP serves multiple HTTPS domains)
```

### 8.2 openssl Commands
```bash
# Check if openssl is installed
openssl version

# Generate a self-signed certificate (for testing only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem \
    -days 365 -nodes \
    -subj "/CN=localhost/O=DevOps Practice/C=BD"

# View certificate details
openssl x509 -in cert.pem -text -noout
openssl x509 -in cert.pem -noout -dates       # just expiry dates
openssl x509 -in cert.pem -noout -subject     # just the subject

# Check a live site's certificate
openssl s_client -connect google.com:443 -servername google.com </dev/null
openssl s_client -connect google.com:443 </dev/null 2>/dev/null | openssl x509 -noout -dates

# Verify a certificate against a CA bundle
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt cert.pem

# Check if private key matches certificate
openssl x509 -noout -modulus -in cert.pem | md5sum
openssl rsa -noout -modulus -in key.pem | md5sum
# Both hashes must match

# Generate key and CSR (to send to a real CA)
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
    -subj "/CN=yourdomain.com/O=YourOrg/C=BD"
```

### 8.3 Let's Encrypt Basics (Certbot)
```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get a certificate for a domain (nginx plugin auto-configures nginx)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Standalone mode (stops nginx briefly)
sudo certbot certonly --standalone -d yourdomain.com

# Certificates are saved to:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem   (cert + chain)
# /etc/letsencrypt/live/yourdomain.com/privkey.pem     (private key)

# Test auto-renewal (certs expire every 90 days, certbot auto-renews)
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer

# nginx HTTPS config after certbot (what certbot auto-adds):
# listen 443 ssl;
# ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

**Challenge 8:** Generate a self-signed certificate for localhost and inspect its expiry date.
```bash
openssl req -x509 -newkey rsa:2048 -keyout /tmp/key.pem -out /tmp/cert.pem \
    -days 365 -nodes -subj "/CN=localhost"
openssl x509 -in /tmp/cert.pem -noout -dates
```

---

## WEEK 2 PROJECT — Secure Multi-Server Setup

**Goal:** On your Ubuntu machine, run two Java apps on ports 8080 and 8081. Configure ufw to allow only those ports from localhost. Set up SSH key-based login with a config alias. Use nginx as a reverse proxy routing `/app1 → 8080` and `/app2 → 8081`.

```bash
# STEP 1: Start two mock apps (simulates Spring Boot on 8080 and 8081)
python3 -m http.server 8080 &
APP1_PID=$!
python3 -m http.server 8081 &
APP2_PID=$!

# Verify they're running
ss -tlnp | grep -E '8080|8081'

# STEP 2: SSH key setup
ssh-keygen -t ed25519 -C "week2-project" -f ~/.ssh/id_ed25519 -N ""
ssh-copy-id -i ~/.ssh/id_ed25519.pub $(whoami)@localhost

# Add config alias
cat >> ~/.ssh/config <<'EOF'
Host devbox
    HostName 127.0.0.1
    User YOUR_USERNAME
    IdentityFile ~/.ssh/id_ed25519
EOF
chmod 600 ~/.ssh/config

# Test key-based login
ssh devbox 'echo "SSH key login works"'

# STEP 3: ufw rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw limit 22/tcp comment 'SSH rate-limited'
sudo ufw allow 80/tcp comment 'nginx HTTP'
sudo ufw allow from 127.0.0.1 to any port 8080 comment 'App1 internal'
sudo ufw allow from 127.0.0.1 to any port 8081 comment 'App2 internal'
sudo ufw enable
sudo ufw status verbose

# STEP 4: nginx multi-service proxy
sudo cp nginx/sites-available/multi-service-proxy /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/multi-service-proxy \
           /etc/nginx/sites-enabled/multi-service-proxy
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# STEP 5: Verify routing
curl http://localhost/health          # nginx health
curl http://localhost/app1/           # → port 8080
curl http://localhost/app2/           # → port 8081

# STEP 6: Confirm 8080/8081 are NOT reachable directly from outside
# (only localhost can reach them — ufw blocks external access)
curl http://localhost:8080            # works (from localhost)
# From another machine: curl http://YOUR_IP:8080 → should be BLOCKED

# Cleanup mock servers
kill $APP1_PID $APP2_PID
```

---

## REAL-WORLD CHALLENGES

### Challenge A — DNS Investigation
Find out what nameservers serve `github.com` and what IP `api.github.com` resolves to.
```bash
dig github.com NS +short
dig api.github.com A +short
```

### Challenge B — Port Scan Simulation
Check which of these ports are open on localhost: 22, 80, 443, 3306, 8080.
```bash
for port in 22 80 443 3306 8080; do
    nc -zv 127.0.0.1 $port 2>&1 | grep -E "open|refused"
done
```

### Challenge C — Log Security Audit
From `logs/nginx_access.log`, identify:
1. Which IP is scanning for vulnerabilities?
2. How many 4xx/5xx responses in total?
3. What endpoints is the attacker hitting?
```bash
# Attacker IP
awk '$9 >= 400 {print $1}' logs/nginx_access.log | sort | uniq -c | sort -rn

# Total error responses
awk '$9 >= 400' logs/nginx_access.log | wc -l

# What the attacker tried to access
grep "203.0.113.5" logs/nginx_access.log | awk '{print $7}'
```

### Challenge D — Certificate Inspection
Check the TLS certificate expiry date of google.com from the command line.
```bash
openssl s_client -connect google.com:443 -servername google.com </dev/null 2>/dev/null \
    | openssl x509 -noout -dates
```

### Challenge E — Full Networking Audit Script
Write a script that checks: (1) firewall status, (2) open ports, (3) nginx running, (4) DNS resolution, (5) SSH key auth works.
```bash
#!/bin/bash
echo "=== Firewall ==="
sudo ufw status | head -3

echo "=== Open Ports ==="
sudo ss -tlnp | grep -E '22|80|443|8080|8081'

echo "=== nginx ==="
systemctl is-active nginx

echo "=== DNS ==="
dig +short google.com | head -1

echo "=== SSH Key Auth ==="
ssh -o BatchMode=yes -o ConnectTimeout=3 devbox 'echo OK' 2>/dev/null || echo "FAILED"
```

---

## QUICK REFERENCE CARD

| Command | What it does |
|---------|-------------|
| `ip addr show` | Show IP addresses |
| `ping -c 4 host` | Test reachability |
| `traceroute host` | Trace network path |
| `sudo ss -tlnp` | Show listening TCP ports |
| `nc -zv host port` | Test if port is open |
| `curl -I http://url` | HTTP headers only |
| `curl -v http://url` | Full HTTP debug |
| `dig domain A +short` | DNS A record lookup |
| `dig domain MX +short` | DNS MX record lookup |
| `nslookup domain` | Simple DNS lookup |
| `ssh-keygen -t ed25519` | Generate key pair |
| `ssh-copy-id user@host` | Copy key to server |
| `ssh -L local:remote:port host` | Local port forward |
| `scp file user@host:/path` | Secure copy to server |
| `sftp user@host` | Interactive file transfer |
| `rsync -avz src/ user@host:/dst/` | Sync directory |
| `sudo ufw status verbose` | Firewall rules |
| `sudo ufw limit 22/tcp` | Rate-limit SSH |
| `sudo iptables -L -n -v` | View iptables rules |
| `sudo nginx -t` | Test nginx config |
| `sudo systemctl reload nginx` | Reload nginx (no downtime) |
| `openssl x509 -in cert.pem -noout -dates` | Check cert expiry |
| `openssl s_client -connect host:443` | Check live TLS cert |
| `sudo certbot --nginx -d domain` | Get Let's Encrypt cert |

---

## DONE? Checklist

- [ ] I understand OSI layers 3–7 and what DevOps tools operate at each layer
- [ ] I can read CIDR notation and know common private IP ranges
- [ ] I know common port numbers (22, 80, 443, 3306, 5432, 6379, 8080)
- [ ] I can use ping, traceroute, ss, netstat to diagnose network issues
- [ ] I can use curl (GET, POST, headers) and nc to test connectivity
- [ ] I can query DNS records with dig and nslookup (A, MX, NS, CNAME)
- [ ] I can generate SSH keys and copy them to a server
- [ ] I can create a ~/.ssh/config with host aliases
- [ ] I can use scp, sftp, and rsync to transfer files
- [ ] I understand SSH port forwarding (-L, -R, -D)
- [ ] I can configure ufw with default deny + specific allow rules
- [ ] I understand iptables chains (INPUT/OUTPUT/FORWARD) and basic rules
- [ ] I can serve a static site with nginx
- [ ] I can configure nginx as a multi-service reverse proxy
- [ ] I understand round-robin vs least-connections load balancing
- [ ] I can generate a self-signed certificate with openssl
- [ ] I know what Let's Encrypt / certbot does and how to use it
- [ ] I completed the Week 2 Project (Secure Multi-Server Setup)

Next: Phase 1 — Week 3: Git Advanced
