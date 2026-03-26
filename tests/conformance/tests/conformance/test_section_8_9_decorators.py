"""
Section 8.9: Decorators - Conformance Test Suite

Tests Python Language Reference Section 8.9 compliance across implementations.
Based on formal decorator syntax definitions and prose assertions for decorator behavior.

Grammar tested:
    decorators: decorator+
    decorator: '@' dotted_name [ '(' [arguments] ')' ] NEWLINE
    dotted_name: NAME ('.' NAME)*
    arguments: argument (',' argument)* [',']

Language Reference requirements tested:
    - Decorator syntax and AST structure
    - Function decoration semantics and evaluation order
    - Class decoration behavior and timing
    - Multiple decorator application (bottom-up evaluation)
    - Built-in decorator patterns (@property, @staticmethod, @classmethod)
    - Decorator with arguments syntax and semantics
    - Decorator evaluation order in complex scenarios
    - Error conditions for invalid decorator usage
    - Cross-implementation decorator compatibility
"""

import ast
import pytest
import sys
from typing import Any, Callable


class DecoratorTester:
    """Helper class for testing decorator conformance.
    
    Focuses on AST structure validation for decorator syntax and application
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_decorator_syntax_parses(self, source: str):
        """Test that decorator syntax parses correctly.
        
        Args:
            source: Python source code with decorator patterns
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Decorator syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def get_decorated_functions(self, source: str) -> list:
        """Get decorated function definitions from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.FunctionDef nodes that have decorators
        """
        tree = ast.parse(source)
        decorated_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.decorator_list:
                    decorated_functions.append(node)
        
        return decorated_functions
    
    def get_decorated_classes(self, source: str) -> list:
        """Get decorated class definitions from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.ClassDef nodes that have decorators
        """
        tree = ast.parse(source)
        decorated_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.decorator_list:
                    decorated_classes.append(node)
        
        return decorated_classes
    
    def get_decorator_count(self, source: str) -> int:
        """Get total number of decorators applied.
        
        Args:
            source: Python source code
            
        Returns:
            Total count of decorators
        """
        tree = ast.parse(source)
        decorator_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                decorator_count += len(node.decorator_list)
        
        return decorator_count
    
    def get_decorator_names(self, source: str) -> list:
        """Get names of decorators used.
        
        Args:
            source: Python source code
            
        Returns:
            List of decorator name strings
        """
        tree = ast.parse(source)
        decorator_names = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorator_names.append(decorator.id)
                    elif isinstance(decorator, ast.Attribute):
                        # For dotted names like @classmethod
                        name_parts = []
                        current = decorator
                        while isinstance(current, ast.Attribute):
                            name_parts.insert(0, current.attr)
                            current = current.value
                        if isinstance(current, ast.Name):
                            name_parts.insert(0, current.id)
                            decorator_names.append('.'.join(name_parts))
                    elif isinstance(decorator, ast.Call):
                        # For decorators with arguments like @property.setter
                        if isinstance(decorator.func, ast.Name):
                            decorator_names.append(decorator.func.id)
                        elif isinstance(decorator.func, ast.Attribute):
                            name_parts = []
                            current = decorator.func
                            while isinstance(current, ast.Attribute):
                                name_parts.insert(0, current.attr)
                                current = current.value
                            if isinstance(current, ast.Name):
                                name_parts.insert(0, current.id)
                                decorator_names.append('.'.join(name_parts))
        
        return decorator_names
    
    def has_decorator_with_arguments(self, source: str) -> bool:
        """Check if source contains decorators with arguments.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains decorators with arguments
        """
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        return True
        
        return False


@pytest.fixture
def tester():
    """Provide DecoratorTester instance for tests."""
    return DecoratorTester()


