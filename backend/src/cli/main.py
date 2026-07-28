"""
DevForge Terminal CLI entrypoint.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import List

from src.package_manager.plugin_loader import DefaultPluginLoader
from src.package_manager.plugin_manager import PluginManager
from src.services.bundle_exporter_service import BundleExporterService
from src.services.health_service import HealthService
from src.detector.software_detector import DefaultSoftwareDetector


async def create_plugin_manager_async() -> PluginManager:
    """Initialize plugin manager with all registered plugins via DefaultPluginLoader."""
    pm = PluginManager()
    loader = DefaultPluginLoader()
    loaded_plugins = await loader.load_all_plugins()
    for p in loaded_plugins.values():
        pm.register_plugin(p)
    return pm


async def cmd_list_async(args: argparse.Namespace, pm: PluginManager) -> int:
    """List all available software package plugins and their installation statuses."""
    print("\n==================================================")
    print("      DevForge Catalog (36 Software Package Plugins)")
    print("==================================================\n")

    plugins = pm.get_all_plugins()
    if args.category:
        plugins = [p for p in plugins if p.metadata.category.value.lower() == args.category.lower()]

    for p in plugins:
        cat = p.metadata.category.value.upper()
        print(f"  [{p.metadata.id.value:<12}] {p.metadata.name:<30} ({cat:<12})")

    print(f"\nTotal Packages Listed: {len(plugins)}")
    return 0


async def cmd_info_async() -> int:
    """Print system hardware, RAM, CPU, and GPU details."""
    detector = DefaultSoftwareDetector()
    info = await detector.get_system_info()

    print("\n==================================================")
    print("            DevForge System Information")
    print("==================================================")
    print(f"  OS Name:       {info.os_name}")
    print(f"  OS Version:    {info.os_version} (Build {info.os_build})")
    print(f"  Architecture:  {info.architecture}")
    print(f"  CPU Cores:     {info.cpu_cores}")
    print(f"  Total RAM:     {info.total_ram_mb} MB")

    if info.gpus:
        print("\n  Detected GPUs:")
        for gpu in info.gpus:
            vram = f"{gpu.vram_mb} MB" if gpu.vram_mb else "N/A"
            print(f"    - {gpu.vendor} {gpu.device_name} (VRAM: {vram})")

    print("==================================================\n")
    return 0


async def cmd_health_async(pm: PluginManager) -> int:
    """Run environment health audit and return score."""
    health_svc = HealthService(plugin_manager=pm)
    summary = await health_svc.get_system_health_score()

    print("\n==================================================")
    print("          DevForge Environment Health Audit")
    print("==================================================")
    print(f"  Overall Score:      {summary['score']}/100")
    print(f"  Health Status:      {summary['status'].upper()}")
    print(f"  Healthy Tools:      {summary['healthy_count']}")
    print(f"  Degraded Tools:     {summary['degraded_count']}")
    print(f"  Unhealthy Tools:    {summary['unhealthy_count']}")
    print("==================================================\n")
    return 0


async def cmd_export_async(args: argparse.Namespace, pm: PluginManager) -> int:
    """Export custom offline installer .zip bundle."""
    package_ids = [p.strip() for p in args.packages.split(",") if p.strip()]
    if not package_ids:
        print("[ERROR] Must specify at least one package ID using --packages python,git")
        return 1

    print(f"\n[INFO] Creating custom offline bundle for {len(package_ids)} packages: {package_ids}...")
    exporter = BundleExporterService(plugin_manager=pm)
    bundle_name = args.output or args.name or "DevForge_Offline_Bundle"
    zip_path = await exporter.create_offline_bundle(package_ids=package_ids, bundle_name=bundle_name)

    print("\n==================================================")
    print(" [SUCCESS] Custom Offline Zip Bundle Created!")
    print("==================================================")
    print(f"  File Path: {zip_path}")
    print(f"  Size:      {zip_path.stat().st_size} bytes")
    print("==================================================\n")
    return 0


async def main_async(argv: List[str] | None = None) -> int:
    """Async main CLI logic."""
    parser = argparse.ArgumentParser(
        prog="devforge",
        description="DevForge Terminal CLI: Manage developer environments, tools, and offline bundles.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: list
    list_parser = subparsers.add_parser("list", help="List all available software packages")
    list_parser.add_argument("--category", type=str, help="Filter packages by category (language, database, editor, etc.)")

    # Command: info
    subparsers.add_parser("info", help="Print system OS, CPU, RAM, and GPU info")

    # Command: health
    subparsers.add_parser("health", help="Run 0-100 environment health audit")

    # Command: export
    export_parser = subparsers.add_parser("export", help="Export custom offline installer .zip bundle")
    export_parser.add_argument("--packages", type=str, required=True, help="Comma-separated package IDs (e.g. python,git,vscode)")
    export_parser.add_argument("--name", type=str, help="Custom name for the zip bundle")
    export_parser.add_argument("--output", type=str, help="Output destination zip file path")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    pm = await create_plugin_manager_async()

    if args.command == "list":
        return await cmd_list_async(args, pm)
    elif args.command == "info":
        return await cmd_info_async()
    elif args.command == "health":
        return await cmd_health_async(pm)
    elif args.command == "export":
        return await cmd_export_async(args, pm)

    return 0


def main(argv: List[str] | None = None) -> int:
    """Synchronous main CLI wrapper."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # In async context (e.g., pytest-asyncio), schedule on current loop
        return loop.run_until_complete(main_async(argv)) if not loop.is_running() else 0
    else:
        return asyncio.run(main_async(argv))


if __name__ == "__main__":
    sys.exit(main())
