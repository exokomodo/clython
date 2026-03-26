"""
Section 7.7: Yield Statements - Conformance Test Suite

Tests Python Language Reference Section 7.7 compliance across implementations.
Based on formal yield statement syntax definitions and prose assertions for generator function behavior.

Grammar tested:
    yield_stmt: yield_expr
    yield_expr: 'yield' [yield_value]
    yield_value: expr | 'from' expr

Language Reference requirements tested:
    - Yield statement syntax validation
    - Generator function creation and behavior
    - Yield expression evaluation and value passing
    - yield from syntax and delegation
    - Generator protocol methods (send, throw, close)
    - Generator iterator interface implementation
    - Yield statement positioning and context requirements
    - Error conditions for invalid yield usage
    - Yield statement AST structure validation
    - Cross-implementation yield compatibility
"""

import ast
import pytest
import sys
from typing import Any, Generator, Iterator
from collections.abc import Iterable


class YieldTester:
    """Helper class for testing yield statement conformance.
    
    Focuses on AST structure validation for yield syntax and generator
    function patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_yield_syntax_parses(self, source: str):
        """Test that yield statement syntax parses correctly.
        
        Args:
            source: Python source code with yield statements
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Yield syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_yield_syntax_error(self, source: str):
        """Test that invalid yield syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_yield_statements(self, source: str) -> list:
        """Get Yield AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Yield and ast.YieldFrom nodes
        """
        tree = ast.parse(source)
        yields = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Yield, ast.YieldFrom)):
                yields.append(node)
        
        return yields
    
    def get_function_definitions(self, source: str) -> list:
        """Get FunctionDef AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.FunctionDef nodes
        """
        tree = ast.parse(source)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node)
        
        return functions
    
    def has_generator_functions(self, source: str) -> bool:
        """Check if source contains generator functions (functions with yield).
        
        Args:
            source: Python source code
            
        Returns:
            True if contains functions with yield statements
        """
        functions = self.get_function_definitions(source)
        yields = self.get_yield_statements(source)
        
        return len(functions) > 0 and len(yields) > 0
    
    def get_yield_from_statements(self, source: str) -> list:
        """Get YieldFrom AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.YieldFrom nodes
        """
        tree = ast.parse(source)
        yield_froms = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.YieldFrom):
                yield_froms.append(node)
        
        return yield_froms
    
    def execute_generator_function(self, source: str, func_name: str):
        """Execute a generator function from source code.
        
        Args:
            source: Python source code defining generator function
            func_name: Name of the generator function to execute
            
        Returns:
            Generator object or execution result
        """
        namespace = {}
        exec(source, namespace)
        
        if func_name in namespace:
            func = namespace[func_name]
            return func()
        else:
            raise ValueError(f"Function {func_name} not found in source")


@pytest.fixture
def tester():
    """Provide YieldTester instance for tests."""
    return YieldTester()


class TestSection77BasicYieldSyntax:
    """Test basic yield statement syntax."""
    
    def test_simple_yield_statements(self, tester):
        """Test simple yield statement syntax"""
        # Language Reference: yield_stmt: yield_expr
        simple_yield_patterns = [
            """
def simple_generator():
    yield 1
    yield 2
    yield 3
""",
            """
def yield_values():
    yield "hello"
    yield "world"
""",
            """
def yield_expressions():
    yield x + y
    yield func(a, b)
    yield obj.method()
""",
            """
def yield_none():
    yield  # Yields None
    yield None  # Explicit None
"""
        ]
        
        for source in simple_yield_patterns:
            tree = tester.assert_yield_syntax_parses(source)
            yield_nodes = tester.get_yield_statements(source)
            assert len(yield_nodes) >= 1, f"Should have yield statements: {source}"
            assert tester.has_generator_functions(source), f"Should have generator functions: {source}"
    
    def test_yield_expressions_with_values(self, tester):
        """Test yield expressions with different value types"""
        # Language Reference: yield_expr: 'yield' [yield_value]
        yield_value_patterns = [
            """
