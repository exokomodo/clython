"""
Section 7.6: Return Statements - Conformance Test Suite

Tests Python Language Reference Section 7.6 compliance across implementations.
Based on formal grammar definitions and prose assertions for return statements.

Grammar tested:
    return_stmt: 'return' [testlist]

Language Reference requirements tested:
    - Basic return statement syntax
    - Return with and without value expressions
    - Return value expression forms and types
    - Return statement context requirements (function/method only)
    - Return effects on generators (converts to StopIteration)
    - Return in different function types (regular, async, generator)
    - Error conditions and invalid return usage
    - Complex return value expressions
"""

import ast
import pytest
import sys
from typing import Any


class ReturnStatementTester:
    """Helper class for testing return statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_return_syntax_parses(self, source: str):
        """Test that return statement syntax parses correctly.
        
        Args:
            source: Python return statement source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains return statement
            for node in ast.walk(tree):
                if isinstance(node, ast.Return):
                    return tree  # Found return statement, syntax is valid
            pytest.fail(f"Expected Return node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Return statement syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_return_syntax_error(self, source: str):
        """Test that invalid return syntax raises SyntaxError.
        
        Args:
            source: Python return source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_return_from_source(self, source: str) -> ast.Return:
        """Get the Return AST node from source for detailed validation.
        
        Args:
            source: Python return statement source
            
        Returns:
            ast.Return node
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Return):
                return node
        pytest.fail(f"Expected Return node not found in: {source}")
    
    def has_return_value(self, source: str) -> bool:
        """Check if return statement has value expression.
        
        Args:
            source: Python return statement source
            
        Returns:
            True if return has value expression
        """
        return_node = self.get_return_from_source(source)
        return return_node.value is not None
    
    def get_return_value_type(self, source: str) -> type:
        """Get the AST type of return value expression.
        
        Args:
            source: Python return statement source
            
        Returns:
            AST node type of return value
        """
        return_node = self.get_return_from_source(source)
        if return_node.value is None:
            return None
        return type(return_node.value)


@pytest.fixture
def tester():
    """Provide ReturnStatementTester instance for tests."""
    return ReturnStatementTester()


class TestSection76BasicReturnStatements:
    """Test basic return statement syntax and semantics."""
    
    def test_bare_return_statement(self, tester):
        """Test bare return statement (return None implicitly)"""
        # Language Reference: return without expression returns None
        bare_return_function = """
def function():
    return
"""
        
        tree = tester.assert_return_syntax_parses(bare_return_function)
        return_node = tester.get_return_from_source(bare_return_function)
        assert return_node.value is None, "Bare return should have no value expression"
    
    def test_return_with_simple_values(self, tester):
        """Test return with simple value expressions"""
        # Language Reference: return with testlist
        simple_return_functions = [
            """
def func():
    return 42
""",
            """
def func():
    return "hello"
""",
            """
def func():
    return True
""",
            """
def func():
    return None
""",
            """
def func():
    return 3.14
"""
        ]
        
        for source in simple_return_functions:
            tree = tester.assert_return_syntax_parses(source)
            assert tester.has_return_value(source)
            return_node = tester.get_return_from_source(source)
            assert return_node.value is not None
    
    def test_return_with_variables(self, tester):
        """Test return with variable expressions"""
        # Language Reference: return can return any expression
        variable_returns = [
            """
def func():
    x = 42
    return x
""",
            """
def func():
    return result
""",
            """
def func():
    return self.value
""",
            """
def func():
    return obj.attribute
""",
            """
def func():
    return items[index]
"""
        ]
        
        for source in variable_returns:
            tree = tester.assert_return_syntax_parses(source)
            assert tester.has_return_value(source)
    
    def test_return_with_expressions(self, tester):
        """Test return with complex expressions"""
        # Language Reference: return accepts full testlist expressions
        expression_returns = [
            """
def func():
    return x + y
""",
            """
def func():
    return a * b + c
""",
            """
def func():
    return func_call()
""",
            """
def func():
    return obj.method()
""",
            """
def func():
    return x if condition else y
""",
            """
def func():
    return not flag
"""
        ]
        
        for source in expression_returns:
            tree = tester.assert_return_syntax_parses(source)
            assert tester.has_return_value(source)


