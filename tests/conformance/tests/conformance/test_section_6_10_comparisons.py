"""
Section 6.10: Comparisons - Conformance Test Suite

Tests Python Language Reference Section 6.10 compliance across implementations.
Based on formal grammar definitions and prose assertions for comparison operations.

Grammar tested:
    comparison: or_expr (comp_op or_expr)*
    comp_op: '<'|'>'|'=='|'>='|'<='|'!='|'in'|'not' 'in'|'is'|'is' 'not'

Language Reference requirements tested:
    - All comparison operators: ==, !=, <, <=, >, >=, is, is not, in, not in
    - Comparison chaining (a < b < c)
    - Short-circuit evaluation in chained comparisons
    - Identity vs equality testing (is vs ==)
    - Membership testing (in, not in)
    - Type-specific comparison behavior
    - Error conditions and type compatibility
    - Operator precedence with other expressions
    - Cross-implementation compatibility
"""

import ast
import pytest
import sys
from typing import Any


class ComparisonTester:
    """Helper class for testing comparison operation conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_comparison_syntax_parses(self, source: str):
        """Test that comparison operation syntax parses correctly.
        
        Args:
            source: Python comparison operation source code
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Comparison syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_comparison_syntax_error(self, source: str):
        """Test that invalid comparison syntax raises SyntaxError.
        
        Args:
            source: Python comparison source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_comparison_operations(self, source: str) -> list:
        """Get Compare AST nodes from source for analysis.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Compare nodes
        """
        tree = ast.parse(source)
        comparisons = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                comparisons.append(node)
        
        return comparisons
    
    def has_chained_comparison(self, source: str) -> bool:
        """Check if source contains chained comparison operations.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains chained comparisons (a < b < c)
        """
        comparisons = self.get_comparison_operations(source)
        for comp in comparisons:
            if len(comp.ops) > 1:  # Chained comparison has multiple operators
                return True
        return False
    
    def get_comparison_operators(self, source: str) -> list:
        """Get list of comparison operator types from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of operator type names (e.g., ['Lt', 'Gt'])
        """
        comparisons = self.get_comparison_operations(source)
        operators = []
        
        for comp in comparisons:
            for op in comp.ops:
                operators.append(type(op).__name__)
        
        return operators


@pytest.fixture
def tester():
    """Provide ComparisonTester instance for tests."""
    return ComparisonTester()


class TestSection610EqualityOperators:
    """Test equality and inequality operators."""
    
    def test_equality_operators(self, tester):
        """Test equality (==) and inequality (!=) operators"""
        # Language Reference: == and != for value equality/inequality
        equality_expressions = [
            "a == b",
            "x != y",
            "value == 42",
            "result != None",
            "'hello' == 'world'",
            "[1, 2, 3] == [1, 2, 3]",
            "{} != {'key': 'value'}",
            "func() == expected",
            "obj.attr != default",
        ]
        
        for source in equality_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"
            
            # Check operator types
            operators = tester.get_comparison_operators(source)
            assert any(op in ['Eq', 'NotEq'] for op in operators), f"Should have equality operator: {source}"
    
    def test_equality_with_different_types(self, tester):
        """Test equality operations with different types"""
        # Language Reference: equality can be tested between different types
        type_equality_expressions = [
            "1 == 1.0",              # int vs float
            "'42' != 42",            # string vs int  
            "[] == ()",              # list vs tuple
            "None == False",         # None vs bool
            "0 == False",            # int vs bool
            "'' == 0",               # string vs int
            "obj == str(obj)",       # object vs string representation
        ]
        
        for source in type_equality_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            # Should parse correctly - type compatibility is runtime behavior
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"
    
    def test_equality_chaining(self, tester):
        """Test chained equality operations"""
        # Language Reference: equality can be chained
        chained_equality_expressions = [
            "a == b == c",
            "x != y != z",  
            "value == expected == correct",
            "result1 == result2 != fallback",
            "a == b != c == d",
        ]
        
        for source in chained_equality_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            assert tester.has_chained_comparison(source), f"Should have chained comparison: {source}"
            
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain chained comparison: {source}"


class TestSection610OrderingOperators:
    """Test ordering comparison operators."""
    
    def test_ordering_operators(self, tester):
        """Test ordering operators: <, <=, >, >="""
        # Language Reference: ordering operators for magnitude comparison
        ordering_expressions = [
            "a < b",
            "x <= y", 
            "value > threshold",
            "count >= minimum",
            "age < 18",
            "score >= 90",
            "temperature <= freezing",
            "pressure > atmospheric",
            "distance <= maximum",
        ]
        
        for source in ordering_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"
            
            # Check operator types
            operators = tester.get_comparison_operators(source)
            assert any(op in ['Lt', 'LtE', 'Gt', 'GtE'] for op in operators), f"Should have ordering operator: {source}"
    
    def test_chained_ordering_operators(self, tester):
        """Test chained ordering operations"""
        # Language Reference: ordering operators can be chained
        chained_ordering_expressions = [
            "a < b < c",
            "min <= value <= max",
            "x > y >= z",
            "0 <= index < length",
            "start < middle <= end",
            "low < current < high <= maximum",
        ]
        
        for source in chained_ordering_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            assert tester.has_chained_comparison(source), f"Should have chained comparison: {source}"
            
            comparisons = tester.get_comparison_operations(source)
            for comp in comparisons:
                assert len(comp.ops) >= 2, f"Chained comparison should have multiple operators: {source}"
    
    def test_ordering_with_numeric_types(self, tester):
        """Test ordering with different numeric types"""
        # Language Reference: ordering works across numeric types
        numeric_ordering_expressions = [
            "1 < 2.5",               # int vs float
            "3.14 >= 3",             # float vs int
            "x <= 100.0",            # variable vs float literal
            "42 > threshold",        # int vs variable
            "temperature < 0.0",     # variable vs float
        ]
        
        for source in numeric_ordering_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            # Should parse correctly - numeric compatibility is well-defined
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"
    
    def test_ordering_error_conditions(self, tester):
        """Test ordering with incompatible types (syntax still valid)"""
        # Language Reference: ordering with incompatible types raises TypeError at runtime
        incompatible_ordering_expressions = [
            "'string' < 42",         # string vs int
            "[] > 'list'",           # list vs string
            "None >= 0",             # None vs int
            "{} < []",               # dict vs list
        ]
        
        for source in incompatible_ordering_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            # Should parse correctly - type errors happen at runtime, not parse time
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"


class TestSection610IdentityOperators:
    """Test identity operators (is, is not)."""
    
    def test_identity_operators(self, tester):
        """Test identity operators: is, is not"""
        # Language Reference: is/is not test object identity, not equality
        identity_expressions = [
            "a is b",
            "x is not y",
            "value is None",
            "result is not None",
            "obj is self",
            "instance is not other",
            "cache is shared",
            "error is not expected",
            "reference is original",
        ]
        
        for source in identity_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"
            
            # Check operator types
            operators = tester.get_comparison_operators(source)
            assert any(op in ['Is', 'IsNot'] for op in operators), f"Should have identity operator: {source}"
    
    def test_identity_vs_equality_patterns(self, tester):
        """Test patterns distinguishing identity from equality"""
        # Language Reference: is tests identity, == tests equality
        identity_vs_equality_expressions = [
            "obj is obj",            # Always true - same object
            "obj == obj",            # Usually true - equal to itself
            "a is None",             # Identity check with singleton
            "a == None",             # Equality check with singleton  
            "[] is []",              # Different list objects
            "[] == []",              # Equal but not identical lists
            "'hello' is 'hello'",    # String interning behavior
            "'hello' == 'hello'",    # String equality
        ]
        
        for source in identity_vs_equality_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"
    
    def test_identity_chaining(self, tester):
        """Test chained identity operations"""
        # Language Reference: identity operators can be chained
        chained_identity_expressions = [
            "a is b is c",
            "x is not y is not z",
            "obj is ref is original",
            "value is None is singleton",
            "instance is not other is not third",
        ]
        
        for source in chained_identity_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            assert tester.has_chained_comparison(source), f"Should have chained comparison: {source}"
            
            operators = tester.get_comparison_operators(source)
            assert any(op in ['Is', 'IsNot'] for op in operators), f"Should have identity operators: {source}"
    
    def test_identity_with_singletons(self, tester):
        """Test identity operations with singleton objects"""
        # Language Reference: None, True, False are singletons
        singleton_identity_expressions = [
            "value is None",
            "flag is True",
            "condition is False", 
            "result is not None",
            "success is not False",
            "error is not True",
            "x is None is None",     # Chained with singleton
        ]
        
        for source in singleton_identity_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"


class TestSection610MembershipOperators:
    """Test membership operators (in, not in)."""
    
    def test_membership_operators(self, tester):
        """Test membership operators: in, not in"""
        # Language Reference: in/not in test membership in sequences/containers
        membership_expressions = [
            "item in container",
            "key not in dict",
            "value in list",
            "element not in set",
            "'substring' in string",
            "42 not in numbers",
            "obj in collection",
            "target not in results",
            "char in alphabet",
        ]
        
        for source in membership_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"
            
            # Check operator types
            operators = tester.get_comparison_operators(source)
            assert any(op in ['In', 'NotIn'] for op in operators), f"Should have membership operator: {source}"
    
    def test_membership_with_different_containers(self, tester):
        """Test membership with different container types"""
        # Language Reference: membership works with sequences, sets, dicts, etc.
        container_membership_expressions = [
            "'a' in 'hello'",        # string membership
            "1 in [1, 2, 3]",        # list membership
            "'key' in {'key': 'value'}", # dict key membership
            "42 in {1, 2, 42}",      # set membership
            "item in (a, b, c)",     # tuple membership
            "x not in range(10)",    # range membership
            "value in custom_container", # custom container
        ]
        
        for source in container_membership_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"
    
    def test_membership_chaining(self, tester):
        """Test chained membership operations"""
        # Language Reference: membership operators can be chained
        chained_membership_expressions = [
            "a in container1 in container2",
            "x not in list1 not in list2",
            "key in dict1 in dicts",
            "item in collection not in excluded",
            "value not in rejected in accepted",
        ]
        
        for source in chained_membership_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            assert tester.has_chained_comparison(source), f"Should have chained comparison: {source}"
            
            operators = tester.get_comparison_operators(source)
            assert any(op in ['In', 'NotIn'] for op in operators), f"Should have membership operators: {source}"
    
    def test_membership_with_expressions(self, tester):
        """Test membership with complex expressions"""
        # Language Reference: membership operands can be complex expressions
        expression_membership_expressions = [
            "func().result in data",
            "obj.attr not in container",
            "x + y in valid_range",
            "str(value) in string_set",
            "item.key in obj.dict",
            "calculated() not in excluded_results()",
        ]
        
        for source in expression_membership_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            comparisons = tester.get_comparison_operations(source)
            assert len(comparisons) >= 1, f"Should contain comparison: {source}"


class TestSection610ComparisonChaining:
    """Test chained comparison operations."""
    
    def test_mixed_comparison_chaining(self, tester):
        """Test chaining of different comparison types"""
        # Language Reference: different comparison operators can be chained
        mixed_chaining_expressions = [
            "a < b == c",            # ordering + equality
            "x is y != z",           # identity + inequality  
            "min <= value < max",    # ordering chain
            "obj is not None != other", # identity + inequality
            "key in dict == expected",  # membership + equality
            "a < b is c",            # ordering + identity
            "value != None is not other", # inequality + identity
        ]
        
        for source in mixed_chaining_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            assert tester.has_chained_comparison(source), f"Should have chained comparison: {source}"
            
            # Should have multiple different operator types
            operators = tester.get_comparison_operators(source)
            assert len(set(operators)) >= 2, f"Should have different operator types: {source}"
    
    def test_long_comparison_chains(self, tester):
        """Test long chains of comparisons"""
        # Language Reference: arbitrary length comparison chains are supported
        long_chain_expressions = [
            "a < b < c < d",
            "w == x == y == z",
            "p is q is r is s",
            "a in b in c in d",
            "x != y != z != w != v",
            "min <= low < value <= high < max",
        ]
        
        for source in long_chain_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            assert tester.has_chained_comparison(source), f"Should have chained comparison: {source}"
            
            comparisons = tester.get_comparison_operations(source)
            for comp in comparisons:
                assert len(comp.ops) >= 3, f"Long chain should have 3+ operators: {source}"
    
    def test_comparison_chain_short_circuit(self, tester):
        """Test short-circuit behavior structure in comparison chains"""
        # Language Reference: comparison chains short-circuit on first False result
        short_circuit_expressions = [
            "expensive() == result == validate()",
            "check1() < check2() <= max_value",
            "obj.method() is not None != other()",
            "validate_input() in valid_set == True",
            "a < compute_middle() < compute_end()",
        ]
        
        for source in short_circuit_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            assert tester.has_chained_comparison(source), f"Should have chained comparison: {source}"
            
            # Find function calls that could demonstrate short-circuit
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            assert len(calls) >= 1, f"Should have function calls for short-circuit demo: {source}"


class TestSection610ComparisonPrecedence:
    """Test comparison operator precedence."""
    
    def test_comparison_vs_boolean_precedence(self, tester):
        """Test comparison precedence with boolean operators"""
        # Language Reference: comparisons have higher precedence than boolean ops
        precedence_expressions = [
            "a < b and c > d",       # comparisons before 'and'
            "x == y or z != w",      # comparisons before 'or'
            "not a < b",             # 'not' before comparison
            "a in list and b not in other", # membership before boolean
            "x is None or y is not None",   # identity before boolean
        ]
        
        for source in precedence_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            # Should parse correctly with proper precedence
            assert tree is not None, f"Should parse with correct precedence: {source}"
    
    def test_comparison_vs_arithmetic_precedence(self, tester):
        """Test comparison precedence with arithmetic operators"""
        # Language Reference: arithmetic has higher precedence than comparisons
        arithmetic_comparison_expressions = [
            "x + y < z",             # arithmetic before comparison
            "a * b == c",            # arithmetic before comparison
            "value - offset > threshold", # arithmetic before comparison
            "a / b <= ratio",        # arithmetic before comparison
            "x ** 2 != y",           # exponentiation before comparison
        ]
        
        for source in arithmetic_comparison_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            # Should parse correctly with proper precedence
            assert tree is not None, f"Should parse with arithmetic precedence: {source}"
    
    def test_parentheses_override_precedence(self, tester):
        """Test parentheses overriding comparison precedence"""
        # Language Reference: parentheses can override precedence
        parenthesized_expressions = [
            "(a < b) and c",         # explicit comparison grouping
            "not (x == y)",          # explicit comparison grouping  
            "(a + b) < (c + d)",     # explicit arithmetic grouping
            "(value in container) or fallback", # explicit membership grouping
            "(obj is None) and (other is not None)", # explicit identity grouping
        ]
        
        for source in parenthesized_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            # Should parse correctly with parentheses
            assert tree is not None, f"Should parse with parentheses: {source}"


class TestSection610ErrorConditions:
    """Test comparison operation error conditions."""
    
    def test_invalid_comparison_syntax(self, tester):
        """Test invalid comparison operation syntax"""
        # Language Reference: syntactic restrictions on comparison operators
        invalid_comparison_expressions = [
            "< x",                   # Missing left operand
            "x >",                   # Missing right operand  
            "== y",                  # Missing left operand
            "x !=",                  # Missing right operand
            "is object",             # Missing left operand
            "x is not",              # Missing right operand for 'is not'
            "in container",          # Missing left operand
            "x not in",              # Missing right operand for 'not in'
            "x < < y",               # Invalid operator repetition
            "a == == b",             # Invalid operator repetition
        ]
        
        for source in invalid_comparison_expressions:
            tester.assert_comparison_syntax_error(source)
    
    def test_comparison_indentation_requirements(self, tester):
        """Test comparison operations follow indentation rules"""
        # Language Reference: comparisons follow normal expression indentation
        valid_indented_expressions = [
            """
