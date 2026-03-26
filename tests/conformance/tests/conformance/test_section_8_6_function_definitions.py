"""
Section 8.6: Function Definitions - Conformance Test Suite

Tests Python Language Reference Section 8.6 compliance across implementations.
Based on formal grammar definitions and prose assertions for function definitions.

Grammar tested:
    funcdef: [decorators] "def" funcname "(" [parameter_list] ")" ["->" expression] ":" suite
    parameter_list: defparameter ("," defparameter)* [,] | "*" [parameter] ("," defparameter)* [","] ["**" parameter [","]] | "**" parameter [","]
    defparameter: parameter ["=" expression]
    parameter: identifier [":" expression]

Language Reference requirements tested:
    - Function definition syntax: "def" keyword with funcname
    - Parameter lists: positional, keyword, defaults, *args, **kwargs
    - Type annotations: parameter and return type hints
    - Function decorators: @decorator on function definitions
    - Positional-only parameters: "/" delimiter (Python 3.8+)
    - Keyword-only parameters: "*" delimiter
    - Nested function definitions
"""

import ast
import pytest
import sys
from typing import Any


class FunctionDefinitionTester:
    """Helper class for testing function definition conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_function_syntax_parses(self, source: str):
        """Test that function definition syntax parses correctly.
        
        Args:
            source: Python function definition source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains function definition
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return tree  # Found function definition, syntax is valid
            pytest.fail(f"Expected FunctionDef not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Function syntax {source!r} failed to parse: {e}")
    
    def assert_function_syntax_error(self, source: str):
        """Test that invalid function syntax raises SyntaxError.
        
        Args:
            source: Python function source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)

    def get_function_def_from_source(self, source: str) -> ast.FunctionDef:
        """Get the FunctionDef AST node from source for detailed validation.
        
        Args:
            source: Python function definition source
            
        Returns:
            ast.FunctionDef node
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                return node
        pytest.fail(f"No FunctionDef found in: {source}")


class TestSection86BasicFunctionDefinitions:
    """Test Section 8.6: Basic Function Definitions"""
    
    @pytest.fixture
    def tester(self):
        return FunctionDefinitionTester()

    def test_basic_function_syntax(self, tester):
        """Test basic function definition syntax"""
        # Language Reference: funcdef: "def" funcname "(" [parameter_list] ")" ":" suite
        basic_functions = [
            "def simple(): pass",
            "def empty():\n    pass",
            "def returns_value():\n    return 42",
            "def with_body():\n    x = 1\n    return x"
        ]
        
        for source in basic_functions:
            tester.assert_function_syntax_parses(source)

    def test_function_with_docstring(self, tester):
        """Test function with docstring"""
        # Functions with docstrings
        docstring_functions = [
            'def documented():\n    """This is a docstring."""\n    pass',
            'def multiline_doc():\n    """This is a\n    multiline docstring."""\n    pass',
            "def single_quote_doc():\n    'Simple docstring.'\n    pass"
        ]
        
        for source in docstring_functions:
            tester.assert_function_syntax_parses(source)

    def test_function_name_validation(self, tester):
        """Test valid function name syntax"""
        # Language Reference: funcname: identifier
        valid_names = [
            "def valid_name(): pass",
            "def _private_name(): pass",  
            "def __dunder_name__(): pass",
            "def camelCase(): pass",
            "def snake_case(): pass",
            "def name123(): pass"
        ]
        
        for source in valid_names:
            tester.assert_function_syntax_parses(source)

    def test_nested_function_definitions(self, tester):
        """Test nested function definitions"""
        # Nested functions
        nested_functions = [
            """def outer():
    def inner():
        pass
    return inner""",
            
            """def container():
    def helper(x):
        return x * 2
    
    def processor(data):
        return [helper(item) for item in data]
    
    return processor"""
        ]
        
        for source in nested_functions:
            tester.assert_function_syntax_parses(source)