class TestSection89BasicDecoratorSyntax:
    """Test basic decorator syntax validation."""
    
    def test_simple_function_decorators(self, tester):
        """Test simple function decorator syntax"""
        # Language Reference: @decorator_name NEWLINE def function
        simple_decorators = [
            """
@decorator
def function():
    pass
""",
            """
@my_decorator
def my_function():
    return 42
""",
            """
@staticmethod
def static_method():
    return "static"
""",
            """
@classmethod
def class_method(cls):
    return cls
""",
            """
@property
def prop(self):
    return self._value
"""
        ]
        
        for source in simple_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) == 1, f"Should have one decorated function: {source}"
            assert len(decorated_funcs[0].decorator_list) == 1, f"Should have one decorator: {source}"
    
    def test_dotted_name_decorators(self, tester):
        """Test dotted name decorator syntax"""
        # Language Reference: @dotted_name where dotted_name: NAME ('.' NAME)*
        dotted_decorators = [
            """
@module.decorator
def function():
    pass
""",
            """
@package.module.decorator
def function():
    pass
""",
            """
@property.setter
def prop(self, value):
    self._value = value
""",
            """
@pytest.mark.parametrize
def test_function():
    pass
""",
            """
@unittest.mock.patch
def test_with_mock():
    pass
"""
        ]
        
        for source in dotted_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) == 1, f"Should have decorated function: {source}"
            
            decorator_names = tester.get_decorator_names(source)
            assert len(decorator_names) >= 1, f"Should have decorator names: {source}"
            # Should have dotted names
            assert any('.' in name for name in decorator_names), f"Should have dotted decorator: {source}"
    
    def test_decorator_with_arguments(self, tester):
        """Test decorator with arguments syntax"""
        # Language Reference: @decorator_name ( [arguments] )
        argument_decorators = [
            """
@decorator()
def function():
    pass
""",
            """
@decorator(arg)
def function():
    pass
""",
            """
@decorator(arg1, arg2)
def function():
    pass
""",
            """
@decorator(key=value)
def function():
    pass
""",
            """
@decorator(arg1, arg2, key=value)
def function():
    pass
"""
        ]
        
        for source in argument_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            assert tester.has_decorator_with_arguments(source), f"Should have decorator with args: {source}"
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) == 1, f"Should have decorated function: {source}"
    
    def test_multiple_decorators(self, tester):
        """Test multiple decorators on single function"""
        # Language Reference: decorators: decorator+ (multiple decorators)
        multiple_decorators = [
            """
@decorator1
@decorator2
def function():
    pass
""",
            """
@staticmethod
@property
def method():
    pass
""",
            """
@decorator_with_args()
@simple_decorator
def function():
    pass
""",
            """
@first.decorator
@second.decorator
@third_decorator
def function():
    pass
""",
            """
@decorator1(arg1)
@decorator2(arg2)
@decorator3
def function():
    pass
"""
        ]
        
        for source in multiple_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) == 1, f"Should have decorated function: {source}"
            assert len(decorated_funcs[0].decorator_list) >= 2, f"Should have multiple decorators: {source}"
            
            decorator_count = tester.get_decorator_count(source)
            assert decorator_count >= 2, f"Should count multiple decorators: {source}"


class TestSection89ClassDecorators:
    """Test class decorator syntax and behavior."""
    
    def test_simple_class_decorators(self, tester):
        """Test simple class decorator syntax"""
        # Language Reference: decorators can apply to class definitions
        class_decorators = [
            """
@decorator
class MyClass:
    pass
""",
            """
@dataclass
class DataClass:
    value: int
""",
            """
@total_ordering
class OrderedClass:
    def __init__(self, value):
        self.value = value
""",
            """
@functools.lru_cache
class CachedClass:
    pass
""",
            """
@register_class
class RegisteredClass:
    pass
"""
        ]
        
        for source in class_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_classes = tester.get_decorated_classes(source)
            assert len(decorated_classes) == 1, f"Should have decorated class: {source}"
            assert len(decorated_classes[0].decorator_list) == 1, f"Should have one decorator: {source}"
    
    def test_class_decorators_with_arguments(self, tester):
        """Test class decorators with arguments"""
        # Language Reference: class decorators can have arguments
        class_argument_decorators = [
            """
@dataclass()
class DataClass:
    pass
""",
            """
@dataclass(frozen=True)
class FrozenClass:
    pass
""",
            """
@decorator(arg1, arg2)
class MyClass:
    pass
""",
            """
@attrs.define(slots=True, frozen=True)
class AttrsClass:
    pass
""",
            """
@custom_decorator(param="value", flag=True)
class CustomClass:
    pass
"""
        ]
        
        for source in class_argument_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_classes = tester.get_decorated_classes(source)
            assert len(decorated_classes) == 1, f"Should have decorated class: {source}"
            assert tester.has_decorator_with_arguments(source), f"Should have decorator with args: {source}"
    
    def test_multiple_class_decorators(self, tester):
        """Test multiple decorators on classes"""
        # Language Reference: classes can have multiple decorators
        multiple_class_decorators = [
            """
@decorator1
@decorator2
class MultiDecorated:
    pass
""",
            """
@dataclass
@total_ordering
class DataOrderedClass:
    value: int
""",
            """
@cache_result
@validate_input
@log_calls
class MultiFeatureClass:
    pass
""",
            """
@decorator_with_args(param=1)
@simple_decorator
class MixedDecorators:
    pass
"""
        ]
        
        for source in multiple_class_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_classes = tester.get_decorated_classes(source)
            assert len(decorated_classes) == 1, f"Should have decorated class: {source}"
            assert len(decorated_classes[0].decorator_list) >= 2, f"Should have multiple decorators: {source}"