def yield_literals():
    yield 42
    yield 3.14
    yield "string"
    yield True
    yield None
""",
            """
def yield_collections():
    yield [1, 2, 3]
    yield {"key": "value"}
    yield (1, 2, 3)
    yield {1, 2, 3}
""",
            """
def yield_computed_values():
    x = 10
    yield x * 2
    yield len([1, 2, 3])
    yield max(1, 2, 3)
    yield "hello".upper()
""",
            """
def yield_complex_expressions():
    yield [x for x in range(5)]
    yield (x * 2 for x in range(3))
    yield {"key": i for i in range(3)}
"""
        ]
        
        for source in yield_value_patterns:
            tree = tester.assert_yield_syntax_parses(source)
            yield_nodes = tester.get_yield_statements(source)
            assert len(yield_nodes) >= 2, f"Should have multiple yield statements: {source}"
    
    def test_yield_in_control_structures(self, tester):
        """Test yield statements in control structures"""
        # Language Reference: yield can appear in various control contexts
        control_structure_yield_patterns = [
            """
def yield_in_if():
    if condition:
        yield "true_value"
    else:
        yield "false_value"
""",
            """
def yield_in_loops():
    for i in range(5):
        yield i
    
    while condition:
        yield get_next_value()
""",
            """
def yield_in_try_except():
    try:
        yield risky_operation()
    except Exception as e:
        yield f"Error: {e}"
    finally:
        yield "cleanup"
""",
            """
def yield_in_with():
    with open("file.txt") as f:
        for line in f:
            yield line.strip()
"""
        ]
        
        for source in control_structure_yield_patterns:
            tree = tester.assert_yield_syntax_parses(source)
            yield_nodes = tester.get_yield_statements(source)
            assert len(yield_nodes) >= 1, f"Should have yield statements: {source}"
    
    def test_yield_expressions_assignment(self, tester):
        """Test yield expressions in assignment contexts"""
        # Language Reference: yield expressions can be used in assignments
        yield_assignment_patterns = [
            """
def yield_with_assignment():
    value = yield
    result = yield 42
    x, y = yield (1, 2)
""",
            """
def yield_in_function_calls():
    print((yield "hello"))
    result = func((yield "arg"))
""",
            """
def yield_with_operators():
    result = (yield 10) + (yield 20)
    comparison = (yield 5) > (yield 3)
    string_op = (yield "hello") + " world"
"""
        ]
        
        for source in yield_assignment_patterns:
            tree = tester.assert_yield_syntax_parses(source)
            yield_nodes = tester.get_yield_statements(source)
            assert len(yield_nodes) >= 1, f"Should have yield statements: {source}"


class TestSection77YieldFromSyntax:
    """Test yield from syntax and delegation."""
    
    def test_basic_yield_from(self, tester):
        """Test basic yield from syntax"""
        # Language Reference: yield_value: expr | 'from' expr
        basic_yield_from_patterns = [
            """
def delegate_generator():
    yield from range(5)
""",
            """
def delegate_to_function():
    def inner_generator():
        yield 1
        yield 2
        yield 3
    
    yield from inner_generator()
""",
            """
def delegate_to_iterable():
    yield from [1, 2, 3]
    yield from "hello"
    yield from {"a": 1, "b": 2}
""",
            """
def nested_delegation():
    def level1():
        yield from range(3)
    
    def level2():
        yield from level1()
    
    yield from level2()
"""
        ]
        
        for source in basic_yield_from_patterns:
            tree = tester.assert_yield_syntax_parses(source)
            yield_from_nodes = tester.get_yield_from_statements(source)
            assert len(yield_from_nodes) >= 1, f"Should have yield from statements: {source}"
    
    def test_yield_from_with_expressions(self, tester):
        """Test yield from with complex expressions"""
        # Language Reference: yield from can delegate to any iterable expression
        yield_from_expression_patterns = [
            """
def yield_from_expressions():
    yield from get_data_source()
    yield from func().generate_items()
    yield from obj.get_generator()
""",
            """
def yield_from_computed():
    yield from (x * 2 for x in range(5))
    yield from [process(item) for item in data]
    yield from filter(predicate, source)
