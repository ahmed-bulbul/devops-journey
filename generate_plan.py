from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import KeepTogether

OUTPUT = "/home/bulbul-ahmed/workspace/aws-learn/DevOps_Roadmap_Java_Developer.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="Pro DevOps Engineer Roadmap — Java Developer",
    author="AWS Learn"
)

W = A4[0] - 4*cm  # usable width

# ── Colour palette ───────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#0D2137")
BLUE   = colors.HexColor("#1565C0")
CYAN   = colors.HexColor("#0288D1")
GREEN  = colors.HexColor("#2E7D32")
ORANGE = colors.HexColor("#E65100")
GREY   = colors.HexColor("#455A64")
LGREY  = colors.HexColor("#ECEFF1")
WHITE  = colors.white

# ── Styles ───────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

cover_title = S("ct", fontSize=28, textColor=WHITE, alignment=TA_CENTER,
                spaceAfter=6, leading=34, fontName="Helvetica-Bold")
cover_sub   = S("cs", fontSize=14, textColor=colors.HexColor("#B0BEC5"),
                alignment=TA_CENTER, spaceAfter=4, fontName="Helvetica")
cover_tag   = S("ctag", fontSize=11, textColor=colors.HexColor("#80CBC4"),
                alignment=TA_CENTER, fontName="Helvetica-Oblique")

h0 = S("h0", fontSize=20, textColor=WHITE, fontName="Helvetica-Bold",
        spaceAfter=2, leading=24, alignment=TA_LEFT)
h1 = S("h1", fontSize=15, textColor=BLUE, fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=4, leading=20)
h2 = S("h2", fontSize=12, textColor=CYAN, fontName="Helvetica-Bold",
        spaceBefore=8, spaceAfter=3, leading=16)
h3 = S("h3", fontSize=11, textColor=GREEN, fontName="Helvetica-Bold",
        spaceBefore=6, spaceAfter=2)

body = S("body", fontSize=9.5, textColor=colors.HexColor("#212121"),
         spaceAfter=3, leading=14, alignment=TA_JUSTIFY)
bullet = S("bullet", fontSize=9.5, textColor=colors.HexColor("#212121"),
           spaceAfter=2, leading=13, leftIndent=14)
note  = S("note", fontSize=8.5, textColor=GREY, leftIndent=14,
          spaceAfter=2, fontName="Helvetica-Oblique")
tag_s = S("tag", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold",
           alignment=TA_CENTER)
week_s = S("week", fontSize=9, textColor=GREY, fontName="Helvetica-Oblique",
            spaceAfter=1)

# ── Helper builders ───────────────────────────────────────────────────────────

def phase_header(num, title, duration, color=BLUE):
    data = [[
        Paragraph(f"PHASE {num}", S(f"ph{num}a", fontSize=9, textColor=WHITE,
                  fontName="Helvetica-Bold")),
        Paragraph(title, S(f"ph{num}b", fontSize=13, textColor=WHITE,
                  fontName="Helvetica-Bold")),
        Paragraph(duration, S(f"ph{num}c", fontSize=9, textColor=colors.HexColor("#B0BEC5"),
                  fontName="Helvetica-Oblique", alignment=TA_CENTER)),
    ]]
    t = Table(data, colWidths=[1.8*cm, W-4.8*cm, 3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color),
        ("ROUNDEDCORNERS", [5]),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (0,0), 10),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (-1,0), (-1,0), 10),
    ]))
    return t

def tag_cell(label, bg):
    return Table([[Paragraph(label, tag_s)]],
                 colWidths=[2.4*cm],
                 style=[("BACKGROUND",(0,0),(-1,-1),bg),
                        ("ROUNDEDCORNERS",[4]),
                        ("TOPPADDING",(0,0),(-1,-1),2),
                        ("BOTTOMPADDING",(0,0),(-1,-1),2)])

def info_row(items):
    cells = [tag_cell(t, c) for t, c in items]
    w = W / len(cells)
    t = Table([cells], colWidths=[w]*len(cells))
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                            ("LEFTPADDING",(0,0),(-1,-1),3),
                            ("RIGHTPADDING",(0,0),(-1,-1),3)]))
    return t

def skill_table(rows):
    data = [[Paragraph(r[0], h2), Paragraph(r[1], body), Paragraph(r[2], note)]
            for r in rows]
    t = Table(data, colWidths=[4*cm, W-7.5*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), LGREY),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE, LGREY]),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#CFD8DC")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),6),
    ]))
    return t

def checklist(items):
    return ListFlowable(
        [ListItem(Paragraph(i, bullet), bulletColor=CYAN, bulletFontSize=9) for i in items],
        bulletType="bullet", leftIndent=10, bulletOffsetY=-1
    )

def section_box(content_list, bg=LGREY):
    inner = Table([[c] for c in content_list],
                  colWidths=[W-1.2*cm])
    inner.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), bg),
        ("TOPPADDING",(0,0),(-1,-1),2),
        ("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("LEFTPADDING",(0,0),(-1,-1),8),
        ("RIGHTPADDING",(0,0),(-1,-1),8),
    ]))
    outer = Table([[inner]], colWidths=[W])
    outer.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),1,CYAN),
        ("ROUNDEDCORNERS",[6]),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    return outer

# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT CONTENT
# ═══════════════════════════════════════════════════════════════════════════════
story = []

