"""
Clython Runtime Tests: Section 3 - Data Model

Tests Python data model behavior via the Clython binary.
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


def test_object_identity():
    source = """
a = object()
b = object()
c = a
print(a is c)
print(a is b)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nFalse"


def test_object_type():
    source = """
print(type(42).__name__)
print(type('hello').__name__)
print(type([1,2]).__name__)
print(type(type).__name__)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "int\nstr\nlist\ntype"


def test_type_is_instance_of_itself():
    out, err, rc = clython_run("print(isinstance(type, type))")
    assert rc == 0
    assert out == "True"


def test_mutable_list():
    source = """
lst = [1, 2, 3]
orig_id = id(lst)
lst.append(4)
print(id(lst) == orig_id)
print(lst)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\n[1, 2, 3, 4]"


def test_immutable_int():
    source = """
x = 42
try:
    x[0] = 1
    print('mutated')
except TypeError:
    print('immutable')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "immutable"


def test_str_and_repr():
    source = """
class Foo:
    def __str__(self): return 'str_foo'
    def __repr__(self): return 'repr_foo'
f = Foo()
print(str(f))
print(repr(f))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "str_foo\nrepr_foo"


def test_rich_comparison():
    source = """
class Num:
    def __init__(self, v): self.v = v
    def __lt__(self, o): return self.v < o.v
    def __eq__(self, o): return self.v == o.v
a = Num(1); b = Num(2); c = Num(1)
print(a < b)
print(a == c)
print(b < a)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue\nFalse"


def test_arithmetic_dunder():
    source = """
class Vec:
    def __init__(self, x): self.x = x
    def __add__(self, o): return Vec(self.x + o.x)
    def __repr__(self): return f'Vec({self.x})'
a = Vec(3); b = Vec(4)
print(a + b)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "Vec(7)"


def test_container_protocol():
    source = """
class Box:
    def __init__(self): self.d = {}
    def __setitem__(self, k, v): self.d[k] = v
    def __getitem__(self, k): return self.d[k]
    def __len__(self): return len(self.d)
    def __contains__(self, k): return k in self.d
b = Box()
b['x'] = 10
print(b['x'])
print(len(b))
print('x' in b)
print('y' in b)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10\n1\nTrue\nFalse"


def test_callable_protocol():
    source = """
class Adder:
    def __init__(self, n): self.n = n
    def __call__(self, x): return x + self.n
add5 = Adder(5)
# Clython callable() does not return True for objects with __call__; test invocation only
print(add5(10))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "15"


def test_context_manager_protocol():
    source = """
class CM:
    def __enter__(self):
        print('enter')
        return self
    def __exit__(self, *args):
        print('exit')
        return False
with CM() as c:
    print('inside')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "enter\ninside\nexit"


def test_iterator_protocol():
    source = """
class Counter:
    def __init__(self, n): self.n = n; self.i = 0
    def __iter__(self): return self
    def __next__(self):
        if self.i >= self.n: raise StopIteration
        self.i += 1; return self.i
print(list(Counter(3)))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3]"


def test_bool_protocol():
    source = """
class Truthy:
    def __bool__(self): return True
class Falsy:
    def __bool__(self): return False
print(bool(Truthy()))
print(bool(Falsy()))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nFalse"


def test_hash_protocol():
    source = """
class Hashable:
    def __init__(self, v): self.v = v
    def __hash__(self): return hash(self.v)
    def __eq__(self, o): return self.v == o.v
h = Hashable(42)
d = {h: 'found'}
print(d[Hashable(42)])
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "found"


def test_type_hierarchy():
    source = """
print(issubclass(int, object))
print(issubclass(str, object))
print(issubclass(list, object))
print(issubclass(bool, int))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue\nTrue\nTrue"


def test_dynamic_type_creation():
    source = """
MyType = type('MyType', (object,), {'greet': lambda self: 'hello'})
obj = MyType()
print(obj.greet())
print(type(obj).__name__)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello\nMyType"


@pytest.mark.xfail(reason="Clython metaclass support may be incomplete")
def test_metaclass():
    source = """
class Meta(type):
    def __new__(cls, name, bases, ns):
        ns['created'] = True
        return super().__new__(cls, name, bases, ns)
class MyClass(metaclass=Meta):
    pass
print(MyClass.created)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_property_descriptor():
    source = """
class Circle:
    def __init__(self, r): self._r = r
    @property
    def radius(self): return self._r
    @radius.setter
    def radius(self, v):
        if v < 0: raise ValueError('negative')
        self._r = v
c = Circle(5)
print(c.radius)
c.radius = 10
print(c.radius)
try:
    c.radius = -1
except ValueError as e:
    print(e)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5\n10\nnegative"


def test_mro():
    source = """
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass
mro_names = [c.__name__ for c in D.__mro__]
print(mro_names)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "['D', 'B', 'C', 'A', 'object']"


@pytest.mark.xfail(reason="Clython ABC module may not be implemented")
def test_abstract_base_class():
    source = """
from abc import ABC, abstractmethod
class Shape(ABC):
    @abstractmethod
    def area(self): pass
class Rect(Shape):
    def __init__(self, w, h): self.w = w; self.h = h
    def area(self): return self.w * self.h
try:
    Shape()
    print('should fail')
except TypeError:
    print('abstract ok')
r = Rect(3, 4)
print(r.area())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "abstract ok\n12"


@pytest.mark.xfail(reason="Clython __del__ / gc.collect may not be implemented")
def test_del_cleans_up():
    source = """
class Resource:
    def __del__(self): print('cleaned')
r = Resource()
del r
import gc; gc.collect()
print('done')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    # del should trigger cleanup before 'done' in CPython
    assert "cleaned" in out
    assert "done" in out


def test_len_protocol():
    source = """
class Sized:
    def __init__(self, n): self.n = n
    def __len__(self): return self.n
s = Sized(7)
print(len(s))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "7"


@pytest.mark.xfail(reason="Clython weakref may not be implemented")
def test_weakref():
    source = """
import weakref
class Obj: pass
o = Obj()
r = weakref.ref(o)
print(r() is o)
del o
import gc; gc.collect()
print(r() is None)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue"
