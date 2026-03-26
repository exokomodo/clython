"""
Section 7.8: Raise Statements - Conformance Test Suite

Tests Python Language Reference Section 7.8 compliance across implementations.
Based on formal grammar definitions and prose assertions for raise statements.

Grammar tested:
    raise_stmt: 'raise' [test ['from' test]]

Language Reference requirements tested:
    - Basic raise statement syntax
    - Raising exceptions with and without arguments
    - Exception chaining with 'from' clause (Python 3.0+)  
    - Re-raising current exception (bare raise)
    - Exception instance vs exception class raising
    - Error conditions and invalid raise usage
    - Integration with try/except statement context
    - Traceback preservation and modification
"""

import ast
import pytest
import sys
from typing import Any


class RaiseStatementTester:
    """Helper class for testing raise statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_raise_syntax_parses(self, source: str):
        """Test that raise statement syntax parses correctly.
        
        Args:
            source: Python raise statement source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains raise statement
            for node in ast.walk(tree):
                if isinstance(node, ast.Raise):
                    return tree  # Found raise statement, syntax is valid
            pytest.fail(f"Expected Raise node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Raise statement syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_raise_syntax_error(self, source: str):
        """Test that invalid raise syntax raises SyntaxError.
        
        Args:
            source: Python raise source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_raise_from_source(self, source: str) -> ast.Raise:
        """Get the Raise AST node from source for detailed validation.
        
        Args:
            source: Python raise statement source
            
        Returns:
            ast.Raise node
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise):
                return node
        pytest.fail(f"Expected Raise node not found in: {source}")
    
    def has_raise_exception(self, source: str) -> bool:
        """Check if raise statement has exception expression.
        
        Args:
            source: Python raise statement source
            
        Returns:
            True if raise has exception expression
        """
        raise_node = self.get_raise_from_source(source)
        return raise_node.exc is not None
    
    def has_raise_from_clause(self, source: str) -> bool:
        """Check if raise statement has 'from' clause.
        
        Args:
            source: Python raise statement source
            
        Returns:
            True if raise has 'from' clause
        """
        raise_node = self.get_raise_from_source(source)
        return raise_node.cause is not None


@pytest.fixture
def tester():
    """Provide RaiseStatementTester instance for tests."""
    return RaiseStatementTester()


class TestSection78BasicRaiseStatements:
    """Test basic raise statement syntax and semantics."""
    
    def test_bare_raise_statement(self, tester):
        """Test bare raise statement (re-raise current exception)"""
        # Language Reference: bare raise re-raises current exception
        bare_raise_context = """
try:
    risky_operation()
except Exception:
    raise
"""
        
        tree = tester.assert_raise_syntax_parses(bare_raise_context)
        raise_node = tester.get_raise_from_source(bare_raise_context)
        assert raise_node.exc is None, "Bare raise should have no exception expression"
        assert raise_node.cause is None, "Bare raise should have no cause"
    
    def test_simple_exception_raising(self, tester):
        """Test raising simple exceptions"""
        # Language Reference: raise with exception class or instance
        simple_raises = [
            "raise Exception",
            "raise ValueError",
            "raise RuntimeError",
            "raise TypeError",
            "raise KeyError"
        ]
        
        for source in simple_raises:
            tree = tester.assert_raise_syntax_parses(source)
            assert tester.has_raise_exception(source)
            assert not tester.has_raise_from_clause(source)
    
    def test_exception_with_arguments(self, tester):
        """Test raising exceptions with arguments"""
        # Language Reference: raise with exception constructor call
        exception_with_args = [
            "raise ValueError('Invalid value')",
            "raise RuntimeError('Something went wrong')",
            "raise TypeError('Expected string, got int')",
            "raise KeyError('missing key')",
            "raise Exception('General error')",
            "raise CustomException('custom message', 42)",
            "raise ValueError(f'Error in {func_name}')"
        ]
        
        for source in exception_with_args:
            tree = tester.assert_raise_syntax_parses(source)
            raise_node = tester.get_raise_from_source(source)
            assert raise_node.exc is not None
            # Should be a function call (exception constructor)
            assert isinstance(raise_node.exc, ast.Call) or isinstance(raise_node.exc, ast.Name)
    
    def test_exception_instance_raising(self, tester):
        """Test raising pre-constructed exception instances"""
        # Language Reference: raise with exception instance
        instance_raises = [
            "raise ValueError('message')",
            "raise exception_instance",
            "raise get_exception()",
            "raise exceptions[0]",
            "raise obj.error",
            "raise Exception() if condition else RuntimeError()"
        ]
        
        for source in instance_raises:
            tree = tester.assert_raise_syntax_parses(source)
            assert tester.has_raise_exception(source)