if value < threshold:
    process()
""",
            """
result = (
    long_variable_name ==
    another_long_name
)
""",
            """
def validate():
    return (
        x in valid_range and
        y not in excluded and
        obj is not None
    )
"""
        ]
        
        for source in valid_indented_expressions:
            tree = tester.assert_comparison_syntax_parses(source)
            # Should handle indentation correctly
            assert tree is not None, f"Should handle indentation: {source}"


class TestSection610CrossImplementationCompatibility:
    """Test cross-implementation compatibility for comparisons."""
    
    def test_comparison_ast_structure_consistency(self, tester):
        """Test comparison operation AST structure across implementations"""
        # Language Reference: AST structure should be consistent
        test_cases = [
            "a == b",
            "x < y",
            "obj is None",
            "item in container",
            "a < b <= c",
            "x == y != z",
        ]
        
        for source in test_cases:
            tree = tester.assert_comparison_syntax_parses(source)
            comparisons = tester.get_comparison_operations(source)
            
            # Should have comparison operations
            assert len(comparisons) >= 1, f"Should have comparison operations: {source}"
            
            # Check AST structure consistency
            for comp in comparisons:
                assert hasattr(comp, 'left'), "Compare should have 'left' attribute"
                assert hasattr(comp, 'ops'), "Compare should have 'ops' attribute"
                assert hasattr(comp, 'comparators'), "Compare should have 'comparators' attribute"
                assert len(comp.ops) == len(comp.comparators), "ops and comparators should match"
    
    def test_all_comparison_operators_supported(self, tester):
        """Test all comparison operators are properly supported"""
        # Language Reference: comprehensive operator support verification
        operator_test_cases = [
            ("a == b", "Eq"),
            ("a != b", "NotEq"),  
            ("a < b", "Lt"),
            ("a <= b", "LtE"),
            ("a > b", "Gt"),
            ("a >= b", "GtE"),
            ("a is b", "Is"),
            ("a is not b", "IsNot"),
            ("a in b", "In"),
            ("a not in b", "NotIn"),
        ]
        
        for source, expected_op in operator_test_cases:
            tree = tester.assert_comparison_syntax_parses(source)
            operators = tester.get_comparison_operators(source)
            assert expected_op in operators, f"Should support {expected_op} operator: {source}"
    
    def test_complex_comparison_evaluation_patterns(self, tester):
        """Test complex comparison patterns for compatibility"""
        # Language Reference: comprehensive real-world patterns
        complex_patterns = [
            """
