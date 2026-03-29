"""
Section 8.7: Class Definitions - Clython Runtime Test Suite

Tests that Clython actually executes class definitions correctly at runtime.
Uses subprocess-based execution via CLYTHON_BIN.
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


def test_basic_class_definition():
    """Basic class can be defined and instantiated"""
    out, err, rc = clython_run(
        "class MyClass: pass\n"
        "obj = MyClass()\n"
        "print(type(obj).__name__)"
    )
    assert rc == 0
    assert out == "MyClass"


def test_class_with_init():
    """Class with __init__ constructor"""
    out, err, rc = clython_run(
        "class Point:\n"
        "    def __init__(self, x, y):\n"
        "        self.x = x\n"
        "        self.y = y\n"
        "p = Point(3, 4)\n"
        "print(p.x, p.y)"
    )
    assert rc == 0
    assert out == "3 4"


def test_class_instance_method():
    """Class instance method works"""
    out, err, rc = clython_run(
        "class Calc:\n"
        "    def add(self, a, b): return a + b\n"
        "c = Calc()\n"
        "print(c.add(10, 20))"
    )
    assert rc == 0
    assert out == "30"


def test_class_str_method():
    """Class with __str__ method"""
    out, err, rc = clython_run(
        "class Foo:\n"
        "    def __init__(self, val): self.val = val\n"
        "    def __str__(self): return f'Foo({self.val})'\n"
        "print(str(Foo(42)))"
    )
    assert rc == 0
    assert out == "Foo(42)"


def test_class_variable():
    """Class-level variable accessible on instances"""
    out, err, rc = clython_run(
        "class Config:\n"
        "    DEFAULT = 42\n"
        "print(Config.DEFAULT)\n"
        "c = Config()\n"
        "print(c.DEFAULT)"
    )
    assert rc == 0
    assert out == "42\n42"


def test_single_inheritance():
    """Single inheritance: child inherits parent method"""
    out, err, rc = clython_run(
        "class Animal:\n"
        "    def speak(self): return 'Animal'\n"
        "class Dog(Animal):\n"
        "    def speak(self): return 'Woof'\n"
        "d = Dog()\n"
        "print(d.speak())"
    )
    assert rc == 0
    assert out == "Woof"


def test_inheritance_calls_parent():
    """Child class can call inherited method"""
    out, err, rc = clython_run(
        "class Base:\n"
        "    def greet(self): return 'Base'\n"
        "class Child(Base): pass\n"
        "c = Child()\n"
        "print(c.greet())"
    )
    assert rc == 0
    assert out == "Base"


def test_super_call():
    """super() calls parent method"""
    out, err, rc = clython_run(
        "class Base:\n"
        "    def greet(self): return 'Base'\n"
        "class Child(Base):\n"
        "    def greet(self): return super().greet() + '+Child'\n"
        "print(Child().greet())"
    )
    assert rc == 0
    assert out == "Base+Child"


def test_multiple_inheritance():
    """Multiple inheritance with MRO"""
    out, err, rc = clython_run(
        "class A:\n"
        "    def who(self): return 'A'\n"
        "class B(A):\n"
        "    def who(self): return 'B'\n"
        "class C(B, A): pass\n"
        "print(C().who())"
    )
    assert rc == 0
    assert out == "B"


def test_staticmethod():
    """@staticmethod works"""
    out, err, rc = clython_run(
        "class Utils:\n"
        "    @staticmethod\n"
        "    def add(a, b): return a + b\n"
        "print(Utils.add(3, 4))"
    )
    assert rc == 0
    assert out == "7"


def test_classmethod():
    """@classmethod works"""
    out, err, rc = clython_run(
        "class Foo:\n"
        "    @classmethod\n"
        "    def name(cls): return cls.__name__\n"
        "print(Foo.name())"
    )
    assert rc == 0
    assert out == "Foo"


def test_property_getter():
    """@property getter works"""
    out, err, rc = clython_run(
        "class Circle:\n"
        "    def __init__(self, r): self._r = r\n"
        "    @property\n"
        "    def radius(self): return self._r\n"
        "c = Circle(5)\n"
        "print(c.radius)"
    )
    assert rc == 0
    assert out == "5"


def test_property_setter():
    """@property setter works"""
    out, err, rc = clython_run(
        "class MyClass:\n"
        "    def __init__(self): self._x = 0\n"
        "    @property\n"
        "    def x(self): return self._x\n"
        "    @x.setter\n"
        "    def x(self, val): self._x = val\n"
        "obj = MyClass()\n"
        "obj.x = 99\n"
        "print(obj.x)"
    )
    assert rc == 0
    assert out == "99"


def test_class_decorator():
    """Class with a custom decorator"""
    out, err, rc = clython_run(
        "def add_method(cls):\n"
        "    cls.extra = lambda self: 'extra'\n"
        "    return cls\n"
        "@add_method\n"
        "class Foo: pass\n"
        "print(Foo().extra())"
    )
    assert rc == 0
    assert out == "extra"


def test_nested_class():
    """Nested class definition"""
    out, err, rc = clython_run(
        "class Outer:\n"
        "    class Inner:\n"
        "        def val(self): return 42\n"
        "print(Outer.Inner().val())"
    )
    assert rc == 0
    assert out == "42"


def test_class_dunder_repr():
    """Class with __repr__"""
    out, err, rc = clython_run(
        "class Thing:\n"
        "    def __repr__(self): return 'Thing()'\n"
        "print(repr(Thing()))"
    )
    assert rc == 0
    assert out == "Thing()"


def test_class_dunder_len():
    """Class with __len__"""
    out, err, rc = clython_run(
        "class Bag:\n"
        "    def __init__(self): self.items = [1,2,3]\n"
        "    def __len__(self): return len(self.items)\n"
        "print(len(Bag()))"
    )
    assert rc == 0
    assert out == "3"


def test_class_dunder_add():
    """Class with __add__ operator"""
    out, err, rc = clython_run(
        "class Vec:\n"
        "    def __init__(self, x): self.x = x\n"
        "    def __add__(self, other): return Vec(self.x + other.x)\n"
        "v = Vec(3) + Vec(4)\n"
        "print(v.x)"
    )
    assert rc == 0
    assert out == "7"


def test_class_isinstance():
    """isinstance works with class hierarchy"""
    out, err, rc = clython_run(
        "class Base: pass\n"
        "class Child(Base): pass\n"
        "c = Child()\n"
        "print(isinstance(c, Child))\n"
        "print(isinstance(c, Base))"
    )
    assert rc == 0
    assert out == "True\nTrue"


def test_class_many_methods():
    """Class with many methods"""
    methods = "\n".join(f"    def m{i}(self): return {i}" for i in range(10))
    out, err, rc = clython_run(
        f"class Big:\n{methods}\n"
        "b = Big()\n"
        "print(b.m0(), b.m5(), b.m9())"
    )
    assert rc == 0
    assert out == "0 5 9"


@pytest.mark.xfail(reason="dataclasses module not yet supported in Clython")
def test_dataclass_decorator():
    """@dataclass works (requires dataclasses module)"""
    out, err, rc = clython_run(
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class Point:\n"
        "    x: int\n"
        "    y: int\n"
        "p = Point(1, 2)\n"
        "print(p.x, p.y)"
    )
    assert rc == 0
    assert out == "1 2"


def test_class_name_attribute():
    """Class has __name__ attribute"""
    out, err, rc = clython_run(
        "class MySpecialClass: pass\n"
        "print(MySpecialClass.__name__)"
    )
    assert rc == 0
    assert out == "MySpecialClass"


def test_class_init_with_defaults():
    """Class __init__ with default parameters"""
    out, err, rc = clython_run(
        "class Config:\n"
        "    def __init__(self, host='localhost', port=8080):\n"
        "        self.host = host\n"
        "        self.port = port\n"
        "c = Config()\n"
        "print(c.host, c.port)\n"
        "d = Config('example.com', 443)\n"
        "print(d.host, d.port)"
    )
    assert rc == 0
    assert out == "localhost 8080\nexample.com 443"


def test_diamond_inheritance():
    """Diamond inheritance MRO"""
    out, err, rc = clython_run(
        "class Base:\n"
        "    def who(self): return 'Base'\n"
        "class Left(Base):\n"
        "    def who(self): return 'Left'\n"
        "class Right(Base): pass\n"
        "class Diamond(Left, Right): pass\n"
        "print(Diamond().who())"
    )
    assert rc == 0
    assert out == "Left"
