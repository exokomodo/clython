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


# ── 3.1 Object identity and mutability (from test_section_3_data_model) ──

class TestSection31ObjectIdentityMutability:
    """Object identity, mutability, and is-operator semantics."""

    def test_is_operator_same_object(self):
        out, _, rc = clython_run("a = [1,2]\nb = a\nprint(a is b)")
        assert rc == 0 and out == "True"

    def test_is_operator_different_objects(self):
        out, _, rc = clython_run("a = [1,2]\nb = [1,2]\nprint(a is b)")
        assert rc == 0 and out == "False"

    def test_mutable_list_identity_preserved(self):
        """Mutating a list does not change its identity."""
        out, _, rc = clython_run(
            "x = [1,2,3]\nold = id(x)\nx.append(4)\nprint(id(x) == old)"
        )
        assert rc == 0 and out == "True"

    def test_none_identity(self):
        out, _, rc = clython_run("print(None is None)")
        assert rc == 0 and out == "True"


# ── 3.2 Type hierarchy (from test_section_3_data_model) ──────────────────

class TestSection32TypeHierarchy:
    """Built-in type hierarchy and issubclass relationships."""

    @pytest.mark.xfail(reason="issubclass(int, object) not yet supported")
    def test_int_is_subclass_of_object(self):
        out, _, rc = clython_run("print(issubclass(int, object))")
        assert rc == 0 and out == "True"

    @pytest.mark.xfail(reason="issubclass(bool, int) not yet supported")
    def test_bool_is_subclass_of_int(self):
        out, _, rc = clython_run("print(issubclass(bool, int))")
        assert rc == 0 and out == "True"

    @pytest.mark.xfail(reason="type(type) identity not yet supported")
    def test_type_of_type_is_type(self):
        out, _, rc = clython_run("print(type(type) is type)")
        assert rc == 0 and out == "True"

    @pytest.mark.xfail(reason="type(int) is type not yet supported")
    def test_type_of_int_is_type(self):
        out, _, rc = clython_run("print(type(int) is type)")
        assert rc == 0 and out == "True"

    @pytest.mark.xfail(reason="issubclass(type, object) not yet supported")
    def test_type_is_subclass_of_object(self):
        out, _, rc = clython_run("print(issubclass(type, object))")
        assert rc == 0 and out == "True"

    @pytest.mark.xfail(reason="issubclass for user-defined classes not yet supported")
    def test_user_class_is_subclass_of_object(self):
        out, _, rc = clython_run("class C: pass\nprint(issubclass(C, object))")
        assert rc == 0 and out == "True"

    def test_user_class_isinstance(self):
        out, _, rc = clython_run(
            "class A: pass\nclass B(A): pass\nb = B()\n"
            "print(isinstance(b, A))\nprint(isinstance(b, B))"
        )
        assert rc == 0 and out == "True\nTrue"


# ── 3.3 Additional special methods (from test_section_3_3) ───────────────

class TestSection33ReflectedArithmetic:
    """Reflected (right-hand) arithmetic dunders."""

    @pytest.mark.xfail(reason="reflected arithmetic (__radd__) may not be implemented")
    def test_radd(self):
        out, _, rc = clython_run(
            "class V:\n"
            "    def __init__(self, x): self.x = x\n"
            "    def __radd__(self, other): return V(other + self.x)\n"
            "v = V(5)\nresult = 10 + v\nprint(result.x)"
        )
        assert rc == 0 and out == "15"

    @pytest.mark.xfail(reason="reflected arithmetic (__rmul__) may not be implemented")
    def test_rmul(self):
        out, _, rc = clython_run(
            "class V:\n"
            "    def __init__(self, x): self.x = x\n"
            "    def __rmul__(self, other): return V(other * self.x)\n"
            "v = V(3)\nresult = 4 * v\nprint(result.x)"
        )
        assert rc == 0 and out == "12"


class TestSection33AugmentedAssignment:
    """Augmented assignment (__iadd__, etc.)."""

    @pytest.mark.xfail(reason="augmented assignment (__iadd__) may not be implemented")
    def test_iadd(self):
        out, _, rc = clython_run(
            "class V:\n"
            "    def __init__(self, x): self.x = x\n"
            "    def __iadd__(self, other):\n"
            "        self.x += other.x\n"
            "        return self\n"
            "v = V(1)\nv += V(2)\nprint(v.x)"
        )
        assert rc == 0 and out == "3"