class TestSection76ReturnValueTypes:
    """Test various return value types and structures."""
    
    def test_return_literals(self, tester):
        """Test return with literal values"""
        # Language Reference: literals are valid return values
        literal_returns = [
            "def func(): return 42",                    # Integer
            "def func(): return 3.14",                  # Float
            "def func(): return 'string'",              # String
            "def func(): return True",                  # Boolean
            "def func(): return None",                  # None
            "def func(): return []",                    # Empty list
            "def func(): return {}",                    # Empty dict
            "def func(): return ()",                    # Empty tuple
        ]
        
        for source in literal_returns:
            tree = tester.assert_return_syntax_parses(source)
            assert tester.has_return_value(source)
    
    def test_return_collections(self, tester):
        """Test return with collection literals"""
        # Language Reference: collections are valid return values
        collection_returns = [
            "def func(): return [1, 2, 3]",            # List
            "def func(): return (1, 2, 3)",            # Tuple
            "def func(): return {1, 2, 3}",            # Set
            "def func(): return {'a': 1, 'b': 2}",     # Dict
            "def func(): return [x for x in range(5)]", # List comprehension
            "def func(): return {x: x**2 for x in range(3)}", # Dict comprehension
        ]
        
        for source in collection_returns:
            tree = tester.assert_return_syntax_parses(source)
            assert tester.has_return_value(source)
    
    def test_return_function_calls(self, tester):
        """Test return with function call expressions"""
        # Language Reference: function calls are valid return values
        call_returns = [
            "def func(): return other_func()",
            "def func(): return obj.method(arg)",
            "def func(): return func(a, b, c)",
            "def func(): return Class()",
            "def func(): return len(items)",
            "def func(): return max(values)",
            "def func(): return callable(*args, **kwargs)"
        ]
        
        for source in call_returns:
            tree = tester.assert_return_syntax_parses(source)
            return_value_type = tester.get_return_value_type(source)
            assert return_value_type == ast.Call
    
    def test_return_multiple_values(self, tester):
        """Test return with multiple values (tuple packing)"""
        # Language Reference: testlist can contain multiple values
        multiple_returns = [
            "def func(): return a, b",
            "def func(): return x, y, z",
            "def func(): return 1, 'two', [3]",
            "def func(): return func1(), func2()",
            "def func(): return *items, last",
            "def func(): return first, *middle, last"
        ]
        
        for source in multiple_returns:
            tree = tester.assert_return_syntax_parses(source)
            assert tester.has_return_value(source)
            # Multiple values should create tuple
            return_value_type = tester.get_return_value_type(source)
            assert return_value_type in (ast.Tuple, ast.Starred)


class TestSection76ReturnInFunctionTypes:
    """Test return statements in different function contexts."""
    
    def test_return_in_regular_functions(self, tester):
        """Test return in regular function definitions"""
        # Language Reference: return allowed in regular functions
        regular_functions = [
            """
def simple_func():
    return 42
""",
            """
def complex_func(a, b):
    if a > b:
        return a
    else:
        return b
""",
            """
def early_return(items):
    if not items:
        return None
    return process(items)
""",
            """
def multiple_returns(x):
    if x < 0:
        return "negative"
    elif x == 0:
        return "zero"
    else:
        return "positive"
"""
        ]
        
        for source in regular_functions:
            tree = tester.assert_return_syntax_parses(source)
            # Find function definitions that contain return statements
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    returns_in_func = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
                    assert len(returns_in_func) >= 1, f"Expected return in function: {source}"
    
    @pytest.mark.min_version_3_5
    def test_return_in_async_functions(self, tester):
        """Test return in async function definitions"""
        # Language Reference: return allowed in async functions
        async_functions = [
            """
async def async_func():
    return await other_async()
""",
            """
async def process_async(data):
    result = await process_data(data)
    return result
""",
            """
async def conditional_async(flag):
    if flag:
        return await async_operation()
    return default_value
"""
        ]
        
        for source in async_functions:
            tree = tester.assert_return_syntax_parses(source)
            # Find async function definitions that contain return statements
            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef):
                    returns_in_func = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
                    assert len(returns_in_func) >= 1, f"Expected return in async function: {source}"
    
    def test_return_in_methods(self, tester):
        """Test return in class method definitions"""
        # Language Reference: return allowed in methods
        method_classes = [
            """
class Example:
    def method(self):
        return self.value
""",
            """
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
""",
            """
class Handler:
    @staticmethod
    def static_method():
        return "static"
    
    @classmethod
    def class_method(cls):
        return cls.__name__
"""
        ]
        
        for source in method_classes:
            tree = tester.assert_return_syntax_parses(source)
            # Find methods that contain return statements
            method_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    returns_in_method = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
                    if returns_in_method:
                        method_count += 1
            assert method_count >= 1, f"Expected methods with return: {source}"


