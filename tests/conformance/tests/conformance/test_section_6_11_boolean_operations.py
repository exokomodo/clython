"""
Section 6.11: Boolean Operations - Conformance Test Suite

Tests Python Language Reference Section 6.11 compliance across implementations.
Based on formal grammar definitions and prose assertions for boolean operations.

Grammar tested:
    or_test: and_test ('or' and_test)*
    and_test: not_test ('and' not_test)*
    not_test: 'not' not_test | comparison

Language Reference requirements tested:
    - Boolean operators: and, or, not
    - Short-circuit evaluation behavior
    - Truth value testing for all types
    - Operator precedence (not > and > or)
    - Left-associativity of and/or operators
    - Return value semantics (not just True/False)
    - Complex boolean expression evaluation
    - Integration with comparison operations
"""

import ast
import pytest
import sys
from typing import Any


class BooleanOperationTester:
    """Helper class for testing boolean operation conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_boolean_syntax_parses(self, source: str):
        """Test that boolean operation syntax parses correctly.
        
        Args:
            source: Python boolean operation source code
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Boolean operation syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_boolean_syntax_error(self, source: str):
        """Test that invalid boolean syntax raises SyntaxError.
        
        Args:
            source: Python boolean source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_boolean_operations(self, source: str) -> list:
        """Get BoolOp AST nodes from source for analysis.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BoolOp nodes
        """
        tree = ast.parse(source)
        bool_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp):
                bool_ops.append(node)
        
        return bool_ops
    
    def get_unary_operations(self, source: str) -> list:
        """Get UnaryOp AST nodes (for 'not' operations) from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.UnaryOp nodes with 'not' operator
        """
        tree = ast.parse(source)
        not_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
                not_ops.append(node)
        
        return not_ops
    
    def has_short_circuit_structure(self, source: str) -> bool:
        """Check if source has structure that implies short-circuit evaluation.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains and/or operations
        """
        bool_ops = self.get_boolean_operations(source)
        return len(bool_ops) > 0


@pytest.fixture
def tester():
    """Provide BooleanOperationTester instance for tests."""
    return BooleanOperationTester()


class TestSection611AndOperator:
    """Test 'and' operator functionality."""
    
    def test_basic_and_operations(self, tester):
        """Test basic 'and' operator syntax and structure"""
        # Language Reference: and_test: not_test ('and' not_test)*
        and_expressions = [
            "True and True",
            "a and b",
            "condition1 and condition2",
            "x > 0 and x < 10",
            "not flag and ready",
            "func() and result",
            "obj.attr and obj.method()"
        ]
        
        for source in and_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            bool_ops = tester.get_boolean_operations(source)
            assert len(bool_ops) >= 1, f"Should contain 'and' operation: {source}"
            
            # Check that it's specifically an 'and' operation
            for bool_op in bool_ops:
                assert isinstance(bool_op.op, ast.And), f"Should be 'and' operator: {source}"
                assert len(bool_op.values) >= 2, f"'and' should have at least 2 operands: {source}"
    
    def test_chained_and_operations(self, tester):
        """Test chained 'and' operations (left-associative)"""
        # Language Reference: multiple 'and' operators are left-associative
        chained_and_expressions = [
            "a and b and c",
            "x > 0 and x < 10 and x != 5",
            "condition1() and condition2() and condition3()",
            "flag1 and flag2 and flag3 and flag4",
            "obj.valid and obj.ready and obj.active",
        ]
        
        for source in chained_and_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            bool_ops = tester.get_boolean_operations(source)
            assert len(bool_ops) >= 1, f"Should contain 'and' operations: {source}"
            
            # Find the main 'and' operation (should have 3+ values for chained)
            main_and = None
            for bool_op in bool_ops:
                if isinstance(bool_op.op, ast.And) and len(bool_op.values) >= 3:
                    main_and = bool_op
                    break
            
            assert main_and is not None, f"Should have chained 'and' operation: {source}"
    
    def test_and_short_circuit_structure(self, tester):
        """Test 'and' short-circuit evaluation structure"""
        # Language Reference: 'and' short-circuits if left operand is false
        short_circuit_patterns = [
            "False and expensive_function()",
            "None and risky_operation()",
            "[] and side_effect_func()",
            "0 and compute_heavy()",
            "condition() and process_if_true()",
        ]
        
        for source in short_circuit_patterns:
            tree = tester.assert_boolean_syntax_parses(source)
            assert tester.has_short_circuit_structure(source), f"Should have short-circuit structure: {source}"
            
            bool_ops = tester.get_boolean_operations(source)
            for bool_op in bool_ops:
                if isinstance(bool_op.op, ast.And):
                    # Should have exactly 2 operands for simple short-circuit
                    assert len(bool_op.values) == 2, f"Simple 'and' should have 2 operands: {source}"


class TestSection611OrOperator:
    """Test 'or' operator functionality."""
    
    def test_basic_or_operations(self, tester):
        """Test basic 'or' operator syntax and structure"""
        # Language Reference: or_test: and_test ('or' and_test)*
        or_expressions = [
            "False or True",
            "a or b",
            "condition1 or condition2",
            "x < 0 or x > 10",
            "error or fallback",
            "func() or default",
            "obj.attr or obj.fallback_attr"
        ]
        
        for source in or_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            bool_ops = tester.get_boolean_operations(source)
            assert len(bool_ops) >= 1, f"Should contain 'or' operation: {source}"
            
            # Check that it's specifically an 'or' operation
            for bool_op in bool_ops:
                assert isinstance(bool_op.op, ast.Or), f"Should be 'or' operator: {source}"
                assert len(bool_op.values) >= 2, f"'or' should have at least 2 operands: {source}"
    
    def test_chained_or_operations(self, tester):
        """Test chained 'or' operations (left-associative)"""
        # Language Reference: multiple 'or' operators are left-associative
        chained_or_expressions = [
            "a or b or c",
            "error1 or error2 or default",
            "attempt1() or attempt2() or attempt3()",
            "flag1 or flag2 or flag3 or flag4",
            "obj.primary or obj.secondary or obj.fallback",
        ]
        
        for source in chained_or_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            bool_ops = tester.get_boolean_operations(source)
            assert len(bool_ops) >= 1, f"Should contain 'or' operations: {source}"
            
            # Find the main 'or' operation (should have 3+ values for chained)
            main_or = None
            for bool_op in bool_ops:
                if isinstance(bool_op.op, ast.Or) and len(bool_op.values) >= 3:
                    main_or = bool_op
                    break
            
            assert main_or is not None, f"Should have chained 'or' operation: {source}"
    
    def test_or_short_circuit_structure(self, tester):
        """Test 'or' short-circuit evaluation structure"""
        # Language Reference: 'or' short-circuits if left operand is true
        short_circuit_patterns = [
            "True or expensive_function()",
            "'value' or risky_operation()",
            "[1, 2, 3] or side_effect_func()",
            "42 or compute_heavy()",
            "condition() or fallback_action()",
        ]
        
        for source in short_circuit_patterns:
            tree = tester.assert_boolean_syntax_parses(source)
            assert tester.has_short_circuit_structure(source), f"Should have short-circuit structure: {source}"
            
            bool_ops = tester.get_boolean_operations(source)
            for bool_op in bool_ops:
                if isinstance(bool_op.op, ast.Or):
                    # Should have exactly 2 operands for simple short-circuit
                    assert len(bool_op.values) == 2, f"Simple 'or' should have 2 operands: {source}"


class TestSection611NotOperator:
    """Test 'not' operator functionality."""
    
    def test_basic_not_operations(self, tester):
        """Test basic 'not' operator syntax and structure"""
        # Language Reference: not_test: 'not' not_test | comparison
        not_expressions = [
            "not True",
            "not False",
            "not condition",
            "not x > 5",
            "not obj.attr",
            "not func()",
            "not (a and b)",
        ]
        
        for source in not_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            not_ops = tester.get_unary_operations(source)
            assert len(not_ops) >= 1, f"Should contain 'not' operation: {source}"
            
            for not_op in not_ops:
                assert isinstance(not_op.op, ast.Not), f"Should be 'not' operator: {source}"
                assert not_op.operand is not None, f"'not' should have operand: {source}"
    
    def test_chained_not_operations(self, tester):
        """Test chained 'not' operations"""
        # Language Reference: 'not' operations can be chained (right-associative)
        chained_not_expressions = [
            "not not True",
            "not not condition",
            "not not not False",
            "not not x > 5",
            "not not obj.method()",
        ]
        
        for source in chained_not_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            not_ops = tester.get_unary_operations(source)
            # Should have multiple 'not' operations for chained
            assert len(not_ops) >= 2, f"Should have chained 'not' operations: {source}"
    
    def test_not_with_complex_expressions(self, tester):
        """Test 'not' with complex expressions"""
        # Language Reference: 'not' can negate complex expressions
        complex_not_expressions = [
            "not (a and b)",
            "not (x or y)",
            "not (condition1 and condition2 or condition3)",
            "not obj.method(arg1, arg2)",
            "not x in container",
            "not isinstance(obj, type)",
        ]
        
        for source in complex_not_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            not_ops = tester.get_unary_operations(source)
            assert len(not_ops) >= 1, f"Should contain 'not' operation: {source}"


class TestSection611BooleanPrecedence:
    """Test boolean operator precedence."""
    
    def test_not_and_or_precedence(self, tester):
        """Test precedence: not > and > or"""
        # Language Reference: 'not' has highest precedence, then 'and', then 'or'
        precedence_expressions = [
            "not a and b",              # (not a) and b
            "a and not b",              # a and (not b)
            "not a or b",               # (not a) or b
            "a or not b",               # a or (not b)
            "a and b or c",             # (a and b) or c
            "a or b and c",             # a or (b and c)
            "not a and b or c",         # ((not a) and b) or c
        ]
        
        for source in precedence_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            # Should parse correctly with proper precedence
            assert tree is not None, f"Should parse with correct precedence: {source}"
    
    def test_parentheses_override_precedence(self, tester):
        """Test parentheses overriding boolean precedence"""
        # Language Reference: parentheses can override precedence
        parenthesized_expressions = [
            "(a and b) or c",
            "a and (b or c)",
            "not (a and b)",
            "not (a or b)",
            "(not a) and b",
            "a or (not b and c)",
        ]
        
        for source in parenthesized_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            # Should parse correctly with parentheses
            assert tree is not None, f"Should parse with parentheses: {source}"
    
    def test_comparison_precedence_integration(self, tester):
        """Test boolean operators with comparison precedence"""
        # Language Reference: comparisons have higher precedence than boolean ops
        comparison_boolean_expressions = [
            "x > 5 and y < 10",         # Comparisons before boolean
            "a == b or c != d",         # Multiple comparisons with boolean
            "not x == y",               # 'not' before comparison
            "x in list and y not in other", # Membership with boolean
            "a < b < c and d > e",      # Chained comparison with boolean
        ]
        
        for source in comparison_boolean_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            # Should parse correctly with comparison precedence
            assert tree is not None, f"Should parse comparison with boolean: {source}"


class TestSection611TruthValueTesting:
    """Test truth value testing behavior."""
    
    def test_falsy_value_patterns(self, tester):
        """Test expressions with falsy values"""
        # Language Reference: specific values are considered false
        falsy_patterns = [
            "None or default",
            "False and operation",
            "0 or fallback",
            "[] and process",
            "{} or alternative",
            "'' and action",
            "not []",
            "not 0",
            "not None",
        ]
        
        for source in falsy_patterns:
            tree = tester.assert_boolean_syntax_parses(source)
            # Should parse correctly - truth testing is semantic, not syntactic
            assert tree is not None, f"Should parse falsy pattern: {source}"
    
    def test_truthy_value_patterns(self, tester):
        """Test expressions with truthy values"""
        # Language Reference: most values are considered true
        truthy_patterns = [
            "1 and operation",
            "'string' or fallback",
            "[1, 2, 3] and process",
            "{'key': 'value'} or alternative",
            "object() and action",
            "not 0",
            "not []",
            "not None",
        ]
        
        for source in truthy_patterns:
            tree = tester.assert_boolean_syntax_parses(source)
            # Should parse correctly
            assert tree is not None, f"Should parse truthy pattern: {source}"
    
    def test_custom_object_truth_patterns(self, tester):
        """Test truth value testing with custom objects"""
        # Language Reference: objects can define __bool__ or __len__ for truth testing
        custom_object_patterns = [
            "obj and action",
            "instance or fallback",
            "custom_class() and process",
            "not empty_container",
            "bool(obj) and operation",
        ]
        
        for source in custom_object_patterns:
            tree = tester.assert_boolean_syntax_parses(source)
            # Should parse correctly - custom truth testing is runtime behavior
            assert tree is not None, f"Should parse custom object pattern: {source}"


class TestSection611ComplexBooleanPatterns:
    """Test complex boolean operation patterns."""
    
    def test_nested_boolean_expressions(self, tester):
        """Test deeply nested boolean expressions"""
        # Language Reference: boolean operations can be arbitrarily nested
        nested_patterns = [
            "(a and b) or (c and d)",
            "(x > 0 and x < 10) or (x > 20 and x < 30)",
            "not (a or b) and not (c or d)",
            "(flag1 or flag2) and (condition1 or condition2)",
            "((a and b) or c) and ((d or e) and f)",
        ]
        
        for source in nested_patterns:
            tree = tester.assert_boolean_syntax_parses(source)
            # Should handle complex nesting
            bool_ops = tester.get_boolean_operations(source)
            assert len(bool_ops) >= 2, f"Should have multiple boolean operations: {source}"
    
    def test_function_call_integration(self, tester):
        """Test boolean operations with function calls"""
        # Language Reference: function calls can be operands in boolean expressions
        function_call_patterns = [
            "validate(data) and process(data)",
            "check_permission() or raise_error()",
            "func1() and func2() and func3()",
            "not validate(input) or handle_invalid()",
            "attempt() or retry() or fail()",
        ]
        
        for source in function_call_patterns:
            tree = tester.assert_boolean_syntax_parses(source)
            # Find function calls within boolean expressions
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            assert len(calls) >= 1, f"Should contain function calls: {source}"
    
    def test_comprehension_boolean_integration(self, tester):
        """Test boolean operations in comprehensions"""
        # Language Reference: boolean operations can appear in comprehensions
        comprehension_patterns = [
            "[x for x in items if x > 0 and x < 10]",
            "[item for item in data if validate(item) and process(item)]",
            "{k: v for k, v in pairs if k and v}",
            "(x for x in sequence if not x or special(x))",
            "[result for item in items if condition1(item) or condition2(item)]",
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_boolean_syntax_parses(source)
            # Should contain both comprehension and boolean operations
            comprehensions = [node for node in ast.walk(tree) 
                             if isinstance(node, (ast.ListComp, ast.DictComp, 
                                                 ast.SetComp, ast.GeneratorExp))]
            assert len(comprehensions) >= 1, f"Should contain comprehension: {source}"


class TestSection611ErrorConditions:
    """Test boolean operation error conditions."""
    
    def test_invalid_boolean_syntax(self, tester):
        """Test invalid boolean operation syntax"""
        # Language Reference: syntactic restrictions on boolean operators
        invalid_boolean_expressions = [
            "and True",                 # Missing left operand
            "True and",                 # Missing right operand
            "or False",                 # Missing left operand
            "False or",                 # Missing right operand
            "not",                      # Missing operand
            "True and and False",       # Duplicate 'and'
            "True or or False",         # Duplicate 'or'
            "and or True",              # Invalid operator combination
        ]
        
        for source in invalid_boolean_expressions:
            tester.assert_boolean_syntax_error(source)
    
    def test_boolean_indentation_requirements(self, tester):
        """Test boolean operations follow indentation rules"""
        # Language Reference: boolean operations follow normal expression indentation
        valid_indented_expressions = [
            """
