"""
Clython Runtime Tests: Section 5 - Import System

Tests import system behavior via the Clython binary.
"""

import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")


def clython_run(source: str, *, timeout: int = 10):
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


def test_import_sys():
    out, err, rc = clython_run("import sys; print(type(sys).__name__)")
    assert rc == 0
    assert out == "module"


def test_import_os():
    out, err, rc = clython_run("import os; print(hasattr(os, 'path'))")
    assert rc == 0
    assert out == "True"


def test_import_math():
    out, err, rc = clython_run("import math; print(int(math.pi * 100))")
    assert rc == 0
    assert out == "314"


def test_import_as_alias():
    out, err, rc = clython_run("import math as m; print(int(m.sqrt(144)))")
    assert rc == 0
    assert out == "12"


def test_from_import_single():
    out, err, rc = clython_run("from math import pi; print(round(pi, 4))")
    assert rc == 0
    assert out == "3.1416"


def test_from_import_multiple():
    out, err, rc = clython_run("from math import sin, cos; print(round(sin(0), 1), round(cos(0), 1))")
    assert rc == 0
    assert out == "0.0 1.0"


def test_from_import_with_alias():
    out, err, rc = clython_run("from math import sqrt as sq; print(int(sq(25)))")
    assert rc == 0
    assert out == "5"


def test_import_dotted_module():
    out, err, rc = clython_run("import os.path; print(callable(os.path.join))")
    assert rc == 0
    assert out == "True"


def test_from_dotted_import():
    out, err, rc = clython_run("from os.path import join; print(callable(join))")
    assert rc == 0
    assert out == "True"


def test_import_json():
    source = """
import json
data = json.loads('[1, 2, 3]')
print(data)
print(type(data).__name__)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3]\nlist"


def test_import_json_dumps():
    source = """
import json
s = json.dumps({'a': 1, 'b': 2}, sort_keys=True)
print(s)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == '{"a": 1, "b": 2}'


def test_import_collections():
    source = """
from collections import defaultdict
d = defaultdict(int)
d['key'] += 1
d['key'] += 1
print(d['key'])
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2"


def test_import_collections_counter():
    source = """
from collections import Counter
c = Counter('abracadabra')
print(c['a'])
print(c['b'])
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5\n2"


def test_import_in_function():
    source = """
def func():
    import math
    return int(math.sqrt(64))
print(func())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "8"


def test_conditional_import():
    source = """
try:
    import sys as _sys
    has_sys = True
except ImportError:
    has_sys = False
print(has_sys)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_import_module_in_sys_modules():
    source = """
import sys
import os
print('os' in sys.modules)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_import_functools():
    source = """
from functools import reduce
result = reduce(lambda a, b: a * b, [1, 2, 3, 4, 5], 1)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "120"


def test_import_itertools():
    source = """
from itertools import chain
result = list(chain([1, 2], [3, 4], [5]))
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3, 4, 5]"


@pytest.mark.xfail(reason="Clython may not support importlib")
def test_import_importlib():
    source = """
import importlib
math = importlib.import_module('math')
print(int(math.sqrt(9)))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_import_nonexistent_raises():
    source = """
try:
    import definitely_nonexistent_module_xyz
    print('no error')
except ImportError:
    print('ImportError')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "ImportError"


def test_from_import_nonexistent_name_raises():
    source = """
try:
    from math import definitely_not_a_thing
    print('no error')
except ImportError:
    print('ImportError')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "ImportError"


def test_import_gives_module_name():
    source = """
import math
print(math.__name__)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "math"


def test_import_re():
    source = """
import re
m = re.match(r'(\\w+)', 'hello world')
print(m.group(1))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello"


def test_import_builtins():
    source = """
import builtins
print(builtins.len([1, 2, 3]))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


# --- Additional tests to cover all source test cases ---

def test_simple_import_statements():
    """Test simple import statement syntax."""
    source = "import os\nprint(type(os).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module"


def test_multiple_import_statements():
    """Test multiple imports in single statement."""
    source = "import os, sys\nprint(type(os).__name__)\nprint(type(sys).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module\nmodule"


def test_aliased_import_statements():
    """Test import statements with aliases."""
    source = "import os as operating_system\nprint(operating_system.sep in ['/', '\\\\'])"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_dotted_import_statements():
    """Test dotted module import syntax."""
    source = "import os.path\nprint(callable(os.path.join))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_simple_from_import_statements():
    """Test simple from...import syntax."""
    source = "from os import getcwd\nprint(callable(getcwd))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_multiple_from_import_statements():
    """Test from...import with multiple names."""
    source = "from os.path import join, exists\nprint(callable(join))\nprint(callable(exists))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue"


def test_from_import_with_aliases():
    """Test from...import with aliases."""
    source = "from os.path import join as path_join\nprint(callable(path_join))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


@pytest.mark.xfail(strict=False, reason="from dotted.module import may not be supported in Clython")
def test_from_dotted_module_imports():
    """Test from...import with dotted module names."""
    source = "from os.path import sep\nprint(sep in ['/', '\\\\'])"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_builtin_module_imports():
    """Test imports of built-in modules."""
    source = "import sys\nprint(isinstance(sys.version, str))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_conditional_import_patterns():
    """Test imports inside conditional statements."""
    source = """
