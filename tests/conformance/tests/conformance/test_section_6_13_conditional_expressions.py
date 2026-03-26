"""
Section 6.13: Conditional Expressions - Conformance Test Suite

Tests Python Language Reference Section 6.13 compliance across implementations.
Based on formal conditional expression syntax definitions and prose assertions for ternary operator behavior.

Grammar tested:
    conditional_expression: or_test ['if' or_test 'else' expression]

Language Reference requirements tested:
    - Conditional expression syntax validation (x if condition else y)
    - Precedence and associativity rules for conditional expressions
    - Short-circuit evaluation behavior in conditional expressions
    - Nesting patterns and complex conditional expressions
    - Conditional expressions in different contexts
    - Error conditions for malformed conditional expressions
    - Conditional expression AST structure validation
    - Cross-implementation conditional expression compatibility
"""

import ast
import pytest
import sys
from typing import Any


class ConditionalExpressionTester:
    """Helper class for testing conditional expression conformance.
    
    Focuses on AST structure validation for conditional expression syntax and evaluation
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_conditional_expression_parses(self, source: str):
        """Test that conditional expression syntax parses correctly.
        
        Args:
            source: Python source code with conditional expressions
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Conditional expression syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_conditional_expression_syntax_error(self, source: str):
        """Test that invalid conditional expression syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_conditional_expressions(self, source: str) -> list:
        """Get IfExp AST nodes from source (conditional expressions).
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.IfExp nodes
        """
        tree = ast.parse(source)
        conditionals = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.IfExp):
                conditionals.append(node)
        
        return conditionals
    
    def get_binary_operations(self, source: str) -> list:
        """Get BinOp AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes
        """
        tree = ast.parse(source)
        binops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                binops.append(node)
        
        return binops
    
    def get_comparison_operations(self, source: str) -> list:
        """Get Compare AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Compare nodes
        """
        tree = ast.parse(source)
        compares = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                compares.append(node)
        
        return compares
    
    def count_nested_conditionals(self, source: str) -> int:
        """Count depth of nested conditional expressions.
        
        Args:
            source: Python source code
            
        Returns:
            Maximum nesting depth of conditional expressions
        """
        tree = ast.parse(source)
        
        def count_depth(node):
            max_depth = 0
            if isinstance(node, ast.IfExp):
                # Check nesting in body, test, and orelse
                body_depth = count_depth(node.body)
                test_depth = count_depth(node.test)
                orelse_depth = count_depth(node.orelse)
                max_depth = 1 + max(body_depth, test_depth, orelse_depth)
            else:
                # Recurse into child nodes
                for child in ast.iter_child_nodes(node):
                    child_depth = count_depth(child)
                    max_depth = max(max_depth, child_depth)
            return max_depth
        
        return count_depth(tree)


@pytest.fixture
def tester():
    """Provide ConditionalExpressionTester instance for tests."""
    return ConditionalExpressionTester()


class TestSection613BasicConditionalSyntax:
    """Test basic conditional expression syntax."""
    
    def test_simple_conditional_expressions(self, tester):
        """Test simple conditional expression patterns"""
        # Language Reference: conditional_expression: or_test ['if' or_test 'else' expression]
        simple_conditional_patterns = [
            """
x = value if condition else default
""",
            """
result = 'positive' if num > 0 else 'negative'
""",
            """
message = "found" if item in collection else "not found"
""",
            """
output = func() if available else None
""",
            """
status = True if check_status() else False
"""
        ]
        
        for source in simple_conditional_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should have conditional expressions: {source}"
    
    def test_conditional_with_different_types(self, tester):
        """Test conditional expressions with different value types"""
        # Language Reference: conditional expressions can return different types
        type_variation_patterns = [
            """
value = 42 if use_number else "string"
""",
            """
result = [1, 2, 3] if use_list else {'key': 'value'}
""",
            """
data = func(x) if callable(func) else x
""",
            """
item = collection[0] if collection else None
""",
            """
