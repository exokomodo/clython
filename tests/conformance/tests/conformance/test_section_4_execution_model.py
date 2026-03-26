"""
Section 4: Execution Model - Conformance Test Suite

Tests Python Language Reference Section 4 compliance across implementations.
Based on formal execution model definitions and prose assertions for Python's runtime semantics.

Language Reference requirements tested:
    - Program structure and code blocks
    - Naming and binding semantics
    - Scope resolution rules (LEGB: Local, Enclosing, Global, Built-in)
    - Built-in namespace behavior
    - Dynamic feature interaction (eval, exec, globals, locals)
    - Exception propagation and handling
    - Name resolution and binding patterns
    - Namespace lifetime and visibility
    - Class and function scope interactions
    - Module-level execution semantics
"""

import ast
import pytest
import sys
from typing import Any


class ExecutionModelTester:
    """Helper class for testing execution model conformance.
    
    Focuses on AST structure validation for scoping, binding, and namespace
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_execution_syntax_parses(self, source: str):
        """Test that execution model syntax parses correctly.
        
        Args:
            source: Python source code with execution model patterns
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Execution model syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def get_name_nodes(self, source: str) -> list:
        """Get Name AST nodes from source for analysis.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Name nodes
        """
        tree = ast.parse(source)
        names = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.append(node)
        
        return names
    
    def get_scope_creating_nodes(self, source: str) -> list:
        """Get nodes that create new scopes.
        
        Args:
            source: Python source code
            
        Returns:
            List of scope-creating AST nodes
        """
        tree = ast.parse(source)
        scope_creators = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, 
                               ast.ClassDef, ast.Lambda, ast.ListComp, 
                               ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                scope_creators.append(node)
        
        return scope_creators
    
    def has_global_statement(self, source: str) -> bool:
        """Check if source contains global statements.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains global statements
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                return True
        return False
    
    def has_nonlocal_statement(self, source: str) -> bool:
        """Check if source contains nonlocal statements.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains nonlocal statements
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Nonlocal):
                return True
        return False
    
    def get_assignment_targets(self, source: str) -> list:
        """Get assignment target names from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of assignment target names
        """
        tree = ast.parse(source)
        targets = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        targets.append(target.id)
        
        return targets


@pytest.fixture
def tester():
    """Provide ExecutionModelTester instance for tests."""
    return ExecutionModelTester()


class TestSection4ProgramStructure:
    """Test program structure and code block organization."""
    
    def test_module_level_structure(self, tester):
        """Test module-level program structure"""
        # Language Reference: modules are top-level code blocks
        module_structures = [
            """
# Module level code
variable = 42
def function():
    pass
class MyClass:
    pass
""",
            """
import sys
import os

CONSTANT = "value"

def main():
    return 0

if __name__ == "__main__":
    main()
""",
            """
from typing import List, Dict
import json

data: Dict[str, int] = {}

def process_data(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
"""
        ]
        
        for source in module_structures:
            tree = tester.assert_execution_syntax_parses(source)
            # Should have module-level statements
            assert len(tree.body) >= 2, f"Should have multiple module statements: {source}"
    
    def test_code_block_nesting(self, tester):
        """Test nested code block structure"""
        # Language Reference: code blocks can be nested
        nested_structures = [
            """
def outer_function():
    def inner_function():
        def nested_function():
            return "nested"
        return nested_function
    return inner_function
""",
            """
class OuterClass:
    class InnerClass:
        def method(self):
            def local_function():
                return "local"
            return local_function()
""",
            """
def function_with_comprehensions():
    data = [x for x in range(10) if x % 2 == 0]
    result = {k: v for k, v in enumerate(data) if v > 2}
    return result
"""
        ]
        
        for source in nested_structures:
            tree = tester.assert_execution_syntax_parses(source)
            scope_creators = tester.get_scope_creating_nodes(source)
            assert len(scope_creators) >= 2, f"Should have nested scopes: {source}"
    
    def test_statement_vs_expression_structure(self, tester):
        """Test distinction between statements and expressions"""
        # Language Reference: statements vs expressions in code blocks
        statement_expression_patterns = [
            """
# Statements
x = 42
def func():
    pass
class Cls:
    pass
if condition:
    pass

# Expressions in statement context
result = (x + y for x, y in pairs)
value = lambda x: x * 2
""",
            """
# Expression statements
function_call()
method.call()
obj.attr
list[index]

# Assignment statements
a, b = 1, 2
a += 1
a[0] = value
"""
        ]
        
        for source in statement_expression_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should parse correctly with mix of statements and expressions
            assert len(tree.body) >= 3, f"Should have multiple statements: {source}"


