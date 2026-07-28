# DevForge — Comprehensive Installation & User Operating Guide

Welcome to the definitive operating guide for **DevForge**, the universal cross-platform developer environment manager.

---

## 📑 Table of Contents

1. [Overview & System Architecture](#1-overview--system-architecture)
2. [Installation Methods](#2-installation-methods)
   - [Method 1: Local Full-Stack Web Dashboard](#method-1-local-full-stack-web-dashboard)
   - [Method 2: Docker Container Sandbox](#method-2-docker-container-sandbox)
   - [Method 3: DevForge Terminal CLI](#method-3-devforge-terminal-cli)
   - [Method 4: Standalone Windows .exe Package](#method-4-standalone-windows-exe-package)
3. [Operating Modes & Workflows](#3-operating-modes--workflows)
   - [Mode A: Web Application Dashboard](#mode-a-web-application-dashboard)
   - [Mode B: Terminal CLI Mode](#mode-b-terminal-cli-mode)
   - [Mode C: 1-Click Workspace Project Scaffolder](#mode-c-1-click-workspace-project-scaffolder)
   - [Mode D: Air-Gapped Offline Bundle Exporter](#mode-d-air-gapped-offline-bundle-exporter)
   - [Mode E: System Tray Background Health Monitor](#mode-e-system-tray-background-health-monitor)
4. [Testing & Verification](#4-testing--verification)
5. [Troubleshooting & FAQs](#5-troubleshooting--faqs)

---

## 1. Overview & System Architecture

DevForge simplifies developer onboarding and environment management across **Windows**, **macOS**, and **Linux**.

### Core Engine Features:
- **36 Verified Package Plugins**: Pre-audited software tools across Languages, Databases, DevOps, AI, Editors, and Runtimes.
- **Topological Dependency Solver**: Resolves dependency graphs and version constraints dynamically.
- **Transaction & LIFO Rollback Engine**: Logs transaction checkpoints and automatically cleans up in reverse order upon installation failure.
- **Privacy Telemetry**: Log sanitizer scrubs local file paths (`C:\Users\<User>\`) before sending error reports.

---

## 2. Installation Methods

### Method 1: Local Full-Stack Web Dashboard

Ideal for running DevForge natively on your workstation with hot-reloading and UI dashboard:

```powershell
# 1. Clone the repository
git clone https://github.com/nihar-rajput/devforge.git
cd devforge

# 2. Setup Backend (Terminal 1)
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload

# 3. Setup Frontend (Terminal 2)
cd ..\frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser!

---

### Method 2: Docker Container Sandbox

Ideal for 100% isolated, non-destructive testing where no files or PATH variables are changed on your host PC:

```powershell
cd devforge
docker-compose up --build
```
Open **`http://localhost:8000/docs`** for interactive API testing!

---

### Method 3: DevForge Terminal CLI

Install DevForge as a terminal CLI utility:

```powershell
cd devforge/backend
pip install -e .

# Usage
devforge list
devforge info
devforge health
devforge export --packages python,git,vscode --output MyBundle
```

---

### Method 4: Standalone Windows `.exe` Package

For distribution without Python pre-installed:
- Push a version tag (`git tag v1.0.0 && git push origin v1.0.0`).
- GitHub Actions automatically compiles the standalone `.exe` installer and attaches it to the **[GitHub Release Page](https://github.com/nihar-rajput/devforge/releases)**.

---

## 3. Operating Modes & Workflows

### Mode A: Web Application Dashboard
- **Catalog View**: Search, filter by category (`Language`, `DevOps`, `Database`), view version info, and trigger 1-click installs.
- **Environment Stacks**: Install curated stacks (`Python Dev`, `Web Dev`, `AI / ML`) in a single click.

### Mode B: Terminal CLI Mode
- **`devforge list`**: Displays ANSI-colored table of all 36 plugins.
- **`devforge info`**: Displays OS, CPU cores, RAM, and GPU hardware details.
- **`devforge health`**: Audits system health and returns a score out of 100.
- **`devforge export`**: Builds custom offline `.zip` installer bundles.

### Mode C: 1-Click Workspace Project Scaffolder
Generates production-grade starter codebases with virtualenv, `.gitignore`, and `git init`:
- **Python App**: `main.py`, `pyproject.toml`, virtualenv setup.
- **Web React**: React + TypeScript + Vite project layout.
- **Rust CLI**: `Cargo.toml`, `src/main.rs`.
- **Go Service**: `go.mod`, `main.go`.

### Mode D: Air-Gapped Offline Bundle Exporter
- Packages installer binaries (`.exe`/`.msi`) or lightweight manifests into a portable `.zip`.
- Includes `manifest.json` (SHA-256 hashes) and 1-click `install_offline.bat` launcher for offline USB deployment.

### Mode E: System Tray Background Health Monitor
- Background worker runs every 5 minutes auditing tool binaries, damaged PATH variables, low disk space (< 10GB), and package updates.

---

## 4. Testing & Verification

Run the automated precision test suite (51 passing unit/integration tests):

```powershell
cd devforge/backend
pytest tests/ -v
```

---

## 5. Troubleshooting & FAQs

- **Docker API Connection Error**: Launch **Docker Desktop** application first until the status shows "Docker Desktop is running".
- **Windows UAC Permission Prompt**: DevForge requests UAC elevation (`ShellExecuteW 'runas'`) only when installing system-wide `.msi`/`.exe` packages to `C:\Program Files`.
- **Log Privacy Guarantee**: All username paths (`C:\Users\<User>\`) are sanitized automatically before telemetry reports are submitted.