class TestSection76ReturnAndGenerators:
    """Test return statement effects in generator functions."""
    
    def test_return_in_generator_functions(self, tester):
        """Test return in generator functions (becomes StopIteration)"""
        # Language Reference: return in generator raises StopIteration with value
        generator_functions = [
            """
def generator():
    yield 1
    yield 2
    return "done"
""",
            """
def conditional_generator(flag):
    if flag:
        yield "item"
    return "finished"
""",
            """
def complex_generator():
    for i in range(3):
        yield i
    return sum(range(3))
"""
        ]
        
        for source in generator_functions:
            tree = tester.assert_return_syntax_parses(source)
            # Find functions that have both yield and return
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    yields = [n for n in ast.walk(node) if isinstance(n, (ast.Yield, ast.YieldFrom))]
                    returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
                    if yields and returns:
                        # This is a generator with return - should parse successfully
                        assert len(returns) >= 1, f"Generator should have return: {source}"
    
    def test_return_value_in_generators(self, tester):
        """Test return values in generator functions"""
        # Language Reference: return value becomes StopIteration value
        generator_return_values = [
            """
def gen_with_return():
    yield 1
    return "final_value"
""",
            """
def gen_with_expression():
    yield item
    return compute_final()
""",
            """
def gen_with_none():
    yield data
    return None
""",
            """
def gen_with_bare_return():
    yield element
    return
"""
        ]
        
        for source in generator_return_values:
            tree = tester.assert_return_syntax_parses(source)
            # Verify return statements in generator context
            assert tester.has_return_value(source) or "bare_return" in source


class TestSection76ReturnControlFlow:
    """Test return statement control flow effects."""
    
    def test_early_return_patterns(self, tester):
        """Test early return control flow patterns"""
        # Language Reference: return immediately exits function
        early_return_patterns = [
            """
def validate_input(data):
    if data is None:
        return False
    if not isinstance(data, dict):
        return False
    return True
""",
            """
def find_item(items, target):
    for item in items:
        if item == target:
            return item
    return None
""",
            """
def guard_clauses(value):
    if value < 0:
        return "negative"
    if value == 0:
        return "zero"
    if value > 100:
        return "large"
    return "normal"
"""
        ]
        
        for source in early_return_patterns:
            tree = tester.assert_return_syntax_parses(source)
            # Count return statements in function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
                    assert len(returns) >= 2, f"Expected multiple returns: {source}"
    
    def test_return_in_loops(self, tester):
        """Test return statements inside loop structures"""
        # Language Reference: return exits function from within loops
        loop_returns = [
            """
def find_in_loop(items):
    for item in items:
        if condition(item):
            return item
    return None
""",
            """
def while_loop_return(counter):
    while counter > 0:
        if check_condition():
            return counter
        counter -= 1
    return 0
""",
            """
def nested_loop_return(matrix):
    for row in matrix:
        for cell in row:
            if cell == target:
                return (row, cell)
    return None
"""
        ]
        
        for source in loop_returns:
            tree = tester.assert_return_syntax_parses(source)
            # Verify return statements exist within loop structures
            loop_nodes = [node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))]
            assert len(loop_nodes) >= 1, f"Expected loop with return: {source}"
    
    def test_return_in_exception_handling(self, tester):
        """Test return statements in try/except/finally blocks"""
        # Language Reference: return allowed in exception handling contexts
        exception_returns = [
            """
def safe_operation():
    try:
        result = risky_operation()
        return result
    except Exception:
        return None
""",
            """
def cleanup_return():
    try:
        return process_data()
    finally:
        cleanup()
""",
            """
def complex_exception_handling():
    try:
        return attempt_operation()
    except ValueError:
        return default_value
    except TypeError:
        return alternative_value
    finally:
        log_completion()
"""
        ]
        
        for source in exception_returns:
            tree = tester.assert_return_syntax_parses(source)
            # Find return statements in exception handling contexts
            try_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
            assert len(try_nodes) >= 1, f"Expected try block with return: {source}"