# ── COVER PAGE ────────────────────────────────────────────────────────────────
cover_bg = Table(
    [[Paragraph("Pro DevOps Engineer", cover_title)],
     [Paragraph("Complete Roadmap for Java Developers", cover_sub)],
     [Spacer(1, 0.3*cm)],
     [Paragraph("Ubuntu · AWS Free Tier · Spring Boot Microservices", cover_tag)],
     [Spacer(1, 0.6*cm)],
     [HRFlowable(width=W*0.6, thickness=1, color=colors.HexColor("#37474F"), hAlign="CENTER")],
     [Spacer(1, 0.4*cm)],
     [Paragraph("6 Months · 8 Phases · 26 Weeks · Hands-On Projects", cover_tag)],
    ],
    colWidths=[W]
)
cover_bg.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1), NAVY),
    ("ROUNDEDCORNERS",[10]),
    ("TOPPADDING",(0,0),(-1,-1),30),
    ("BOTTOMPADDING",(0,0),(-1,-1),30),
    ("LEFTPADDING",(0,0),(-1,-1),20),
    ("RIGHTPADDING",(0,0),(-1,-1),20),
]))
story += [cover_bg, Spacer(1, 0.8*cm)]

# Quick-stat bar
stat_data = [["26 Weeks", "8 Phases", "20+ Projects", "AWS Free Tier", "Java/Spring Boot"]]
stat_t = Table(stat_data, colWidths=[W/5]*5)
stat_t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1), BLUE),
    ("TEXTCOLOR",(0,0),(-1,-1), WHITE),
    ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),9),
    ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("TOPPADDING",(0,0),(-1,-1),8),
    ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ("GRID",(0,0),(-1,-1),0.5,NAVY),
]))
story += [stat_t, Spacer(1, 0.5*cm)]

story.append(Paragraph("How to Use This Roadmap", h1))
story.append(Paragraph(
    "Follow each phase in order. Every phase ends with a hands-on project you deploy on AWS Free Tier. "
    "Mark each checklist item complete before moving to the next. Expected commitment: 2–3 hours/day on weekdays. "
    "Total duration: ~26 weeks (6 months).", body))
story.append(Spacer(1, 0.3*cm))

# ── TABLE OF CONTENTS ─────────────────────────────────────────────────────────
story.append(Paragraph("Table of Contents", h1))
toc = [
    ["Phase 0", "Linux & Networking Foundations",        "Week 1–2"],
    ["Phase 1", "Git, Docker & Containerisation",        "Week 3–5"],
    ["Phase 2", "CI/CD Pipelines",                       "Week 6–8"],
    ["Phase 3", "AWS Core Services",                     "Week 9–12"],
    ["Phase 4", "Kubernetes & EKS",                      "Week 13–16"],
    ["Phase 5", "Infrastructure as Code",                "Week 17–19"],
    ["Phase 6", "Monitoring & Observability",            "Week 20–21"],
    ["Phase 7", "Security & DevSecOps",                  "Week 22–23"],
    ["Phase 8", "Advanced DevOps & Certifications",      "Week 24–26"],
]
toc_table = Table(
    [[Paragraph(r[0], S("tc0", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE)),
      Paragraph(r[1], S("tc1", fontSize=9, fontName="Helvetica", textColor=NAVY)),
      Paragraph(r[2], S("tc2", fontSize=9, fontName="Helvetica-Oblique", textColor=GREY, alignment=TA_CENTER))]
     for r in toc],
    colWidths=[2*cm, W-5*cm, 3*cm]
)
toc_table.setStyle(TableStyle([
    ("ROWBACKGROUNDS",(0,0),(-1,-1),[NAVY, LGREY]),
    ("TEXTCOLOR",(0,0),(0,-1), WHITE),
    ("FONTNAME",(0,0),(-1,-1),"Helvetica"),
    ("FONTSIZE",(0,0),(-1,-1),9),
    ("TOPPADDING",(0,0),(-1,-1),6),
    ("BOTTOMPADDING",(0,0),(-1,-1),6),
    ("LEFTPADDING",(0,0),(-1,-1),8),
    ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#B0BEC5")),
]))
story += [toc_table, PageBreak()]

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 0 — Linux & Networking
# ══════════════════════════════════════════════════════════════════════════════
story.append(phase_header(0, "Linux & Networking Foundations", "Week 1 – 2", NAVY))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "As a Java developer you already know how to code — now you need to master the OS and network layer "
    "that everything runs on. Ubuntu is your daily driver; these skills are prerequisite to every later phase.", body))