@pytest.mark.min_version_3_0  
class TestSection78ExceptionChaining:
    """Test exception chaining with 'from' clause (Python 3.0+)."""
    
    def test_raise_from_exception(self, tester):
        """Test raise ... from ... syntax for exception chaining"""
        # Language Reference: 'from' clause for explicit chaining
        chaining_raises = [
            "raise ValueError('new error') from original_error",
            "raise RuntimeError() from e",
            "raise CustomException('wrapped') from caught_exception",
            "raise Exception('general') from None",  # Suppress chaining
            "raise TypeError() from get_cause()"
        ]
        
        for source in chaining_raises:
            tree = tester.assert_raise_syntax_parses(source)
            raise_node = tester.get_raise_from_source(source)
            assert raise_node.exc is not None, f"Chained raise should have exception: {source}"
            assert raise_node.cause is not None, f"Chained raise should have cause: {source}"
    
    def test_suppress_chaining_with_none(self, tester):
        """Test suppressing exception chaining with 'from None'"""
        # Language Reference: 'from None' suppresses exception chaining
        suppress_chaining = [
            "raise ValueError('new') from None",
            "raise RuntimeError() from None",
            "raise CustomError('message') from None"
        ]
        
        for source in suppress_chaining:
            tree = tester.assert_raise_syntax_parses(source)
            raise_node = tester.get_raise_from_source(source)
            assert raise_node.cause is not None, f"'from None' should have cause node: {source}"
            # The cause should be a Constant(None) or NameConstant(None) node
            assert isinstance(raise_node.cause, (ast.Constant, ast.NameConstant))
    
    def test_complex_chaining_expressions(self, tester):
        """Test complex expressions in exception chaining"""
        # Language Reference: chaining accepts any expression
        complex_chaining = [
            "raise ValueError() from exceptions[index]",
            "raise RuntimeError() from obj.error",
            "raise TypeError() from get_original_error()",
            "raise Exception() from (e if condition else None)",
            "raise CustomError() from chain.cause"
        ]
        
        for source in complex_chaining:
            tree = tester.assert_raise_syntax_parses(source)
            assert tester.has_raise_from_clause(source)


class TestSection78RaiseInContext:
    """Test raise statements in different contexts."""
    
    def test_raise_in_except_blocks(self, tester):
        """Test raise statements inside except blocks"""
        # Language Reference: raise behavior in exception handlers
        except_raises = [
            """
try:
    operation()
except ValueError:
    raise RuntimeError('Wrapped error')
""",
            """
try:
    risky_call()
except Exception as e:
    raise ValueError('New error') from e
""",
            """
try:
    process()
except (TypeError, ValueError):
    raise
""",
            """
try:
    action()
except Exception:
    log_error()
    raise  # Re-raise current exception
"""
        ]
        
        for source in except_raises:
            tree = tester.assert_raise_syntax_parses(source)
            # Find raise statements within try/except structure
            raise_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Raise)]
            assert len(raise_nodes) >= 1, f"Should contain raise statement: {source}"
    
    def test_raise_in_functions(self, tester):
        """Test raise statements inside function definitions"""
        # Language Reference: raise statements can appear in any function context
        function_raises = [
            """
def validate(value):
    if not value:
        raise ValueError('Invalid value')
""",
            """
async def async_validate(data):
    if not data:
        raise RuntimeError('Empty data')
""",
            """
def process():
    try:
        risky_operation()
    except Exception as e:
        raise ProcessingError('Failed') from e
""",
            """
def generator():
    try:
        yield value
    except GeneratorExit:
        raise StopIteration
"""
        ]
        
        for source in function_raises:
            tree = tester.assert_raise_syntax_parses(source)
            # Find function definitions that contain raise statements
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    raises_in_func = [n for n in ast.walk(node) if isinstance(n, ast.Raise)]
                    assert len(raises_in_func) >= 1, f"Expected raise in function: {source}"
    
    def test_raise_in_finally_blocks(self, tester):
        """Test raise statements in finally blocks"""
        # Language Reference: raise can appear in finally blocks
        finally_raises = [
            """
try:
    operation()
finally:
    if error_condition:
        raise CleanupError('Cleanup failed')
""",
            """
try:
    risky_call()
except Exception:
    handle_error()
finally:
    raise FinalError('Always fails')
"""
        ]
        
        for source in finally_raises:
            tree = tester.assert_raise_syntax_parses(source)
            # Verify finally blocks contain raise statements
            finally_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
            assert len(finally_nodes) >= 1, f"Should have try statement: {source}"


