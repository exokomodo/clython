"""
Pytest configuration for Python Language Reference Conformance Test Suite.

When CLYTHON_BIN is set, routes all execution through the Clython interpreter
instead of CPython. This is the mechanism for testing Clython conformance.
"""

import os
import subprocess
import sys
import pytest


CLYTHON_BIN = os.environ.get("CLYTHON_BIN")


class ClythonRunner:
    """Execute Python source through the Clython CLI."""

    def __init__(self, bin_path: str):
        self.bin_path = bin_path

    def run(self, source: str, timeout: float = 30.0):
        """Run source through Clython, return (stdout, stderr, returncode)."""
        result = subprocess.run(
            [self.bin_path, "-c", source],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr, result.returncode

    def parse(self, source: str, timeout: float = 30.0):
        """Parse-only through Clython, return (stdout, stderr, returncode)."""
        result = subprocess.run(
            [self.bin_path, "--parse-only", "-c", source],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr, result.returncode

    def eval(self, source: str, timeout: float = 30.0):
        """Evaluate an expression and return its string representation."""
        stdout, stderr, rc = self.run(source, timeout)
        if rc != 0:
            raise RuntimeError(f"Clython eval failed (rc={rc}): {stderr}")
        return stdout.strip()


@pytest.fixture(scope="session")
def clython():
    """Provide a ClythonRunner if CLYTHON_BIN is set, else None."""
    if CLYTHON_BIN:
        return ClythonRunner(CLYTHON_BIN)
    return None





def pytest_runtest_setup(item):
    """Automatically skip tests based on version markers."""
    for marker in item.iter_markers():
        if marker.name.startswith("min_version_"):
            version_str = marker.name.replace("min_version_", "")
            if "_" in version_str:
                version_parts = version_str.split("_")
                required_version = tuple(int(part) for part in version_parts)
            else:
                required_version = (int(version_str),)

            if sys.version_info < required_version:
                pytest.skip(f"Requires Python {'.'.join(map(str, required_version))}+")

        elif marker.name == "feature_match" and sys.version_info < (3, 10):
            pytest.skip("Match statements require Python 3.10+")
        elif marker.name == "feature_walrus" and sys.version_info < (3, 8):
            pytest.skip("Walrus operator requires Python 3.8+")
        elif marker.name == "feature_fstrings" and sys.version_info < (3, 6):
            pytest.skip("F-strings require Python 3.6+")
        elif marker.name == "cpython_only" and not hasattr(sys, "_getframe"):
            pytest.skip("CPython-specific test")
        elif marker.name == "pypy_skip" and hasattr(sys, "pypy_version_info"):
            pytest.skip("Known PyPy compatibility issue")