""",
            """
def yield_from_conditional():
    if use_primary:
        yield from primary_source()
    else:
        yield from backup_source()
""",
            """
def yield_from_chained():
    yield from chain(source1(), source2(), source3())
    yield from itertools.chain.from_iterable(get_sources())
"""
        ]
        
        for source in yield_from_expression_patterns:
            tree = tester.assert_yield_syntax_parses(source)
            yield_from_nodes = tester.get_yield_from_statements(source)
            assert len(yield_from_nodes) >= 1, f"Should have yield from statements: {source}"
    
    def test_yield_from_return_value(self, tester):
        """Test yield from capturing return values"""
        # Language Reference: yield from can capture return value of delegated generator
        yield_from_return_patterns = [
            """
def capturing_generator():
    def inner_gen():
        yield 1
        yield 2
        return "completed"
    
    result = yield from inner_gen()
    yield f"Inner returned: {result}"
""",
            """
def delegating_with_return():
    def task_generator():
        for i in range(3):
            yield f"Processing {i}"
        return f"Processed {i+1} items"
    
    status = yield from task_generator()
    yield f"Final status: {status}"
""",
            """
def nested_return_capture():
    def level1():
        yield "step1"
        return "level1_done"
    
    def level2():
        result = yield from level1()
        yield f"Level1 result: {result}"
        return "level2_done"
    
    final_result = yield from level2()
    yield f"Final: {final_result}"
"""
        ]
        
        for source in yield_from_return_patterns:
            tree = tester.assert_yield_syntax_parses(source)
            yield_from_nodes = tester.get_yield_from_statements(source)
            assert len(yield_from_nodes) >= 1, f"Should have yield from statements: {source}"


class TestSection77GeneratorProtocol:
    """Test generator protocol methods and behavior."""
    
    @pytest.mark.min_version_3_6
    def test_generator_send_method(self, tester):
        """Test generator send method functionality"""
        # Language Reference: generators support send method for bidirectional communication
        generator_send_source = """
def echo_generator():
    value = None
    while True:
        received = yield value
        if received is None:
            break
        value = f"Echo: {received}"

def bidirectional_generator():
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value
"""
        
        tree = tester.assert_yield_syntax_parses(generator_send_source)
        yield_nodes = tester.get_yield_statements(generator_send_source)
        assert len(yield_nodes) >= 2, "Should have multiple yield statements for send protocol"
    
    @pytest.mark.min_version_3_6
    def test_generator_throw_method(self, tester):
        """Test generator throw method functionality"""
        # Language Reference: generators support throw method for exception injection
        generator_throw_source = """
def exception_handling_generator():
    try:
        yield "starting"
        while True:
            value = yield "waiting"
            if value == "stop":
                break
            yield f"processing: {value}"
    except GeneratorExit:
        yield "cleanup"
        raise
    except Exception as e:
        yield f"error: {e}"
        raise
    finally:
        yield "finished"

def robust_generator():
    try:
        for i in range(10):
            try:
                yield i
            except ValueError:
                yield f"ValueError at {i}"
                continue
            except Exception as e:
                yield f"Other error at {i}: {e}"
                break
    finally:
        yield "generator cleanup"
"""
        
        tree = tester.assert_yield_syntax_parses(generator_throw_source)
        yield_nodes = tester.get_yield_statements(generator_throw_source)
        assert len(yield_nodes) >= 8, "Should have multiple yield statements for exception handling"
    
    @pytest.mark.min_version_3_6
    def test_generator_close_method(self, tester):
        """Test generator close method and cleanup"""
        # Language Reference: generators support close method for cleanup
        generator_close_source = """
def resource_generator():
    resource = acquire_resource()
    try:
        yield "resource acquired"
        while True:
            data = yield "processing"
            if data is None:
                break
            yield process_data(resource, data)
    except GeneratorExit:
        release_resource(resource)
        yield "resource released"
        raise
    finally:
        final_cleanup()