class TestSection78RaiseExpressionForms:
    """Test various expression forms in raise statements."""
    
    def test_complex_exception_expressions(self, tester):
        """Test complex expressions for exception raising"""
        # Language Reference: raise accepts any expression that evaluates to exception
        complex_expressions = [
            "raise exceptions[error_type]",
            "raise obj.get_exception()",
            "raise factory.create_error(message)",
            "raise (ValueError if condition else TypeError)(msg)",
            "raise exception_class(*args, **kwargs)",
            "raise getattr(module, exception_name)()",
            "raise exception if exception else RuntimeError()"
        ]
        
        for source in complex_expressions:
            tree = tester.assert_raise_syntax_parses(source)
            raise_node = tester.get_raise_from_source(source)
            assert raise_node.exc is not None, f"Should have exception expression: {source}"
    
    def test_exception_attribute_access(self, tester):
        """Test raising exceptions via attribute access"""
        # Language Reference: exception can be accessed via attributes
        attribute_raises = [
            "raise module.CustomError('message')",
            "raise pkg.exceptions.ValidationError()",
            "raise self.error_class('error')",
            "raise obj.exception",
            "raise errors.HTTP_404('Not found')"
        ]
        
        for source in attribute_raises:
            tree = tester.assert_raise_syntax_parses(source)
            assert tester.has_raise_exception(source)
    
    def test_exception_subscript_access(self, tester):
        """Test raising exceptions via subscript access"""
        # Language Reference: exception can be accessed via subscripting
        subscript_raises = [
            "raise exceptions['ValueError']('message')",
            "raise error_classes[error_type]()",
            "raise exception_map[key]",
            "raise errors[status_code](description)"
        ]
        
        for source in subscript_raises:
            tree = tester.assert_raise_syntax_parses(source)
            assert tester.has_raise_exception(source)


class TestSection78ErrorConditions:
    """Test raise statement error conditions and edge cases."""
    
    def test_invalid_raise_syntax(self, tester):
        """Test invalid raise statement syntax"""
        # Language Reference: various syntactic restrictions
        invalid_raises = [
            "raise from error",                 # Missing exception before 'from'
            "raise ValueError from",            # Missing cause after 'from'
            "raise from",                       # Both missing
            "raise ValueError() from from e",   # Multiple 'from' keywords
            "raise ValueError TypeError",       # Multiple exceptions without comma
            "raise ValueError() from from",     # Invalid from clause
        ]
        
        for source in invalid_raises:
            tester.assert_raise_syntax_error(source)
    
    def test_raise_indentation_requirements(self, tester):
        """Test raise statement indentation requirements"""
        # Language Reference: raise statement follows normal indentation rules
        valid_indented_raises = [
            """
if condition:
    raise ValueError('error')
""",
            """
try:
    operation()
except Exception:
    raise RuntimeError('wrapped')
""",
            """
def function():
    if error:
        raise CustomError()
"""
        ]
        
        for source in valid_indented_raises:
            tester.assert_raise_syntax_parses(source)
    
    def test_bare_raise_outside_except(self, tester):
        """Test that bare raise has special semantic meaning"""
        # Note: Bare raise outside except block is syntactically valid 
        # but semantically invalid (runtime error). Test syntax only.
        bare_raise_contexts = [
            "raise",  # Syntactically valid, runtime error
            """
def func():
    raise
""",
            """
if condition:
    raise
"""
        ]
        
        for source in bare_raise_contexts:
            # Should parse successfully (syntax is valid)
            tree = tester.assert_raise_syntax_parses(source)
            raise_node = tester.get_raise_from_source(source)
            assert raise_node.exc is None, "Bare raise should have no exception"