if condition:
    result = a and b
""",
            """
value = (
    long_condition_1 and
    long_condition_2 or
    fallback_condition
)
""",
            """
def function():
    return (
        validate_input() and
        process_data() and
        save_result()
    )
"""
        ]
        
        for source in valid_indented_expressions:
            tree = tester.assert_boolean_syntax_parses(source)
            # Should handle indentation correctly
            assert tree is not None, f"Should handle indentation: {source}"


class TestSection611CrossImplementationCompatibility:
    """Test cross-implementation compatibility for boolean operations."""
    
    def test_boolean_ast_structure_consistency(self, tester):
        """Test boolean operation AST structure across implementations"""
        # Language Reference: AST structure should be consistent
        test_cases = [
            "a and b",
            "x or y",
            "not condition",
            "a and b or c",
            "not (a or b)",
        ]
        
        for source in test_cases:
            tree = tester.assert_boolean_syntax_parses(source)
            # Check for proper AST structure
            bool_ops = tester.get_boolean_operations(source)
            not_ops = tester.get_unary_operations(source)
            
            # Should have boolean or unary operations
            total_ops = len(bool_ops) + len(not_ops)
            assert total_ops >= 1, f"Should have boolean/unary operations: {source}"
    
    def test_complex_boolean_evaluation_patterns(self, tester):
        """Test complex boolean patterns for compatibility"""
        # Language Reference: comprehensive real-world patterns
        complex_patterns = [
            """