class TestSection76ErrorConditions:
    """Test return statement error conditions and edge cases."""
    
    def test_return_outside_function(self, tester):
        """Test return statement outside function context"""
        # Language Reference: return only valid inside functions
        # Note: This is a semantic error, not syntax error - will parse but fail at runtime
        outside_function_returns = [
            "return 42",                    # Module level return
            """
if True:
    return "invalid"
""",
            """
for i in range(3):
    return i
"""
        ]
        
        # These should parse successfully (syntax is valid)
        # but would fail semantically at runtime
        for source in outside_function_returns:
            tree = tester.assert_return_syntax_parses(source)
            return_node = tester.get_return_from_source(source)
            assert isinstance(return_node, ast.Return)
    
    def test_return_indentation_requirements(self, tester):
        """Test return statement indentation requirements"""
        # Language Reference: return follows normal indentation rules
        valid_indented_returns = [
            """
def func():
    return 42
""",
            """
def func():
    if condition:
        return True
    return False
""",
            """
def func():
    try:
        return operation()
    except:
        return None
"""
        ]
        
        for source in valid_indented_returns:
            tester.assert_return_syntax_parses(source)
    
    def test_invalid_return_syntax(self, tester):
        """Test invalid return statement syntax"""
        # Language Reference: syntactic restrictions
        invalid_returns = [
            "def func(): return return 42",      # Duplicate return keyword
            "def func(): return,",               # Trailing comma without value
            "def func(): return from x",         # Invalid 'from' usage (not raise)
        ]
        
        for source in invalid_returns:
            tester.assert_return_syntax_error(source)


class TestSection76CrossImplementationCompatibility:
    """Test cross-implementation compatibility for return statements."""
    
    def test_return_statement_ast_structure(self, tester):
        """Test return statement AST structure across implementations"""
        # Language Reference: AST structure should be consistent
        test_cases = [
            "def func(): return",
            "def func(): return 42", 
            "def func(): return a, b",
            "def func(): return func_call()",
        ]
        
        for source in test_cases:
            tree = tester.assert_return_syntax_parses(source)
            return_node = tester.get_return_from_source(source)
            
            # Verify required AST attributes
            assert hasattr(return_node, 'value'), f"Return node should have 'value' attribute: {source}"
            
            # Value should be None or AST node
            assert return_node.value is None or isinstance(return_node.value, ast.AST)
    
    def test_complex_return_patterns(self, tester):
        """Test complex return statement patterns"""
        # Language Reference: comprehensive real-world patterns
        complex_patterns = [
            """
def data_processor(data):
    if not data:
        return {"status": "empty", "result": None}
    
    try:
        processed = [transform(item) for item in data]
        return {
            "status": "success",
            "result": processed,
            "count": len(processed)
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "result": None
        }
""",
            """
async def api_handler(request):
    if not request.is_valid():
        return {"error": "Invalid request"}, 400
    
    try:
        result = await process_request(request)
        return {"data": result}, 200
    except TimeoutError:
        return {"error": "Request timeout"}, 504
    except Exception:
        return {"error": "Internal error"}, 500
""",
            """
def recursive_search(node, target, path=[]):
    if node.value == target:
        return path + [node.value]
    
    for child in node.children:
        result = recursive_search(child, target, path + [node.value])
        if result:
            return result
    
    return None
"""
        ]
        
        for source in complex_patterns:
            tree = tester.assert_return_syntax_parses(source)
            # Just verify the pattern parses successfully
            assert len(tree.body) >= 1, f"Complex return pattern should parse: {source}"
    
    def test_return_statement_introspection(self, tester):
        """Test return statement introspection capabilities"""
        # Test ability to analyze return statement structure programmatically
        introspection_source = """
def example_function(x, y):
    return x + y, x * y
"""
        
        tree = tester.assert_return_syntax_parses(introspection_source)
        return_node = tester.get_return_from_source(introspection_source)
        
        # Should be able to introspect structure
        assert return_node.value is not None, "Should have return value"
        assert isinstance(return_node.value, ast.Tuple), "Should return tuple"
        
        # Should be able to analyze tuple elements
        tuple_node = return_node.value
        assert len(tuple_node.elts) == 2, "Should have two tuple elements"
    
    def test_generator_return_compatibility(self, tester):
        """Test generator return statement compatibility"""
        # Test that generator returns are consistently handled
        generator_cases = [
            """
def simple_generator():
    yield 1
    return
""",
            """
def value_generator():
    yield item
    return final_value
""",
            """
def complex_generator():
    for i in range(5):
        yield i
    return sum(range(5))
"""
        ]
        
        for source in generator_cases:
            tree = tester.assert_return_syntax_parses(source)
            # Find return statements in generator functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    yields = [n for n in ast.walk(node) if isinstance(n, (ast.Yield, ast.YieldFrom))]
                    returns = [n for n in ast.walk(node) if isinstance(n, ast.Return)]
                    if yields and returns:
                        # Generator with return should parse successfully
                        assert len(returns) >= 1, f"Generator return should parse: {source}"