story.append(Paragraph("Week 1 — Linux CLI Mastery", h1))
story += [
    Paragraph("Core Commands", h2),
    checklist([
        "File system navigation: ls, cd, pwd, find, locate",
        "File operations: cp, mv, rm, mkdir, chmod, chown, ln -s",
        "Text processing: cat, less, head, tail, grep, awk, sed, cut, sort, uniq",
        "Process management: ps, top, htop, kill, systemctl, journalctl",
        "Package management: apt update/upgrade, apt install/remove, dpkg",
        "Disk & memory: df, du, free, lsblk, mount",
        "Archiving: tar, zip, gzip, rsync",
        "User management: useradd, passwd, sudo, /etc/sudoers",
        "Shell scripting: variables, loops, if/else, functions, cron jobs",
    ]),
    Paragraph("Week 1 Project", h2),
    section_box([
        Paragraph("Shell Script Automation Suite", h3),
        Paragraph("Write 5 bash scripts: (1) system health checker (CPU/RAM/Disk alerts), "
                  "(2) log rotator with compression, (3) automated backup to a local folder, "
                  "(4) user creation wizard, (5) Spring Boot app start/stop/status manager.", body),
    ]),
    Spacer(1, 0.2*cm),
    Paragraph("Week 2 — Networking & SSH", h1),
    Paragraph("Networking Fundamentals", h2),
    checklist([
        "OSI model layers and their DevOps relevance",
        "IP addressing, CIDR notation, subnets (e.g. 10.0.0.0/16)",
        "DNS: A, CNAME, MX records; dig, nslookup commands",
        "Ports & protocols: TCP/UDP, HTTP/HTTPS, SSH (22), common app ports",
        "Tools: ping, traceroute, netstat, ss, curl, wget, nc (netcat)",
        "Firewall: ufw enable/disable, ufw allow/deny, iptables basics",
        "SSH: key pair generation, ssh-keygen, ~/.ssh/config, scp, sftp",
        "VPN concepts: tunneling, port forwarding, ssh -L/-R/-D",
        "Load balancing concepts: round-robin, least-connections",
        "TLS/SSL: certificates, openssl commands, Let's Encrypt basics",
    ]),
    Paragraph("Week 2 Project", h2),
    section_box([
        Paragraph("Secure Multi-Server Setup", h3),
        Paragraph("On your Ubuntu machine: run two Java apps on ports 8080 and 8081. "
                  "Configure ufw to allow only those ports. Set up SSH key-based login "
                  "with a config alias. Use nginx as a local reverse proxy routing /app1 → 8080 and /app2 → 8081.", body),
    ]),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Git, Docker & Containerisation
# ══════════════════════════════════════════════════════════════════════════════
story.append(phase_header(1, "Git, Docker & Containerisation", "Week 3 – 5", BLUE))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("Week 3 — Git Advanced", h1))
story += [
    checklist([
        "Branching strategies: GitFlow, trunk-based development, GitHub Flow",
        "git rebase vs merge — when to use each",
        "Interactive rebase: squash, fixup, reorder commits",
        "git stash, git cherry-pick, git bisect",
        "Resolving merge conflicts like a pro",
        "git hooks: pre-commit (lint/test), commit-msg (conventional commits)",
        "GitHub: PRs, code reviews, branch protection rules, GitHub Actions triggers",
        "Signed commits with GPG keys",
        "Monorepo vs polyrepo patterns for microservices",
        "Git submodules and subtrees",
    ]),
    Paragraph("Week 4 — Docker", h1),
    checklist([
        "Docker architecture: daemon, client, registry, image, container, layer",
        "Dockerfile: FROM, RUN, COPY, WORKDIR, ENV, EXPOSE, CMD, ENTRYPOINT",
        "Multi-stage builds for Java — build with Maven, run with JRE only",
        "docker build, run, exec, logs, inspect, stats, rm, rmi",
        "Docker networking: bridge, host, overlay — container-to-container comms",
        "Docker volumes: bind mounts vs named volumes",
        "Docker Hub: push/pull, private repos, image tagging strategy",
        "docker compose: services, networks, volumes, depends_on, env_file",
        ".dockerignore — exclude target/ and .git from build context",
        "Docker security: non-root user, read-only filesystem, image scanning",
    ]),
    Paragraph("Week 4 — Spring Boot Docker", h2),
    checklist([
        "Spring Boot Maven/Gradle Docker plugin (Jib) — build without Dockerfile",
        "Layered JARs for optimal Docker cache efficiency",
        "Environment-specific config via ENV / Spring profiles",
        "Health checks in Dockerfile and compose",
        "Connecting Spring Boot to MySQL/Postgres containers via compose",
    ]),
    Paragraph("Week 5 — Docker Compose Full Stack", h1),
    checklist([
        "Run multi-service Spring Boot app: API + DB + Redis + nginx",
        "Override files: docker-compose.override.yml for local dev",
        "Secrets management in compose (file-based)",
        "Resource limits: mem_limit, cpu_shares",
        "Logging drivers: json-file, syslog",
    ]),
    Paragraph("Phase 1 Project", h2),
    section_box([
        Paragraph("Containerised Spring Boot Microservices", h3),
        Paragraph("Build 3 Spring Boot services (User, Order, Product). "
                  "Write optimised multi-stage Dockerfiles. "
                  "Wire them with docker-compose including MySQL, Redis, and nginx reverse proxy. "
                  "Push images to Docker Hub. Document the Compose setup.", body),
    ]),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — CI/CD Pipelines
# ══════════════════════════════════════════════════════════════════════════════
story.append(phase_header(2, "CI/CD Pipelines", "Week 6 – 8", colors.HexColor("#6A1B9A")))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("Week 6 — GitHub Actions", h1))
story += [
    checklist([
        "Workflow YAML: on, jobs, steps, uses, env, secrets",
        "Runners: ubuntu-latest, self-hosted runners on your Ubuntu machine",
        "Build & test Spring Boot: actions/checkout, setup-java, mvn test",
        "Cache Maven dependencies: actions/cache",
        "Build and push Docker image: docker/build-push-action",
        "Matrix builds: test across Java 17/21",
        "Environment secrets: DOCKER_HUB_TOKEN, AWS_ACCESS_KEY_ID",
        "Artifacts: upload-artifact, download-artifact",
        "Deployment jobs with needs: and environment: approvals",
        "Reusable workflows: workflow_call",
    ]),
    Paragraph("Week 7 — Jenkins", h1),
    checklist([
        "Install Jenkins on Ubuntu via Docker",
        "Jenkinsfile: declarative pipeline syntax",
        "Stages: Checkout → Build → Test → Docker Build → Push → Deploy",
        "Jenkins agents and parallel stages",
        "Credentials management in Jenkins (not plaintext)",
        "Blue Ocean UI for pipeline visualisation",
        "Webhooks: trigger Jenkins from GitHub push",
        "SonarQube integration for code quality gates",
        "Nexus/Artifactory for Maven artifact storage",
        "Pipeline shared libraries",
    ]),
    Paragraph("Week 8 — Quality & Security Gates", h1),
    checklist([
        "Unit tests: JUnit 5, Mockito — coverage report with JaCoCo",
        "Integration tests: Testcontainers (real DB in pipeline)",
        "Code quality: SonarQube quality gate (block merge if fails)",
        "Dependency scanning: OWASP Dependency-Check Maven plugin",
        "Docker image scanning: Trivy in CI pipeline",
        "Conventional commits + semantic versioning automation",
        "Changelog generation: git-cliff or standard-version",
        "Slack/email notifications on build failure",
    ]),
    Paragraph("Phase 2 Project", h2),
    section_box([
        Paragraph("Full CI/CD Pipeline", h3),
        Paragraph("GitHub Actions pipeline: on PR → run tests + SonarQube + Trivy scan. "
                  "On merge to main → build Docker image → push to ECR → deploy to EC2 via SSH. "
                  "Jenkins pipeline as alternative with same stages. "
                  "Enforce quality gate: PRs blocked if coverage < 80%.", body),
    ]),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — AWS Core Services
# ══════════════════════════════════════════════════════════════════════════════
story.append(phase_header(3, "AWS Core Services", "Week 9 – 12", colors.HexColor("#00695C")))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("Week 9 — Identity & Networking (IAM + VPC)", h1))
story += [
    checklist([
        "IAM: users, groups, roles, policies (inline vs managed)",
        "Least-privilege principle — deny by default",
        "IAM roles for EC2, Lambda, ECS tasks (no hardcoded keys!)",
        "STS: AssumeRole, temporary credentials",
        "MFA enforcement, password policy, IAM Access Analyzer",
        "VPC: CIDR, subnets (public/private), route tables, internet gateway",
        "NAT Gateway vs NAT Instance (cost trade-off on Free Tier)",
        "Security Groups vs NACLs — stateful vs stateless",
        "VPC Peering and VPC Endpoints (S3/DynamoDB gateway endpoints)",
        "AWS CLI: configure, profiles, --query, --output json/table",
    ]),
    Paragraph("Week 10 — Compute (EC2 + Auto Scaling + ALB)", h1),
    checklist([
        "EC2: instance types, AMIs, key pairs, user data scripts",
        "Free Tier: t2.micro/t3.micro — one always-free instance",
        "EC2 Spot instances for CI runners (80% cheaper)",
        "Launch Templates and Auto Scaling Groups",
        "ALB: listeners, target groups, health checks, path-based routing",
        "Deploy Spring Boot on EC2: systemd service, auto-start on reboot",
        "Elastic IP vs public IP — when to use each",
        "EC2 Instance Connect and SSM Session Manager (no SSH port needed)",
        "AMI creation from running instance (backup strategy)",
        "EC2 cost optimisation: stop when not in use, Savings Plans",
    ]),
    Paragraph("Week 11 — Storage & Database (S3 + RDS)", h1),
    checklist([
        "S3: buckets, objects, prefixes, storage classes",
        "S3 versioning, lifecycle rules, replication",
        "S3 static website hosting, pre-signed URLs",
        "S3 SDK in Spring Boot: upload, download, delete, list objects",
        "S3 event notifications → Lambda/SQS",
        "RDS: MySQL/PostgreSQL on Free Tier (db.t3.micro, 20GB)",
        "RDS Multi-AZ vs read replicas",
        "RDS automated backups, snapshots, point-in-time recovery",
        "Connect Spring Boot to RDS (spring.datasource in Secrets Manager)",
        "ElastiCache: Redis on Free Tier — Spring Boot cache integration",
    ]),
    Paragraph("Week 12 — Containers on AWS (ECR + ECS)", h1),
    checklist([
        "ECR: create repo, push/pull Docker images, lifecycle policies",
        "ECS concepts: cluster, task definition, service, container",
        "ECS launch types: Fargate (serverless) vs EC2",
        "Fargate Free Tier: limited — use EC2 launch type to stay free",
        "Task definitions: CPU/memory, env vars, secrets from SSM/SecretsManager",
        "ECS service: desired count, rolling update deployment",
        "ECS with ALB: service discovery via target groups",
        "ECS Exec — exec into running container (like docker exec)",
        "CloudWatch Logs for ECS container output",
        "ECS autoscaling: Application Auto Scaling on CPU/memory",
    ]),
    Paragraph("Phase 3 Project", h2),
    section_box([
        Paragraph("Production-Grade AWS Deployment", h3),
        Paragraph("Deploy the Phase 1 microservices to AWS: "
                  "VPC with public/private subnets. EC2 instances in private subnet behind ALB. "
                  "RDS MySQL in private subnet. S3 for file storage integrated into User service. "
                  "CI/CD pipeline pushes to ECR and triggers ECS rolling deployment. "
                  "All secrets in AWS Secrets Manager.", body),
    ]),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — Kubernetes & EKS
# ══════════════════════════════════════════════════════════════════════════════
story.append(phase_header(4, "Kubernetes & EKS", "Week 13 – 16", colors.HexColor("#1565C0")))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("Week 13 — Kubernetes Fundamentals (Local)", h1))
story += [
    checklist([
        "Install minikube or kind on Ubuntu for local K8s",
        "Core objects: Pod, ReplicaSet, Deployment, Service, ConfigMap, Secret",
        "Namespaces: separate dev/staging/prod workloads",
        "kubectl: get, describe, apply, delete, logs, exec, port-forward",
        "YAML manifests: write from scratch — no GUI copy-paste",
        "Deployments: rolling update, rollback (kubectl rollout undo)",
        "Services: ClusterIP, NodePort, LoadBalancer types",
        "Persistent Volumes and Persistent Volume Claims",
        "Resource requests and limits (cpu/memory) — always set these!",
        "Liveness and readiness probes for Spring Boot (/actuator/health)",
    ]),
    Paragraph("Week 14 — Kubernetes Intermediate", h1),
    checklist([
        "Ingress controllers: nginx-ingress, path/host-based routing",
        "ConfigMaps and Secrets — mount as env vars or volume files",
        "Horizontal Pod Autoscaler (HPA) based on CPU",
        "StatefulSets for databases (Postgres on K8s)",
        "DaemonSets: node-level agents (log collectors, monitoring)",
        "Jobs and CronJobs for batch tasks",
        "RBAC: ClusterRole, Role, RoleBinding — least privilege in K8s",
        "Network Policies: restrict pod-to-pod communication",
        "Pod Disruption Budgets for zero-downtime maintenance",
        "Kustomize: environment-specific overlays without Helm",
    ]),
    Paragraph("Week 15 — Helm", h1),
    checklist([
        "Helm concepts: chart, release, values.yaml, templates",
        "helm install, upgrade, rollback, uninstall, list",
        "Write a Helm chart for your Spring Boot service",
        "values.yaml overrides per environment (values-prod.yaml)",
        "Helm hooks: pre-install database migrations",
        "Artifact Hub: find charts for nginx-ingress, cert-manager, prometheus",
        "Helmfile: manage multiple charts declaratively",
        "Chart testing with helm lint and helm template",
    ]),
    Paragraph("Week 16 — Amazon EKS", h1),
    checklist([
        "EKS: managed control plane, you manage node groups",
        "eksctl: create cluster, add node group, delete cluster",
        "Free Tier warning: EKS control plane costs $0.10/hour — spin up only when practising",
        "IAM roles for service accounts (IRSA) — pods assume AWS IAM roles",
        "AWS Load Balancer Controller — replaces in-tree ALB integration",
        "EBS CSI driver for persistent storage on EKS",
        "EKS managed add-ons: CoreDNS, kube-proxy, VPC CNI",
        "Cluster Autoscaler or Karpenter for node autoscaling",
        "kubectl auth: aws eks update-kubeconfig",
        "Deploy Phase 1 microservices to EKS with Helm charts",
    ]),
    Paragraph("Phase 4 Project", h2),
    section_box([
        Paragraph("Kubernetes Microservices Deployment", h3),
        Paragraph("Write K8s manifests + Helm charts for all 3 microservices. "
                  "Deploy to minikube locally. Configure HPA, readiness probes, resource limits. "
                  "Set up nginx Ingress with path routing. "
                  "Deploy to EKS (spend 2–3 hours max, then delete cluster to save cost). "
                  "CI/CD: helm upgrade --install in GitHub Actions.", body),
    ]),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — Infrastructure as Code
# ══════════════════════════════════════════════════════════════════════════════
story.append(phase_header(5, "Infrastructure as Code (IaC)", "Week 17 – 19", ORANGE))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("Week 17 — Terraform", h1))
story += [
    checklist([
        "Terraform concepts: provider, resource, data source, output, variable",
        "HCL syntax: blocks, arguments, expressions, functions",
        "terraform init, plan, apply, destroy, state",
        "State management: local vs S3 backend with DynamoDB locking",
        "AWS provider: configure with IAM role (not access keys in code!)",
        "Resources: aws_vpc, aws_subnet, aws_security_group, aws_instance",
        "Resources: aws_s3_bucket, aws_rds_instance, aws_ecs_service",
        "Modules: write reusable VPC, EC2, RDS modules",
        "Variables: terraform.tfvars, environment variable TF_VAR_*",
        "Workspace: terraform workspace for dev/staging/prod",
    ]),
    Paragraph("Week 18 — Terraform Advanced + CloudFormation", h1),
    checklist([
        "Remote state: S3 backend, state locking with DynamoDB",
        "terraform import: bring existing resources under IaC management",
        "Terraform Cloud (free tier) for state and remote runs",
        "for_each and count for creating multiple similar resources",
        "Dynamic blocks and conditional expressions",
        "Terraform modules from Terraform Registry",
        "CloudFormation basics: stacks, templates, parameters, outputs",
        "CloudFormation vs Terraform — when AWS uses CFN natively (CDK, SAM)",
        "AWS CDK: write infrastructure in Java — create a CDK app",
        "CDK constructs: L1 (cfn), L2 (opinionated), L3 (patterns)",
    ]),
    Paragraph("Week 19 — Ansible", h1),
    checklist([
        "Ansible concepts: inventory, playbook, task, module, role",
        "Install and configure software on EC2 via Ansible",
        "Ansible roles: structure, defaults, vars, tasks, handlers",
        "Ansible Vault: encrypt secrets in playbooks",
        "Ansible Galaxy: download community roles",
        "Use Ansible to configure EC2 after Terraform provisions it",
        "Idempotency: run playbooks multiple times safely",
        "Dynamic inventory: aws_ec2 plugin auto-discovers instances",
    ]),
    Paragraph("Phase 5 Project", h2),
    section_box([
        Paragraph("Full IaC-Managed AWS Environment", h3),
        Paragraph("Terraform code that provisions: VPC, subnets, SGs, ALB, EC2 ASG, RDS, ElastiCache, S3, ECR. "
                  "Remote state in S3 + DynamoDB. Modules for VPC and compute. "
                  "Ansible playbook configures EC2 (Java, Docker, nginx). "
                  "CDK bonus: rewrite VPC + ECS in Java CDK.", body),
    ]),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — Monitoring & Observability
# ══════════════════════════════════════════════════════════════════════════════
story.append(phase_header(6, "Monitoring & Observability", "Week 20 – 21", GREEN))
story.append(Spacer(1, 0.3*cm))

story += [
    Paragraph("Week 20 — AWS CloudWatch + Prometheus + Grafana", h1),
    checklist([
        "CloudWatch metrics: EC2, RDS, ECS, ALB built-in metrics",
        "CloudWatch Logs: log groups, log streams, log insights queries",
        "CloudWatch Alarms: SNS notifications for CPU > 80%, error rates",
        "CloudWatch Dashboards: composite view of your stack",
        "CloudWatch Agent on EC2: collect custom metrics and logs",
        "AWS X-Ray: distributed tracing for Spring Boot (add Spring Cloud Sleuth + X-Ray)",
        "Prometheus: install on EC2, scrape Spring Boot /actuator/prometheus",
        "Spring Boot Actuator: expose metrics with Micrometer + Prometheus registry",
        "Grafana: connect to Prometheus, import Spring Boot dashboard (ID 12900)",
        "Grafana alerts: PagerDuty/Slack integration",
    ]),
    Paragraph("Week 21 — ELK Stack + Distributed Tracing", h1),
    checklist([
        "ELK: Elasticsearch + Logstash + Kibana — run via Docker Compose",
        "Filebeat: ship Spring Boot logs from EC2 to Elasticsearch",
        "Logback JSON format in Spring Boot for structured logging",
        "Kibana: create index patterns, visualizations, dashboards",
        "OpenTelemetry: instrument Spring Boot with OTLP exporter",
        "Jaeger: distributed tracing backend — run locally with Docker",
        "Trace context propagation across microservices (W3C TraceContext)",
        "SLI/SLO/SLA definitions for your services",
        "Error budget concept and alerting strategy",
        "Runbook template: how to respond to each alert",
    ]),
    Paragraph("Phase 6 Project", h2),
    section_box([
        Paragraph("Full Observability Stack", h3),
        Paragraph("Spring Boot services expose metrics + traces + structured logs. "
                  "Prometheus scrapes metrics → Grafana dashboard with 5 key panels. "
                  "ELK stack receives all logs → Kibana error dashboard. "
                  "Jaeger shows end-to-end trace for cross-service requests. "
                  "CloudWatch alarm triggers SNS email when error rate > 5%.", body),
    ]),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 7 — Security & DevSecOps
# ══════════════════════════════════════════════════════════════════════════════
story.append(phase_header(7, "Security & DevSecOps", "Week 22 – 23", colors.HexColor("#B71C1C")))
story.append(Spacer(1, 0.3*cm))

story += [
    Paragraph("Week 22 — AWS Security Services", h1),
    checklist([
        "AWS Secrets Manager: store DB passwords, API keys — rotate automatically",
        "AWS KMS: create CMKs, encrypt S3, RDS, EBS — envelope encryption",
        "AWS Cognito: user pools (auth), identity pools (AWS resource access)",
        "Spring Boot + Cognito: JWT validation, OAuth2 resource server",
        "AWS WAF: web ACL, rate limiting, SQL injection rules on ALB/CloudFront",
        "AWS Shield Standard (free): DDoS protection",
        "AWS GuardDuty: threat detection (30-day free trial)",
        "AWS Config: track configuration changes, compliance rules",
        "AWS Security Hub: aggregated security findings",
        "AWS Inspector: vulnerability scanning for EC2 and ECR images",
    ]),
    Paragraph("Week 23 — DevSecOps in CI/CD", h1),
    checklist([
        "SAST: SpotBugs + SonarQube in Maven build — block on HIGH issues",
        "DAST: OWASP ZAP automated scan against deployed app",
        "SCA: OWASP Dependency-Check — CVE scanning of Maven dependencies",
        "Secret scanning: git-secrets / truffleHog — prevent keys in git",
        "Docker image scanning: Trivy in CI, fail on CRITICAL CVEs",
        "Kubernetes security: Pod Security Standards, OPA Gatekeeper",
        "Network segmentation: SGs allow only required ports, NACLs as backstop",
        "Principle of least privilege in IAM — audit with IAM Access Analyzer",
        "Compliance as code: AWS Config rules checked in pipeline",
        "OWASP Top 10 — map each to a Spring Boot mitigation",
    ]),
    Paragraph("Phase 7 Project", h2),
    section_box([
        Paragraph("Secure Spring Boot Deployment", h3),
        Paragraph("Cognito-protected API Gateway → Spring Boot (JWT validation). "
                  "All secrets in Secrets Manager. KMS-encrypted S3 bucket and RDS. "
                  "WAF rules on ALB. CI pipeline: SAST + SCA + Trivy scan before deploy. "
                  "GuardDuty enabled. IAM roles with minimal permissions audited by Access Analyzer.", body),
    ]),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 8 — Advanced DevOps & Certifications
# ══════════════════════════════════════════════════════════════════════════════
story.append(phase_header(8, "Advanced DevOps & Certifications", "Week 24 – 26", GREY))
story.append(Spacer(1, 0.3*cm))

story += [
    Paragraph("Week 24 — Advanced Deployment Strategies", h1),
    checklist([
        "Blue/Green deployment on ECS and EKS — zero downtime",
        "Canary deployment: Route 53 weighted routing or AWS CodeDeploy",
        "Feature flags: AWS AppConfig or LaunchDarkly",
        "GitOps with ArgoCD: deploy K8s manifests from git automatically",
        "Flux CD: alternative GitOps operator",
        "Rollback automation: auto-rollback on CloudWatch alarm",
        "Database migrations in CI/CD: Flyway/Liquibase with zero-downtime patterns",
        "AWS CodePipeline + CodeDeploy: native AWS CI/CD alternative",
    ]),
    Paragraph("Week 25 — Cost Optimisation & SRE Practices", h1),
    checklist([
        "AWS Cost Explorer: analyse spending by service/tag",
        "Resource tagging strategy: env, team, project tags on all resources",
        "AWS Compute Optimizer: rightsizing recommendations",
        "Spot Instances for batch jobs and CI runners (save 70–90%)",
        "Reserved Instances and Savings Plans for stable workloads",
        "S3 Intelligent-Tiering for variable-access objects",
        "SRE concepts: error budgets, toil reduction, blameless postmortems",
        "Chaos engineering: AWS Fault Injection Simulator (FIS)",
        "Runbooks and incident response playbooks",
        "On-call rotations and escalation policies (PagerDuty)",
    ]),
    Paragraph("Week 26 — Certifications Roadmap", h1),
    skill_table([
        ["AWS CCP", "AWS Certified Cloud Practitioner — broad overview, good if you want a starting cert.", "~1 month prep"],
        ["AWS SAA-C03", "AWS Solutions Architect Associate — THE key cert for DevOps on AWS. Study this first.", "~2 months prep"],
        ["AWS DVA-C02", "AWS Developer Associate — covers CodePipeline, Lambda, DynamoDB deeply.", "~1.5 months prep"],
        ["AWS SysOps", "AWS SysOps Administrator — operations, monitoring, automation.", "~2 months prep"],
        ["AWS DevOps Pro", "AWS DevOps Engineer Professional — gold standard. Requires SAA or DVA first.", "~3 months prep"],
        ["CKA", "Certified Kubernetes Administrator — essential for K8s-heavy roles.", "~2 months prep"],
        ["Terraform Assoc", "HashiCorp Terraform Associate — validates IaC skills.", "~3 weeks prep"],
    ]),
    Spacer(1, 0.3*cm),
    Paragraph("Recommended Cert Order:", h2),
    checklist([
        "Month 7: AWS Solutions Architect Associate (SAA-C03)",
        "Month 9: CKA — Certified Kubernetes Administrator",
        "Month 11: Terraform Associate",
        "Month 13: AWS DevOps Engineer Professional",
    ]),
]
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# FREE TIER CHEAT SHEET
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("AWS Free Tier Cheat Sheet", h0.clone("h0b")))

free_data = [
    ["Service", "Free Tier Allowance", "Expires"],
    ["EC2 t2.micro", "750 hrs/month", "12 months"],
    ["RDS db.t3.micro", "750 hrs/month + 20GB storage", "12 months"],
    ["S3", "5GB storage, 20K GET, 2K PUT", "Forever"],
    ["Lambda", "1M requests/month, 400K GB-sec", "Forever"],
    ["CloudWatch", "10 custom metrics, 10 alarms, 5GB logs", "Forever"],
    ["DynamoDB", "25GB storage, 25 RCU/WCU", "Forever"],
    ["ECR", "500MB/month private storage", "Forever"],
    ["SNS", "1M publishes, 100K HTTP deliveries", "Forever"],
    ["SQS", "1M requests/month", "Forever"],
    ["Secrets Manager", "30-day free trial per secret", "Trial only"],
    ["EKS", "$0.10/hour for control plane — NOT free!", "—"],
    ["NAT Gateway", "NOT free — use NAT Instance (t2.micro)", "—"],
]

ft = Table(free_data, colWidths=[4.5*cm, W-8*cm, 3.5*cm])
ft.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0), NAVY),
    ("TEXTCOLOR",(0,0),(-1,0), WHITE),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),9),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LGREY]),
    ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#B0BEC5")),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),6),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    # Highlight warning rows
    ("BACKGROUND",(0,12),(-1,12), colors.HexColor("#FFCDD2")),
    ("BACKGROUND",(0,13),(-1,13), colors.HexColor("#FFCDD2")),
])
)
story += [ft, Spacer(1, 0.4*cm)]

