"""
Audit & Download Speed Verification Script for DevForge Package Plugins.
"""

import asyncio
import time
import urllib.request
import urllib.error
import ssl
from pathlib import Path
import sys

# Ensure backend root is on pythonpath
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.package_manager.plugin_loader import DefaultPluginLoader
from src.package_manager.plugin_manager import PluginManager


async def verify_plugin_links():
    plugins_dir = Path(__file__).parent.parent / "src" / "plugins"
    loader = DefaultPluginLoader(plugin_dir=plugins_dir)
    loaded_dict = await loader.load_all_plugins()
    plugin_mgr = PluginManager()
    for p in loaded_dict.values():
        plugin_mgr.register_plugin(p)

    plugins = plugin_mgr.get_all_plugins()

    print(f"\n==================================================")
    print(f"  DevForge Link Integrity & Speed Audit ({len(plugins)} Plugins)")
    print(f"==================================================\n")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    results = []

    for p in plugins:
        url = "Unknown"
        try:
            ver = await p.get_latest_version()
            info = await p.get_download_info(ver)
            url = info.url

            print(f"Checking [{p.metadata.id.value}] {p.metadata.name} (v{ver})...")
            print(f"  URL: {url}")

            start_time = time.time()
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DevForge/0.1.0"},
            )

            # Test connection & fetch initial 256 KB chunk to measure real download speed
            with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
                headers = resp.headers
                content_length = headers.get("Content-Length")
                status = resp.status

                chunk = resp.read(256 * 1024)  # 256 KB
                elapsed = time.time() - start_time

                chunk_size_mb = len(chunk) / (1024 * 1024)
                speed_mbps = (chunk_size_mb / elapsed) * 8 if elapsed > 0 else 0

                size_str = f"{int(content_length) / (1024*1024):.1f} MB" if content_length else "Unknown"

                print(f"  Status: HTTP {status} OK | Remote Size: {size_str}")
                print(f"  Sample Speed: {speed_mbps:.2f} Mbps (TTFB + 256KB in {elapsed:.2f}s)\n")

                results.append(
                    {
                        "id": p.metadata.id.value,
                        "name": p.metadata.name,
                        "url": url,
                        "status": status,
                        "size": size_str,
                        "speed_mbps": speed_mbps,
                        "ok": True,
                    }
                )

        except Exception as e:
            print(f"  [FAIL] ERROR: {e}\n")
            results.append(
                {
                    "id": p.metadata.id.value,
                    "name": p.metadata.name,
                    "url": url,
                    "status": "FAILED",
                    "error": str(e),
                    "ok": False,
                }
            )

    print(f"==================================================")
    print(f"  Summary Audit Results")
    print(f"==================================================")
    passed = sum(1 for r in results if r["ok"])
    failed = sum(1 for r in results if not r["ok"])
    print(f"Total Plugins Audited: {len(results)}")
    print(f"Passed (HTTP OK & Readable): {passed}")
    print(f"Failed (Broken URL / Timeout): {failed}")

    if failed > 0:
        print("\nBroken Packages:")
        for r in results:
            if not r["ok"]:
                print(f"  - [{r['id']}] {r['name']}: {r.get('error')} (URL: {r['url']})")


if __name__ == "__main__":
    asyncio.run(verify_plugin_links())