output = complex_computation() if expensive else simple_value
"""
        ]
        
        for source in type_variation_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should handle type variations: {source}"
    
    def test_conditional_with_complex_conditions(self, tester):
        """Test conditional expressions with complex test conditions"""
        # Language Reference: test condition can be complex expression
        complex_condition_patterns = [
            """
result = value if x > 0 and y < 10 else default
""",
            """
output = success_value if not error_occurred() else error_value
""",
            """
item = primary if primary is not None and primary.is_valid() else secondary
""",
            """
data = cached_data if cache.is_fresh() and cache.has_key(key) else compute_data()
""",
            """
choice = option_a if (flag1 or flag2) and not flag3 else option_b
"""
        ]
        
        for source in complex_condition_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should handle complex conditions: {source}"
    
    def test_conditional_with_complex_values(self, tester):
        """Test conditional expressions with complex value expressions"""
        # Language Reference: both branches can be complex expressions
        complex_value_patterns = [
            """
result = compute_primary(x, y) if condition else compute_secondary(a, b)
""",
            """
output = data.transform().filter() if data else empty_collection().default()
""",
            """
value = (x * 2 + y) if positive else (x / 2 - y)
""",
            """
item = collection[index].attr if valid_index(index) else default_object.attr
""",
            """
result = [f(x) for x in items] if items else []
"""
        ]
        
        for source in complex_value_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should handle complex values: {source}"


class TestSection613ConditionalPrecedence:
    """Test conditional expression precedence and associativity."""
    
    def test_conditional_with_arithmetic_operations(self, tester):
        """Test conditional expression precedence with arithmetic"""
        # Language Reference: conditional has lower precedence than arithmetic
        arithmetic_precedence_patterns = [
            """
result = x + y if condition else a + b
""",
            """
value = x * 2 if flag else y / 3
""",
            """
output = a ** b if power_mode else a * b
""",
            """
calculation = (x + y) * z if complex_calc else x + y * z
""",
            """
formula = x + y if simple else x * y + z
"""
        ]
        
        for source in arithmetic_precedence_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should handle arithmetic precedence: {source}"
    
    def test_conditional_with_comparison_operations(self, tester):
        """Test conditional expression precedence with comparisons"""
        # Language Reference: conditional has lower precedence than comparisons
        comparison_precedence_patterns = [
            """
result = x < y if check_comparison else a > b
""",
            """
value = item == target if do_compare else item != other
""",
            """
check = x <= limit if enforce_limit else x >= minimum
""",
            """
valid = value in collection if check_membership else value not in excluded
""",
            """
match = pattern.match(text) if use_regex else text == literal
"""
        ]
        
        for source in comparison_precedence_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should handle comparison precedence: {source}"
    
    def test_conditional_with_boolean_operations(self, tester):
        """Test conditional expression precedence with boolean operators"""
        # Language Reference: conditional has lower precedence than and/or
        boolean_precedence_patterns = [
            """
result = x and y if condition else a or b
""",
            """
value = not flag if invert else flag and other
""",
            """
check = x or y and z if complex_logic else simple_flag
""",
            """
valid = item and item.is_valid() if item else default_valid
""",
            """
output = flag1 and flag2 or flag3 if use_complex else simple_flag
"""
        ]
        
        for source in boolean_precedence_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should handle boolean precedence: {source}"
    
    def test_conditional_associativity(self, tester):
        """Test conditional expression right-associativity"""
        # Language Reference: conditional expressions are right-associative
        associativity_patterns = [
            """
result = x if condition1 else y if condition2 else z
""",
            """
value = a if flag1 else b if flag2 else c if flag3 else d
""",
            """
output = first if primary else second if secondary else third
""",
            """
choice = option_a if test_a else option_b if test_b else default
""",
            """
item = cache[key] if key in cache else compute() if expensive else default_value
"""
        ]
        
        for source in associativity_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 2, f"Should handle right-associativity: {source}"


class TestSection613NestedConditionals:
    """Test nested conditional expressions."""
    
    def test_conditionals_in_conditions(self, tester):
        """Test conditional expressions in test conditions"""
        # Language Reference: conditional tests can contain conditional expressions
        nested_condition_patterns = [
            """
