# DevForge

**One-click developer environment manager.** Select your development stack, click Install, and everything works.

## What is DevForge?

DevForge automatically installs, configures, verifies, repairs, and updates complete programming environments. Instead of manually installing Python, Git, VS Code, pip, and virtual environments, just select "Python Development" and click Install.

## Quick Start

```powershell
# Clone the repository
git clone <repo-url>
cd devforge

# Install backend dependencies
cd backend
pip install -e ".[dev]"

# Start the backend server
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

## Architecture

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, TypeScript, Tailwind CSS
- **Desktop**: Tauri 2.x (Rust shell)
- **Design**: Clean Architecture, SOLID, Plugin-based

See [docs/architecture.md](docs/architecture.md) for details.

## Development Stacks

| Stack | Packages |
|---|---|
| Python Development | Python, Git, VS Code, pip, uv |
| AI / Machine Learning | Python, Git, VS Code, Ollama, Docker, CUDA*, Jupyter |
| Web Development | Node.js, Git, VS Code, Chrome, Postman |
| Java Development | Java JDK, Maven, Git, IntelliJ IDEA CE |
| And more... | Rust, Go, C++, Android, DevOps, Data Science |

## License

MIT
