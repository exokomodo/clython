"""
Clython import system tests — verify module loading, caching, and stdlib access.

Tests run through the Clython binary (CLYTHON_BIN) and verify that the
import system correctly handles built-in modules, pure-Python stdlib modules,
and various import syntaxes.

Coverage:
  - Simple import statements
  - Dotted imports (import os.path)
  - from...import syntax
  - Import aliases (as)
  - Multiple imports in single statement
  - Module caching
  - Import error handling
  - Built-in module access
  - Dynamic import patterns (__import__)
  - Conditional imports
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


# ═══════════════════════════════════════════════════════════════════════════════
# Basic Import Statements
# ═══════════════════════════════════════════════════════════════════════════════


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


class TestImportSimpleModules:
    """Test importing simple built-in modules."""

    def test_import_math(self):
        out, _, rc = clython_run("import math\nprint(type(math).__name__)")
        assert rc == 0 and out == "module"

    def test_import_math_pi(self):
        out, _, rc = clython_run("import math\nprint(math.pi)")
        assert rc == 0 and out == "3.141592653589793"

    def test_import_math_sqrt(self):
        out, _, rc = clython_run("import math\nprint(math.sqrt(16))")
        assert rc == 0 and out == "4.0"

    def test_import_math_floor(self):
        out, _, rc = clython_run("import math\nprint(math.floor(3.7))")
        assert rc == 0 and out == "3"

    def test_import_math_ceil(self):
        out, _, rc = clython_run("import math\nprint(math.ceil(3.2))")
        assert rc == 0 and out == "4"


class TestFromImport:
    """Test from...import syntax."""

    def test_from_sys_import_argv(self):
        out, _, rc = clython_run("from sys import argv\nprint(type(argv).__name__)")
        assert rc == 0 and out == "list"

    def test_from_sys_import_version_info(self):
        out, _, rc = clython_run("from sys import version_info\nprint(version_info[0])")
        assert rc == 0 and out == "3"

    def test_from_math_import_pi(self):
        out, _, rc = clython_run("from math import pi\nprint(pi)")
        assert rc == 0 and out == "3.141592653589793"

    def test_from_math_import_multiple(self):
        out, _, rc = clython_run("from math import pi, sqrt\nprint(sqrt(4))")
        assert rc == 0 and out == "2.0"

    def test_from_import_with_alias(self):
        out, _, rc = clython_run("from math import pi as PI\nprint(PI)")
        assert rc == 0 and out == "3.141592653589793"


class TestDottedImports:
    """Test dotted module import syntax."""

    @pytest.mark.xfail(reason="os module import not yet supported (parse error)")
    def test_import_os_path(self):
        out, _, rc = clython_run("import os.path\nprint(type(os.path).__name__)")
        assert rc == 0 and out == "module"

    @pytest.mark.xfail(reason="os module import not yet supported (parse error)")
    def test_from_os_import_path(self):
        out, _, rc = clython_run("from os import path\nprint(type(path).__name__)")
        assert rc == 0 and out == "module"

    @pytest.mark.xfail(reason="os module import not yet supported (parse error)")
    def test_from_os_path_import_join(self):
        out, _, rc = clython_run("from os.path import join\nprint(type(join).__name__)")
        assert rc == 0 and out == "function"


class TestImportAliases:
    """Test import with alias (as) clause."""

    def test_import_module_as(self):
        out, _, rc = clython_run("import math as m\nprint(m.pi)")
        assert rc == 0 and out == "3.141592653589793"

    def test_from_import_as(self):
        out, _, rc = clython_run("from math import sqrt as square_root\nprint(square_root(9))")
        assert rc == 0 and out == "3.0"

    def test_alias_does_not_bind_original(self):
        """When using 'as', original name should not be bound."""
        _, _, rc = clython_run("import math as m\nprint(math)")
        assert rc != 0


class TestMultipleImports:
    """Test multiple imports in single statement."""

    def test_import_multiple_modules(self):
        out, _, rc = clython_run("import sys, math\nprint(type(sys).__name__, type(math).__name__)")
        assert rc == 0 and out == "module module"

    def test_from_import_multiple_names(self):
        out, _, rc = clython_run("from math import pi, e\nprint(type(pi).__name__, type(e).__name__)")
        assert rc == 0 and out == "float float"


# ═══════════════════════════════════════════════════════════════════════════════
# Stdlib Module Tests
# ═══════════════════════════════════════════════════════════════════════════════


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

    def test_keyword_iskeyword_false(self):
        out, _, rc = clython_run("import keyword\nprint(keyword.iskeyword('hello'))")
        assert rc == 0 and out == "False"

    def test_keyword_kwlist_contains_for(self):
        out, _, rc = clython_run("import keyword\nprint('for' in keyword.kwlist)")
        assert rc == 0 and out == "True"

    @pytest.mark.xfail(reason="json module import not yet supported (parse error)")
    def test_import_json(self):
        out, _, rc = clython_run("import json\nprint(json.dumps({'a': 1}))")
        assert rc == 0 and out == '{"a": 1}'

    @pytest.mark.xfail(reason="collections module import not yet supported (parse error)")
    def test_import_collections(self):
        out, _, rc = clython_run("import collections\nprint(type(collections).__name__)")
        assert rc == 0 and out == "module"

    @pytest.mark.xfail(reason="os module import not yet supported (parse error)")
    def test_import_os(self):
        out, _, rc = clython_run("import os\nprint(type(os).__name__)")
        assert rc == 0 and out == "module"


# ═══════════════════════════════════════════════════════════════════════════════
# sys Module Tests
# ═══════════════════════════════════════════════════════════════════════════════


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

    @pytest.mark.xfail(reason="sys.modules does not track imported modules")
    def test_sys_modules(self):
        out, _, rc = clython_run("import sys\nprint('sys' in sys.modules)")
        assert rc == 0 and out == "True"

    def test_sys_maxsize(self):
        out, _, rc = clython_run("import sys\nprint(type(sys.maxsize).__name__)")
        assert rc == 0 and out == "int"

    @pytest.mark.xfail(reason="sys.executable not yet implemented")
    def test_sys_executable(self):
        out, _, rc = clython_run("import sys\nprint(type(sys.executable).__name__)")
        assert rc == 0 and out == "str"


# ═══════════════════════════════════════════════════════════════════════════════
# Module Caching
# ═══════════════════════════════════════════════════════════════════════════════


class TestModuleCaching:
    """Test that modules are cached after first import."""

    def test_double_import(self):
        """Importing the same module twice should return the same object."""
        out, _, rc = clython_run(
            "import sys\nimport sys\nprint(type(sys).__name__)"
        )
        assert rc == 0 and out == "module"

    def test_import_caching_identity(self):
        """Same module imported twice should be the same object."""
        out, _, rc = clython_run(
            "import sys\nimport sys as s2\nprint(sys is s2)"
        )
        assert rc == 0 and out == "True"

    @pytest.mark.xfail(reason="sys.modules does not track imported modules")
    def test_sys_modules_populated(self):
        """After import, module appears in sys.modules."""
        out, _, rc = clython_run(
            "import math\nimport sys\nprint('math' in sys.modules)"
        )
        assert rc == 0 and out == "True"


# ═══════════════════════════════════════════════════════════════════════════════
# Import Error Conditions
# ═══════════════════════════════════════════════════════════════════════════════


class TestImportErrors:
    """Test import error handling."""

    def test_import_nonexistent_module(self):
        _, err, rc = clython_run("import totally_fake_module_xyz")
        assert rc != 0
        assert "ImportError" in err or "ModuleNotFoundError" in err

    def test_from_import_nonexistent_name(self):
        """Importing a name that doesn't exist in a module."""
        _, err, rc = clython_run("from sys import nonexistent_attr_xyz")
        assert rc != 0

    def test_import_error_doesnt_crash(self):
        """Import error should raise exception, not segfault."""
        out, err, rc = clython_run(
            "try:\n    import fake_module_xyz\nexcept (ImportError, ModuleNotFoundError):\n    print('caught')"
        )
        assert rc == 0 and out == "caught"