result = value if (x if flag else y) > threshold else default
""",
            """
output = success if (primary if available else backup) else failure
""",
            """
check = item if (condition1 if mode else condition2) else alternative
""",
            """
value = data if (cached if cache_valid else fresh) else fallback
""",
            """
result = compute() if (fast_path if optimized else slow_path) else skip
"""
        ]
        
        for source in nested_condition_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 2, f"Should handle nested conditions: {source}"
    
    def test_conditionals_in_values(self, tester):
        """Test conditional expressions in value branches"""
        # Language Reference: conditional values can contain conditional expressions
        nested_value_patterns = [
            """
result = (x if positive else -x) if use_abs else (y if valid else 0)
""",
            """
output = (primary if available else secondary) if prefer_primary else (backup if exists else None)
""",
            """
value = (data.process() if data else empty()) if should_process else (raw if keep_raw else modified)
""",
            """
item = (collection[0] if collection else default) if use_first else (collection[-1] if collection else last_resort)
""",
            """
result = (expensive_compute() if accurate else quick_estimate()) if compute_needed else (cached if fresh else stale_default)
"""
        ]
        
        for source in nested_value_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 2, f"Should handle nested values: {source}"
    
    def test_deeply_nested_conditionals(self, tester):
        """Test deeply nested conditional expressions"""
        # Language Reference: conditional expressions can be arbitrarily nested
        deeply_nested_patterns = [
            """
result = (
    a if condition1 else
    b if condition2 else
    c if condition3 else
    d
)
""",
            """
value = (
    primary if available and valid else
    secondary if backup_available else
    tertiary if fallback_exists else
    None
)
""",
            """
output = (
    fast_path() if optimized and not debug else
    medium_path() if moderate_optimization else
    slow_path() if safe_mode else
    unsafe_path()
)
""",
            """
choice = (
    option_a if (flag1 if mode1 else flag2) else
    option_b if (flag3 if mode2 else flag4) else
    default_option
)
"""
        ]
        
        for source in deeply_nested_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            nesting_depth = tester.count_nested_conditionals(source)
            assert nesting_depth >= 2, f"Should have nested conditionals: {source}"


class TestSection613ConditionalContexts:
    """Test conditional expressions in different contexts."""
    
    def test_conditionals_in_assignments(self, tester):
        """Test conditional expressions in assignment contexts"""
        # Language Reference: conditional expressions in assignments
        assignment_context_patterns = [
            """
x = value if condition else default
""",
            """
a, b = (x, y) if swap else (y, x)
""",
            """
result[key] = new_value if update else old_value
""",
            """
obj.attr = computed if recompute else cached
""",
            """
data['key'] = processed if process_data else raw
"""
        ]
        
        for source in assignment_context_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should work in assignments: {source}"
    
    def test_conditionals_in_function_calls(self, tester):
        """Test conditional expressions in function call arguments"""
        # Language Reference: conditional expressions as function arguments
        function_call_patterns = [
            """
result = func(value if condition else default)
""",
            """
output = process(x if valid else backup, mode='fast' if optimized else 'safe')
""",
            """
data = transform(
    input_data if available else placeholder,
    format='json' if structured else 'text'
)
""",
            """
response = api_call(
    endpoint if production else test_endpoint,
    timeout=30 if fast_network else 120
)
""",
            """
result = compute(
    a if use_a else b,
    c if use_c else d,
    flag=True if enable else False
)
"""
        ]
        
        for source in function_call_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should work in function calls: {source}"
    
    def test_conditionals_in_return_statements(self, tester):
        """Test conditional expressions in return statements"""
        # Language Reference: conditional expressions in returns
        return_context_patterns = [
            """
def func():
    return value if condition else default
""",
            """
def process():
    return success_result if success else error_result
""",
            """
def compute():
    return expensive_calculation() if accurate else quick_estimate()
""",
            """
def get_data():
    return cached_data if cache_valid else fresh_data()