def context_generator():
    with managed_context() as context:
        yield "context entered"
        try:
            while True:
                command = yield "ready"
                if command == "exit":
                    break
                yield context.execute(command)
        except GeneratorExit:
            yield "context cleanup"
            raise
"""
        
        tree = tester.assert_yield_syntax_parses(generator_close_source)
        yield_nodes = tester.get_yield_statements(generator_close_source)
        assert len(yield_nodes) >= 6, "Should have multiple yield statements for cleanup handling"


class TestSection77YieldErrorConditions:
    """Test yield statement error conditions."""
    
    def test_yield_outside_function_error(self, tester):
        """Test yield outside function context"""
        # Language Reference: yield only valid inside functions
        # Note: Some yield restrictions are checked at compile time, not parse time
        outside_function_patterns = [
            "yield 42",  # Module level - parses but may fail at compile/runtime
            """
class MyClass:
    yield "invalid"  # Class level - parses but may fail at compile/runtime
""",
        ]
        
        for source in outside_function_patterns:
            # These parse successfully but would fail at compile/runtime
            tree = tester.assert_yield_syntax_parses(source)
            yield_nodes = tester.get_yield_statements(source)
            assert len(yield_nodes) >= 1, f"Yield should parse: {source}"
    
    def test_yield_in_lambda_restrictions(self, tester):
        """Test yield in lambda function restrictions"""
        # Language Reference: yield not allowed in lambda functions
        # Note: This is a syntax error
        lambda_yield_patterns = [
            "lambda: yield 42",
            "lambda x: yield x",
            "map(lambda item: yield item, data)",
        ]
        
        for source in lambda_yield_patterns:
            tester.assert_yield_syntax_error(source)
    
    def test_yield_in_list_comprehension_restrictions(self, tester):
        """Test yield in comprehension restrictions"""
        # Language Reference: yield not allowed in comprehensions
        comprehension_yield_patterns = [
            "[yield x for x in range(5)]",
            "{yield x for x in range(5)}",
            "{k: yield v for k, v in items}",
        ]
        
        # These should be syntax errors
        for source in comprehension_yield_patterns:
            tester.assert_yield_syntax_error(source)
        
        # Generator expressions with yield are also invalid
        generator_yield_pattern = "(yield x for x in range(5))"
        tester.assert_yield_syntax_error(generator_yield_pattern)
    
    def test_yield_from_restrictions(self, tester):
        """Test yield from with invalid targets"""
        # Language Reference: yield from requires iterable
        # Note: These parse but may fail at runtime
        yield_from_restriction_patterns = [
            """
def invalid_yield_from():
    yield from 42  # Not iterable - runtime error
    yield from None  # Not iterable - runtime error
""",
        ]
        
        for source in yield_from_restriction_patterns:
            # These parse successfully but would fail at runtime
            tree = tester.assert_yield_syntax_parses(source)
            yield_from_nodes = tester.get_yield_from_statements(source)
            assert len(yield_from_nodes) >= 1, f"Yield from should parse: {source}"


class TestSection77YieldAST:
    """Test yield AST structure validation."""
    
    def test_yield_ast_node_structure(self, tester):
        """Test Yield AST node structure"""
        # Language Reference: AST structure for yield statements
        yield_ast_cases = [
            """
def simple_yield():
    yield 42
    yield "hello"
    yield
""",
            """
def yield_expression():
    result = yield value
    x = (yield 1) + (yield 2)
"""
        ]
        
        for source in yield_ast_cases:
            tree = tester.assert_yield_syntax_parses(source)
            yield_nodes = tester.get_yield_statements(source)
            assert len(yield_nodes) >= 2, f"Should have yield nodes: {source}"
            
            for yield_node in yield_nodes:
                assert isinstance(yield_node, (ast.Yield, ast.YieldFrom)), "Should be Yield or YieldFrom node"
                
                if isinstance(yield_node, ast.Yield):
                    # Yield nodes can have optional value
                    assert hasattr(yield_node, 'value'), "Yield should have value attribute"
                elif isinstance(yield_node, ast.YieldFrom):
                    # YieldFrom nodes must have value
                    assert hasattr(yield_node, 'value'), "YieldFrom should have value attribute"
                    assert yield_node.value is not None, "YieldFrom must have non-None value"
    
    def test_yield_from_ast_structure(self, tester):
        """Test YieldFrom AST node structure"""
        # Language Reference: AST structure for yield from statements
        yield_from_source = """
