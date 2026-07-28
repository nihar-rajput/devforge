# DevForge — Universal Developer Environment Manager 🚀

**DevForge** is a production-quality, cross-platform developer environment manager running natively on **Windows**, **macOS**, and **Linux**. Select your development stack, click Install, and everything is configured, verified, and added to your PATH automatically.

---

## 🌟 Key Features

- 📦 **36 Verified Package Plugins** (100% audit pass rate: Python, Node, Rust, Go, Java, Docker, VS Code, CUDA, Ollama, Terraform, Kubernetes, etc.)
- 🍏 **Universal Cross-Platform Engine** (Windows, macOS, Linux)
- 🐳 **Docker Sandbox & Multi-Stage Deployment**
- 💻 **DevForge Terminal CLI** (`devforge list`, `info`, `health`, `export`)
- 🏗️ **1-Click Workspace Project Scaffolder** (Python, React, Rust, Go)
- 📦 **Air-Gapped Offline Bundle Exporter** (Streaming `.zip` archives & 1-click `install_offline.bat` launchers)
- 🔔 **System Tray Background Health Monitor** (Periodic checks for PATH integrity, broken binaries, low disk space, and updates)
- 🔒 **Privacy-Preserving Telemetry & Error Reporter** (User consent modal with automatic path sanitization)
- 🧪 **51 Precision Unit & Integration Tests** (100% test pass rate)

---

## 📖 Comprehensive Documentation & Operating Guide

For complete installation steps, operational modes, CLI commands, offline bundler usage, and Docker setup:

👉 **[docs/installation_and_usage_guide.md](docs/installation_and_usage_guide.md)**

---

## ⚡ Quick Start

### 1. Web Application Mode
```powershell
# Clone the repository
git clone https://github.com/nihar-rajput/devforge.git
cd devforge/backend

# Install & launch backend (http://127.0.0.1:8000)
pip install -r requirements.txt
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Docker Container Sandbox Mode
```powershell
cd devforge
docker-compose up --build
```
Open **`http://localhost:8000/docs`** for live interactive API testing!

### 3. DevForge Terminal CLI
```powershell
cd devforge/backend
python -m src.cli.main list
python -m src.cli.main info
python -m src.cli.main health
python -m src.cli.main export --packages python,git,vscode --output MyOfflineBundle
```

### 4. Run Automated Precision Tests
```powershell
cd devforge/backend
pytest tests/ -v
```

---

## 📄 License

MIT License © 2026 DevForge Contributors
