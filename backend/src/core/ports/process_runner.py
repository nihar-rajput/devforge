"""
Process runner port.

Abstract interface for executing system commands with output
streaming, timeout management, and admin elevation support.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Command:
    """A command to execute on the system."""

    executable: str
    args: list[str] = field(default_factory=list)
    working_dir: Path | None = None
    env_override: dict[str, str] = field(default_factory=dict)
    requires_admin: bool = False
    timeout_seconds: int = 600

    @property
    def full_command(self) -> str:
        """The complete command string for logging."""
        parts = [self.executable, *self.args]
        return " ".join(parts)


@dataclass(frozen=True)
class CommandResult:
    """Result of executing a system command."""

    return_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False

    @property
    def success(self) -> bool:
        """Check if the command exited successfully."""
        return self.return_code == 0 and not self.timed_out


@dataclass(frozen=True)
class VerifyCommand:
    """
    A command used to verify software installation.

    Runs the command and checks if the output matches an expected pattern.
    """

    command: str
    expect_pattern: str
    description: str = ""


class ProcessRunner(ABC):
    """
    Abstract interface for executing system commands.

    Provides async execution with output streaming, timeout enforcement,
    and transparent UAC elevation on Windows when admin rights are needed.
    """

    @abstractmethod
    async def run(self, command: Command) -> CommandResult:
        """
        Execute a command and wait for completion.

        If the command requires admin and the current process is not
        elevated, the implementation should handle UAC elevation.

        Args:
            command: Command to execute.

        Returns:
            Command result with exit code, stdout, stderr.
        """

    @abstractmethod
    async def run_streaming(
        self,
        command: Command,
        on_stdout: callable | None = None,
        on_stderr: callable | None = None,
    ) -> CommandResult:
        """
        Execute a command and stream output line-by-line.

        Output lines are passed to callback functions in real-time,
        enabling live log display in the UI.

        Args:
            command: Command to execute.
            on_stdout: Callback for each stdout line.
            on_stderr: Callback for each stderr line.

        Returns:
            Complete command result after execution finishes.
        """

    @abstractmethod
    async def is_admin(self) -> bool:
        """Check if the current process has administrator privileges."""

    @abstractmethod
    async def verify_installation(self, verify_command: VerifyCommand) -> bool:
        """
        Run a verification command and check output against expected pattern.

        Args:
            verify_command: Command and expected output pattern.

        Returns:
            True if the output matches the expected pattern.
        """
