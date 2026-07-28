"""
Health report entity.

Represents the result of running health checks on a package installation.
The health score is computed from individual check results weighted by importance.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from src.core.enums import HealthStatus
from src.core.value_objects.package_id import PackageId


class HealthCheck(BaseModel):
    """
    A single health check performed on a package installation.

    Each check tests one aspect of the installation health
    (binary exists, correct version, PATH configured, etc.).
    """

    name: str = Field(..., description="Check name (e.g., 'binary_exists', 'version_match').")
    description: str = Field(..., description="What this check verifies.")
    passed: bool = Field(..., description="Whether the check passed.")
    weight: int = Field(
        default=25,
        ge=0,
        le=100,
        description="Weight of this check in the overall score (0-100).",
    )
    details: str | None = Field(
        default=None,
        description="Details about the result (e.g., 'Found Python 3.12.1 at C:\\...').",
    )
    remediation: str | None = Field(
        default=None,
        description="Suggested fix if the check failed.",
    )


class HealthReport(BaseModel):
    """
    Aggregate health report for a package installation.

    Composed of individual HealthCheck results, each weighted by
    importance. The overall score is a weighted average.

    Score interpretation:
        - 80-100: HEALTHY — everything works
        - 40-79:  DEGRADED — some issues, package may partially work
        - 0-39:   UNHEALTHY — critical failures, needs repair
        - -1:     UNKNOWN — not yet assessed

    Standard checks and their weights:
        - binary_exists (25): Main executable is present
        - version_match (25): Installed version matches expected
        - path_configured (20): PATH entries are correct
        - deps_satisfied (20): All dependencies installed
        - recent_verify (10): Last verification was recent
    """

    package_id: PackageId = Field(..., description="Package this report is for.")
    checks: list[HealthCheck] = Field(
        default_factory=list, description="Individual check results."
    )
    overall_score: int = Field(
        default=-1,
        ge=-1,
        le=100,
        description="Weighted aggregate score (0-100, or -1 if not assessed).",
    )
    status: HealthStatus = Field(
        default=HealthStatus.UNKNOWN,
        description="Overall health status category.",
    )
    assessed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this assessment was performed.",
    )
    error: str | None = Field(
        default=None,
        description="Error message if the health check itself failed to run.",
    )

    def compute_score(self) -> None:
        """
        Calculate the overall score from individual check results.

        Uses weighted average where each check contributes its weight
        to the total score if passed, and 0 if failed.
        """
        if not self.checks:
            self.overall_score = -1
            self.status = HealthStatus.UNKNOWN
            return

        total_weight = sum(check.weight for check in self.checks)
        if total_weight == 0:
            self.overall_score = 0
            self.status = HealthStatus.UNHEALTHY
            return

        earned = sum(check.weight for check in self.checks if check.passed)
        self.overall_score = int((earned / total_weight) * 100)

        if self.overall_score >= 80:
            self.status = HealthStatus.HEALTHY
        elif self.overall_score >= 40:
            self.status = HealthStatus.DEGRADED
        else:
            self.status = HealthStatus.UNHEALTHY

    @property
    def failed_checks(self) -> list[HealthCheck]:
        """Get all checks that failed."""
        return [check for check in self.checks if not check.passed]

    @property
    def passed_checks(self) -> list[HealthCheck]:
        """Get all checks that passed."""
        return [check for check in self.checks if check.passed]

    def add_check(
        self,
        name: str,
        description: str,
        passed: bool,
        weight: int = 25,
        details: str | None = None,
        remediation: str | None = None,
    ) -> None:
        """Add a health check result and recompute the score."""
        self.checks.append(
            HealthCheck(
                name=name,
                description=description,
                passed=passed,
                weight=weight,
                details=details,
                remediation=remediation,
            )
        )
        self.compute_score()