# ═══════════════════════════════════════════════════════════════════════════════
# Dynamic Import Patterns
# ═══════════════════════════════════════════════════════════════════════════════


class TestDynamicImports:
    """Test dynamic import patterns."""

    def test_dunder_import(self):
        """__import__ builtin should work."""
        out, _, rc = clython_run("m = __import__('math')\nprint(type(m).__name__)")
        assert rc == 0 and out == "module"

    def test_dunder_import_use(self):
        out, _, rc = clython_run("m = __import__('math')\nprint(m.pi)")
        assert rc == 0 and out == "3.141592653589793"


class TestConditionalImports:
    """Test conditional import patterns."""

    def test_import_in_if(self):
        out, _, rc = clython_run(
            "x = True\nif x:\n    import math\n    print(math.pi)"
        )
        assert rc == 0 and out == "3.141592653589793"

    def test_import_in_try_except(self):
        out, _, rc = clython_run(
            "try:\n    import math\n    print('ok')\nexcept ImportError:\n    print('fail')"
        )
        assert rc == 0 and out == "ok"

    def test_import_in_function(self):
        out, _, rc = clython_run(
            "def f():\n    import math\n    return math.pi\nprint(f())"
        )
        assert rc == 0 and out == "3.141592653589793"


# ═══════════════════════════════════════════════════════════════════════════════
# Built-in Module Access
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuiltinModules:
    """Test accessing built-in modules and their attributes."""

    def test_math_sin(self):
        out, _, rc = clython_run("import math\nprint(math.sin(0))")
        assert rc == 0 and out == "0.0"

    def test_math_cos(self):
        out, _, rc = clython_run("import math\nprint(math.cos(0))")
        assert rc == 0 and out == "1.0"

    def test_math_e(self):
        out, _, rc = clython_run("import math\nprint(type(math.e).__name__)")
        assert rc == 0 and out == "float"

    def test_math_inf(self):
        out, _, rc = clython_run("import math\nprint(math.inf > 1000000)")
        assert rc == 0 and out == "True"

    def test_math_isnan(self):
        out, _, rc = clython_run("import math\nprint(math.isnan(float('nan')))")
        assert rc == 0 and out == "True"

    def test_math_pow(self):
        out, _, rc = clython_run("import math\nprint(math.pow(2, 3))")
        assert rc == 0 and out == "8.0"

    def test_math_abs(self):
        out, _, rc = clython_run("import math\nprint(math.fabs(-3.5))")
        assert rc == 0 and out == "3.5"

    def test_math_log(self):
        out, _, rc = clython_run("import math\nprint(math.log(1))")
        assert rc == 0 and out == "0.0"