class TestSection86ParameterLists:
    """Test function parameter list syntax"""
    
    @pytest.fixture
    def tester(self):
        return FunctionDefinitionTester()

    def test_positional_parameters(self, tester):
        """Test positional parameter syntax"""
        # Basic positional parameters
        positional_params = [
            "def func(x): pass",
            "def func(x, y): pass",
            "def func(x, y, z): pass",
            "def func(first, second, third): pass"
        ]
        
        for source in positional_params:
            tester.assert_function_syntax_parses(source)

    def test_default_parameters(self, tester):
        """Test default parameter syntax"""
        # Language Reference: defparameter: parameter ["=" expression]
        default_params = [
            "def func(x=42): pass",
            "def func(x, y=None): pass",
            "def func(x=1, y=2): pass",
            "def func(name='default', count=0): pass",
            "def func(x, y=[], z={}): pass"
        ]
        
        for source in default_params:
            tester.assert_function_syntax_parses(source)

    def test_varargs_parameters(self, tester):
        """Test *args parameter syntax"""
        # *args syntax
        varargs_params = [
            "def func(*args): pass",
            "def func(x, *args): pass",
            "def func(x, y, *args): pass",
            "def func(x=1, *args): pass"
        ]
        
        for source in varargs_params:
            tester.assert_function_syntax_parses(source)

    def test_kwargs_parameters(self, tester):
        """Test **kwargs parameter syntax"""
        # **kwargs syntax
        kwargs_params = [
            "def func(**kwargs): pass",
            "def func(x, **kwargs): pass",
            "def func(x, y, **kwargs): pass",
            "def func(*args, **kwargs): pass",
            "def func(x, *args, **kwargs): pass"
        ]
        
        for source in kwargs_params:
            tester.assert_function_syntax_parses(source)

    def test_keyword_only_parameters(self, tester):
        """Test keyword-only parameter syntax (Python 3+)"""
        # Keyword-only parameters with * separator
        kwonly_params = [
            "def func(*, x): pass",
            "def func(a, *, b): pass", 
            "def func(a, b, *, c, d): pass",
            "def func(a, *, b=None): pass",
            "def func(a, *args, b): pass",
            "def func(*, x, y, **kwargs): pass"
        ]
        
        for source in kwonly_params:
            tester.assert_function_syntax_parses(source)

    @pytest.mark.min_version_3_8
    def test_positional_only_parameters(self, tester):
        """Test positional-only parameter syntax (Python 3.8+)"""
        # Positional-only parameters with / separator
        posonly_params = [
            "def func(x, /): pass",
            "def func(x, y, /): pass",
            "def func(x, /, y): pass", 
            "def func(x, y, /, z): pass",
            "def func(a, b=1, /): pass",
            "def func(a, /, b, *, c): pass",
            "def func(a, /, b, *args, **kwargs): pass"
        ]
        
        for source in posonly_params:
            tester.assert_function_syntax_parses(source)

    def test_complex_parameter_combinations(self, tester):
        """Test complex parameter list combinations"""
        # Complex parameter patterns
        complex_params = [
            "def func(a, b=1, *args, c, d=2, **kwargs): pass",
            "def func(req, opt=None, *args, kwonly, kwopt=42, **kwargs): pass"
        ]
        for source in complex_params:
            tester.assert_function_syntax_parses(source)

    @pytest.mark.min_version_3_8 
    def test_complex_parameters_with_positional_only(self, tester):
        """Test complex parameter combinations with positional-only (Python 3.8+)"""
        posonly_complex_params = [
            "def func(a, b, /, c, d=1, *args, e, f=2, **kwargs): pass",
            "def func(posonly, /, normal, default=1, *args, kwonly, kwdefault=2, **kwargs): pass"
        ]
        
        for source in posonly_complex_params:
            tester.assert_function_syntax_parses(source)

    def test_parameter_list_ast_structure(self, tester):
        """Test parameter list AST structure"""
        # Verify AST structure for complex parameters  
        source = "def func(a, b=1, c=2, *args, d, e=3, **kwargs): pass"
        
        funcdef = tester.get_function_def_from_source(source)
        args = funcdef.args
        
        # Verify parameter structure exists
        assert len(args.args) >= 2  # At least a, b, c
        assert len(args.defaults) >= 1  # At least b=1
        assert args.vararg is not None  # *args
        assert len(args.kwonlyargs) >= 2  # At least d, e
        assert args.kwarg is not None  # **kwargs