class TestSection33UnaryOperations:
    """Unary operations: __pos__, __abs__, __invert__."""

    def test_pos(self):
        out, _, rc = clython_run(
            "class V:\n"
            "    def __init__(self, x): self.x = x\n"
            "    def __pos__(self): return V(+self.x)\n"
            "v = +V(5)\nprint(v.x)"
        )
        assert rc == 0 and out == "5"

    def test_abs(self):
        out, _, rc = clython_run(
            "class V:\n"
            "    def __init__(self, x): self.x = x\n"
            "    def __abs__(self): return V(abs(self.x))\n"
            "v = abs(V(-5))\nprint(v.x)"
        )
        assert rc == 0 and out == "5"

    def test_invert(self):
        out, _, rc = clython_run(
            "class V:\n"
            "    def __init__(self, x): self.x = x\n"
            "    def __invert__(self): return V(~self.x)\n"
            "v = ~V(5)\nprint(v.x)"
        )
        assert rc == 0 and out == "-6"


class TestSection33MoreComparisons:
    """Additional comparison dunders: __ne__, __le__, __gt__, __ge__."""

    def test_ne(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def __init__(self, v): self.v = v\n"
            "    def __ne__(self, other): return self.v != other.v\n"
            "print(C(1) != C(2))\nprint(C(1) != C(1))"
        )
        assert rc == 0 and out == "True\nFalse"

    def test_le(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def __init__(self, v): self.v = v\n"
            "    def __le__(self, other): return self.v <= other.v\n"
            "print(C(1) <= C(2))\nprint(C(2) <= C(2))\nprint(C(3) <= C(2))"
        )
        assert rc == 0 and out == "True\nTrue\nFalse"

    def test_gt(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def __init__(self, v): self.v = v\n"
            "    def __gt__(self, other): return self.v > other.v\n"
            "print(C(2) > C(1))\nprint(C(1) > C(2))"
        )
        assert rc == 0 and out == "True\nFalse"

    def test_ge(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def __init__(self, v): self.v = v\n"
            "    def __ge__(self, other): return self.v >= other.v\n"
            "print(C(2) >= C(1))\nprint(C(2) >= C(2))\nprint(C(1) >= C(2))"
        )
        assert rc == 0 and out == "True\nTrue\nFalse"


class TestSection33HashProtocol:
    """__hash__ protocol for custom classes."""

    def test_custom_hash(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def __init__(self, v): self.v = v\n"
            "    def __hash__(self): return hash(self.v)\n"
            "print(hash(C(42)) == hash(42))"
        )
        assert rc == 0 and out == "True"


class TestSection33DelitemProtocol:
    """__delitem__ protocol."""

    def test_delitem(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def __init__(self): self.data = {'a': 1, 'b': 2}\n"
            "    def __delitem__(self, key): del self.data[key]\n"
            "c = C()\ndel c['a']\nprint(c.data)"
        )
        assert rc == 0 and out == "{'b': 2}"


class TestSection33ContextManagerProtocol:
    """__enter__/__exit__ context manager protocol."""

    def test_context_manager_basic(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self):\n"
            "        print('enter')\n"
            "        return self\n"
            "    def __exit__(self, et, ev, tb):\n"
            "        print('exit')\n"
            "        return False\n"
            "with CM() as c:\n"
            "    print('body')"
        )
        assert rc == 0 and out == "enter\nbody\nexit"


class TestSection33DescriptorProtocol:
    """Descriptor protocol (__get__, __set__)."""

    @pytest.mark.xfail(reason="descriptor protocol may not be implemented")
    def test_data_descriptor(self):
        out, _, rc = clython_run(
            "class Desc:\n"
            "    def __get__(self, obj, objtype=None):\n"
            "        return obj._val * 2\n"
            "    def __set__(self, obj, value):\n"
            "        obj._val = value\n"
            "class C:\n"
            "    x = Desc()\n"
            "c = C()\nc.x = 5\nprint(c.x)"
        )
        assert rc == 0 and out == "10"


class TestSection33MethodTypes:
    """classmethod and staticmethod."""

    def test_classmethod(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    count = 0\n"
            "    @classmethod\n"
            "    def inc(cls):\n"
            "        cls.count += 1\n"
            "C.inc()\nC.inc()\nprint(C.count)"
        )
        assert rc == 0 and out == "2"

    def test_staticmethod(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    @staticmethod\n"
            "    def add(a, b):\n"
            "        return a + b\n"
            "print(C.add(3, 4))"
        )
        assert rc == 0 and out == "7"