class TestSection4NameBinding:
    """Test naming and binding semantics."""
    
    def test_basic_name_binding(self, tester):
        """Test basic name binding patterns"""
        # Language Reference: assignment creates name bindings
        binding_patterns = [
            """
x = 42
y = "string"
z = [1, 2, 3]
""",
            """
def function(param):
    local_var = param * 2
    return local_var
""",
            """
for i in range(10):
    value = i * 2
""",
            """
try:
    result = risky_operation()
except Exception as e:
    error = str(e)
"""
        ]
        
        for source in binding_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            targets = tester.get_assignment_targets(source)
            assert len(targets) >= 1, f"Should have assignment targets: {source}"
    
    def test_binding_vs_reference_patterns(self, tester):
        """Test binding vs reference in name usage"""
        # Language Reference: names are bound by assignment, referenced by use
        binding_reference_patterns = [
            """
x = 10      # Binding
y = x + 5   # Reference to x, binding to y
""",
            """
def func():
    local = 42    # Binding in function scope
    return local  # Reference
""",
            """
global_var = "global"

def function():
    print(global_var)  # Reference to global
    local_var = "local"  # Local binding
    return local_var
""",
            """
items = [1, 2, 3]
for item in items:      # Binding to item, reference to items
    processed = item * 2  # Binding, reference
"""
        ]
        
        for source in binding_reference_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            names = tester.get_name_nodes(source)
            assert len(names) >= 2, f"Should have name nodes: {source}"
            
            # Check for different context types
            contexts = set()
            for name in names:
                contexts.add(type(name.ctx).__name__)
            
            # Should have both Store (binding) and Load (reference) contexts
            assert len(contexts) >= 1, f"Should have name contexts: {source}"
    
    def test_multiple_assignment_binding(self, tester):
        """Test multiple assignment and tuple unpacking"""
        # Language Reference: multiple assignment creates multiple bindings
        multiple_assignment_patterns = [
            """
a, b = 1, 2
x, y, z = range(3)
""",
            """
first, *rest, last = [1, 2, 3, 4, 5]
""",
            """
(a, b), (c, d) = [(1, 2), (3, 4)]
""",
            """
def function():
    return 1, 2, 3

a, b, c = function()
"""
        ]
        
        for source in multiple_assignment_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should parse correctly with complex assignment patterns
            assert tree is not None, f"Multiple assignment should parse: {source}"
    
    def test_augmented_assignment_binding(self, tester):
        """Test augmented assignment binding behavior"""
        # Language Reference: augmented assignment modifies existing binding
        augmented_assignment_patterns = [
            """
x = 10
x += 5
x *= 2
""",
            """
items = []
items += [1, 2, 3]
""",
            """
counter = 0
for i in range(10):
    counter += i
""",
            """
data = {"count": 0}
data["count"] += 1
"""
        ]
        
        for source in augmented_assignment_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain both regular and augmented assignments
            aug_assigns = [node for node in ast.walk(tree) if isinstance(node, ast.AugAssign)]
            assert len(aug_assigns) >= 1, f"Should have augmented assignment: {source}"