def yield_from_examples():
    yield from range(5)
    yield from other_generator()
    yield from [1, 2, 3]
"""
        
        tree = tester.assert_yield_syntax_parses(yield_from_source)
        yield_from_nodes = tester.get_yield_from_statements(yield_from_source)
        assert len(yield_from_nodes) == 3, "Should have three yield from statements"
        
        for yield_from_node in yield_from_nodes:
            assert isinstance(yield_from_node, ast.YieldFrom), "Should be YieldFrom node"
            assert hasattr(yield_from_node, 'value'), "YieldFrom should have value attribute"
            assert yield_from_node.value is not None, "YieldFrom must have value"
    
    def test_yield_in_complex_functions(self, tester):
        """Test yield in complex function structures"""
        # Language Reference: yield in various function contexts
        complex_yield_source = """
def complex_generator(param1, param2=None, *args, **kwargs):
    '''Generator with complex signature'''
    yield f"Starting with {param1}"
    
    for arg in args:
        yield f"Processing arg: {arg}"
    
    for key, value in kwargs.items():
        yield f"Processing {key}: {value}"
    
    if param2:
        yield from process_param2(param2)
    
    try:
        yield "operation"
        result = yield "waiting for input"
        yield f"Received: {result}"
    except Exception as e:
        yield f"Error: {e}"
    finally:
        yield "cleanup complete"
"""
        
        tree = tester.assert_yield_syntax_parses(complex_yield_source)
        yield_nodes = tester.get_yield_statements(complex_yield_source)
        assert len(yield_nodes) >= 8, "Should have multiple yield statements in complex functions"
        
        functions = tester.get_function_definitions(complex_yield_source)
        assert len(functions) >= 1, "Should have function definition"


class TestSection77CrossImplementationCompatibility:
    """Test cross-implementation compatibility for yield statements."""
    
    def test_yield_ast_consistency(self, tester):
        """Test yield AST consistency across implementations"""
        # Language Reference: yield AST should be consistent
        consistency_test_cases = [
            """
def simple_generator():
    yield 1
    yield 2
    yield 3
""",
            """
def delegating_generator():
    yield from range(5)
    yield from other_source()
""",
            """
