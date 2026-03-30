"""
Clython Runtime Tests: Section 9 - Top-level Components

Tests complete program execution via the Clython binary.
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


def test_minimal_print():
    out, err, rc = clython_run('print("Hello, World!")')
    assert rc == 0
    assert out == "Hello, World!"


def test_pass_statement():
    out, err, rc = clython_run("pass")
    assert rc == 0
    assert out == ""


def test_module_level_assignment():
    out, err, rc = clython_run("x = 42; print(x)")
    assert rc == 0
    assert out == "42"


def test_module_level_function():
    source = """
def greet(name):
    return f'Hello, {name}!'
print(greet('World'))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "Hello, World!"


def test_module_level_class():
    source = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f'Point({self.x}, {self.y})'
p = Point(3, 4)
print(p)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "Point(3, 4)"


def test_main_guard_pattern():
    source = """
def main():
    print('main called')
    return 0

if __name__ == '__main__':
    main()
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "main called"


def test_imports_and_functions():
    source = """
import math

def hypotenuse(a, b):
    return math.sqrt(a**2 + b**2)

print(hypotenuse(3, 4))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5.0"


def test_module_docstring_does_not_break():
    source = '''"""This is a module docstring."""
print("after docstring")
'''
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "after docstring"


def test_module_level_constants():
    source = """
VERSION = '1.0.0'
MAX_SIZE = 100
print(VERSION)
print(MAX_SIZE)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1.0.0\n100"


def test_nested_class_and_function():
    source = """
class Outer:
    class Inner:
        def method(self):
            return 'inner method'
    
    def create_inner(self):
        return self.Inner()

o = Outer()
i = o.create_inner()
print(i.method())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "inner method"


def test_conditional_module_level():
    source = """
DEBUG = False
if DEBUG:
    print('debug mode')
else:
    print('release mode')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "release mode"


def test_for_loop_at_module_level():
    source = """
total = 0
for i in range(5):
    total += i
print(total)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_try_except_at_module_level():
    source = """
try:
    x = int('not a number')
except ValueError:
    x = -1
print(x)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "-1"


def test_class_with_class_method():
    source = """
class Factory:
    _instances = []
    
    @classmethod
    def create(cls):
        obj = cls()
        cls._instances.append(obj)
        return obj
    
    @classmethod
    def count(cls):
        return len(cls._instances)

Factory.create()
Factory.create()
print(Factory.count())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2"


def test_comprehension_at_module_level():
    source = """
squares = [x**2 for x in range(6)]
print(squares)
evens = {x for x in range(10) if x % 2 == 0}
print(sorted(evens))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[0, 1, 4, 9, 16, 25]\n[0, 2, 4, 6, 8]"


def test_generator_at_module_level():
    source = """
gen = (x * 2 for x in range(4))
print(list(gen))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[0, 2, 4, 6]"


def test_multiple_functions_calling_each_other():
    source = """
def add(a, b): return a + b
def multiply(a, b): return a * b
def combined(a, b, c): return add(multiply(a, b), c)
print(combined(2, 3, 4))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_class_inheritance():
    source = """
class Animal:
    def __init__(self, name): self.name = name
    def speak(self): return '...'

class Dog(Animal):
    def speak(self): return 'Woof'

class Cat(Animal):
    def speak(self): return 'Meow'

animals = [Dog('Rex'), Cat('Whiskers')]
for a in animals:
    print(f'{a.name}: {a.speak()}')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "Rex: Woof\nWhiskers: Meow"


def test_exception_handling_program():
    source = """
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None

print(safe_divide(10, 2))
print(safe_divide(10, 0))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5.0\nNone"


def test_async_function_at_module_level():
    source = """
import asyncio

async def main():
    print('async main')
    return 42

result = asyncio.run(main())
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "async main\n42"


def test_with_statement_at_module_level():
    source = """
import io
buf = io.StringIO()
with buf:
    buf.write('hello')
    val = buf.getvalue()
print(val)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello"


def test_data_driven_program():
    source = """
data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
unique_sorted = sorted(set(data))
total = sum(data)
print(unique_sorted)
print(total)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3, 4, 5, 6, 9]\n39"


def test_recursive_function():
    source = """
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
print([fib(i) for i in range(8)])
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[0, 1, 1, 2, 3, 5, 8, 13]"