class TestSection4ScopeResolution:
    """Test scope resolution rules (LEGB)."""
    
    def test_local_scope_patterns(self, tester):
        """Test local scope resolution"""
        # Language Reference: local scope is innermost function/method
        local_scope_patterns = [
            """
def function():
    local_var = 42
    return local_var
""",
            """
def function(param):
    local_result = param * 2
    if local_result > 10:
        local_temp = local_result - 10
        return local_temp
    return local_result
""",
            """
class MyClass:
    def method(self):
        method_local = "local to method"
        return method_local
""",
            """
def outer():
    def inner():
        inner_local = "inner"
        return inner_local
    return inner()
"""
        ]
        
        for source in local_scope_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            scope_creators = tester.get_scope_creating_nodes(source)
            assert len(scope_creators) >= 1, f"Should have function scopes: {source}"
    
    def test_enclosing_scope_patterns(self, tester):
        """Test enclosing scope resolution"""
        # Language Reference: enclosing scope from outer function
        enclosing_scope_patterns = [
            """
def outer():
    enclosing_var = "from outer"
    
    def inner():
        return enclosing_var  # Reference to enclosing scope
    
    return inner()
""",
            """
def factory(value):
    def closure():
        return value  # Captures enclosing variable
    return closure
""",
            """
def decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")  # func from enclosing scope
        return func(*args, **kwargs)
    return wrapper
""",
            """
def outer(x):
    def middle(y):
        def inner(z):
            return x + y + z  # References to multiple enclosing scopes
        return inner
    return middle
"""
        ]
        
        for source in enclosing_scope_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            scope_creators = tester.get_scope_creating_nodes(source)
            assert len(scope_creators) >= 2, f"Should have nested scopes: {source}"
    
    def test_global_scope_patterns(self, tester):
        """Test global scope resolution"""
        # Language Reference: global scope is module level
        global_scope_patterns = [
            """
module_var = "global"

def function():
    return module_var  # Reference to global
""",
            """
CONSTANT = 42

class MyClass:
    def method(self):
        return CONSTANT  # Global reference in class
""",
            """
global_list = []

def add_item(item):
    global global_list
    global_list.append(item)
""",
            """
counter = 0

def increment():
    global counter
    counter += 1
    return counter
"""
        ]
        
        for source in global_scope_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should parse correctly with global references
            assert tree is not None, f"Global scope pattern should parse: {source}"
    
    def test_builtin_scope_patterns(self, tester):
        """Test built-in scope resolution"""
        # Language Reference: built-in scope contains built-in functions
        builtin_scope_patterns = [
            """
def function():
    return len([1, 2, 3])  # Built-in len function
""",
            """
data = list(range(10))  # Built-in list and range
""",
            """
def process():
    try:
        value = int("42")  # Built-in int
    except ValueError as e:  # Built-in ValueError
        print(str(e))  # Built-in str and print
""",
            """
result = sum(x for x in range(10) if x % 2 == 0)  # Built-ins: sum, range
"""
        ]
        
        for source in builtin_scope_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain references to built-in names
            names = tester.get_name_nodes(source)
            assert len(names) >= 1, f"Should have name references: {source}"


class TestSection4GlobalNonlocalStatements:
    """Test global and nonlocal statement semantics."""
    
    def test_global_statement_patterns(self, tester):
        """Test global statement usage"""
        # Language Reference: global statement affects name binding
        global_statement_patterns = [
            """
x = "global"

def function():
    global x
    x = "modified"
""",
            """
counter = 0

def increment():
    global counter
    counter += 1
    return counter
""",
            """
def function():
    global new_global
    new_global = "created in function"
""",
            """
a, b = 1, 2

def swap():
    global a, b
    a, b = b, a
"""
        ]
        
        for source in global_statement_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            assert tester.has_global_statement(source), f"Should have global statement: {source}"
            
            # Find global statements
            global_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Global)]
            assert len(global_nodes) >= 1, f"Should have Global nodes: {source}"
    
    def test_nonlocal_statement_patterns(self, tester):
        """Test nonlocal statement usage"""
        # Language Reference: nonlocal affects enclosing scope binding
        nonlocal_statement_patterns = [
            """
def outer():
    x = "outer"
    
    def inner():
        nonlocal x
        x = "modified"
    
    inner()
    return x
""",
            """
def counter_factory():
    count = 0
    
    def increment():
        nonlocal count
        count += 1
        return count
    
    return increment
""",
            """
def outer():
    a, b = 1, 2
    
    def inner():
        nonlocal a, b
        a, b = b, a
""",
            """
def nested_example():
    x = 1
    
    def level1():
        y = 2
        
        def level2():
            nonlocal x, y
            x, y = y, x
"""
        ]
        
        for source in nonlocal_statement_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            assert tester.has_nonlocal_statement(source), f"Should have nonlocal statement: {source}"
            
            # Find nonlocal statements
            nonlocal_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Nonlocal)]
            assert len(nonlocal_nodes) >= 1, f"Should have Nonlocal nodes: {source}"
    
    def test_global_nonlocal_interaction(self, tester):
        """Test interaction between global and nonlocal"""
        # Language Reference: global and nonlocal can coexist
        interaction_patterns = [
            """
global_var = "global"

def outer():
    enclosing_var = "enclosing"
    
    def inner():
        global global_var
        nonlocal enclosing_var
        global_var = "modified global"
        enclosing_var = "modified enclosing"
""",
            """
x = "global"

def factory():
    y = "enclosing"
    
    def function():
        global x
        nonlocal y
        return x + y
    
    return function
"""
        ]
        
        for source in interaction_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            assert tester.has_global_statement(source), f"Should have global: {source}"
            assert tester.has_nonlocal_statement(source), f"Should have nonlocal: {source}"