# ══════════════════════════════════════════════════════════════════════════════
# LEARNING RESOURCES
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("Essential Learning Resources", h1))
res_data = [
    ["Resource", "What It Covers", "Cost"],
    ["AWS Skill Builder", "Official AWS courses, practice exams, labs", "Free tier available"],
    ["Linux Journey (linuxjourney.com)", "Interactive Linux CLI learning", "Free"],
    ["Play with Docker (labs.play-with-docker.com)", "Browser-based Docker labs", "Free"],
    ["Killercoda", "K8s, Linux, Docker labs in browser", "Free"],
    ["A Cloud Guru / Udemy", "AWS + DevOps video courses", "Paid (~$15)"],
    ["Terraform Up & Running (book)", "Terraform best practices by Yevgeniy Brikman", "Paid"],
    ["The DevOps Handbook (book)", "DevOps culture and practices", "Paid"],
    ["AWS Well-Architected Framework docs", "Official AWS architecture pillars", "Free"],
    ["GitHub: awesome-devops", "Curated DevOps tools and resources", "Free"],
]
rt = Table(res_data, colWidths=[5*cm, W-8.5*cm, 3.5*cm])
rt.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0), BLUE),
    ("TEXTCOLOR",(0,0),(-1,0), WHITE),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),9),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LGREY]),
    ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#B0BEC5")),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),6),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
]))
story += [rt, Spacer(1, 0.4*cm)]