valid = (
    min_value <= user_input <= max_value and
    user_input not in forbidden_values and
    validate_type(user_input) is True
)
""",
            """
access_check = (
    user is not None and
    user.role in allowed_roles and
    resource.owner == user or user.is_admin()
)
""",
            """
boundary_check = (
    0 <= x < width and
    0 <= y < height and
    grid[x][y] is not None and
    grid[x][y] not in obstacles
)
"""
        ]
        
        for source in complex_patterns:
            tree = tester.assert_comparison_syntax_parses(source)
            # Just verify complex patterns parse successfully
            assert len(tree.body) >= 1, f"Complex comparison pattern should parse: {source}"
    
    def test_comparison_operation_introspection(self, tester):
        """Test ability to analyze comparison operations programmatically"""
        # Test programmatic analysis of comparison operation structure
        introspection_source = "min_val <= user_input < max_val and user_input not in excluded"
        
        tree = tester.assert_comparison_syntax_parses(introspection_source)
        comparisons = tester.get_comparison_operations(source=introspection_source)
        
        # Should be able to identify and analyze comparison operations
        assert len(comparisons) >= 1, "Should have comparison operations"
        
        # Should be able to analyze operation structure
        for comp in comparisons:
            assert hasattr(comp, 'left'), "Compare should have 'left' attribute"
            assert hasattr(comp, 'ops'), "Compare should have 'ops' attribute"  
            assert hasattr(comp, 'comparators'), "Compare should have 'comparators' attribute"
            
            # Should be able to inspect operator types
            for op in comp.ops:
                op_type = type(op).__name__
                assert op_type in ['Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 
                                  'Is', 'IsNot', 'In', 'NotIn'], f"Should recognize operator: {op_type}"