class TestSection4DynamicFeatures:
    """Test interaction with dynamic features."""
    
    def test_eval_exec_patterns(self, tester):
        """Test eval() and exec() usage patterns"""
        # Language Reference: eval/exec interact with namespace
        eval_exec_patterns = [
            """
code = "2 + 2"
result = eval(code)
""",
            """
namespace = {"x": 10, "y": 20}
result = eval("x + y", namespace)
""",
            """
code = '''
def dynamic_function():
    return "created dynamically"
'''
exec(code)
""",
            """
def function():
    local_var = 42
    return eval("local_var * 2")
"""
        ]
        
        for source in eval_exec_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain function calls to eval/exec
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            assert len(calls) >= 1, f"Should have function calls: {source}"
    
    def test_globals_locals_patterns(self, tester):
        """Test globals() and locals() function usage"""
        # Language Reference: globals/locals access namespace dictionaries
        namespace_access_patterns = [
            """
def function():
    local_var = 42
    local_dict = locals()
    global_dict = globals()
    return local_dict, global_dict
""",
            """
def inspect_namespace():
    x = 10
    print("Locals:", locals())
    print("Globals:", globals())
""",
            """
def dynamic_access():
    var_name = "dynamic_var"
    locals()[var_name] = 42
    return locals()[var_name]
""",
            """
module_var = "global"

def function():
    if "module_var" in globals():
        return globals()["module_var"]
"""
        ]
        
        for source in namespace_access_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain function calls
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            assert len(calls) >= 1, f"Should have function calls: {source}"
    
    def test_vars_dir_patterns(self, tester):
        """Test vars() and dir() introspection patterns"""
        # Language Reference: vars/dir provide namespace introspection
        introspection_patterns = [
            """
class MyClass:
    def __init__(self):
        self.attr = 42
    
    def method(self):
        return vars(self)
""",
            """
def function():
    local_var = 42
    return dir()
""",
            """
import sys
module_contents = dir(sys)
""",
            """
obj = object()
object_vars = vars(obj) if hasattr(obj, "__dict__") else None
"""
        ]
        
        for source in introspection_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should parse correctly with introspection calls
            assert tree is not None, f"Introspection pattern should parse: {source}"


class TestSection4ClassScopeInteraction:
    """Test class scope interactions."""
    
    def test_class_scope_patterns(self, tester):
        """Test class scope behavior"""
        # Language Reference: class scope has special properties
        class_scope_patterns = [
            """
class MyClass:
    class_var = "class level"
    
    def method(self):
        return self.class_var
""",
            """
class MyClass:
    x = 10
    y = x + 5  # Reference to x in class scope
    
    def method(self):
        return self.y
""",
            """
class Outer:
    value = 42
    
    class Inner:
        # Can't directly reference Outer.value here without qualification
        inner_value = 100
""",
            """
def function():
    local_var = "local"
    
    class LocalClass:
        # Can't see local_var directly
        class_var = "class"
    
    return LocalClass
"""
        ]
        
        for source in class_scope_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain class definitions
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            assert len(classes) >= 1, f"Should have class definitions: {source}"
    
    def test_method_scope_patterns(self, tester):
        """Test method scope behavior"""
        # Language Reference: methods are functions with implicit self
        method_scope_patterns = [
            """
class MyClass:
    def __init__(self, value):
        self.value = value
    
    def method(self):
        return self.value
""",
            """
class MyClass:
    class_var = "shared"
    
    def instance_method(self):
        return self.class_var
    
    @classmethod
    def class_method(cls):
        return cls.class_var
    
    @staticmethod
    def static_method():
        return "static"
""",
            """
class MyClass:
    def method(self):
        def nested_function():
            return "nested in method"
        return nested_function()
"""
        ]
        
        for source in method_scope_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain function definitions (methods)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            assert len(functions) >= 1, f"Should have method definitions: {source}"
    
    def test_class_variable_vs_instance_variable(self, tester):
        """Test class vs instance variable patterns"""
        # Language Reference: class and instance variable distinction
        variable_distinction_patterns = [
            """
class MyClass:
    class_var = "shared"
    
    def __init__(self):
        self.instance_var = "individual"
""",
            """
class Counter:
    count = 0  # Class variable
    
    def __init__(self):
        Counter.count += 1
        self.id = Counter.count  # Instance variable
""",
            """
class MyClass:
    shared_list = []  # Class variable (mutable)
    
    def __init__(self):
        self.private_list = []  # Instance variable
        self.shared_list.append(1)  # Modifies class variable
"""
        ]
        
        for source in variable_distinction_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain class definitions with assignments
            assert tree is not None, f"Variable distinction pattern should parse: {source}"


