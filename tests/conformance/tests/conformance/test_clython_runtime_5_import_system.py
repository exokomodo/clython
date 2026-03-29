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


@pytest.mark.xfail(reason="Clython json module may not be implemented")
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


@pytest.mark.xfail(reason="Clython json module may not be implemented")
def test_import_json_dumps():
    source = """
import json
s = json.dumps({'a': 1, 'b': 2}, sort_keys=True)
print(s)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == '{"a": 1, "b": 2}'


@pytest.mark.xfail(reason="Clython collections module may not be implemented")
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


@pytest.mark.xfail(reason="Clython collections module may not be implemented")
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


@pytest.mark.xfail(reason="Clython sys.modules may not track all imported modules")
def test_import_module_in_sys_modules():
    source = """
import sys
import os
print('os' in sys.modules)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


@pytest.mark.xfail(reason="Clython functools module may not be implemented")
def test_import_functools():
    source = """
from functools import reduce
result = reduce(lambda a, b: a * b, [1, 2, 3, 4, 5], 1)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "120"


@pytest.mark.xfail(reason="Clython itertools module may not be implemented")
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


@pytest.mark.xfail(reason="Clython re module may not be implemented")
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
