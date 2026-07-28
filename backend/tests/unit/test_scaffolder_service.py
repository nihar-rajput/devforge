"""
Unit tests for ScaffolderService.
"""

import tempfile
from pathlib import Path
import pytest

from src.api.schemas.scaffold_schemas import ScaffoldProjectRequest
from src.services.scaffolder_service import ScaffolderService


def test_scaffold_python_app():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = ScaffolderService()
        req = ScaffoldProjectRequest(
            template="python-app",
            project_name="my_python_project",
            target_directory=tmpdir,
            initialize_git=True,
        )
        res = service.scaffold_project(req)

        assert res.success is True
        assert res.project_name == "my_python_project"

        proj_path = Path(res.project_path)
        assert (proj_path / "pyproject.toml").exists()
        assert (proj_path / "main.py").exists()
        assert (proj_path / "tests/test_main.py").exists()
        assert (proj_path / ".gitignore").exists()


def test_scaffold_web_react():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = ScaffolderService()
        req = ScaffoldProjectRequest(
            template="web-react",
            project_name="my_react_app",
            target_directory=tmpdir,
            initialize_git=False,
        )
        res = service.scaffold_project(req)

        assert res.success is True
        proj_path = Path(res.project_path)
        assert (proj_path / "package.json").exists()
        assert (proj_path / "src/App.tsx").exists()
        assert (proj_path / "index.html").exists()


def test_scaffold_rust_cli():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = ScaffolderService()
        req = ScaffoldProjectRequest(
            template="rust-cli",
            project_name="my_rust_cli",
            target_directory=tmpdir,
            initialize_git=False,
        )
        res = service.scaffold_project(req)

        assert res.success is True
        proj_path = Path(res.project_path)
        assert (proj_path / "Cargo.toml").exists()
        assert (proj_path / "src/main.rs").exists()


def test_scaffold_go_service():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = ScaffolderService()
        req = ScaffoldProjectRequest(
            template="go-service",
            project_name="my_go_service",
            target_directory=tmpdir,
            initialize_git=False,
        )
        res = service.scaffold_project(req)

        assert res.success is True
        proj_path = Path(res.project_path)
        assert (proj_path / "go.mod").exists()
        assert (proj_path / "main.go").exists()
        assert (proj_path / "Makefile").exists()