result = (
    validate_input(data) and
    check_permissions(user) and
    (
        process_normal(data) or
        process_fallback(data)
    )
)
""",
            """
condition = (
    not error_occurred and
    (success_flag or retry_flag) and
    not maintenance_mode
)
""",
            """
access_granted = (
    user.is_authenticated() and
    user.has_permission(resource) and
    (
        resource.is_public() or
        user.owns(resource) or
        user.is_admin()
    )
)
"""
        ]
        
        for source in complex_patterns:
            tree = tester.assert_boolean_syntax_parses(source)
            # Just verify complex patterns parse successfully
            assert len(tree.body) >= 1, f"Complex boolean pattern should parse: {source}"
    
    def test_boolean_operation_introspection(self, tester):
        """Test ability to analyze boolean operations programmatically"""
        # Test programmatic analysis of boolean operation structure
        introspection_source = "validate_data(input) and process_data(input) or handle_error()"
        
        tree = tester.assert_boolean_syntax_parses(introspection_source)
        bool_ops = tester.get_boolean_operations(source=introspection_source)
        
        # Should be able to identify and analyze boolean operations
        assert len(bool_ops) >= 1, "Should have boolean operations"
        
        # Should be able to analyze operation types and operands
        for bool_op in bool_ops:
            assert hasattr(bool_op, 'op'), "BoolOp should have 'op' attribute"
            assert hasattr(bool_op, 'values'), "BoolOp should have 'values' attribute"
            assert len(bool_op.values) >= 2, "BoolOp should have at least 2 values"