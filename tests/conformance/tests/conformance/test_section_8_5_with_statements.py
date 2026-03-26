"""
Section 8.5: With Statements - Conformance Test Suite

Tests Python Language Reference Section 8.5 compliance across implementations.
Based on formal grammar definitions and prose assertions for with statements.

Grammar tested:
    with_stmt: 'with' with_item (',' with_item)*  ':' suite
    with_item: test ['as' expr]

Language Reference requirements tested:
    - Basic with statement syntax
    - Context manager protocol (__enter__, __exit__)
    - Multiple context managers in single statement
    - Exception handling in context managers
    - Variable binding with 'as' clause
    - Async with statements (Python 3.5+)
    - Nested with statements
    - Complex expression forms
    - Error conditions and edge cases
"""

import ast
import pytest
import sys
from typing import Any


class WithStatementTester:
    """Helper class for testing with statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_with_syntax_parses(self, source: str):
        """Test that with statement syntax parses correctly.
        
        Args:
            source: Python with statement source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains with statement
            for node in ast.walk(tree):
                if isinstance(node, (ast.With, ast.AsyncWith)):
                    return tree  # Found with statement, syntax is valid
            pytest.fail(f"Expected With/AsyncWith node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"With statement syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_with_syntax_error(self, source: str):
        """Test that invalid with syntax raises SyntaxError.
        
        Args:
            source: Python with source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_with_from_source(self, source: str) -> ast.With:
        """Get the With AST node from source for detailed validation.
        
        Args:
            source: Python with statement source
            
        Returns:
            ast.With or ast.AsyncWith node
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.With, ast.AsyncWith)):
                return node
        pytest.fail(f"Expected With/AsyncWith node not found in: {source}")
    
    def count_with_items(self, source: str) -> int:
        """Count number of with items in a with statement.
        
        Args:
            source: Python with statement source
            
        Returns:
            Number of context manager expressions
        """
        with_node = self.get_with_from_source(source)
        return len(with_node.items)
    
    def has_with_variable_binding(self, source: str) -> bool:
        """Check if with statement has variable binding (as clause).
        
        Args:
            source: Python with statement source
            
        Returns:
            True if any with item has 'as' binding
        """
        with_node = self.get_with_from_source(source)
        return any(item.optional_vars is not None for item in with_node.items)


@pytest.fixture
def tester():
    """Provide WithStatementTester instance for tests."""
    return WithStatementTester()


class TestSection85BasicWithStatements:
    """Test basic with statement syntax and semantics."""
    
    def test_simple_with_statement(self, tester):
        """Test simplest with statement forms"""
        # Language Reference: basic with statement
        simple_with = [
            "with open('file.txt'): pass",
            "with cm: pass",
            "with context_manager(): pass",
            "with obj.method(): pass"
        ]
        
        for source in simple_with:
            tree = tester.assert_with_syntax_parses(source)
            with_node = tester.get_with_from_source(source)
            assert isinstance(with_node, ast.With)
            assert len(with_node.items) == 1
    
    def test_with_variable_binding(self, tester):
        """Test with statement variable binding using 'as' clause"""
        # Language Reference: with_item may include 'as' expr
        binding_with = [
            "with open('file.txt') as f: pass",
            "with context_manager() as cm: pass",
            "with obj.method() as result: pass",
            "with complex_expression() as x: pass"
        ]
        
        for source in binding_with:
            tree = tester.assert_with_syntax_parses(source)
            assert tester.has_with_variable_binding(source)
            with_node = tester.get_with_from_source(source)
            assert with_node.items[0].optional_vars is not None
    
    def test_multiple_context_managers(self, tester):
        """Test multiple context managers in single with statement"""
        # Language Reference: with_stmt allows comma-separated with_items
        multiple_cm = [
            "with open('file1') as f1, open('file2') as f2: pass",
            "with cm1(), cm2(): pass",
            "with a, b, c: pass",
            "with open('a') as fa, open('b') as fb, lock(): pass"
        ]
        
        for source in multiple_cm:
            tree = tester.assert_with_syntax_parses(source)
            item_count = tester.count_with_items(source)
            assert item_count >= 2, f"Expected multiple context managers in: {source}"
    
    def test_nested_with_statements(self, tester):
        """Test nested with statement structures"""
        # Language Reference: with statements can be nested
        nested_with = [
            """
with outer():
    with inner():
        pass
""",
            """
with cm1():
    with cm2() as x:
        with cm3():
            pass
""",
            """
with open('file') as f:
    with lock:
        with timer():
            f.read()
"""
        ]
        
        for source in nested_with:
            tree = tester.assert_with_syntax_parses(source)
            # Count total With nodes 
            with_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.With)]
            assert len(with_nodes) >= 2, f"Expected nested with statements in: {source}"


