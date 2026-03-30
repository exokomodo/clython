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


@pytest.mark.xfail(reason="Clython io.StringIO or with statement may not be fully implemented")
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


# --- Additional tests to cover all source test cases ---

def test_minimal_programs():
    """Test minimal program structures."""
    out, err, rc = clython_run("pass")
    assert rc == 0
    assert out == ""


def test_simple_complete_programs():
    """Test simple complete programs."""
    out, err, rc = clython_run("print('hello, world')")
    assert rc == 0
    assert out == "hello, world"


def test_simple_expressions():
    """Test simple expressions at top level."""
    out, err, rc = clython_run("1 + 2\nprint('ok')")
    assert rc == 0
    assert out == "ok"


def test_expression_statements_in_programs():
    """Test expression statements in programs."""
    source = "x = 42\nx\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_module_level_statements():
    """Test module-level statement execution."""
    source = "x = 1\ny = 2\nz = x + y\nprint(z)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_function_definition_patterns():
    """Test function definition at module level."""
    source = "def greet(name):\n    return f'Hello, {name}!'\nprint(greet('World'))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "Hello, World!"


def test_class_definition_patterns():
    """Test class definition at module level."""
    source = "class Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\np = Point(3, 4)\nprint(p.x, p.y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3 4"


def test_import_statement_patterns():
    """Test import statements at module level."""
    source = "import os\nprint(type(os).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module"


def test_import_organization():
    """Test import organization patterns."""
    source = "import sys\nimport os\nprint(isinstance(sys.version, str))\nprint(type(os).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nmodule"


@pytest.mark.xfail(strict=False, reason="Module __doc__ attribute may not be set in Clython")
def test_module_docstrings():
    """Test module docstrings."""
    source = '"""Module docstring."""\nprint(__doc__)'
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "Module docstring."


def test_module_ast_structure():
    """Test module AST structure."""
    source = "x = 1\ndef f(): return x\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1"


def test_nested_definitions():
    """Test nested function/class definitions."""
    source = """
def outer():
    def inner():
        return 42
    return inner()
print(outer())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_main_guard_patterns():
    """Test __name__ == '__main__' pattern."""
    source = "if __name__ == '__main__':\n    print('main')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "main"


def test_complex_expressions():
    """Test complex expressions at top level."""
    source = "result = [x**2 for x in range(5) if x % 2 == 0]\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[0, 4, 16]"


def test_module_initialization_patterns():
    """Test module initialization patterns."""
    source = "CONSTANT = 42\nDEFAULT = 'value'\nprint(CONSTANT)\nprint(DEFAULT)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42\nvalue"


@pytest.mark.xfail(strict=False, reason="Script vs module distinction may differ in Clython")
def test_script_vs_module_patterns():
    """Test script vs module patterns."""
    source = "print(__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "__main__"


def test_program_organization_patterns():
    """Test program organization patterns."""
    source = """
import sys

CONST = 100

def compute(x):
    return x * CONST

class Result:
    def __init__(self, v):
        self.v = v

r = Result(compute(2))
print(r.v)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "200"


def test_program_component_integration():
    """Test program component integration."""
    source = """
def add(a, b): return a + b
def mul(a, b): return a * b
result = mul(add(2, 3), add(1, 4))
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "25"


def test_program_consistency():
    """Test program consistency."""
    source = "x = 5\ny = x * 2\nz = y + x\nprint(z)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "15"


@pytest.mark.xfail(strict=False, reason="dir() at module level may not be implemented in Clython")
def test_program_introspection_capabilities():
    """Test program introspection capabilities."""
    source = "x = 42\nprint('x' in dir())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_comprehensive_program_patterns():
    """Test comprehensive real-world program patterns."""
    source = """
def fibonacci(n):
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

class FibSequence:
    def __init__(self, n):
        self.seq = fibonacci(n)
    def __str__(self):
        return str(self.seq)

fs = FibSequence(8)
print(str(fs))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[0, 1, 1, 2, 3, 5, 8, 13]"