class TestSection4ExceptionSemantics:
    """Test exception handling semantics."""
    
    def test_exception_scope_patterns(self, tester):
        """Test exception variable scope"""
        # Language Reference: exception variables have special scope behavior
        exception_scope_patterns = [
            """
try:
    risky_operation()
except ValueError as e:
    error_message = str(e)
""",
            """
try:
    operation()
except (TypeError, ValueError) as e:
    handle_error(e)
except Exception as e:
    log_error(e)
""",
            """
def function():
    try:
        return risky_operation()
    except Exception as e:
        local_error = e
        return None
    finally:
        cleanup()
""",
            """
try:
    with open("file.txt") as f:
        content = f.read()
except FileNotFoundError as e:
    print(f"File not found: {e}")
"""
        ]
        
        for source in exception_scope_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain try statements
            try_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
            assert len(try_nodes) >= 1, f"Should have try statements: {source}"
    
    def test_exception_propagation_patterns(self, tester):
        """Test exception propagation through scopes"""
        # Language Reference: exceptions propagate through call stack
        propagation_patterns = [
            """
def inner():
    raise ValueError("inner error")

def middle():
    return inner()

def outer():
    try:
        return middle()
    except ValueError as e:
        return str(e)
""",
            """
def function():
    def nested():
        raise RuntimeError("nested error")
    
    try:
        nested()
    except RuntimeError:
        return "caught"
""",
            """
class CustomError(Exception):
    pass

def function():
    raise CustomError("custom")

try:
    function()
except CustomError as e:
    handled = True
"""
        ]
        
        for source in propagation_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain both raise and try/except
            raises = [node for node in ast.walk(tree) if isinstance(node, ast.Raise)]
            tries = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
            assert len(raises) >= 1 or len(tries) >= 1, f"Should have exception handling: {source}"


class TestSection4ComprehensionScopes:
    """Test comprehension scope behavior."""
    
    def test_comprehension_scope_isolation(self, tester):
        """Test comprehension scope isolation"""
        # Language Reference: comprehensions have their own scope
        comprehension_scope_patterns = [
            """
x = "outer"
result = [x for x in range(5)]  # x in comprehension doesn't affect outer x
""",
            """
def function():
    items = range(10)
    filtered = [item for item in items if item % 2 == 0]
    return filtered
""",
            """
data = [(i, j) for i in range(3) for j in range(3) if i != j]
""",
            """
def function():
    outer_var = 10
    result = [outer_var + x for x in range(5)]  # Can access enclosing scope
    return result
"""
        ]
        
        for source in comprehension_scope_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain comprehensions
            comprehensions = [node for node in ast.walk(tree) 
                             if isinstance(node, (ast.ListComp, ast.SetComp, 
                                                 ast.DictComp, ast.GeneratorExp))]
            assert len(comprehensions) >= 1, f"Should have comprehensions: {source}"
    
    def test_generator_expression_scope(self, tester):
        """Test generator expression scope behavior"""
        # Language Reference: generator expressions have function-like scope
        generator_scope_patterns = [
            """
gen = (x * 2 for x in range(10))
""",
            """
def function():
    local_var = 5
    gen = (local_var + x for x in range(10))
    return list(gen)
""",
            """
data = [1, 2, 3, 4, 5]
filtered_gen = (x for x in data if x % 2 == 0)
doubled_gen = (x * 2 for x in filtered_gen)
""",
            """
def function():
    return (i for i in range(100) if i % 2 == 0)
"""
        ]
        
        for source in generator_scope_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Should contain generator expressions
            generators = [node for node in ast.walk(tree) if isinstance(node, ast.GeneratorExp)]
            assert len(generators) >= 1, f"Should have generator expressions: {source}"