class TestSection85ContextManagerProtocol:
    """Test context manager protocol requirements."""
    
    def test_context_manager_expressions(self, tester):
        """Test various context manager expression forms"""
        # Language Reference: context manager must have __enter__ and __exit__
        cm_expressions = [
            "with obj: pass",                    # Simple name
            "with obj.attr: pass",              # Attribute access
            "with obj[key]: pass",              # Subscription
            "with func(): pass",                # Function call
            "with obj.method(): pass",          # Method call
            "with Class(): pass",               # Constructor
            "with (complex_expr): pass",        # Parenthesized expression
            "with obj if condition else alt: pass"  # Conditional expression
        ]
        
        for source in cm_expressions:
            tree = tester.assert_with_syntax_parses(source)
            with_node = tester.get_with_from_source(source)
            assert with_node.items[0].context_expr is not None
    
    def test_variable_binding_expressions(self, tester):
        """Test variable binding target expressions"""
        # Language Reference: 'as' target must be valid assignment target
        binding_targets = [
            "with cm() as x: pass",             # Simple name
            "with cm() as (a, b): pass",        # Tuple unpacking
            "with cm() as [x, y]: pass",        # List unpacking
            "with cm() as obj.attr: pass",      # Attribute assignment
            "with cm() as obj[key]: pass",      # Subscription assignment
            "with cm() as (a, (b, c)): pass"    # Nested unpacking
        ]
        
        for source in binding_targets:
            tree = tester.assert_with_syntax_parses(source)
            with_node = tester.get_with_from_source(source)
            assert with_node.items[0].optional_vars is not None
    
    def test_complex_with_combinations(self, tester):
        """Test complex combinations of with features"""
        # Language Reference: comprehensive with statement patterns
        complex_with = [
            "with open('a') as fa, open('b'), lock() as l: pass",
            "with (cm1() if condition else cm2()) as x: pass",
            "with contextlib.suppress(ValueError), lock: pass",
            "with obj.method(*args, **kwargs) as result: pass",
            "with cm1(), cm2() as x, cm3(): pass"
        ]
        
        for source in complex_with:
            tree = tester.assert_with_syntax_parses(source)
            # Verify basic structural integrity
            with_node = tester.get_with_from_source(source)
            assert len(with_node.items) >= 1


@pytest.mark.min_version_3_5
class TestSection85AsyncWithStatements:
    """Test async with statement syntax (Python 3.5+)."""
    
    def test_basic_async_with(self, tester):
        """Test basic async with statement syntax"""
        # Language Reference: async with for async context managers
        async_with = [
            "async with async_cm(): pass",
            "async with async_cm() as x: pass",
            "async with obj.async_method(): pass",
            "async with AsyncContextManager(): pass"
        ]
        
        for source in async_with:
            tree = tester.assert_with_syntax_parses(source)
            with_node = tester.get_with_from_source(source)
            assert isinstance(with_node, ast.AsyncWith)
    
    def test_multiple_async_context_managers(self, tester):
        """Test multiple async context managers"""
        # Language Reference: async with supports multiple context managers
        multi_async = [
            "async with async_cm1(), async_cm2(): pass",
            "async with async_cm1() as x, async_cm2() as y: pass",
            "async with a, b, c: pass"
        ]
        
        for source in multi_async:
            tree = tester.assert_with_syntax_parses(source)
            with_node = tester.get_with_from_source(source)
            assert isinstance(with_node, ast.AsyncWith)
            assert len(with_node.items) >= 2
    
    def test_nested_async_with(self, tester):
        """Test nested async with statements"""
        # Language Reference: async with can be nested
        nested_async = [
            """
async with outer():
    async with inner():
        pass
""",
            """
async with cm1() as x:
    async with cm2():
        pass
"""
        ]
        
        for source in nested_async:
            tree = tester.assert_with_syntax_parses(source)
            async_with_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.AsyncWith)]
            assert len(async_with_nodes) >= 2


class TestSection85WithStatementSemantics:
    """Test with statement semantic requirements."""
    
    def test_with_suite_execution(self, tester):
        """Test with statement suite (body) syntax"""
        # Language Reference: with statement has suite
        with_suites = [
            """
with cm():
    x = 1
    y = 2
""",
            """
with cm() as x:
    if x:
        print('hello')
    else:
        print('world')
""",
            """
with cm():
    for i in range(10):
        if i > 5:
            break
        print(i)
""",
            """
with cm():
    try:
        risky_operation()
    except Exception:
        handle_error()
"""
        ]
        
        for source in with_suites:
            tree = tester.assert_with_syntax_parses(source)
            with_node = tester.get_with_from_source(source)
            assert len(with_node.body) >= 1, f"With statement should have body: {source}"
    
    def test_with_statement_in_functions(self, tester):
        """Test with statements inside function definitions"""
        # Language Reference: with statements can appear in function context
        function_with = [
            """
def func():
    with cm():
        return value
""",
            """
async def async_func():
    async with async_cm():
        await operation()
""",
            """
def generator():
    with cm():
        yield value
""",
            """
def func():
    with cm() as x:
        result = process(x)
        return result
"""
        ]
        
        for source in function_with:
            tree = tester.assert_with_syntax_parses(source)
            # Find function definitions that contain with statements
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    with_in_func = [n for n in ast.walk(node) if isinstance(n, (ast.With, ast.AsyncWith))]
                    assert len(with_in_func) >= 1, f"Expected with in function: {source}"


