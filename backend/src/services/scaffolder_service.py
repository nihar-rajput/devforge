"""
Scaffolder Service implementation for 1-click workspace project generation.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import List

from src.api.schemas.scaffold_schemas import ScaffoldProjectRequest, ScaffoldProjectResponse
from src.logger.structured_logger import StructuredLogger

logger = StructuredLogger("services.scaffolder")


class ScaffolderService:
    """Service responsible for generating project workspaces and templates."""

    def scaffold_project(self, request: ScaffoldProjectRequest) -> ScaffoldProjectResponse:
        """Generate a project workspace folder from a selected template."""
        parent_dir = Path(request.target_directory) if request.target_directory else Path.cwd()
        project_dir = parent_dir / request.project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        template = request.template.lower().strip()
        files_created: List[str] = []

        if template == "python-app":
            files_created = self._scaffold_python_app(project_dir, request.project_name)
        elif template == "web-react":
            files_created = self._scaffold_web_react(project_dir, request.project_name)
        elif template == "rust-cli":
            files_created = self._scaffold_rust_cli(project_dir, request.project_name)
        elif template == "go-service":
            files_created = self._scaffold_go_service(project_dir, request.project_name)
        else:
            raise ValueError(f"Unsupported project template: '{request.template}'")

        # Initialize Git repository if requested
        if request.initialize_git:
            try:
                subprocess.run(["git", "init"], cwd=str(project_dir), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                files_created.append(".git/")
            except Exception as e:
                logger.warning(f"Failed to initialize git repository: {e}")

        logger.info(f"Scaffolded '{template}' project at '{project_dir}' ({len(files_created)} files).")
        return ScaffoldProjectResponse(
            success=True,
            project_name=request.project_name,
            project_path=str(project_dir),
            files_created=files_created,
            message=f"Successfully created '{request.project_name}' project workspace using '{template}' template.",
        )

    def _scaffold_python_app(self, target_dir: Path, name: str) -> List[str]:
        """Scaffold Python project with pyproject.toml, main.py, pytest, and .gitignore."""
        created = []

        pyproject = f"""[project]
name = "{name}"
version = "0.1.0"
description = "Python project created with DevForge"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "pytest>=8.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
        (target_dir / "pyproject.toml").write_text(pyproject, encoding="utf-8")
        created.append("pyproject.toml")

        main_py = """def hello(name: str = "World") -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello())
"""
        (target_dir / "main.py").write_text(main_py, encoding="utf-8")
        created.append("main.py")

        tests_dir = target_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        test_py = """from main import hello

def test_hello():
    assert hello("DevForge") == "Hello, DevForge!"
"""
        (tests_dir / "test_main.py").write_text(test_py, encoding="utf-8")
        created.append("tests/test_main.py")

        gitignore = """__pycache__/
*.pyc
.venv/
dist/
.pytest_cache/
.coverage
"""
        (target_dir / ".gitignore").write_text(gitignore, encoding="utf-8")
        created.append(".gitignore")

        readme = f"# {name}\n\nCreated with DevForge 1-Click Workspace Scaffolder."
        (target_dir / "README.md").write_text(readme, encoding="utf-8")
        created.append("README.md")

        return created

    def _scaffold_web_react(self, target_dir: Path, name: str) -> List[str]:
        """Scaffold React + Vite + TypeScript web application."""
        created = []

        package_json = f"""{{
  "name": "{name}",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "tsc && vite build"
  }},
  "dependencies": {{
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.460.0"
  }},
  "devDependencies": {{
    "typescript": "^5.6.0",
    "vite": "^5.4.0"
  }}
}}"""
        (target_dir / "package.json").write_text(package_json, encoding="utf-8")
        created.append("package.json")

        src_dir = target_dir / "src"
        src_dir.mkdir(exist_ok=True)

        app_tsx = """import React from "react";

export function App() {
  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", color: "#333" }}>
      <h1>⚡ Welcome to Your React App</h1>
      <p>Scaffolded automatically with DevForge.</p>
    </div>
  );
}

export default App;
"""
        (src_dir / "App.tsx").write_text(app_tsx, encoding="utf-8")
        created.append("src/App.tsx")

        index_html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>{name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>"""
        (target_dir / "index.html").write_text(index_html, encoding="utf-8")
        created.append("index.html")

        main_tsx = """import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
        (src_dir / "main.tsx").write_text(main_tsx, encoding="utf-8")
        created.append("src/main.tsx")

        gitignore = "node_modules/\ndist/\n.env\n"
        (target_dir / ".gitignore").write_text(gitignore, encoding="utf-8")
        created.append(".gitignore")

        return created

    def _scaffold_rust_cli(self, target_dir: Path, name: str) -> List[str]:
        """Scaffold Rust Cargo binary project."""
        created = []

        cargo_toml = f"""[package]
name = "{name}"
version = "0.1.0"
edition = "2021"

[dependencies]
"""
        (target_dir / "Cargo.toml").write_text(cargo_toml, encoding="utf-8")
        created.append("Cargo.toml")

        src_dir = target_dir / "src"
        src_dir.mkdir(exist_ok=True)

        main_rs = """fn main() {
    println!("Hello from Rust CLI scaffolded with DevForge!");
}
"""
        (src_dir / "main.rs").write_text(main_rs, encoding="utf-8")
        created.append("src/main.rs")

        gitignore = "target/\n**/*.rs.bk\n"
        (target_dir / ".gitignore").write_text(gitignore, encoding="utf-8")
        created.append(".gitignore")

        return created

    def _scaffold_go_service(self, target_dir: Path, name: str) -> List[str]:
        """Scaffold Go module microservice."""
        created = []

        go_mod = f"module {name}\n\ngo 1.22\n"
        (target_dir / "go.mod").write_text(go_mod, encoding="utf-8")
        created.append("go.mod")

        main_go = """package main

import "fmt"

func main() {
    fmt.Println("Hello from Go service scaffolded with DevForge!")
}
"""
        (target_dir / "main.go").write_text(main_go, encoding="utf-8")
        created.append("main.go")

        makefile = """build:
\tgo build -o bin/app main.go

run:
\tgo run main.go
"""
        (target_dir / "Makefile").write_text(makefile, encoding="utf-8")
        created.append("Makefile")

        gitignore = "bin/\nvendor/\n.env\n"
        (target_dir / ".gitignore").write_text(gitignore, encoding="utf-8")
        created.append(".gitignore")

        return created