class TestSection86TypeAnnotations:
    """Test function type annotation syntax"""
    
    @pytest.fixture
    def tester(self):
        return FunctionDefinitionTester()

    @pytest.mark.min_version_3_5
    def test_parameter_type_annotations(self, tester):
        """Test parameter type annotation syntax (Python 3.5+)"""
        # Language Reference: parameter: identifier [":" expression]
        param_annotations = [
            "def func(x: int): pass",
            "def func(x: int, y: str): pass",
            "def func(name: str, count: int): pass",
            "def func(data: list, config: dict): pass",
            "def func(x: 'ForwardRef'): pass"
        ]
        
        for source in param_annotations:
            tester.assert_function_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_return_type_annotations(self, tester):
        """Test return type annotation syntax (Python 3.5+)"""
        # Language Reference: funcdef with "-> expression"
        return_annotations = [
            "def func() -> int: pass",
            "def func(x: int) -> str: pass",
            "def func() -> list: pass", 
            "def func() -> 'ReturnType': pass",
            "def func() -> None: pass"
        ]
        
        for source in return_annotations:
            tester.assert_function_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_complex_type_annotations(self, tester):
        """Test complex type annotation expressions"""
        # Complex type expressions
        complex_annotations = [
            "def func(x: List[int]) -> Dict[str, int]: pass",
            "def func(callback: Callable[[int], str]) -> None: pass",
            "def func(x: Union[int, str]) -> Optional[bool]: pass",
            "def func(x: Tuple[int, ...]) -> Generator[str, None, None]: pass"
        ]
        
        for source in complex_annotations:
            tester.assert_function_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_annotations_with_defaults(self, tester):
        """Test type annotations combined with default values"""
        # Annotations + defaults
        annotated_defaults = [
            "def func(x: int = 42): pass",
            "def func(name: str = 'default'): pass",
            "def func(x: int, y: str = None): pass",
            "def func(data: list = None, config: dict = {}): pass"
        ]
        
        for source in annotated_defaults:
            tester.assert_function_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_annotations_with_varargs(self, tester):
        """Test type annotations with *args and **kwargs"""
        # Annotations with varargs
        varargs_annotations = [
            "def func(*args: int): pass",
            "def func(**kwargs: str): pass", 
            "def func(x: int, *args: float, **kwargs: bool): pass"
        ]
        
        for source in varargs_annotations:
            tester.assert_function_syntax_parses(source)


class TestSection86FunctionDecorators:
    """Test function decorator syntax"""
    
    @pytest.fixture
    def tester(self):
        return FunctionDefinitionTester()

    def test_single_decorator(self, tester):
        """Test single function decorator"""
        # Language Reference: decorators on funcdef
        single_decorators = [
            "@decorator\ndef func(): pass",
            "@property\ndef method(self): pass",
            "@staticmethod\ndef func(): pass",
            "@classmethod\ndef method(cls): pass"
        ]
        
        for source in single_decorators:
            tester.assert_function_syntax_parses(source)

    def test_multiple_decorators(self, tester):
        """Test multiple function decorators"""
        # Multiple decorators
        multiple_decorators = [
            "@decorator1\n@decorator2\ndef func(): pass",
            "@property\n@cached\ndef value(self): pass", 
            "@deco1\n@deco2\n@deco3\ndef func(): pass",
            "@validate('input')\n@cache\ndef process(data): pass"
        ]
        
        for source in multiple_decorators:
            tester.assert_function_syntax_parses(source)

    def test_decorator_with_arguments(self, tester):
        """Test decorators with arguments"""
        # Decorators with arguments
        decorator_args = [
            "@decorator(arg=value)\ndef func(): pass",
            "@cache(maxsize=128)\ndef expensive_func(): pass",
            "@validate('input', 'output')\ndef process(): pass",
            "@retry(times=3, delay=1)\ndef network_call(): pass"
        ]
        
        for source in decorator_args:
            tester.assert_function_syntax_parses(source)

    def test_decorator_ast_structure(self, tester):
        """Test decorator AST structure"""
        # Verify decorator AST structure
        source = "@decorator1\n@decorator2(arg=value)\ndef decorated(): pass"
        funcdef = tester.get_function_def_from_source(source)
        
        assert len(funcdef.decorator_list) == 2
        assert isinstance(funcdef.decorator_list[0], ast.Name)  # Simple decorator
        assert isinstance(funcdef.decorator_list[1], ast.Call)  # Decorator with args


