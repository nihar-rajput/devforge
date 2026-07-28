# Design Decisions

## 1. FastAPI Sidecar (vs. Everything in Rust / Electron)

**Decision**: Use Tauri as the desktop shell with FastAPI bundled as a sidecar executable.

**Rationale**: Python has excellent libraries for Windows system integration (`winreg`, `subprocess`, `pynvml`, `ctypes`). Implementing the same in Rust would require extensive unsafe FFI. The sidecar pattern gives us Python's ecosystem with Tauri's small binary size.

**Trade-off**: Two processes instead of one, minor IPC overhead.

## 2. SQLite (vs. JSON Files)

**Decision**: Use SQLite via async SQLAlchemy for all persistent state.

**Rationale**: We need queries like "all packages in category X with health < 50" and transactions for rollback. SQLite provides ACID guarantees with zero configuration — perfect for a desktop app.

**Trade-off**: Slightly more complex than flat files, but dramatically more capable.

## 3. Direct Installers (vs. Winget/Chocolatey Delegation)

**Decision**: Download and execute official installers directly with silent flags.

**Rationale**: DevForge's core value is "install from scratch with zero prerequisites." Requiring winget or Chocolatey defeats that purpose. Direct control enables custom health checks, precise PATH management, and rollback.

**Trade-off**: More plugin code per package, but full control.

## 4. Python Plugin Classes (vs. YAML/JSON Definitions)

**Decision**: Each package is a Python class implementing `BasePlugin` ABC.

**Rationale**: Many packages require conditional logic (CUDA checks GPU compute capability, Docker checks Hyper-V). Python classes provide full expressiveness while maintaining a predictable contract.

**Trade-off**: Requires Python knowledge to author new plugins.

## 5. Event-Driven Architecture (vs. Direct Callbacks)

**Decision**: In-process async event bus decoupling engines from UI/logging.

**Rationale**: The installation engine shouldn't know about WebSockets. The event bus lets the engine emit domain events, consumed independently by WebSocket handlers, logger, and event store. Adding a new consumer requires zero changes to the engine.

**Trade-off**: Slight indirection, but massive maintainability gain.

## 6. Exponential Backoff with Decorrelated Jitter

**Decision**: Use AWS-recommended decorrelated jitter for retry delays.

**Rationale**: In scenarios where multiple downloads fail simultaneously (e.g., CDN issue), simple exponential backoff causes all retries to hit the server at the same intervals (thundering herd). Decorrelated jitter spreads retries randomly.

## 7. Multi-Segment Parallel Downloads

**Decision**: Split large files (>50MB) into 4 segments downloaded in parallel.

**Rationale**: Large files like CUDA Toolkit (~3GB) benefit from parallel connections, especially on high-bandwidth links where single-connection throughput is limited by TCP window scaling. Falls back gracefully if the server doesn't support Range requests.
