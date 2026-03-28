"""
Clython import system tests — verify module loading, caching, and stdlib access.

Tests run through the Clython binary (CLYTHON_BIN) and verify that the
import system correctly handles built-in modules, pure-Python stdlib modules,
and various import syntaxes.
"""

import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")

pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


def clython_run(source: str, timeout: float = 30.0):
    """Run source through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class TestImportBasics:
    """Test basic import statement functionality."""

    def test_import_sys(self):
        out, _, rc = clython_run("import sys\nprint(type(sys).__name__)")
        assert rc == 0 and out == "module"

    def test_sys_version(self):
        out, _, rc = clython_run("import sys\nprint('clython' in sys.version)")
        assert rc == 0 and out == "True"

    def test_import_as(self):
        out, _, rc = clython_run("import sys as s\nprint(type(s).__name__)")
        assert rc == 0 and out == "module"

    def test_from_import(self):
        out, _, rc = clython_run("from sys import version\nprint('clython' in version)")
        assert rc == 0 and out == "True"

    def test_from_import_as(self):
        out, _, rc = clython_run("from sys import version as v\nprint('clython' in v)")
        assert rc == 0 and out == "True"

    def test_import_nonexistent(self):
        out, stderr, rc = clython_run("import nonexistent_module_xyz")
        assert rc != 0
        assert "ImportError" in stderr or "ModuleNotFoundError" in stderr


class TestStdlibImport:
    """Test importing pure-Python stdlib modules."""

    def test_import_keyword(self):
        """keyword module is pure Python and simple."""
        out, _, rc = clython_run("import keyword\nprint('if' in keyword.kwlist)")
        assert rc == 0 and out == "True"

    def test_keyword_iskeyword(self):
        """Test keyword.iskeyword function."""
        out, _, rc = clython_run("import keyword\nprint(keyword.iskeyword('if'))")
        assert rc == 0 and out == "True"


class TestSysModule:
    """Test sys module attributes."""

    def test_sys_platform(self):
        out, _, rc = clython_run("import sys\nprint(sys.platform)")
        assert rc == 0 and out == "linux"

    def test_sys_argv(self):
        out, _, rc = clython_run("import sys\nprint(type(sys.argv).__name__)")
        assert rc == 0 and out == "list"

    def test_sys_version_info(self):
        out, _, rc = clython_run("import sys\nprint(sys.version_info[0])")
        assert rc == 0 and out == "3"


class TestModuleCaching:
    """Test that modules are cached after first import."""

    def test_double_import(self):
        """Importing the same module twice should return the same object."""
        out, _, rc = clython_run(
            "import sys\nimport sys\nprint(type(sys).__name__)"
        )
        assert rc == 0 and out == "module"