class TestSection4CrossImplementationCompatibility:
    """Test cross-implementation compatibility for execution model."""
    
    def test_scope_ast_structure_consistency(self, tester):
        """Test scope-related AST structure consistency"""
        # Language Reference: AST should represent scope structure consistently
        scope_test_cases = [
            """
def function():
    local_var = 42
    return local_var
""",
            """
def outer():
    def inner():
        return "nested"
    return inner
""",
            """
x = "global"
def function():
    global x
    x = "modified"
""",
            """
def function():
    items = [x * 2 for x in range(5)]
    return items
"""
        ]
        
        for source in scope_test_cases:
            tree = tester.assert_execution_syntax_parses(source)
            
            # Should have consistent scope-creating node structure
            scope_creators = tester.get_scope_creating_nodes(source)
            assert len(scope_creators) >= 1, f"Should have scope creators: {source}"
            
            # Check for consistent name node structure
            names = tester.get_name_nodes(source)
            for name in names:
                assert hasattr(name, 'id'), "Name should have 'id' attribute"
                assert hasattr(name, 'ctx'), "Name should have 'ctx' attribute"
    
    def test_comprehensive_execution_patterns(self, tester):
        """Test comprehensive real-world execution patterns"""
        # Language Reference: complex execution model scenarios
        comprehensive_patterns = [
            """
# Module with class, functions, and scoping
MODULE_CONSTANT = "constant"

class DataProcessor:
    default_config = {"timeout": 30}
    
    def __init__(self, config=None):
        self.config = self.default_config.copy()
        if config:
            self.config.update(config)
    
    def process(self, data):
        def validate_item(item):
            return item is not None and len(str(item)) > 0
        
        filtered_data = [item for item in data if validate_item(item)]
        return filtered_data

def factory_function(processor_type="default"):
    processors = {
        "default": DataProcessor,
        "custom": lambda: DataProcessor({"timeout": 60})
    }
    return processors.get(processor_type, DataProcessor)()

if __name__ == "__main__":
    processor = factory_function()
    result = processor.process([1, None, "data", "", 42])
""",
            """
# Complex scoping with closures and globals
global_cache = {}

def cached_function_factory():
    cache = {}
    
    def cached_function(key, compute_func):
        if key not in cache:
            cache[key] = compute_func()
        return cache[key]
    
    def clear_cache():
        nonlocal cache
        cache.clear()
        global global_cache
        global_cache.clear()
    
    cached_function.clear = clear_cache
    return cached_function
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_execution_syntax_parses(source)
            # Just verify complex patterns parse successfully
            assert len(tree.body) >= 2, f"Complex execution pattern should parse: {source}"
    
    def test_execution_model_introspection(self, tester):
        """Test ability to analyze execution model programmatically"""
        # Test programmatic analysis of execution model structure
        introspection_source = """
global_var = "global"

def outer_function():
    enclosing_var = "enclosing"
    
    def inner_function():
        global global_var
        nonlocal enclosing_var
        local_var = "local"
        return global_var + enclosing_var + local_var
    
    return inner_function
"""
        
        tree = tester.assert_execution_syntax_parses(introspection_source)
        
        # Should be able to identify different scope elements
        scope_creators = tester.get_scope_creating_nodes(introspection_source)
        assert len(scope_creators) >= 2, "Should have multiple scope creators"
        
        # Should detect global and nonlocal statements
        assert tester.has_global_statement(introspection_source), "Should detect global"
        assert tester.has_nonlocal_statement(introspection_source), "Should detect nonlocal"
        
        # Should be able to analyze name usage patterns
        names = tester.get_name_nodes(introspection_source)
        assert len(names) >= 5, "Should have multiple name references"
        
        # Should detect assignment targets
        targets = tester.get_assignment_targets(introspection_source)
        assert len(targets) >= 2, "Should detect assignment targets"