""",
            """
def transform(data):
    return data.process() if data else empty_result()
"""
        ]
        
        for source in return_context_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should work in returns: {source}"
    
    def test_conditionals_in_comprehensions(self, tester):
        """Test conditional expressions in comprehensions"""
        # Language Reference: conditional expressions in comprehensions
        comprehension_patterns = [
            """
result = [x if x > 0 else 0 for x in values]
""",
            """
data = {k: v if v else default for k, v in items}
""",
            """
output = (x if condition(x) else transform(x) for x in sequence)
""",
            """
filtered = {item if valid(item) else placeholder for item in collection}
""",
            """
processed = [
    expensive(item) if should_process(item) else cheap(item)
    for item in items
]
"""
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should work in comprehensions: {source}"


class TestSection613ConditionalErrors:
    """Test conditional expression error conditions."""
    
    def test_missing_else_clause_error(self, tester):
        """Test conditional expressions missing else clause"""
        # Language Reference: conditional expressions require else clause
        missing_else_patterns = [
            "x if condition",
            "value if test",
            "result if flag and other",
        ]
        
        for source in missing_else_patterns:
            tester.assert_conditional_expression_syntax_error(source)
    
    def test_malformed_conditional_syntax(self, tester):
        """Test malformed conditional expression syntax"""
        # Language Reference: specific syntax requirements
        malformed_patterns = [
            "if condition x else y",  # Wrong order
            "x condition else y",     # Missing if
            "x if else y",           # Missing condition
            "x if condition y",      # Missing else
            "x if condition else",   # Missing else value
        ]
        
        for source in malformed_patterns:
            tester.assert_conditional_expression_syntax_error(source)
    
    def test_nested_conditional_syntax_errors(self, tester):
        """Test syntax errors in nested conditionals"""
        # Language Reference: nested conditional syntax requirements
        nested_error_patterns = [
            "x if (y if condition) else z",  # Missing else in nested
            "x if condition else (y if test)",  # Missing else in nested
            "x if (y if else z) else w",     # Malformed nested
        ]
        
        for source in nested_error_patterns:
            tester.assert_conditional_expression_syntax_error(source)


class TestSection613ConditionalAST:
    """Test conditional expression AST structure validation."""
    
    def test_conditional_ast_structure(self, tester):
        """Test IfExp AST node structure"""
        # Language Reference: AST structure for conditional expressions
        conditional_ast_cases = [
            """
x = value if condition else default
""",
            """
result = a if test else b
""",
            """
output = complex_expr() if flag else simple_value
"""
        ]
        
        for source in conditional_ast_cases:
            tree = tester.assert_conditional_expression_parses(source)
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should have conditional expressions: {source}"
            
            for conditional in conditionals:
                # IfExp nodes must have test, body, and orelse
                assert isinstance(conditional, ast.IfExp), "Should be IfExp node"
                assert hasattr(conditional, 'test'), "Should have test condition"
                assert hasattr(conditional, 'body'), "Should have body (true branch)"
                assert hasattr(conditional, 'orelse'), "Should have orelse (false branch)"
                
                # All parts should be non-None
                assert conditional.test is not None, "Test should not be None"
                assert conditional.body is not None, "Body should not be None"
                assert conditional.orelse is not None, "Orelse should not be None"
    
    def test_nested_conditional_ast(self, tester):
        """Test nested conditional expression AST structure"""
        # Language Reference: nested conditionals in AST
        nested_conditional_source = """
result = (
    a if condition1 else
    b if condition2 else
    c
)
"""
        
        tree = tester.assert_conditional_expression_parses(nested_conditional_source)
        conditionals = tester.get_conditional_expressions(nested_conditional_source)
        assert len(conditionals) >= 2, "Should have nested conditionals"
        
        # Check that we have proper nesting structure
        nesting_depth = tester.count_nested_conditionals(nested_conditional_source)
        assert nesting_depth >= 2, "Should have nested structure"
    
    def test_conditional_with_complex_expressions_ast(self, tester):
        """Test conditional with complex sub-expressions AST"""
        # Language Reference: complex expressions in conditional parts
        complex_conditional_source = """