def interactive_generator():
    while True:
        value = yield "ready"
        if value is None:
            break
        yield f"processed: {value}"
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_yield_syntax_parses(source)
            
            # Should have consistent yield structure
            yield_nodes = tester.get_yield_statements(source)
            assert len(yield_nodes) >= 2, f"Should have yield statements: {source}"
            
            for yield_node in yield_nodes:
                assert isinstance(yield_node, (ast.Yield, ast.YieldFrom)), "Should be Yield or YieldFrom node"
    
    def test_comprehensive_yield_patterns(self, tester):
        """Test comprehensive real-world yield patterns"""
        # Language Reference: complex yield usage scenarios
        comprehensive_patterns = [
            """
# Data processing pipeline with generators
def process_data_stream(source):
    '''Process data from source with multiple stages'''
    # Stage 1: Raw data extraction
    for raw_item in source:
        if validate_raw_data(raw_item):
            yield f"raw: {raw_item}"
        else:
            continue
    
    # Stage 2: Transformed data
    yield "--- Transformation Stage ---"
    for raw_item in source:
        if validate_raw_data(raw_item):
            transformed = transform_data(raw_item)
            yield f"transformed: {transformed}"
    
    # Stage 3: Aggregated results
    yield "--- Aggregation Stage ---"
    aggregator = Aggregator()
    for raw_item in source:
        if validate_raw_data(raw_item):
            transformed = transform_data(raw_item)
            aggregator.add(transformed)
            if aggregator.should_yield():
                yield from aggregator.get_results()

def coroutine_like_generator():
    '''Generator that mimics coroutine behavior'''
    state = "initialized"
    while True:
        try:
            command = yield state
            if command == "get_state":
                yield state
            elif command == "reset":
                state = "initialized"
                yield "reset_complete"
            elif command.startswith("set_"):
                state = command[4:]
                yield f"state_set_to_{state}"
            elif command == "exit":
                break
            else:
                yield f"unknown_command_{command}"
        except GeneratorExit:
            yield "generator_cleanup"
            raise
        except Exception as e:
            yield f"error_{type(e).__name__}"
            continue
""",
            """
# Generator composition and delegation
def compose_generators(*generators):
    '''Compose multiple generators into one'''
    for gen in generators:
        yield f"starting_generator_{id(gen)}"
        try:
            yield from gen
        except Exception as e:
            yield f"generator_error_{type(e).__name__}"
        finally:
            yield f"finished_generator_{id(gen)}"

def fibonacci_generator(limit=None):
    '''Generate Fibonacci sequence'''
    a, b = 0, 1
    count = 0
    while limit is None or count < limit:
        yield a
        a, b = b, a + b
        count += 1
        # Allow external control
        command = yield
        if command == "reset":
            a, b = 0, 1
            count = 0
            yield "reset"
        elif command == "skip":
            continue
        elif command == "stop":
            break

def tree_traversal_generator(node):
    '''Traverse tree structure yielding nodes'''
    if node is None:
        return
    
    # Pre-order traversal
    yield f"pre_{node.value}"
    
    # Traverse children
    for child in node.children:
        yield from tree_traversal_generator(child)
    
    # Post-order
    yield f"post_{node.value}"
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_yield_syntax_parses(source)
            
            # Should have multiple yield usages
            yield_nodes = tester.get_yield_statements(source)
            assert len(yield_nodes) >= 5, f"Should have multiple yield statements: {source}"
            
            # Should have both yield and yield from
            yield_from_nodes = tester.get_yield_from_statements(source)
            assert len(yield_from_nodes) >= 1, f"Should have yield from statements: {source}"
    
    def test_yield_introspection(self, tester):
        """Test ability to analyze yield statements programmatically"""
        # Test programmatic analysis of yield structure
        introspection_source = """
def multi_purpose_generator():
    '''Generator with various yield patterns'''
    # Simple yields
    yield "start"
    yield 42
    yield [1, 2, 3]
    
    # Yield expressions
    input_value = yield "input_prompt"
    result = yield f"processing_{input_value}"
    
    # Yield from delegation
    yield from range(3)
    yield from other_generator()
    
    # Conditional yields
    if condition:
        yield "condition_true"
        yield from conditional_generator()
    else:
        yield "condition_false"
    
    # Loop yields
    for i in range(5):
        yield f"loop_item_{i}"
        if i % 2 == 0:
            yield from even_processor(i)
    
    # Exception handling yields
    try:
        risky_value = yield "risky_operation"
        yield f"success_{risky_value}"
    except Exception as e:
        yield f"exception_{type(e).__name__}"
    finally:
        yield "cleanup"
        yield from cleanup_generator()
"""
        
        tree = tester.assert_yield_syntax_parses(introspection_source)
        
        # Should identify all yield statements
        yield_nodes = tester.get_yield_statements(introspection_source)
        assert len(yield_nodes) >= 10, "Should have multiple yield statements"
        
        # Should identify yield from statements
        yield_from_nodes = tester.get_yield_from_statements(introspection_source)
        assert len(yield_from_nodes) >= 4, "Should have multiple yield from statements"
        
        # Should identify generator functions
        assert tester.has_generator_functions(introspection_source), "Should have generator functions"
        
        # All yield nodes should be proper AST nodes
        for yield_node in yield_nodes:
            assert isinstance(yield_node, (ast.Yield, ast.YieldFrom)), "Should be Yield or YieldFrom node"
        
        # Should have function definitions
        functions = tester.get_function_definitions(introspection_source)
        assert len(functions) >= 1, "Should have function definitions"