class TestSection86ErrorConditions:
    """Test error conditions for function definitions"""
    
    @pytest.fixture
    def tester(self):
        return FunctionDefinitionTester()

    def test_invalid_function_syntax(self, tester):
        """Test invalid function definition syntax"""
        # Invalid syntax
        invalid_syntax = [
            "def: pass",              # Missing function name
            "def 123invalid(): pass", # Invalid name (starts with number)
            "def for(): pass",        # Keyword as name
            "def valid()",            # Missing colon
            "def valid() pass"        # Missing colon alternative
        ]
        
        for source in invalid_syntax:
            tester.assert_function_syntax_error(source)

    def test_invalid_parameter_syntax(self, tester):
        """Test invalid parameter list syntax"""
        # Invalid parameter syntax
        invalid_params = [
            "def func(x=): pass",        # Missing default value
            "def func(x, y=, z): pass",  # Missing default value
            "def func(**kwargs, x): pass", # **kwargs not at end
            "def func(*args, *more): pass" # Multiple *args
        ]
        
        for source in invalid_params:
            tester.assert_function_syntax_error(source)

    @pytest.mark.min_version_3_8
    def test_invalid_positional_only_syntax(self, tester):
        """Test invalid positional-only parameter syntax (Python 3.8+)"""
        invalid_posonly = [
            "def func(/, x): pass",      # / must follow parameters
            "def func(x, /, /, y): pass", # Multiple / separators
            "def func(x, /, *args, /): pass" # / after *args
        ]
        
        for source in invalid_posonly:
            tester.assert_function_syntax_error(source)

    def test_reserved_keywords_as_function_names(self, tester):
        """Test reserved keywords cannot be function names"""
        # Keywords that should not be valid function names
        invalid_names = [
            "def if(): pass",
            "def for(): pass", 
            "def while(): pass",
            "def class(): pass",
            "def def(): pass",
            "def import(): pass"
        ]
        
        for source in invalid_names:
            tester.assert_function_syntax_error(source)

    def test_invalid_type_annotation_syntax(self, tester):
        """Test invalid type annotation syntax"""
        # Invalid annotation syntax
        invalid_annotations = [
            "def func(x:): pass",        # Missing type
            "def func() ->: pass",       # Missing return type
            "def func(x: int=): pass",   # Missing default after annotation
            "def func(x:int:str): pass"  # Multiple colons
        ]
        
        for source in invalid_annotations:
            tester.assert_function_syntax_error(source)