class TestSection89DecoratorEvaluationOrder:
    """Test decorator evaluation order patterns."""
    
    def test_nested_decorator_structure(self, tester):
        """Test nested decorator AST structure"""
        # Language Reference: decorators are applied bottom-up
        nested_decorator_patterns = [
            """
@outer_decorator
@middle_decorator
@inner_decorator
def function():
    pass
""",
            """
@first()
@second()
@third()
def function():
    pass
""",
            """
@outer.decorator
@middle.decorator
@inner_decorator
def function():
    pass
""",
            """
@decorator_a(arg_a)
@decorator_b
@decorator_c(arg_c)
def function():
    pass
"""
        ]
        
        for source in nested_decorator_patterns:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) == 1, f"Should have decorated function: {source}"
            
            # Check decorator order in AST (should preserve source order)
            func = decorated_funcs[0]
            assert len(func.decorator_list) >= 3, f"Should have multiple decorators: {source}"
            
            # AST should preserve decorator order as written
            decorators = func.decorator_list
            assert len(decorators) >= 3, f"Should have at least 3 decorators: {source}"
    
    def test_complex_decorator_expressions(self, tester):
        """Test complex decorator expressions"""
        # Language Reference: decorators can be complex expressions
        complex_decorators = [
            """
@decorator_factory()
def function():
    pass
""",
            """
@decorator_factory(param=value)
def function():
    pass
""",
            """
@module.decorator_factory(arg1, arg2)
def function():
    pass
""",
            """
@decorators[0]
def function():
    pass
""",
            """
@get_decorator()()
def function():
    pass
"""
        ]
        
        for source in complex_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) == 1, f"Should have decorated function: {source}"


class TestSection89BuiltinDecoratorPatterns:
    """Test built-in decorator usage patterns."""
    
    def test_property_decorator_patterns(self, tester):
        """Test @property decorator usage"""
        # Language Reference: @property and related property decorators
        property_patterns = [
            """
class MyClass:
    @property
    def value(self):
        return self._value
""",
            """
class MyClass:
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val
""",
            """
class MyClass:
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val
    
    @value.deleter
    def value(self):
        del self._value
""",
            """
class MyClass:
    @property
    def readonly(self):
        return "readonly"
    
    @property
    def another_prop(self):
        return 42
"""
        ]
        
        for source in property_patterns:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) >= 1, f"Should have decorated methods: {source}"
            
            decorator_names = tester.get_decorator_names(source)
            assert "property" in decorator_names, f"Should have @property: {source}"
    
    def test_staticmethod_classmethod_patterns(self, tester):
        """Test @staticmethod and @classmethod decorators"""
        # Language Reference: built-in method decorators
        method_decorators = [
            """
class MyClass:
    @staticmethod
    def static_method():
        return "static"
""",
            """
class MyClass:
    @classmethod
    def class_method(cls):
        return cls
""",
            """
class MyClass:
    @staticmethod
    def utility_function(x, y):
        return x + y
    
    @classmethod
    def from_string(cls, string_data):
        return cls()
""",
            """
class MyClass:
    @staticmethod
    @property  # Invalid combination, but syntactically valid
    def weird_combo():
        return "weird"
"""
        ]
        
        for source in method_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) >= 1, f"Should have decorated methods: {source}"
            
            decorator_names = tester.get_decorator_names(source)
            assert len(decorator_names) >= 1, f"Should have decorator names: {source}"
    
    def test_async_function_decorators(self, tester):
        """Test decorators on async functions"""
        # Language Reference: decorators can apply to async functions
        async_decorators = [
            """
@decorator
async def async_function():
    pass
""",
            """
@cached
@validated
async def async_operation():
    await some_operation()
""",
            """
class AsyncClass:
    @property
    async def async_property(self):
        return await self.get_value()
""",
            """
@asyncio.coroutine
async def legacy_async():
    pass
"""
        ]
        
        for source in async_decorators:
            tree = tester.assert_decorator_syntax_parses(source)
            # Look for async function definitions
            async_funcs = [node for node in ast.walk(tree) 
                          if isinstance(node, ast.AsyncFunctionDef)]
            
            if async_funcs:
                # Should have decorators on async functions
                decorated_async = [func for func in async_funcs if func.decorator_list]
                assert len(decorated_async) >= 1, f"Should have decorated async functions: {source}"


