"""
Async process runner implementation.

Implements ProcessRunner port using asyncio.create_subprocess_exec/shell.
Supports stdout/stderr streaming callbacks, timeout enforcement, verification
pattern matching, and UAC elevation.
"""

from __future__ import annotations

import asyncio
import re
import time
from typing import Callable

from src.core.ports.process_runner import Command, CommandResult, ProcessRunner, VerifyCommand
from src.logger.structured_logger import StructuredLogger
from src.system.admin_elevation import is_admin, run_as_admin

logger = StructuredLogger("system.process_runner")


class AsyncProcessRunner(ProcessRunner):
    """
    Concrete implementation of ProcessRunner port interface.
    """

    async def run(self, command: Command) -> CommandResult:
        return await self.run_streaming(command)

    async def run_streaming(
        self,
        command: Command,
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
    ) -> CommandResult:
        if command.requires_admin and not await self.is_admin():
            logger.info(f"Command requires admin, attempting elevation: {command.full_command}")
            code, msg = await run_as_admin(command.executable, command.args)
            return CommandResult(
                return_code=code,
                stdout=msg,
                stderr="",
                duration_seconds=0.0,
            )

        start_time = time.monotonic()
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        try:
            if command.args:
                proc = await asyncio.create_subprocess_exec(
                    command.executable,
                    *command.args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=command.working_dir,
                    env=command.env_override if command.env_override else None,
                )
            else:
                proc = await asyncio.create_subprocess_shell(
                    command.executable,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=command.working_dir,
                    env=command.env_override if command.env_override else None,
                )

            async def read_stream(stream: asyncio.StreamReader, is_err: bool) -> None:
                while True:
                    line_bytes = await stream.readline()
                    if not line_bytes:
                        break
                    line = line_bytes.decode("utf-8", errors="replace").rstrip()
                    if is_err:
                        stderr_lines.append(line)
                        if on_stderr:
                            on_stderr(line)
                    else:
                        stdout_lines.append(line)
                        if on_stdout:
                            on_stdout(line)

            try:
                await asyncio.wait_for(
                    asyncio.gather(
                        read_stream(proc.stdout, False),  # type: ignore[arg-type]
                        read_stream(proc.stderr, True),   # type: ignore[arg-type]
                        proc.wait(),
                    ),
                    timeout=command.timeout_seconds,
                )
                timed_out = False
            except asyncio.TimeoutError:
                timed_out = True
                try:
                    proc.terminate()
                    await asyncio.sleep(0.5)
                    if proc.returncode is None:
                        proc.kill()
                except Exception:
                    pass

            duration = time.monotonic() - start_time
            stdout_str = "\n".join(stdout_lines)
            stderr_str = "\n".join(stderr_lines)

            return CommandResult(
                return_code=proc.returncode if proc.returncode is not None else -1,
                stdout=stdout_str,
                stderr=stderr_str,
                duration_seconds=duration,
                timed_out=timed_out,
            )

        except Exception as exc:
            duration = time.monotonic() - start_time
            logger.error(f"Failed to execute command '{command.full_command}': {exc}")
            return CommandResult(
                return_code=-1,
                stdout="",
                stderr=str(exc),
                duration_seconds=duration,
                timed_out=False,
            )

    async def is_admin(self) -> bool:
        return is_admin()

    async def verify_installation(self, verify_command: VerifyCommand) -> bool:
        cmd = Command(executable=verify_command.command, timeout_seconds=15)
        res = await self.run(cmd)

        if not res.success:
            return False

        output = f"{res.stdout}\n{res.stderr}"
        match = re.search(verify_command.expect_pattern, output)
        return match is not None