class TestSection86ComplexFunctionFeatures:
    """Test complex function definition features"""
    
    @pytest.fixture
    def tester(self):
        return FunctionDefinitionTester()

    def test_function_with_all_features(self, tester):
        """Test function with multiple advanced features"""
        # Complex function with many features (without positional-only)
        complex_function = """
@cache
@validate('input')
def complex_function(
    normal: float,
    normal_default: bool = True,
    *args: int,
    keyword_only: str,
    keyword_default: dict = None,
    **kwargs: Any
) -> Optional[Dict[str, Any]]:
    \"\"\"A complex function demonstrating all parameter types.\"\"\"
    return {'result': 'complex'}
"""
        
        tree = tester.assert_function_syntax_parses(complex_function)
        assert len(tree.body) == 1
        funcdef = tree.body[0]
        assert isinstance(funcdef, ast.FunctionDef)
        
    @pytest.mark.min_version_3_8
    def test_function_with_positional_only_features(self, tester):
        """Test function with positional-only parameters (Python 3.8+)"""
        complex_posonly_function = """
@cache
@validate('input')
def complex_function(
    pos_only: int,
    /,
    normal: float,
    pos_only_default: str = 'default',
    normal_default: bool = True,
    *args: int,
    keyword_only: str,
    keyword_default: dict = None,
    **kwargs: Any
) -> Optional[Dict[str, Any]]:
    \"\"\"A complex function demonstrating all parameter types.\"\"\"
    return {'result': 'complex'}
"""
        
        tester.assert_function_syntax_parses(complex_posonly_function)

    def test_generator_function_syntax(self, tester):
        """Test generator function syntax"""
        # Generator functions with yield
        generator_functions = [
            """def simple_generator():
    yield 1""",
            
            """def count_up_to(max):
    count = 1
    while count <= max:
        yield count
        count += 1""",
        
            """def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b"""
        ]
        
        for source in generator_functions:
            tester.assert_function_syntax_parses(source)

    def test_lambda_vs_def_syntax(self, tester):
        """Test that lambda and def are distinct"""
        # Lambda expressions (different from def)
        lambda_expressions = [
            "lambda: 42",
            "lambda x: x * 2",
            "lambda x, y: x + y",
            "lambda x, y=1: x * y"
        ]
        
        # These should parse as expressions, not function definitions
        for expr in lambda_expressions:
            try:
                ast.parse(expr, mode='eval')
            except SyntaxError:
                pytest.fail(f"Lambda expression {expr!r} should parse")

    def test_closure_and_scope_syntax(self, tester):
        """Test closure syntax patterns"""
        # Closure patterns
        closure_patterns = [
            """def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter""",
            
            """def make_adder(n):
    def adder(x):
        return x + n
    return adder""",
            
            """def outer():
    x = 'outer'
    def inner():
        x = 'inner'
        def innermost():
            return x
        return innermost
    return inner"""
        ]
        
        for source in closure_patterns:
            tester.assert_function_syntax_parses(source)


class TestSection86CrossImplementationCompatibility:
    """Test function features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return FunctionDefinitionTester()

    def test_large_function_definitions(self, tester):
        """Test very large function definitions"""
        # Large function with many statements
        statements = "\n".join([f"    x_{i} = {i}" for i in range(100)])
        large_function = f"def large_func():\n{statements}\n    return x_99"
        
        tester.assert_function_syntax_parses(large_function)

    def test_deep_function_nesting(self, tester):
        """Test deep function nesting"""
        # Deeply nested functions
        nested_levels = ["def level_0():"]
        for i in range(1, 10):
            nested_levels.append("    " * i + f"def level_{i}():")
        nested_levels.append("    " * 10 + "return 'deep'")
        
        deep_nesting = "\n".join(nested_levels)
        tester.assert_function_syntax_parses(deep_nesting)

    def test_function_with_many_parameters(self, tester):
        """Test function with many parameters"""
        # Function with many parameters (reasonable limit)
        params = ", ".join([f"param_{i}=None" for i in range(50)])
        many_params = f"def func({params}): pass"
        
        tester.assert_function_syntax_parses(many_params)

    def test_function_definition_introspection(self, tester):
        """Test function definition AST introspection"""
        # Detailed AST validation
        source = """
@decorator
def test_function(a: int, b: str = 'default') -> bool:
    return True
"""
        
        funcdef = tester.get_function_def_from_source(source)
        
        # Validate AST structure
        assert funcdef.name == "test_function"
        assert len(funcdef.args.args) == 2  # a, b
        assert len(funcdef.args.defaults) == 1  # b='default'
        assert len(funcdef.decorator_list) == 1  # @decorator
        assert funcdef.returns is not None  # -> bool

    def test_function_with_many_decorators(self, tester):
        """Test function with many decorators"""
        # Many decorators (reasonable limit)
        decorators = "\n".join([f"@decorator_{i}" for i in range(20)])
        many_decorators = f"{decorators}\ndef func(): pass"
        
        tester.assert_function_syntax_parses(many_decorators)

    def test_recursive_function_patterns(self, tester):
        """Test recursive function definition patterns"""
        # Recursive function patterns
        recursive_patterns = [
            """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)""",
            
            """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)""",
            
            """def mutual_recursion_a(n):
    if n <= 0:
        return 0
    return mutual_recursion_b(n - 1)
    
def mutual_recursion_b(n):
    if n <= 0:
        return 1
    return mutual_recursion_a(n - 1)"""
        ]
        
        for source in recursive_patterns:
            tester.assert_function_syntax_parses(source)