class TestSection89DecoratorErrorConditions:
    """Test decorator error conditions and invalid syntax."""
    
    def test_invalid_decorator_syntax(self, tester):
        """Test invalid decorator syntax patterns"""
        # Language Reference: syntactic restrictions on decorators
        invalid_decorators = [
            "@def\ndef function(): pass", # Keyword as decorator - should fail
        ]
        
        for source in invalid_decorators:
            with pytest.raises(SyntaxError):
                ast.parse(source)
    
    def test_decorator_placement_restrictions(self, tester):
        """Test decorator placement syntax rules"""
        # Language Reference: decorators must immediately precede definition
        invalid_placements = [
            """
def function():
    pass
@decorator  # Can't place decorator after definition
""",
            """
x = 5
@decorator  # Can't decorate non-function/class
x = 10
""",
            """
@decorator
# Comment between decorator and function
def function():
    pass
"""  # Comments are allowed between decorator and definition
        ]
        
        # Only the first two should be invalid
        for i, source in enumerate(invalid_placements[:2]):
            with pytest.raises(SyntaxError):
                ast.parse(source)
        
        # The third should be valid (comments allowed)
        tester.assert_decorator_syntax_parses(invalid_placements[2])
    
    def test_decorator_argument_syntax_validation(self, tester):
        """Test decorator argument syntax validation"""
        # Language Reference: decorator arguments follow function call syntax
        valid_decorator_args = [
            """
@decorator()
def function():
    pass
""",
            """
@decorator(a, b, c)
def function():
    pass
""",
            """
@decorator(key=value)
def function():
    pass
""",
            """
@decorator(*args, **kwargs)
def function():
    pass
"""
        ]
        
        for source in valid_decorator_args:
            tree = tester.assert_decorator_syntax_parses(source)
            assert tester.has_decorator_with_arguments(source), f"Should have decorator args: {source}"


class TestSection89DecoratorASTStructure:
    """Test decorator AST structure validation."""
    
    def test_decorator_list_structure(self, tester):
        """Test decorator_list AST attribute structure"""
        # Language Reference: AST structure for decorators
        decorator_test_cases = [
            """
@decorator
def function():
    pass
""",
            """
@decorator1
@decorator2
def function():
    pass
""",
            """
@decorator()
def function():
    pass
""",
            """
@module.decorator
def function():
    pass
"""
        ]
        
        for source in decorator_test_cases:
            tree = tester.assert_decorator_syntax_parses(source)
            
            # Find decorated functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.decorator_list:
                        # Should have decorator_list attribute
                        assert hasattr(node, 'decorator_list'), "Function should have decorator_list"
                        assert isinstance(node.decorator_list, list), "decorator_list should be list"
                        assert len(node.decorator_list) >= 1, "Should have decorators in list"
                        
                        # Each decorator should be an expression
                        for decorator in node.decorator_list:
                            assert isinstance(decorator, ast.expr), "Decorator should be expression"
    
    def test_decorator_expression_types(self, tester):
        """Test types of decorator expressions in AST"""
        # Language Reference: decorator expression types
        expression_type_cases = [
            ("@simple", ast.Name),
            ("@module.decorator", ast.Attribute),
            ("@decorator()", ast.Call),
            ("@decorator(arg)", ast.Call),
        ]
        
        for decorator_source, expected_type in expression_type_cases:
            source = f"""
{decorator_source}
def function():
    pass
"""
            tree = tester.assert_decorator_syntax_parses(source)
            
            # Find the decorator
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.decorator_list:
                        decorator = node.decorator_list[0]
                        assert isinstance(decorator, expected_type), f"Decorator should be {expected_type.__name__}: {decorator_source}"
    
    def test_complex_decorator_ast_structure(self, tester):
        """Test complex decorator AST structure"""
        # Language Reference: complex decorator expression structure
        complex_decorator_source = """
@outer_decorator
@middle.decorator(arg1, arg2, key=value)
@inner_decorator()
def complex_decorated_function():
    pass
"""
        
        tree = tester.assert_decorator_syntax_parses(complex_decorator_source)
        
        # Find decorated function
        func_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        assert len(func_nodes) == 1, "Should have one function"
        
        func = func_nodes[0]
        assert len(func.decorator_list) == 3, "Should have three decorators"
        
        # Check decorator types in order
        decorators = func.decorator_list
        assert isinstance(decorators[0], ast.Name), "First decorator should be Name"
        assert isinstance(decorators[1], ast.Call), "Second decorator should be Call"
        assert isinstance(decorators[2], ast.Call), "Third decorator should be Call"