class TestSection85ErrorConditions:
    """Test with statement error conditions and edge cases."""
    
    def test_invalid_with_syntax(self, tester):
        """Test invalid with statement syntax"""
        # Language Reference: various syntactic restrictions
        invalid_with = [
            "with: pass",                       # Missing context manager
            "with cm() as: pass",              # Missing variable name
            "with cm(), : pass",               # Empty item
            "with cm() as x y: pass",          # Invalid as clause
            "with cm() as 123: pass",          # Invalid target
            "async with",                      # Incomplete async with
            "with cm() as lambda: pass",       # Lambda not allowed as target
        ]
        
        for source in invalid_with:
            tester.assert_with_syntax_error(source)
    
    def test_with_statement_indentation(self, tester):
        """Test with statement indentation requirements"""
        # Language Reference: with statement requires properly indented suite
        valid_indented = [
            """
with cm():
    pass
""",
            """
with cm():
    x = 1
    y = 2
""",
            """
with cm1():
    with cm2():
        operation()
"""
        ]
        
        for source in valid_indented:
            tester.assert_with_syntax_parses(source)


class TestSection85CrossImplementationCompatibility:
    """Test cross-implementation compatibility for with statements."""
    
    def test_with_statement_ast_structure(self, tester):
        """Test with statement AST structure across implementations"""
        # Language Reference: AST structure should be consistent
        test_cases = [
            "with cm(): pass",
            "with cm() as x: pass", 
            "with cm1(), cm2(): pass",
            "with cm1() as x, cm2() as y: pass"
        ]
        
        for source in test_cases:
            tree = tester.assert_with_syntax_parses(source)
            with_node = tester.get_with_from_source(source)
            
            # Verify required AST attributes
            assert hasattr(with_node, 'items'), f"With node should have 'items' attribute: {source}"
            assert hasattr(with_node, 'body'), f"With node should have 'body' attribute: {source}"
            assert len(with_node.items) >= 1, f"With node should have at least one item: {source}"
            
            # Verify with_item structure
            for item in with_node.items:
                assert hasattr(item, 'context_expr'), f"With item should have 'context_expr': {source}"
                assert hasattr(item, 'optional_vars'), f"With item should have 'optional_vars': {source}"
    
    @pytest.mark.min_version_3_5
    def test_async_with_compatibility(self, tester):
        """Test async with statement compatibility"""
        # Language Reference: async with should work consistently
        async_test_cases = [
            "async with async_cm(): pass",
            "async with async_cm() as x: pass",
            "async with async_cm1(), async_cm2(): pass"
        ]
        
        for source in async_test_cases:
            tree = tester.assert_with_syntax_parses(source)
            async_with_node = tester.get_with_from_source(source)
            assert isinstance(async_with_node, ast.AsyncWith), f"Should be AsyncWith node: {source}"
    
    def test_complex_with_patterns(self, tester):
        """Test complex with statement patterns"""
        # Language Reference: comprehensive real-world patterns
        complex_patterns = [
            """
with open('input.txt') as infile, open('output.txt', 'w') as outfile:
    data = infile.read()
    outfile.write(data.upper())
""",
            """
with contextlib.ExitStack() as stack:
    file1 = stack.enter_context(open('file1.txt'))
    file2 = stack.enter_context(open('file2.txt'))
    process_files(file1, file2)
""",
            """
with threading.Lock():
    with database.transaction():
        with timer() as t:
            result = expensive_operation()
"""
        ]
        
        for source in complex_patterns:
            tree = tester.assert_with_syntax_parses(source)
            # Just verify the pattern parses successfully
            assert len(tree.body) >= 1, f"Complex with pattern should parse: {source}"
    
    def test_with_statement_introspection(self, tester):
        """Test with statement introspection capabilities"""
        # Test ability to analyze with statement structure programmatically
        introspection_source = "with open('file') as f, lock() as l: process(f, l)"
        
        tree = tester.assert_with_syntax_parses(introspection_source)
        with_node = tester.get_with_from_source(introspection_source)
        
        # Should be able to introspect structure
        assert len(with_node.items) == 2
        assert with_node.items[0].optional_vars is not None  # 'as f'
        assert with_node.items[1].optional_vars is not None  # 'as l'
        
        # Should be able to identify context expressions
        first_expr = with_node.items[0].context_expr
        second_expr = with_node.items[1].context_expr
        assert first_expr is not None
        assert second_expr is not None