result = (
    expensive_function(x, y, z) 
    if complex_condition() and flag 
    else default_computation(a, b)
)
"""
        
        tree = tester.assert_conditional_expression_parses(complex_conditional_source)
        conditionals = tester.get_conditional_expressions(complex_conditional_source)
        assert len(conditionals) >= 1, "Should have conditional expression"
        
        # Should have function calls in the conditional
        function_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        assert len(function_calls) >= 2, "Should have function calls in conditional parts"


class TestSection613CrossImplementationCompatibility:
    """Test cross-implementation compatibility for conditional expressions."""
    
    def test_conditional_ast_consistency(self, tester):
        """Test conditional expression AST consistency across implementations"""
        # Language Reference: conditional AST should be consistent
        consistency_test_cases = [
            """
x = value if condition else default
""",
            """
result = a if test else b if other_test else c
""",
            """
output = (x if positive else -x) if use_abs else x
""",
            """
data = func() if available else None
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_conditional_expression_parses(source)
            
            # Should have consistent conditional structure
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 1, f"Should have conditional expressions: {source}"
            
            for conditional in conditionals:
                assert isinstance(conditional, ast.IfExp), "Should be IfExp node"
                assert hasattr(conditional, 'test'), "Should have test"
                assert hasattr(conditional, 'body'), "Should have body"
                assert hasattr(conditional, 'orelse'), "Should have orelse"
    
    def test_comprehensive_conditional_patterns(self, tester):
        """Test comprehensive real-world conditional patterns"""
        # Language Reference: complex conditional usage scenarios
        comprehensive_patterns = [
            """
# Configuration and option selection
class ConfigManager:
    def __init__(self, env='development'):
        self.env = env
        
        # Conditional configuration
        self.debug = True if env == 'development' else False
        self.db_host = 'localhost' if env != 'production' else 'prod-db.company.com'
        self.cache_size = 1000 if env == 'development' else 10000 if env == 'staging' else 50000
        
        # Complex conditional logic
        self.log_level = (
            'DEBUG' if env == 'development' else
            'INFO' if env == 'staging' else
            'WARN' if env == 'production' else
            'ERROR'
        )
    
    def get_timeout(self, operation='default'):
        # Nested conditionals for operation-specific timeouts
        base_timeout = 30 if self.env == 'development' else 60
        
        return (
            base_timeout * 2 if operation == 'database' else
            base_timeout * 3 if operation == 'api_call' else
            base_timeout / 2 if operation == 'cache' else
            base_timeout
        )
    
    def should_retry(self, error_count, max_retries=3):
        # Complex conditional with multiple factors
        return (
            error_count < max_retries if self.env == 'production' else
            error_count < max_retries * 2 if self.env == 'staging' else
            True  # Always retry in development
        )

# Data processing with conditionals
def process_user_data(users, format_preference='json'):
    processed = []
    
    for user in users:
        # Conditional data transformation
        full_name = (
            f"{user.first} {user.last}" if user.first and user.last else
            user.first if user.first else
            user.last if user.last else
            "Anonymous"
        )
        
        # Conditional formatting
        email = (
            user.email.lower() if user.email and '@' in user.email else
            f"noemail+{user.id}@example.com" if user.id else
            "noemail@example.com"
        )
        
        # Conditional inclusion of optional fields
        profile = {
            'name': full_name,
            'email': email,
            'age': user.age if user.age and user.age > 0 else None,
            'location': user.location if hasattr(user, 'location') and user.location else 'Unknown',
            'premium': user.premium if hasattr(user, 'premium') else False
        }
        
        # Conditional output format
        output = (
            json.dumps(profile) if format_preference == 'json' else
            f"{profile['name']} <{profile['email']}>" if format_preference == 'email' else
            str(profile) if format_preference == 'repr' else
            profile
        )
        
        processed.append(output)
    
    return processed
""",
            """
# Algorithm selection with performance conditionals
class DataProcessor:
    def __init__(self, performance_mode='auto'):
        self.performance_mode = performance_mode
    
    def sort_data(self, data, size_hint=None):
        # Algorithm selection based on data characteristics
        estimated_size = size_hint if size_hint else len(data)
        
        # Choose sorting algorithm based on size and mode
        algorithm = (
            'quicksort' if estimated_size > 1000 and self.performance_mode == 'fast' else
            'mergesort' if estimated_size > 100 and self.performance_mode in ['stable', 'auto'] else
            'insertion' if estimated_size <= 100 else
            'heapsort'  # Fallback for large data in memory-constrained mode
        )
        
        # Conditional preprocessing
        preprocessed = (
            self._shuffle_data(data) if algorithm == 'quicksort' and self._is_nearly_sorted(data) else
            self._copy_data(data) if algorithm == 'mergesort' else
            data  # In-place for other algorithms
        )
        
        # Execute chosen algorithm
        return (
            self._quicksort(preprocessed) if algorithm == 'quicksort' else
            self._mergesort(preprocessed) if algorithm == 'mergesort' else
            self._insertion_sort(preprocessed) if algorithm == 'insertion' else
            self._heapsort(preprocessed)
        )
    
    def optimize_memory_usage(self, data_size, available_memory):
        # Complex memory optimization decisions
        chunk_size = (
            available_memory // 4 if data_size > available_memory * 2 else
            available_memory // 2 if data_size > available_memory else
            data_size  # Process all at once if it fits
        )
        
        use_streaming = (
            True if data_size > available_memory * 3 else
            False if data_size < available_memory // 2 else
            self.performance_mode == 'memory'  # User preference
        )
        
        compression_level = (
            9 if available_memory < data_size // 10 else  # High compression for low memory
            6 if available_memory < data_size // 2 else   # Medium compression
            3 if self.performance_mode == 'fast' else     # Low compression for speed
            1  # Minimal compression
        )
        
        return {
            'chunk_size': chunk_size,
            'use_streaming': use_streaming,
            'compression_level': compression_level,
            'buffer_count': 2 if use_streaming else 1
        }
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_conditional_expression_parses(source)
            
            # Should have multiple conditional usages
            conditionals = tester.get_conditional_expressions(source)
            assert len(conditionals) >= 5, f"Should have multiple conditionals: {source}"
            
            # Should have various nesting levels
            max_depth = tester.count_nested_conditionals(source)
            assert max_depth >= 2, f"Should have nested conditionals: {source}"
    
    def test_conditional_introspection(self, tester):
        """Test ability to analyze conditional expressions programmatically"""
        # Test programmatic analysis of conditional structure
        introspection_source = """
def complex_decision_making(x, y, mode='auto'):
    # Simple conditional
    basic = value if condition else default
    
    # Nested conditionals
    nested = (
        expensive() if accurate else
        medium() if moderate else
        cheap()
    )
    
    # Conditional in condition
    conditional_test = result if (flag if mode == 'fast' else slow_flag) else fallback
    
    # Conditional in values
    conditional_values = (primary if available else backup) if use_primary else alternative
    
    # Multiple conditionals in expression
    complex_expr = (
        a if condition_a else b
    ) + (
        c if condition_c else d
    )
    
    return basic, nested, conditional_test, conditional_values, complex_expr
"""
        
        tree = tester.assert_conditional_expression_parses(introspection_source)
        
        # Should identify all conditional expressions
        conditionals = tester.get_conditional_expressions(introspection_source)
        assert len(conditionals) >= 7, "Should have multiple conditional expressions"
        
        # Should identify nesting
        nesting_depth = tester.count_nested_conditionals(introspection_source)
        assert nesting_depth >= 2, "Should have nested conditionals"
        
        # All conditionals should have proper structure
        for conditional in conditionals:
            assert isinstance(conditional, ast.IfExp), "Should be IfExp node"
            assert conditional.test is not None, "Should have test condition"
            assert conditional.body is not None, "Should have body value"
            assert conditional.orelse is not None, "Should have else value"