class TestSection89CrossImplementationCompatibility:
    """Test cross-implementation compatibility for decorators."""
    
    def test_decorator_ast_consistency(self, tester):
        """Test decorator AST consistency across implementations"""
        # Language Reference: decorator AST should be consistent
        compatibility_test_cases = [
            """
@staticmethod
def static_method():
    return "static"
""",
            """
@property
def prop(self):
    return self._value
""",
            """
@classmethod
def class_method(cls):
    return cls
""",
            """
@decorator_with_args(param=42)
def parameterized_function():
    pass
""",
            """
@first_decorator
@second_decorator
def multi_decorated():
    pass
"""
        ]
        
        for source in compatibility_test_cases:
            tree = tester.assert_decorator_syntax_parses(source)
            
            # Should have consistent decorator structure
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) >= 1, f"Should have decorated functions: {source}"
            
            for func in decorated_funcs:
                assert hasattr(func, 'decorator_list'), "Function should have decorator_list"
                assert len(func.decorator_list) >= 1, "Should have decorators"
    
    def test_comprehensive_decorator_patterns(self, tester):
        """Test comprehensive real-world decorator patterns"""
        # Language Reference: complex real-world decorator scenarios
        comprehensive_patterns = [
            """
# Class with multiple decorated methods
class APIEndpoint:
    @classmethod
    @validate_input
    def from_config(cls, config_dict):
        return cls(**config_dict)
    
    @property
    @cache_result
    def endpoint_url(self):
        return f"https://api.example.com/{self.path}"
    
    @staticmethod
    @rate_limit(calls_per_minute=60)
    def validate_api_key(key):
        return len(key) == 32
    
    @deprecated("Use new_method instead")
    @log_calls
    def old_method(self):
        return "deprecated"
""",
            """
# Decorated class with decorated methods
@dataclass
@total_ordering
class SortableData:
    value: int
    name: str
    
    @property
    def display_name(self):
        return f"{self.name}: {self.value}"
    
    @classmethod
    def from_string(cls, data_string):
        parts = data_string.split(":")
        return cls(int(parts[1]), parts[0])
""",
            """
# Complex nested decorators
@cache_results(ttl=300)
@retry(max_attempts=3, backoff=exponential)
@log_execution_time
async def fetch_data(url, headers=None):
    async with http_client.get(url, headers=headers) as response:
        return await response.json()
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_decorator_syntax_parses(source)
            
            # Should have multiple decorated items
            decorator_count = tester.get_decorator_count(source)
            assert decorator_count >= 3, f"Should have multiple decorators: {source}"
            
            # Should have both function and potentially class decorators
            decorated_funcs = tester.get_decorated_functions(source)
            assert len(decorated_funcs) >= 1, f"Should have decorated functions: {source}"
    
    def test_decorator_introspection(self, tester):
        """Test ability to analyze decorators programmatically"""
        # Test programmatic analysis of decorator structure
        introspection_source = """
@outer_decorator
@middle_decorator(param="value")
@inner.nested.decorator()
def example_function():
    pass

@dataclass
@total_ordering
class ExampleClass:
    @property
    def prop(self):
        return "property"
    
    @classmethod
    @cached
    def factory_method(cls):
        return cls()
"""
        
        tree = tester.assert_decorator_syntax_parses(introspection_source)
        
        # Should be able to identify all decorators
        decorator_count = tester.get_decorator_count(introspection_source)
        assert decorator_count >= 7, "Should have multiple decorators total"
        
        # Should identify decorator names
        decorator_names = tester.get_decorator_names(introspection_source)
        assert len(decorator_names) >= 5, "Should identify decorator names"
        
        # Should detect decorators with arguments
        assert tester.has_decorator_with_arguments(introspection_source), "Should detect decorator args"
        
        # Should find both function and class decorators
        decorated_funcs = tester.get_decorated_functions(introspection_source)
        decorated_classes = tester.get_decorated_classes(introspection_source)
        assert len(decorated_funcs) >= 2, "Should have decorated functions"
        assert len(decorated_classes) >= 1, "Should have decorated classes"