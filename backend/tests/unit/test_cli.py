"""
Unit tests for DevForge CLI.
"""

import pytest
from src.cli.main import main, main_async


def test_cli_list_command(capsys):
    ret = main(["list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "DevForge Catalog" in captured.out
    assert "python" in captured.out


def test_cli_list_with_category_filter(capsys):
    ret = main(["list", "--category", "language"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "python" in captured.out


@pytest.mark.asyncio
async def test_cli_info_command(capsys):
    ret = await main_async(["info"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "DevForge System Information" in captured.out


@pytest.mark.asyncio
async def test_cli_health_command(capsys):
    ret = await main_async(["health"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "DevForge Environment Health Audit" in captured.out


@pytest.mark.asyncio
async def test_cli_export_command(capsys):
    ret = await main_async(["export", "--packages", "python,git", "--name", "Test_CLI_Export"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Custom Offline Zip Bundle Created!" in captured.out