class TestSection33PropertyDecorator:
    """@property decorator."""

    def test_property_getter(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def __init__(self, v):\n"
            "        self._v = v\n"
            "    @property\n"
            "    def v(self):\n"
            "        return self._v\n"
            "c = C(42)\nprint(c.v)"
        )
        assert rc == 0 and out == "42"

    def test_property_setter(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def __init__(self, v):\n"
            "        self._v = v\n"
            "    @property\n"
            "    def v(self):\n"
            "        return self._v\n"
            "    @v.setter\n"
            "    def v(self, val):\n"
            "        self._v = val\n"
            "c = C(1)\nc.v = 42\nprint(c.v)"
        )
        assert rc == 0 and out == "42"


class TestSection3MROAndMultipleInheritance:
    """Method Resolution Order and multiple inheritance."""

    def test_multiple_inheritance_basic(self):
        out, _, rc = clython_run(
            "class A:\n"
            "    def who(self): return 'A'\n"
            "class B(A):\n"
            "    def who(self): return 'B'\n"
            "class C(A):\n"
            "    def who(self): return 'C'\n"
            "class D(B, C):\n"
            "    pass\n"
            "print(D().who())"
        )
        assert rc == 0 and out == "B"

    @pytest.mark.xfail(reason="MRO __mro__ attribute may not be exposed")
    def test_mro_order(self):
        out, _, rc = clython_run(
            "class A: pass\n"
            "class B(A): pass\n"
            "class C(A): pass\n"
            "class D(B, C): pass\n"
            "print([c.__name__ for c in D.__mro__])"
        )
        assert rc == 0 and out == "['D', 'B', 'C', 'A', 'object']"

    def test_super_with_multiple_inheritance(self):
        out, _, rc = clython_run(
            "class A:\n"
            "    def __init__(self):\n"
            "        self.a = 'A'\n"
            "class B(A):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.b = 'B'\n"
            "b = B()\nprint(b.a, b.b)"
        )
        assert rc == 0 and out == "A B"


class TestSection33StrReprFormat:
    """Additional string representation tests."""

    @pytest.mark.xfail(reason="__format__ may not be implemented for custom classes")
    def test_format_dunder(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def __format__(self, spec):\n"
            "        return f'formatted:{spec}'\n"
            "print(format(C(), 'xyz'))"
        )
        assert rc == 0 and out == "formatted:xyz"


class TestSection3DynamicTypeConstruction:
    """Dynamic type creation with type()."""

    @pytest.mark.xfail(reason="three-arg type() may not be implemented")
    def test_type_three_arg(self):
        out, _, rc = clython_run(
            "C = type('C', (object,), {'x': 42})\nprint(C.x)"
        )
        assert rc == 0 and out == "42"


class TestSection33ComprehensiveClass:
    """Test a class implementing many dunders at once."""

    def test_class_with_multiple_dunders(self):
        out, _, rc = clython_run(
            "class Num:\n"
            "    def __init__(self, v): self.v = v\n"
            "    def __repr__(self): return f'Num({self.v})'\n"
            "    def __str__(self): return str(self.v)\n"
            "    def __eq__(self, other): return self.v == other.v\n"
            "    def __add__(self, other): return Num(self.v + other.v)\n"
            "    def __len__(self): return abs(self.v)\n"
            "n = Num(3) + Num(4)\n"
            "print(repr(n))\nprint(str(n))\nprint(len(n))\nprint(n == Num(7))"
        )
        assert rc == 0 and out == "Num(7)\n7\n7\nTrue"


class TestSection33InheritanceSpecialMethods:
    """Inherited special methods should work on subclasses."""

    @pytest.mark.xfail(reason="inherited __str__ not yet dispatched for subclasses")
    def test_inherited_str(self):
        out, _, rc = clython_run(
            "class A:\n"
            "    def __str__(self): return 'A-str'\n"
            "class B(A): pass\n"
            "print(str(B()))"
        )
        assert rc == 0 and out == "A-str"

    def test_overridden_str(self):
        out, _, rc = clython_run(
            "class A:\n"
            "    def __str__(self): return 'A-str'\n"
            "class B(A):\n"
            "    def __str__(self): return 'B-str'\n"
            "print(str(B()))"
        )
        assert rc == 0 and out == "B-str"

    @pytest.mark.xfail(reason="inherited __add__ not yet dispatched for subclasses")
    def test_inherited_add(self):
        out, _, rc = clython_run(
            "class V:\n"
            "    def __init__(self, x): self.x = x\n"
            "    def __add__(self, o): return V(self.x + o.x)\n"
            "class W(V): pass\n"
            "r = W(3) + W(4)\nprint(r.x)"
        )
        assert rc == 0 and out == "7"