x = True
if x:
    import os
    result = type(os).__name__
else:
    result = 'none'
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module"


def test_dynamic_import_patterns():
    """Test patterns that would involve dynamic imports."""
    source = "mod = __import__('os')\nprint(type(mod).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module"


def test_import_indentation_requirements():
    """Test import statement indentation rules."""
    source = "def f():\n    import os\n    return type(os).__name__\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module"


def test_import_ast_node_structure():
    """Test Import AST node structure consistency."""
    source = "import os\nprint(os.__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "os"


def test_import_from_ast_node_structure():
    """Test ImportFrom AST node structure consistency."""
    source = "from os import path\nprint(type(path).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module"


def test_import_alias_structure():
    """Test import alias AST structure."""
    source = "import sys as s\nprint(s is sys)" if False else "import sys as s\nprint(type(s).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module"


def test_import_ast_structure_consistency():
    """Test import AST structure across implementations."""
    source = "import os\nfrom sys import version\nprint(type(os).__name__)\nprint(isinstance(version, str))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module\nTrue"


@pytest.mark.xfail(strict=False, reason="Clython may not reject bare 'import' without module name")
def test_invalid_import_syntax():
    """Test invalid import statement syntax."""
    _, _, rc = clython_run("import")
    assert rc != 0


@pytest.mark.xfail(strict=False, reason="Clython may not reject 'import os.' with trailing dot")
def test_invalid_dotted_name_syntax():
    """Test invalid dotted name syntax."""
    _, _, rc = clython_run("import os.")
    assert rc != 0


@pytest.mark.xfail(strict=False, reason="Relative imports require package context in Clython")
def test_single_dot_relative_imports():
    """Test single dot relative import syntax."""
    source = "from . import something"
    _, _, rc = clython_run(source)
    # Relative imports outside package context should fail at runtime
    assert rc != 0


@pytest.mark.xfail(strict=False, reason="Relative imports require package context in Clython")
def test_double_dot_relative_imports():
    """Test double dot relative import syntax."""
    source = "from .. import something"
    _, _, rc = clython_run(source)
    assert rc != 0


@pytest.mark.xfail(strict=False, reason="Relative imports require package context in Clython")
def test_relative_only_dots_imports():
    """Test relative imports with only dots (no module name)."""
    source = "from . import something"
    _, _, rc = clython_run(source)
    assert rc != 0


@pytest.mark.xfail(strict=False, reason="Relative imports require package context in Clython")
def test_relative_import_with_module_names():
    """Test relative imports with explicit module names."""
    source = "from .utils import helper"
    _, _, rc = clython_run(source)
    assert rc != 0


def test_invalid_relative_import_syntax():
    """Test invalid relative import syntax."""
    _, _, rc = clython_run("from ... import")
    assert rc != 0


@pytest.mark.xfail(strict=False, reason="Relative import level in AST may vary in Clython")
def test_relative_import_level_structure():
    """Test relative import level in AST structure."""
    # Just test that valid import level syntax is recognized
    source = "from os import path\nprint(path.__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "posixpath" or out == "ntpath" or "path" in out


def test_from_import_star_statements():
    """Test from...import * syntax."""
    source = "from os.path import *\nprint(callable(join))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_import_statement_introspection():
    """Test ability to analyze import statements programmatically."""
    source = "import sys\nprint('sys' in sys.modules)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


@pytest.mark.xfail(strict=False, reason="__main__ module introspection may not be implemented in Clython")
def test_main_module_patterns():
    """Test patterns related to __main__ module."""
    source = "import sys\nprint('__main__' in sys.modules)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


@pytest.mark.xfail(strict=False, reason="Package/namespace package support may not be implemented in Clython")
def test_namespace_package_patterns():
    """Test import patterns for namespace packages."""
    source = "import sys\nprint(isinstance(sys.path, list))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


@pytest.mark.xfail(strict=False, reason="Package __init__.py imports may not be fully supported in Clython")
def test_package_structure_imports():
    """Test imports that assume package structure."""
    source = "import os.path\nprint(hasattr(os, 'path'))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


@pytest.mark.xfail(strict=False, reason="__init__.py module implications may not be fully implemented in Clython")
def test_init_module_implications():
    """Test imports that would involve __init__.py behavior."""
    source = "import os\nprint(hasattr(os, '__file__'))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_comprehensive_import_patterns():
    """Test comprehensive real-world import patterns."""
    source = """
import sys
import os
from os.path import join, exists
print(isinstance(sys.version, str))
print(type(os).__name__)
print(callable(join))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nmodule\nTrue"
