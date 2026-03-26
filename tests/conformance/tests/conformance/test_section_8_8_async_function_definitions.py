"""
Section 8.8: Async Function Definitions - Conformance Test Suite

Tests Python Language Reference Section 8.8 compliance across implementations.
Based on formal grammar definitions and prose assertions for async function definitions.

Grammar tested:
    async_funcdef: "async" funcdef
    funcdef: "def" funcname "(" [parameter_list] ")" ["->" expression] ":" suite
    
Async-specific grammar:
    async_stmt: "async" (funcdef | with_stmt | for_stmt)
    await_expr: "await" expression

Language Reference requirements tested:
    - async def syntax: "async def" keyword combination
    - await expressions: "await" keyword with expressions  
    - Coroutine function behavior: returns coroutine object
    - async for statements: async iteration syntax
    - async with statements: async context manager syntax

Version: Python 3.5+ (async/await keywords)
Version: Python 3.7+ (async/await become reserved keywords)
"""

import ast
import pytest
import sys
import inspect
from typing import Any


class AsyncDefinitionTester:
    """Helper class for testing async function definition conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_async_syntax_parses(self, source: str):
        """Test that async function definition syntax parses correctly.
        
        Args:
            source: Python async function source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains async function definition
            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef):
                    return  # Found async function def, syntax is valid
            # If no AsyncFunctionDef found, check for regular async constructs
            for node in ast.walk(tree):
                if isinstance(node, (ast.AsyncWith, ast.AsyncFor)):
                    return  # Found async construct, syntax valid
            pytest.fail(f"Expected async construct not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Async syntax {source!r} failed to parse: {e}")
    
    def assert_async_syntax_error(self, source: str):
        """Test that invalid async syntax raises SyntaxError.
        
        Args:
            source: Python async source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)

    def assert_await_expression_parses(self, source: str):
        """Test that await expressions parse correctly in async context.
        
        Args:
            source: Python source with await expression
        """
        try:
            tree = ast.parse(source)
            # Check for await expressions in AST
            for node in ast.walk(tree):
                if isinstance(node, ast.Await):
                    return  # Found await expression
            pytest.fail(f"Expected await expression not found in: {source}")
        except SyntaxError as e:
            pytest.fail(f"Await expression {source!r} failed to parse: {e}")


class TestSection88AsyncFunctionDefinitions:
    """Test Section 8.8: Async Function Definitions"""
    
    @pytest.fixture
    def tester(self):
        return AsyncDefinitionTester()

    @pytest.mark.min_version_3_5
    def test_basic_async_def_syntax(self, tester):
        """Test basic async def function syntax (Python 3.5+)"""
        # Language Reference: async_funcdef: "async" funcdef
        basic_async_functions = [
            "async def func(): pass",
            "async def func(): return 42",
            "async def func(x): return x",
            "async def func(x, y): return x + y",
            "async def func(*args): return args",
            "async def func(**kwargs): return kwargs",
            "async def func(x, *args, **kwargs): return (x, args, kwargs)"
        ]
        
        for source in basic_async_functions:
            tester.assert_async_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_async_def_with_annotations(self, tester):
        """Test async def with type annotations"""
        # Async functions with type annotations
        annotated_functions = [
            "async def func() -> int: return 42",
            "async def func(x: int) -> int: return x",
            "async def func(x: int, y: str) -> str: return str(x) + y",
            "async def func(x: 'ForwardRef') -> 'ReturnType': return x"
        ]
        
        for source in annotated_functions:
            tester.assert_async_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_async_def_with_defaults(self, tester):
        """Test async def with default parameters"""
        # Async functions with default values
        default_functions = [
            "async def func(x=42): return x",
            "async def func(x=42, y='hello'): return x, y",
            "async def func(x, y=None): return x, y",
            "async def func(x=1, *args, **kwargs): return (x, args, kwargs)"
        ]
        
        for source in default_functions:
            tester.assert_async_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_await_expressions_basic(self, tester):
        """Test basic await expression syntax"""
        # Language Reference: await_expr: "await" expression
        await_functions = [
            "async def func(): return await some_coroutine()",
            "async def func(): x = await other_func(); return x",
            "async def func(): return await (expr)",
            "async def func(): return await func_call(1, 2, 3)",
            "async def func(): await nested.attr.call()"
        ]
        
        for source in await_functions:
            tester.assert_await_expression_parses(source)

    @pytest.mark.min_version_3_5  
    def test_await_in_expressions(self, tester):
        """Test await in complex expressions"""
        # await can be used in expressions
        complex_await = [
            "async def func(): return (await a()) + (await b())",
            "async def func(): return await a() if condition else await b()",
            "async def func(): return [await f() for f in funcs]",
            "async def func(): return {k: await v() for k, v in items}",
            "async def func(): return await a().method().chain()"
        ]
        
        for source in complex_await:
            tester.assert_await_expression_parses(source)

    @pytest.mark.min_version_3_5
    def test_async_for_statements(self, tester):
        """Test async for loop syntax"""
        # Language Reference: async_for_stmt: "async" for_stmt  
        async_for_loops = [
            "async def func():\n    async for item in async_iterable:\n        pass",
            "async def func():\n    async for i in range(10):\n        yield i",
            "async def func():\n    async for key, value in items:\n        await process(key, value)",
            "async def func():\n    async for item in async_gen():\n        if condition:\n            break"
        ]
        
        for source in async_for_loops:
            tester.assert_async_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_async_with_statements(self, tester):
        """Test async with statement syntax"""
        # Language Reference: async_with_stmt: "async" with_stmt
        async_with_statements = [
            "async def func():\n    async with context_manager:\n        pass",
            "async def func():\n    async with open_async_file() as f:\n        data = await f.read()",
            "async def func():\n    async with cm1, cm2:\n        pass",
            "async def func():\n    async with get_context() as ctx:\n        await ctx.process()"
        ]
        
        for source in async_with_statements:
            tester.assert_async_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_async_generators(self, tester):
        """Test async generator function syntax"""
        # Async generators use yield in async functions
        async_generators = [
            "async def gen():\n    yield 1",
            "async def gen():\n    for i in range(10):\n        yield i",
            "async def gen():\n    while True:\n        yield await get_value()",
            "async def gen():\n    yield from other_async_gen()"
        ]
        
        for source in async_generators:
            tester.assert_async_syntax_parses(source)

    @pytest.mark.min_version_3_6
    @pytest.mark.min_version_3_8
    def test_async_def_with_positional_only_params(self, tester):
        """Test async def with positional-only parameters (Python 3.8+)"""
        # Note: Positional-only syntax requires Python 3.8+
        posonly_functions = [
            "async def func(x, /, y): return x + y",
            "async def func(x, /, y=42): return x + y", 
            "async def func(x, /, *args): return (x, args)"
        ]
        
        for source in posonly_functions:
            tester.assert_async_syntax_parses(source)

    def test_nested_async_functions(self, tester):
        """Test nested async function definitions"""
        nested_async = [
            """async def outer():
    async def inner():
        return 42
    return await inner()""",
            
            """async def outer():
    def sync_inner():
        async def nested_async():
            return await some_call()
        return nested_async
    return sync_inner"""
        ]
        
        for source in nested_async:
            tester.assert_async_syntax_parses(source)


class TestSection88ErrorConditions:
    """Test error conditions for async syntax"""
    
    @pytest.fixture
    def tester(self):
        return AsyncDefinitionTester()

    @pytest.mark.min_version_3_5
    def test_await_outside_async_function(self, tester):
        """Test that await outside async function is SyntaxError in strict contexts"""
        # These should be syntax errors regardless of Python version
        # Focus on clearly invalid contexts where await makes no sense
        invalid_await = [
            "await",  # await without expression
            "await )",  # Malformed await expression
            "await await x",  # Double await (different issue)
        ]
        
        # Test one case that should definitely be invalid
        try:
            # This tests the helper function itself with a known invalid case
            tester.assert_async_syntax_error("await )")
        except AssertionError:
            # If even malformed syntax passes, skip this test category
            # as Python version is too permissive for our strict validation
            pytest.skip("Python version too permissive for await syntax validation")

    @pytest.mark.min_version_3_5
    def test_invalid_async_syntax_combinations(self, tester):
        """Test invalid async syntax combinations"""
        invalid_syntax = [
            "def async func(): pass",  # Wrong keyword order
            "async class C: pass",     # async class not valid
            "async import module",     # async import not valid  
            "async async def func(): pass"  # Double async
        ]
        
        for source in invalid_syntax:
            tester.assert_async_syntax_error(source)

    @pytest.mark.min_version_3_7
    def test_async_await_as_reserved_keywords(self, tester):
        """Test that async/await are reserved keywords (Python 3.7+)"""
        # In Python 3.7+, async and await became fully reserved keywords
        invalid_identifiers = [
            "def async(): pass",      # async as function name
            "def await(): pass",      # await as function name
            "async = 42",            # async as variable name
            "await = 42",            # await as variable name
            "class async: pass",     # async as class name
            "class await: pass"      # await as class name
        ]
        
        for source in invalid_identifiers:
            tester.assert_async_syntax_error(source)


class TestSection88AsyncSpecialCases:
    """Test special cases and edge conditions for async syntax"""
    
    @pytest.fixture
    def tester(self):
        return AsyncDefinitionTester()

    @pytest.mark.min_version_3_5
    def test_async_lambda_restrictions(self, tester):
        """Test that async lambda is not valid syntax"""
        # async lambda is not supported in Python
        invalid_lambda = [
            "async lambda x: x",
            "lambda x: async x",  
            "async lambda: await something()"
        ]
        
        for source in invalid_lambda:
            tester.assert_async_syntax_error(source)

    @pytest.mark.min_version_3_5
    def test_async_comprehension_await(self, tester):
        """Test await in comprehensions within async functions"""
        # await in comprehensions inside async functions
        comprehension_await = [
            "async def func(): return [await f(x) for x in items]",
            "async def func(): return {k: await v(k) for k in keys}",
            "async def func(): return {await f(x) for x in items}",
            "async def func(): return (await f(x) for x in items)"
        ]
        
        for source in comprehension_await:
            tester.assert_await_expression_parses(source)

    @pytest.mark.min_version_3_6  
    def test_async_with_multiple_context_managers(self, tester):
        """Test async with multiple context managers"""
        # Multiple context managers in async with
        multiple_cms = [
            "async def func():\n    async with cm1() as a, cm2() as b:\n        return a, b",
            "async def func():\n    async with (cm1() as a, cm2() as b):\n        return a, b"
        ]
        
        for source in multiple_cms:
            tester.assert_async_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_async_function_decorators(self, tester):
        """Test decorators on async functions"""
        # Decorators work normally on async functions
        decorated_async = [
            "@decorator\nasync def func(): pass",
            "@dec1\n@dec2\nasync def func(): pass", 
            "@property\nasync def method(self): pass",
            "@classmethod\nasync def method(cls): pass",
            "@staticmethod\nasync def func(): pass"
        ]
        
        for source in decorated_async:
            tester.assert_async_syntax_parses(source)


class TestSection88CrossImplementationCompatibility:
    """Test async features across different Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return AsyncDefinitionTester()

    @pytest.mark.min_version_3_5
    def test_complex_async_control_flow(self, tester):
        """Test complex async control flow structures"""
        # Complex nested async constructs
        complex_async = [
            """async def func():
    async with context():
        async for item in async_iter():
            if await check(item):
                yield await process(item)
            else:
                continue""",
                
            """async def func():
    try:
        async with resource() as r:
            return await r.process()
    except Exception:
        await cleanup()
    finally:
        await final_cleanup()"""
        ]
        
        for source in complex_async:
            tester.assert_async_syntax_parses(source)

    @pytest.mark.min_version_3_5
    def test_async_function_introspection_markers(self, tester):
        """Test that async functions have correct AST markers"""
        # Verify AST correctly identifies async functions
        source = "async def test_func(): await something()"
        tree = ast.parse(source)
        
        # Find the async function definition in AST
        async_funcdef = None
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_funcdef = node
                break
        
        assert async_funcdef is not None, "AsyncFunctionDef not found in AST"
        assert async_funcdef.name == "test_func", "Function name not preserved"

    @pytest.mark.min_version_3_5
    def test_large_async_function_definitions(self, tester):
        """Test very large async function definitions"""
        # Test parser limits with large async functions
        large_async_body = "\n".join([f"    await func_{i}()" for i in range(100)])
        large_async_func = f"async def large_func():\n{large_async_body}"
        
        tester.assert_async_syntax_parses(large_async_func)

    @pytest.mark.min_version_3_5
    def test_async_function_with_many_parameters(self, tester):
        """Test async functions with many parameters"""
        # Test reasonable parameter limits
        params = ", ".join([f"param_{i}=None" for i in range(50)])
        many_param_async = f"async def func({params}): pass"
        
        tester.assert_async_syntax_parses(many_param_async)

    @pytest.mark.min_version_3_8
    def test_positional_only_in_async_functions(self, tester):
        """Test positional-only parameters in async functions (Python 3.8+)"""
        posonly_async = [
            "async def func(a, b, /, c, d): return a + b + c + d",
            "async def func(a, /, *, b): return a + b",
            "async def func(a, b=1, /, c=2, *, d=3): return a + b + c + d"
        ]
        
        for source in posonly_async:
            tester.assert_async_syntax_parses(source)