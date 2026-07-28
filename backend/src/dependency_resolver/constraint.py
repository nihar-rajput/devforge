"""
Version constraint parser and matcher.
"""

from __future__ import annotations

import re
from typing import List

from src.core.value_objects.version import Version


class VersionConstraint:
    """
    Parses and checks version constraints (e.g., ">=3.10.0", "~=2.0.0", "<4.0.0").
    """

    def __init__(self, raw_constraint: str | None) -> None:
        self.raw_constraint = raw_constraint
        self._parsed_rules: List[tuple[str, Version]] = []
        if raw_constraint:
            self._parse(raw_constraint)

    def _parse(self, constraint_str: str) -> None:
        parts = [p.strip() for p in constraint_str.split(",") if p.strip()]
        for part in parts:
            match = re.match(r"^(>=|<=|>|<|==|!=|~=)\s*(.+)$", part)
            if not match:
                # Default to == if no operator supplied
                op = "=="
                ver_str = part
            else:
                op, ver_str = match.group(1), match.group(2)

            ver = Version.parse(ver_str)
            self._parsed_rules.append((op, ver))

    def is_satisfied_by(self, version: Version) -> bool:
        """Check if a Version object satisfies all parsed rules in this constraint."""
        if not self._parsed_rules:
            return True

        for op, target in self._parsed_rules:
            if op == ">=":
                if not (version >= target):
                    return False
            elif op == "<=":
                if not (version <= target):
                    return False
            elif op == ">":
                if not (version > target):
                    return False
            elif op == "<":
                if not (version < target):
                    return False
            elif op == "==":
                if not (version == target):
                    return False
            elif op == "!=":
                if not (version != target):
                    return False
            elif op == "~=":
                upper = Version(major=target.major, minor=target.minor + 1, patch=0)
                if not (version >= target and version < upper):
                    return False

        return True