class TestSection78CrossImplementationCompatibility:
    """Test cross-implementation compatibility for raise statements."""
    
    def test_raise_statement_ast_structure(self, tester):
        """Test raise statement AST structure across implementations"""
        # Language Reference: AST structure should be consistent
        test_cases = [
            "raise ValueError()",
            "raise exception",
            "raise ValueError() from e",
            "raise"
        ]
        
        for source in test_cases:
            tree = tester.assert_raise_syntax_parses(source)
            raise_node = tester.get_raise_from_source(source)
            
            # Verify required AST attributes
            assert hasattr(raise_node, 'exc'), f"Raise node should have 'exc' attribute: {source}"
            assert hasattr(raise_node, 'cause'), f"Raise node should have 'cause' attribute: {source}"
            
            # exc and cause should be None or AST nodes
            assert raise_node.exc is None or isinstance(raise_node.exc, ast.AST)
            assert raise_node.cause is None or isinstance(raise_node.cause, ast.AST)
    
    def test_complex_raise_patterns(self, tester):
        """Test complex raise statement patterns"""
        # Language Reference: comprehensive real-world patterns
        complex_patterns = [
            """
try:
    response = api_call()
    if response.status_code != 200:
        raise HTTPError(f'Status {response.status_code}') from None
except ConnectionError as e:
    raise APIConnectionError('Failed to connect') from e
except Timeout as e:
    raise APITimeoutError('Request timed out') from e
""",
            """
def validate_user_input(data):
    if not isinstance(data, dict):
        raise TypeError('Expected dict, got {}'.format(type(data).__name__))
    
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in data:
            raise ValueError(f'Missing required field: {field}')
    
    if '@' not in data['email']:
        raise ValueError('Invalid email format')
""",
            """
async def process_batch(items):
    errors = []
    for i, item in enumerate(items):
        try:
            await process_item(item)
        except ProcessingError as e:
            errors.append(f'Item {i}: {e}')
    
    if errors:
        error_msg = '\\n'.join(errors)
        raise BatchProcessingError(f'Failed to process {len(errors)} items:\\n{error_msg}')
"""
        ]
        
        for source in complex_patterns:
            tree = tester.assert_raise_syntax_parses(source)
            # Just verify the pattern parses successfully
            assert len(tree.body) >= 1, f"Complex raise pattern should parse: {source}"
    
    def test_raise_statement_introspection(self, tester):
        """Test raise statement introspection capabilities"""
        # Test ability to analyze raise statement structure programmatically
        introspection_source = "raise CustomError('message') from original_exception"
        
        tree = tester.assert_raise_syntax_parses(introspection_source)
        raise_node = tester.get_raise_from_source(introspection_source)
        
        # Should be able to introspect structure
        assert raise_node.exc is not None, "Should have exception expression"
        assert raise_node.cause is not None, "Should have cause expression"
        
        # Should be able to identify exception type
        assert isinstance(raise_node.exc, ast.Call), "Exception should be function call"
        assert isinstance(raise_node.cause, ast.Name), "Cause should be name reference"
    
    def test_exception_chaining_compatibility(self, tester):
        """Test exception chaining across Python versions"""
        # Test that chaining syntax is consistently handled
        chaining_test_cases = [
            "raise ValueError() from e",
            "raise RuntimeError('error') from None",
            "raise Exception() from get_cause()"
        ]
        
        for source in chaining_test_cases:
            tree = tester.assert_raise_syntax_parses(source)
            raise_node = tester.get_raise_from_source(source)
            
            # Chaining should always have both exc and cause
            assert raise_node.exc is not None, f"Chained raise should have exception: {source}"
            assert raise_node.cause is not None, f"Chained raise should have cause: {source}"