"""Clython conformance tests — Section 3: Data Model.

Tests that the Clython interpreter correctly implements Python 3.12 data model:
special method names (__init__, __repr__, __str__, __len__, __add__, etc.),
class creation, inheritance, and object protocol.
"""
import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")

def clython_run(source: str, *, timeout: int = 10):
    """Run source through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


# ── 3.1 Objects, values and types ──────────────────────────────────────────

class TestSection31ObjectsValuesTypes:
    def test_identity(self):
        """Every object has an identity (id)."""
        out, _, rc = clython_run("x = 42\nprint(type(id(x)).__name__)")
        assert rc == 0 and out == "int"

    def test_type_of_int(self):
        out, _, rc = clython_run("print(type(42).__name__)")
        assert rc == 0 and out == "int"

    def test_type_of_str(self):
        out, _, rc = clython_run("print(type('hello').__name__)")
        assert rc == 0 and out == "str"

    def test_type_of_list(self):
        out, _, rc = clython_run("print(type([]).__name__)")
        assert rc == 0 and out == "list"

    def test_type_of_dict(self):
        out, _, rc = clython_run("print(type({}).__name__)")
        assert rc == 0 and out == "dict"

    def test_type_of_none(self):
        out, _, rc = clython_run("print(type(None).__name__)")
        assert rc == 0 and out == "NoneType"

    def test_type_of_bool(self):
        out, _, rc = clython_run("print(type(True).__name__)")
        assert rc == 0 and out == "bool"

    def test_isinstance_basic(self):
        out, _, rc = clython_run("print(isinstance(42, int))")
        assert rc == 0 and out == "True"

    def test_isinstance_str(self):
        out, _, rc = clython_run("print(isinstance('hello', str))")
        assert rc == 0 and out == "True"

    def test_isinstance_negative(self):
        out, _, rc = clython_run("print(isinstance(42, str))")
        assert rc == 0 and out == "False"


# ── 3.3 Special method names ──────────────────────────────────────────────

class TestSection33SpecialMethodRepr:
    def test_repr(self):
        out, _, rc = clython_run(
            "class C:\n    def __repr__(self):\n        return 'C()'\nc = C()\nprint(repr(c))"
        )
        assert rc == 0 and out == "C()"

    def test_str(self):
        out, _, rc = clython_run(
            "class C:\n    def __str__(self):\n        return 'hello'\nc = C()\nprint(str(c))"
        )
        assert rc == 0 and out == "hello"

    def test_str_falls_back_to_repr(self):
        out, _, rc = clython_run(
            "class C:\n    def __repr__(self):\n        return 'C-repr'\nc = C()\nprint(str(c))"
        )
        assert rc == 0 and out == "C-repr"

    def test_print_uses_str(self):
        out, _, rc = clython_run(
            "class C:\n    def __str__(self):\n        return 'printed'\n    def __repr__(self):\n        return 'repr'\nc = C()\nprint(c)"
        )
        assert rc == 0 and out == "printed"


class TestSection33SpecialMethodLen:
    def test_len(self):
        out, _, rc = clython_run(
            "class C:\n    def __len__(self):\n        return 5\nc = C()\nprint(len(c))"
        )
        assert rc == 0 and out == "5"

    def test_bool_from_len_zero(self):
        out, _, rc = clython_run(
            "class C:\n    def __len__(self):\n        return 0\nc = C()\nprint(bool(c))"
        )
        assert rc == 0 and out == "False"

    def test_bool_from_len_nonzero(self):
        out, _, rc = clython_run(
            "class C:\n    def __len__(self):\n        return 3\nc = C()\nprint(bool(c))"
        )
        assert rc == 0 and out == "True"


class TestSection33SpecialMethodBool:
    def test_bool_true(self):
        out, _, rc = clython_run(
            "class C:\n    def __bool__(self):\n        return True\nc = C()\nprint(bool(c))"
        )
        assert rc == 0 and out == "True"

    def test_bool_false(self):
        out, _, rc = clython_run(
            "class C:\n    def __bool__(self):\n        return False\nc = C()\nprint(bool(c))"
        )
        assert rc == 0 and out == "False"

    def test_bool_overrides_len(self):
        out, _, rc = clython_run(
            "class C:\n    def __bool__(self):\n        return True\n    def __len__(self):\n        return 0\nc = C()\nprint(bool(c))"
        )
        assert rc == 0 and out == "True"


class TestSection33ArithmeticDunders:
    def test_add(self):
        out, _, rc = clython_run(
            "class V:\n    def __init__(self, x):\n        self.x = x\n    def __add__(self, other):\n        return V(self.x + other.x)\nv = V(1) + V(2)\nprint(v.x)"
        )
        assert rc == 0 and out == "3"

    def test_sub(self):
        out, _, rc = clython_run(
            "class V:\n    def __init__(self, x):\n        self.x = x\n    def __sub__(self, other):\n        return V(self.x - other.x)\nv = V(5) - V(3)\nprint(v.x)"
        )
        assert rc == 0 and out == "2"

    def test_mul(self):
        out, _, rc = clython_run(
            "class V:\n    def __init__(self, x):\n        self.x = x\n    def __mul__(self, other):\n        return V(self.x * other.x)\nv = V(3) * V(4)\nprint(v.x)"
        )
        assert rc == 0 and out == "12"

    def test_neg(self):
        out, _, rc = clython_run(
            "class V:\n    def __init__(self, x):\n        self.x = x\n    def __neg__(self):\n        return V(-self.x)\nv = -V(5)\nprint(v.x)"
        )
        assert rc == 0 and out == "-5"


class TestSection33ComparisonDunders:
    def test_eq(self):
        out, _, rc = clython_run(
            "class C:\n    def __init__(self, v):\n        self.v = v\n    def __eq__(self, other):\n        return self.v == other.v\nprint(C(1) == C(1))\nprint(C(1) == C(2))"
        )
        assert rc == 0 and out == "True\nFalse"

    def test_lt(self):
        out, _, rc = clython_run(
            "class C:\n    def __init__(self, v):\n        self.v = v\n    def __lt__(self, other):\n        return self.v < other.v\nprint(C(1) < C(2))\nprint(C(2) < C(1))"
        )
        assert rc == 0 and out == "True\nFalse"


class TestSection33ContainerDunders:
    def test_getitem(self):
        out, _, rc = clython_run(
            "class C:\n    def __getitem__(self, key):\n        return key * 2\nc = C()\nprint(c[5])"
        )
        assert rc == 0 and out == "10"

    def test_setitem(self):
        out, _, rc = clython_run(
            "class C:\n    def __init__(self):\n        self.data = {}\n    def __setitem__(self, key, val):\n        self.data[key] = val\nc = C()\nc['x'] = 42\nprint(c.data['x'])"
        )
        assert rc == 0 and out == "42"

    def test_contains(self):
        out, _, rc = clython_run(
            "class C:\n    def __contains__(self, item):\n        return item == 'yes'\nc = C()\nprint('yes' in c)\nprint('no' in c)"
        )
        assert rc == 0 and out == "True\nFalse"


class TestSection33IteratorProtocol:
    def test_iter_next(self):
        out, _, rc = clython_run(
            "class Counter:\n    def __init__(self, n):\n        self.n = n\n        self.i = 0\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.i >= self.n:\n            raise StopIteration\n        self.i += 1\n        return self.i\nfor x in Counter(3):\n    print(x)"
        )
        assert rc == 0 and out == "1\n2\n3"


class TestSection33CallableObjects:
    def test_call(self):
        out, _, rc = clython_run(
            "class Adder:\n    def __init__(self, n):\n        self.n = n\n    def __call__(self, x):\n        return self.n + x\na = Adder(10)\nprint(a(5))"
        )
        assert rc == 0 and out == "15"


# ── Inheritance and MRO ───────────────────────────────────────────────────

class TestSection33Inheritance:
    def test_single_inheritance(self):
        out, _, rc = clython_run(
            "class A:\n    def greet(self):\n        return 'hello'\nclass B(A):\n    pass\nprint(B().greet())"
        )
        assert rc == 0 and out == "hello"

    def test_method_override(self):
        out, _, rc = clython_run(
            "class A:\n    def greet(self):\n        return 'A'\nclass B(A):\n    def greet(self):\n        return 'B'\nprint(B().greet())"
        )
        assert rc == 0 and out == "B"

    def test_super_call(self):
        out, _, rc = clython_run(
            "class A:\n    def __init__(self):\n        self.x = 1\nclass B(A):\n    def __init__(self):\n        super().__init__()\n        self.y = 2\nb = B()\nprint(b.x, b.y)"
        )
        assert rc == 0 and out == "1 2"

    def test_isinstance_inheritance(self):
        out, _, rc = clython_run(
            "class A:\n    pass\nclass B(A):\n    pass\nb = B()\nprint(isinstance(b, A))\nprint(isinstance(b, B))"
        )
        assert rc == 0 and out == "True\nTrue"

    def test_class_variables(self):
        out, _, rc = clython_run(
            "class C:\n    count = 0\n    def __init__(self):\n        C.count += 1\nC()\nC()\nprint(C.count)"
        )
        assert rc == 0 and out == "2"


# ── Property-like patterns ────────────────────────────────────────────────

class TestSection33Properties:
    def test_attribute_access(self):
        out, _, rc = clython_run(
            "class C:\n    def __init__(self):\n        self.x = 10\nc = C()\nprint(c.x)\nc.x = 20\nprint(c.x)"
        )
        assert rc == 0 and out == "10\n20"

    def test_dynamic_attribute(self):
        out, _, rc = clython_run(
            "class C:\n    pass\nc = C()\nc.name = 'test'\nprint(c.name)"
        )
        assert rc == 0 and out == "test"

    def test_hasattr_pattern(self):
        """Test attribute existence via try/except."""
        out, _, rc = clython_run(
            "class C:\n    pass\nc = C()\nc.x = 1\ntry:\n    print(c.x)\nexcept AttributeError:\n    print('missing')\ntry:\n    print(c.y)\nexcept AttributeError:\n    print('missing')"
        )
        assert rc == 0 and out == "1\nmissing"