# ══════════════════════════════════════════════════════════════════════════════
# WEEK-BY-WEEK QUICK REFERENCE
# ══════════════════════════════════════════════════════════════════════════════
story.append(Paragraph("26-Week Quick Reference Timeline", h1))
weeks = [
    ("Wk 1",  "Linux CLI — shell scripting, file system, processes"),
    ("Wk 2",  "Networking — TCP/IP, DNS, SSH, ufw, nginx reverse proxy"),
    ("Wk 3",  "Git advanced — branching, rebase, hooks, GPG signing"),
    ("Wk 4",  "Docker — Dockerfiles, multi-stage, compose, Spring Boot"),
    ("Wk 5",  "Docker Compose full stack — multi-service, volumes, secrets"),
    ("Wk 6",  "GitHub Actions — build/test/push pipeline, matrix builds"),
    ("Wk 7",  "Jenkins — Jenkinsfile, webhooks, SonarQube, Nexus"),
    ("Wk 8",  "Quality gates — JaCoCo, Testcontainers, Trivy, OWASP DC"),
    ("Wk 9",  "AWS IAM + VPC — least privilege, subnets, SGs, NACLs"),
    ("Wk 10", "EC2 + ALB + Auto Scaling — deploy Spring Boot on AWS"),
    ("Wk 11", "S3 + RDS + ElastiCache — storage and database on AWS"),
    ("Wk 12", "ECR + ECS — containerised deployment with rolling updates"),
    ("Wk 13", "Kubernetes fundamentals — pods, deployments, services"),
    ("Wk 14", "K8s intermediate — Ingress, RBAC, HPA, NetworkPolicy"),
    ("Wk 15", "Helm — write charts, upgrade, rollback, helmfile"),
    ("Wk 16", "EKS — managed K8s on AWS, IRSA, ALB controller"),
    ("Wk 17", "Terraform — HCL, state, modules, AWS resources"),
    ("Wk 18", "Terraform advanced + CloudFormation + AWS CDK (Java)"),
    ("Wk 19", "Ansible — playbooks, roles, dynamic inventory, vault"),
    ("Wk 20", "CloudWatch + Prometheus + Grafana — metrics and dashboards"),
    ("Wk 21", "ELK + OpenTelemetry + Jaeger — logs and distributed tracing"),
    ("Wk 22", "AWS security — Cognito, KMS, Secrets Manager, WAF, GuardDuty"),
    ("Wk 23", "DevSecOps — SAST, DAST, SCA, secret scanning in CI/CD"),
    ("Wk 24", "Blue/Green, canary, GitOps (ArgoCD), Flyway migrations"),
    ("Wk 25", "Cost optimisation, SRE, chaos engineering, FIS"),
    ("Wk 26", "Certification prep — SAA-C03, CKA, Terraform Associate"),
]
rows = []
for i in range(0, len(weeks), 2):
    row = []
    for j in range(2):
        if i+j < len(weeks):
            w, desc = weeks[i+j]
            row.append(Paragraph(f"<b>{w}</b> — {desc}", S(f"wr{i}", fontSize=8.5, leading=12)))
        else:
            row.append(Paragraph("", body))
    rows.append(row)

wt = Table(rows, colWidths=[W/2, W/2])
wt.setStyle(TableStyle([
    ("ROWBACKGROUNDS",(0,0),(-1,-1),[LGREY, WHITE]),
    ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#CFD8DC")),
    ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",(0,0),(-1,-1),6),
    ("VALIGN",(0,0),(-1,-1),"TOP"),
]))
story += [wt, Spacer(1, 0.5*cm)]

# ── Footer note ───────────────────────────────────────────────────────────────
story.append(HRFlowable(width=W, thickness=1, color=GREY))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    "Generated for Bulbul Ahmed · 6+ Years Java/Spring Boot · AWS Free Tier · Ubuntu · June 2026 · "
    "Follow phases in order — each builds on the last. Good luck! 🚀",
    S("footer", fontSize=8, textColor=GREY, alignment=TA_CENTER)
))

# ── Build PDF ─────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF created: {OUTPUT}")
