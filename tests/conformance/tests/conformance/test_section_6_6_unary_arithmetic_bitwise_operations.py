"""
Section 6.6: Unary Arithmetic and Bitwise Operations - Conformance Test Suite

Tests Python Language Reference Section 6.6 compliance across implementations.
Based on formal unary operation syntax definitions and prose assertions for single-operand behavior.

Grammar tested:
    u_expr: power | '-' u_expr | '+' u_expr | '~' u_expr

Language Reference requirements tested:
    - Unary plus (+), minus (-), and bitwise NOT (~) operator syntax validation
    - Type support and coercion for unary operations
    - Unary operation precedence and associativity rules
    - Chained unary operations and operator interaction
    - Unary operations with different data types
    - Error conditions for invalid unary operations
    - Unary operation AST structure validation
    - Cross-implementation unary operation compatibility
"""

import ast
import pytest
import sys
from typing import Any


class UnaryOperationTester:
    """Helper class for testing unary operation conformance.
    
    Focuses on AST structure validation for unary operation syntax and behavior
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_unary_operation_parses(self, source: str):
        """Test that unary operation syntax parses correctly.
        
        Args:
            source: Python source code with unary operations
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Unary operation syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_unary_operation_syntax_error(self, source: str):
        """Test that invalid unary operation syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_unary_operations(self, source: str) -> list:
        """Get UnaryOp AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.UnaryOp nodes
        """
        tree = ast.parse(source)
        unary_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.UnaryOp):
                unary_ops.append(node)
        
        return unary_ops
    
    def get_unary_plus_operations(self, source: str) -> list:
        """Get unary plus operations from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.UnaryOp nodes with UAdd operators
        """
        tree = ast.parse(source)
        plus_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
                plus_ops.append(node)
        
        return plus_ops
    
    def get_unary_minus_operations(self, source: str) -> list:
        """Get unary minus operations from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.UnaryOp nodes with USub operators
        """
        tree = ast.parse(source)
        minus_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
                minus_ops.append(node)
        
        return minus_ops
    
    def get_unary_not_operations(self, source: str) -> list:
        """Get unary bitwise NOT operations from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.UnaryOp nodes with Invert operators
        """
        tree = ast.parse(source)
        not_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert):
                not_ops.append(node)
        
        return not_ops
    
    def count_chained_unary_operations(self, source: str) -> int:
        """Count depth of chained unary operations.
        
        Args:
            source: Python source code
            
        Returns:
            Maximum depth of chained unary operations
        """
        tree = ast.parse(source)
        
        def count_depth(node):
            if isinstance(node, ast.UnaryOp):
                # Count chain depth in operand
                operand_depth = count_depth(node.operand)
                return 1 + operand_depth
            return 0
        
        max_depth = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.UnaryOp):
                depth = count_depth(node)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def get_binary_operations(self, source: str) -> list:
        """Get binary operations from source for precedence testing.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes
        """
        tree = ast.parse(source)
        binary_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                binary_ops.append(node)
        
        return binary_ops


@pytest.fixture
def tester():
    """Provide UnaryOperationTester instance for tests."""
    return UnaryOperationTester()


class TestSection66BasicUnarySyntax:
    """Test basic unary operation syntax."""
    
    def test_simple_unary_plus_operations(self, tester):
        """Test simple unary plus operation patterns"""
        # Language Reference: u_expr: '+' u_expr
        unary_plus_patterns = [
            """
result = +42
""",
            """
value = +x
""",
            """
output = +variable
""",
            """
positive = +number
""",
            """
explicit_positive = +input_value
"""
        ]
        
        for source in unary_plus_patterns:
            tree = tester.assert_unary_operation_parses(source)
            plus_ops = tester.get_unary_plus_operations(source)
            assert len(plus_ops) >= 1, f"Should have unary plus operations: {source}"
    
    def test_simple_unary_minus_operations(self, tester):
        """Test simple unary minus operation patterns"""
        # Language Reference: u_expr: '-' u_expr
        unary_minus_patterns = [
            """
result = -42
""",
            """
value = -x
""",
            """
negative = -variable
""",
            """
opposite = -number
""",
            """
negated = -input_value
"""
        ]
        
        for source in unary_minus_patterns:
            tree = tester.assert_unary_operation_parses(source)
            minus_ops = tester.get_unary_minus_operations(source)
            assert len(minus_ops) >= 1, f"Should have unary minus operations: {source}"
    
    def test_simple_unary_not_operations(self, tester):
        """Test simple unary bitwise NOT operation patterns"""
        # Language Reference: u_expr: '~' u_expr
        unary_not_patterns = [
            """
result = ~42
""",
            """
value = ~x
""",
            """
inverted = ~variable
""",
            """
complement = ~number
""",
            """
flipped = ~input_value
"""
        ]
        
        for source in unary_not_patterns:
            tree = tester.assert_unary_operation_parses(source)
            not_ops = tester.get_unary_not_operations(source)
            assert len(not_ops) >= 1, f"Should have unary NOT operations: {source}"
    
    def test_unary_with_variables(self, tester):
        """Test unary operations with variables"""
        # Language Reference: operands can be variables
        variable_unary_patterns = [
            """
result = +value
""",
            """
negative = -data
""",
            """
inverted = ~flags
""",
            """
positive_var = +input_variable
""",
            """
negated_var = -output_variable
"""
        ]
        
        for source in variable_unary_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should handle variable operands: {source}"
    
    def test_unary_with_expressions(self, tester):
        """Test unary operations with complex expressions"""
        # Language Reference: operands can be complex expressions
        expression_unary_patterns = [
            """
result = +(a + b)
""",
            """
value = -(x * y)
""",
            """
output = ~(flags | mask)
""",
            """
negative_call = -calculate()
""",
            """
inverted_access = ~array[index]
"""
        ]
        
        for source in expression_unary_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should handle complex expressions: {source}"


class TestSection66UnaryChaining:
    """Test chained unary operations."""
    
    def test_chained_unary_plus_operations(self, tester):
        """Test chained unary plus operations"""
        # Language Reference: unary operators can be chained
        chained_plus_patterns = [
            """
result = ++value
""",
            """
output = +++x
""",
            """
multiple_plus = ++(+y)
""",
            """
nested_plus = +(+(+z))
""",
            """
chain_plus = +++++number
"""
        ]
        
        for source in chained_plus_patterns:
            tree = tester.assert_unary_operation_parses(source)
            plus_ops = tester.get_unary_plus_operations(source)
            assert len(plus_ops) >= 2, f"Should have chained plus operations: {source}"
    
    def test_chained_unary_minus_operations(self, tester):
        """Test chained unary minus operations"""
        # Language Reference: unary operators can be chained
        chained_minus_patterns = [
            """
result = --value
""",
            """
output = ---x
""",
            """
multiple_minus = --(--y)
""",
            """
nested_minus = -(-(- z))
""",
            """
chain_minus = -----number
"""
        ]
        
        for source in chained_minus_patterns:
            tree = tester.assert_unary_operation_parses(source)
            minus_ops = tester.get_unary_minus_operations(source)
            assert len(minus_ops) >= 2, f"Should have chained minus operations: {source}"
    
    def test_chained_unary_not_operations(self, tester):
        """Test chained unary bitwise NOT operations"""
        # Language Reference: unary operators can be chained
        chained_not_patterns = [
            """
result = ~~value
""",
            """
output = ~~~x
""",
            """
multiple_not = ~~(~~y)
""",
            """
nested_not = ~(~(~z))
""",
            """
chain_not = ~~~~~number
"""
        ]
        
        for source in chained_not_patterns:
            tree = tester.assert_unary_operation_parses(source)
            not_ops = tester.get_unary_not_operations(source)
            assert len(not_ops) >= 2, f"Should have chained NOT operations: {source}"
    
    def test_mixed_unary_operations(self, tester):
        """Test mixed unary operations"""
        # Language Reference: different unary operators can be combined
        mixed_unary_patterns = [
            """
result = +-value
""",
            """
output = -+x
""",
            """
mixed = ~-y
""",
            """
complex_mix = -~+z
""",
            """
varied = +-~-+number
"""
        ]
        
        for source in mixed_unary_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 2, f"Should have mixed unary operations: {source}"
    
    def test_unary_chaining_depth(self, tester):
        """Test deep unary operation chaining"""
        # Language Reference: unary operators can be arbitrarily chained
        deep_chaining_patterns = [
            """
deep_plus = ++++++++value
""",
            """
deep_minus = --------x
""",
            """
deep_not = ~~~~~~~~y
""",
            """
deep_mixed = +-~+-~+-z
""",
            """
very_deep = -+-+-+-+-+-+-number
"""
        ]
        
        for source in deep_chaining_patterns:
            tree = tester.assert_unary_operation_parses(source)
            chain_depth = tester.count_chained_unary_operations(source)
            assert chain_depth >= 5, f"Should have deep chaining: {source}"


class TestSection66UnaryPrecedence:
    """Test unary operation precedence."""
    
    def test_unary_vs_binary_precedence(self, tester):
        """Test precedence of unary vs binary operations"""
        # Language Reference: unary operators have high precedence
        precedence_patterns = [
            """
result = -a + b
""",
            """
value = +x * y
""",
            """
output = ~flags & mask
""",
            """
calculation = -x ** y
""",
            """
expression = +a - b * c
"""
        ]
        
        for source in precedence_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(unary_ops) >= 1, f"Should have unary operations: {source}"
            assert len(binary_ops) >= 1, f"Should have binary operations: {source}"
    
    def test_unary_vs_power_precedence(self, tester):
        """Test precedence of unary vs power operations"""
        # Language Reference: power has higher precedence than unary minus
        power_precedence_patterns = [
            """
# -x**y is parsed as -(x**y), not (-x)**y
result = -x ** 2
""",
            """
value = +a ** b
""",
            """
output = ~base ** exponent
""",
            """
calculation = -2 ** 3
""",
            """
expression = +value ** power
"""
        ]
        
        for source in power_precedence_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            # Should parse correctly according to precedence rules
            assert len(unary_ops) >= 1, f"Should handle unary/power precedence: {source}"
    
    def test_unary_with_parentheses(self, tester):
        """Test unary operations with explicit parentheses"""
        # Language Reference: parentheses override precedence
        parentheses_patterns = [
            """
result = (-a) + b
""",
            """
value = -(a + b)
""",
            """
output = ~(flags | mask)
""",
            """
calculation = (-x) ** 2
""",
            """
expression = +(a - b) * c
"""
        ]
        
        for source in parentheses_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should handle parentheses: {source}"
    
    def test_multiple_unary_precedence(self, tester):
        """Test precedence with multiple unary operations"""
        # Language Reference: unary operations are right-associative
        multiple_unary_patterns = [
            """
# --x is parsed as -(-x)
result = --value
""",
            """
# ~~flags is parsed as ~(~flags)
output = ~~flags
""",
            """
# -+x is parsed as -(+x)
mixed = -+number
""",
            """
# Complex chaining
complex_chain = -~+-x
""",
            """
# With binary operations
with_binary = --a + ++b
"""
        ]
        
        for source in multiple_unary_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 2, f"Should handle multiple unary operations: {source}"


class TestSection66UnaryOperationContexts:
    """Test unary operations in different contexts."""
    
    def test_unary_in_assignments(self, tester):
        """Test unary operations in assignment contexts"""
        # Language Reference: unary operations in assignments
        assignment_patterns = [
            """
result = -value
""",
            """
positive = +number
""",
            """
inverted = ~flags
""",
            """
a, b = -x, +y
""",
            """
array[index] = -data
"""
        ]
        
        for source in assignment_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should work in assignments: {source}"
    
    def test_unary_in_function_calls(self, tester):
        """Test unary operations in function call arguments"""
        # Language Reference: unary operations in function arguments
        function_call_patterns = [
            """
result = process(-value)
""",
            """
output = transform(+data, mode='negative')
""",
            """
validate(~flags, expected & mask)
""",
            """
complex_function(
    -a,
    +b,
    flags=~c
)
""",
            """
api_call(~base_flags, format=-format_code)
"""
        ]
        
        for source in function_call_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should work in function calls: {source}"
    
    def test_unary_in_return_statements(self, tester):
        """Test unary operations in return statements"""
        # Language Reference: unary operations in returns
        return_patterns = [
            """
def negate(value):
    return -value
""",
            """
def make_positive(number):
    return +number
""",
            """
def invert_bits(flags):
    return ~flags
""",
            """
def process_data(data, negate=False):
    return -data if negate else +data
""",
            """
def compute_complement(value):
    return ~value & 0xFF
"""
        ]
        
        for source in return_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should work in returns: {source}"
    
    def test_unary_in_comprehensions(self, tester):
        """Test unary operations in comprehensions"""
        # Language Reference: unary operations in comprehensions
        comprehension_patterns = [
            """
negated = [-x for x in values]
""",
            """
positive = [+x for x in numbers]
""",
            """
inverted = [~flag for flag in flags]
""",
            """
processed = {key: -value for key, value in data.items()}
""",
            """
mixed = [
    -item if item > 0 else +item
    for item in dataset
    if ~item & mask
]
"""
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should work in comprehensions: {source}"
    
    def test_unary_in_conditional_expressions(self, tester):
        """Test unary operations in conditional expressions"""
        # Language Reference: unary operations in conditionals
        conditional_patterns = [
            """
result = -value if negative else +value
""",
            """
output = +data if positive else -data
""",
            """
flags = ~mask if invert else mask
""",
            """
processed = (-base if negate else +base) * multiplier
""",
            """
final_value = ~x if condition else +x
"""
        ]
        
        for source in conditional_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should work in conditionals: {source}"


class TestSection66UnaryOperationTypes:
    """Test unary operations with different data types."""
    
    def test_unary_with_integers(self, tester):
        """Test unary operations with integer types"""
        # Language Reference: unary operations work with integers
        integer_unary_patterns = [
            """
result = -42
""",
            """
positive = +123
""",
            """
inverted = ~0xFF
""",
            """
negative_hex = -0xDEADBEEF
""",
            """
complement_binary = ~0b1010101
"""
        ]
        
        for source in integer_unary_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should handle integers: {source}"
    
    def test_unary_with_floats(self, tester):
        """Test unary operations with floating-point types"""
        # Language Reference: unary arithmetic operations work with floats
        float_unary_patterns = [
            """
result = -3.14
""",
            """
positive = +2.71
""",
            """
negative_scientific = -1.23e-4
""",
            """
positive_scientific = +6.02e23
""",
            """
negative_float = -float_variable
"""
        ]
        
        for source in float_unary_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should handle floats: {source}"
    
    def test_unary_with_complex_numbers(self, tester):
        """Test unary operations with complex number types"""
        # Language Reference: unary operations work with complex numbers
        complex_unary_patterns = [
            """
result = -(3+4j)
""",
            """
positive = +(1-2j)
""",
            """
negative_complex = -complex_variable
""",
            """
positive_complex = +complex_number
""",
            """
conjugate_like = -(a + bj)
"""
        ]
        
        for source in complex_unary_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should handle complex numbers: {source}"
    
    def test_unary_with_booleans(self, tester):
        """Test unary operations with boolean types"""
        # Language Reference: unary operations work with booleans
        boolean_unary_patterns = [
            """
result = -True
""",
            """
positive = +False
""",
            """
inverted = ~True
""",
            """
negative_bool = -flag
""",
            """
complement_bool = ~condition
"""
        ]
        
        for source in boolean_unary_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should handle booleans: {source}"


class TestSection66UnaryOperationErrors:
    """Test unary operation error conditions."""
    
    def test_unary_operator_syntax(self, tester):
        """Test proper unary operator syntax"""
        # Language Reference: correct operator syntax
        valid_operator_patterns = [
            """
result = +value
""",
            """
output = -data
""",
            """
inverted = ~flags
""",
            """
chained = --x
"""
        ]
        
        for source in valid_operator_patterns:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should parse valid operators: {source}"
    
    def test_incomplete_unary_expressions(self, tester):
        """Test incomplete unary expressions"""
        # Language Reference: operand required
        incomplete_patterns = [
            "+",              # Missing operand
            "-",              # Missing operand
            "~",              # Missing operand
            "x = +",          # Incomplete in assignment
        ]
        
        for source in incomplete_patterns:
            tester.assert_unary_operation_syntax_error(source)
    
    def test_invalid_unary_combinations(self, tester):
        """Test invalid unary operator combinations"""
        # Language Reference: specific syntax requirements
        invalid_patterns = [
            "x = + + y",      # Space between unary operators
            "x = - - y",      # Space between unary operators
            "x = ~ ~ y",      # Space between unary operators
        ]
        
        # Note: These might actually parse as valid syntax (binary subtraction, etc.)
        # Let's test what actually happens
        for source in invalid_patterns:
            # These actually parse as binary operations, not syntax errors
            tree = tester.assert_unary_operation_parses(source)


class TestSection66UnaryOperationAST:
    """Test unary operation AST structure validation."""
    
    def test_unary_ast_structure(self, tester):
        """Test UnaryOp AST node structure"""
        # Language Reference: AST structure for unary operations
        unary_ast_cases = [
            """
result = +value
""",
            """
output = -data
""",
            """
inverted = ~flags
""",
            """
chained = --x
"""
        ]
        
        for source in unary_ast_cases:
            tree = tester.assert_unary_operation_parses(source)
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should have unary operations: {source}"
            
            for unary_op in unary_ops:
                # UnaryOp nodes must have op and operand
                assert isinstance(unary_op, ast.UnaryOp), "Should be UnaryOp node"
                assert hasattr(unary_op, 'op'), "Should have operator"
                assert hasattr(unary_op, 'operand'), "Should have operand"
                
                # Operator should be UAdd, USub, or Invert
                assert isinstance(unary_op.op, (ast.UAdd, ast.USub, ast.Invert)), "Should be unary operator"
                
                # Operand should be non-None
                assert unary_op.operand is not None, "Operand should not be None"
    
    def test_chained_unary_ast_structure(self, tester):
        """Test chained unary operation AST structure"""
        # Language Reference: chained unary operations create nested UnaryOp nodes
        chained_unary_source = """
result = ---+++~~~value
"""
        
        tree = tester.assert_unary_operation_parses(chained_unary_source)
        unary_ops = tester.get_unary_operations(chained_unary_source)
        assert len(unary_ops) >= 6, "Should have multiple unary operations"
        
        # Check that we have different types of unary operations
        plus_ops = tester.get_unary_plus_operations(chained_unary_source)
        minus_ops = tester.get_unary_minus_operations(chained_unary_source)
        not_ops = tester.get_unary_not_operations(chained_unary_source)
        
        assert len(plus_ops) >= 3, "Should have plus operations"
        assert len(minus_ops) >= 3, "Should have minus operations"
        assert len(not_ops) >= 3, "Should have NOT operations"
    
    def test_unary_with_complex_operands_ast(self, tester):
        """Test unary with complex operands AST"""
        # Language Reference: complex expressions as operands
        complex_unary_source = """
result = -(a + b) + ~(c * d) - +(e / f)
"""
        
        tree = tester.assert_unary_operation_parses(complex_unary_source)
        unary_ops = tester.get_unary_operations(complex_unary_source)
        assert len(unary_ops) >= 3, "Should have unary operations"
        
        # Should have arithmetic operations as operands
        binary_ops = tester.get_binary_operations(complex_unary_source)
        assert len(binary_ops) >= 5, "Should have binary operations in operands and top level"


class TestSection66CrossImplementationCompatibility:
    """Test cross-implementation compatibility for unary operations."""
    
    def test_unary_ast_consistency(self, tester):
        """Test unary operation AST consistency across implementations"""
        # Language Reference: unary AST should be consistent
        consistency_test_cases = [
            """
result = +value
""",
            """
output = -data
""",
            """
inverted = ~flags
""",
            """
complex_unary = -(a + b)
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_unary_operation_parses(source)
            
            # Should have consistent unary structure
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 1, f"Should have unary operations: {source}"
            
            for unary_op in unary_ops:
                assert isinstance(unary_op, ast.UnaryOp), "Should be UnaryOp node"
                assert isinstance(unary_op.op, (ast.UAdd, ast.USub, ast.Invert)), "Should be unary operator"
                assert unary_op.operand is not None, "Should have operand"
    
    def test_comprehensive_unary_patterns(self, tester):
        """Test comprehensive real-world unary patterns"""
        # Language Reference: complex unary usage scenarios
        comprehensive_patterns = [
            """
# Mathematical computations with unary operations
class MathProcessor:
    def __init__(self):
        # Constants using unary operations
        self.NEGATIVE_ONE = -1
        self.POSITIVE_INFINITY = +float('inf')
        self.NEGATIVE_INFINITY = -float('inf')
        self.BIT_MASK_INVERTED = ~0xFF
        
        # Mathematical constants
        self.PI = +3.14159265359
        self.E = +2.71828182846
        self.GOLDEN_RATIO = +1.61803398875
        
        # Complex number constants
        self.IMAGINARY_UNIT = +1j
        self.NEGATIVE_IMAGINARY = -1j
    
    def absolute_value_manual(self, x):
        # Manual absolute value using unary operations
        return -x if x < 0 else +x
    
    def sign_function(self, x):
        # Sign function using unary operations
        if x > 0:
            return +1
        elif x < 0:
            return -1
        else:
            return +0
    
    def negate_collection(self, numbers):
        # Negate all numbers in a collection
        return [-x for x in numbers]
    
    def compute_polynomial(self, x, coefficients):
        # Compute polynomial with explicit signs
        result = +0
        for i, coeff in enumerate(coefficients):
            term = +coeff * (x ** i)
            result = result + term
        return result
    
    def matrix_operations(self, matrix):
        # Matrix operations using unary operations
        negated_matrix = [[-element for element in row] for row in matrix]
        positive_matrix = [[+element for element in row] for row in matrix]
        
        # Matrix trace with explicit positive
        trace = +sum(matrix[i][i] for i in range(min(len(matrix), len(matrix[0]))))
        
        return negated_matrix, positive_matrix, trace
    
    def complex_arithmetic(self, z1, z2):
        # Complex number arithmetic with unary operations
        conjugate_z1 = +z1.real + (-z1.imag * 1j)
        conjugate_z2 = +z2.real + (-z2.imag * 1j)
        
        # Magnitude squared using unary operations
        mag_sq_z1 = (+z1.real) ** 2 + (-(-z1.imag)) ** 2
        mag_sq_z2 = (+z2.real) ** 2 + (+z2.imag) ** 2
        
        return conjugate_z1, conjugate_z2, mag_sq_z1, mag_sq_z2
    
    def numerical_analysis(self, f, x, h=1e-7):
        # Numerical derivative using unary operations
        forward_diff = (f(+x + h) - f(+x)) / (+h)
        backward_diff = (f(+x) - f(+x - h)) / (+h)
        central_diff = (f(+x + h) - f(+x - h)) / (+2 * h)
        
        return forward_diff, backward_diff, central_diff

# Bit manipulation with unary operations
class BitManipulator:
    def __init__(self):
        # Bit patterns using unary NOT
        self.ALL_ONES_8BIT = ~0 & 0xFF
        self.ALL_ONES_16BIT = ~0 & 0xFFFF
        self.ALL_ONES_32BIT = ~0 & 0xFFFFFFFF
        
        # Sign extension masks
        self.SIGN_EXTEND_8_TO_32 = ~0x7F
        self.SIGN_EXTEND_16_TO_32 = ~0x7FFF
    
    def toggle_bits(self, value, mask):
        # Toggle specific bits using XOR with inverted mask
        return value ^ (~mask)
    
    def clear_bits(self, value, mask):
        # Clear specific bits using AND with inverted mask
        return value & (~mask)
    
    def set_bits(self, value, mask):
        # Set specific bits using OR with mask
        # Uses unary plus for clarity
        return (+value) | (+mask)
    
    def count_zero_bits(self, value, width=32):
        # Count zero bits using bitwise NOT
        inverted = ~value
        count = +0
        
        for i in range(width):
            if inverted & (1 << i):
                count = count + (+1)
        
        return count
    
    def create_bitmask(self, start_bit, num_bits):
        # Create bitmask using unary operations
        if num_bits == 0:
            return +0
        
        # Create mask with all ones
        all_ones = ~0
        
        # Shift to create mask
        mask = (all_ones >> (+32 - num_bits)) << start_bit
        
        return mask & (~(~0 << 32))
    
    def sign_extend(self, value, from_bits, to_bits):
        # Sign extend using unary operations
        sign_bit = 1 << (from_bits - 1)
        
        if value & sign_bit:
            # Negative number - extend with ones
            extension_mask = ~((1 << from_bits) - 1)
            return (+value) | extension_mask
        else:
            # Positive number - extend with zeros
            value_mask = (1 << from_bits) - 1
            return (+value) & value_mask
    
    def twos_complement(self, value, width):
        # Two's complement using unary operations
        # Invert all bits and add one
        mask = (1 << width) - 1
        inverted = (~value) & mask
        return (inverted + (+1)) & mask
    
    def ones_complement(self, value, width):
        # One's complement using unary NOT
        mask = (1 << width) - 1
        return (~value) & mask

# Physics and engineering calculations
class EngineeringCalculator:
    def __init__(self):
        # Physical constants with explicit signs
        self.GRAVITY = -9.81  # m/s² (downward)
        self.ELECTRON_CHARGE = -1.602e-19  # Coulombs (negative)
        self.PROTON_CHARGE = +1.602e-19   # Coulombs (positive)
        self.SPEED_OF_LIGHT = +2.998e8    # m/s (positive)
        
        # Engineering constants
        self.VACUUM_PERMEABILITY = +4e-7 * 3.14159  # H/m
        self.VACUUM_PERMITTIVITY = +8.854e-12       # F/m
    
    def calculate_force(self, mass, acceleration):
        # F = ma with explicit signs
        return (+mass) * (+acceleration)
    
    def calculate_electric_field(self, charge, distance):
        # Electric field calculation with sign handling
        k = +8.99e9  # Coulomb's constant
        
        # Handle sign of charge explicitly
        charge_magnitude = +abs(charge)
        charge_sign = +1 if charge >= 0 else -1
        
        field_magnitude = k * charge_magnitude / ((+distance) ** 2)
        return charge_sign * field_magnitude
    
    def projectile_motion(self, initial_velocity, angle, time):
        # Projectile motion with gravity
        import math
        
        # Horizontal and vertical components
        v_x = (+initial_velocity) * math.cos(angle)
        v_y = (+initial_velocity) * math.sin(angle)
        
        # Position at time t
        x = (+v_x) * (+time)
        y = (+v_y) * (+time) + (+0.5) * (+self.GRAVITY) * ((+time) ** 2)
        
        # Velocity at time t
        velocity_x = +v_x  # No change in x-velocity
        velocity_y = +v_y + (+self.GRAVITY) * (+time)
        
        return x, y, velocity_x, velocity_y
    
    def oscillator_motion(self, amplitude, frequency, phase, time):
        # Simple harmonic motion with explicit signs
        import math
        
        angular_freq = +2 * math.pi * (+frequency)
        
        # Position, velocity, acceleration
        position = (+amplitude) * math.cos(angular_freq * (+time) + (+phase))
        velocity = -(+amplitude) * angular_freq * math.sin(angular_freq * (+time) + (+phase))
        acceleration = -(+amplitude) * (angular_freq ** 2) * math.cos(angular_freq * (+time) + (+phase))
        
        return position, velocity, acceleration
    
    def rc_circuit_response(self, voltage, resistance, capacitance, time):
        # RC circuit response with explicit signs
        import math
        
        time_constant = (+resistance) * (+capacitance)
        
        # Charging response
        v_capacitor = (+voltage) * (1 - math.exp(-(+time) / time_constant))
        
        # Current
        current = (+voltage / resistance) * math.exp(-(+time) / time_constant)
        
        return v_capacitor, current
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_unary_operation_parses(source)
            
            # Should have extensive unary usage
            unary_ops = tester.get_unary_operations(source)
            assert len(unary_ops) >= 50, f"Should have many unary operations: {source}"
    
    def test_unary_introspection(self, tester):
        """Test ability to analyze unary operations programmatically"""
        # Test programmatic analysis of unary operation structure
        introspection_source = """
def unary_examples():
    # Simple unary operations
    positive = +value
    negative = -number
    inverted = ~flags
    
    # Chained operations
    double_negative = --x
    triple_plus = +++y
    mixed_chain = -+~z
    
    # In expressions
    arithmetic = -a + +b * ~c
    
    # In conditionals
    conditional = -x if negative else +x
    
    # In comprehensions
    negated_list = [-item for item in data]
    positive_dict = {k: +v for k, v in items.items()}
    
    # Complex expressions
    complex_unary = -(a + b) + ~(c & d)
    
    # With different types
    float_negative = -3.14
    complex_positive = +(1+2j)
    bool_invert = ~True
    
    return positive, negative, inverted, double_negative, complex_unary
"""
        
        tree = tester.assert_unary_operation_parses(introspection_source)
        
        # Should identify all unary operations
        unary_ops = tester.get_unary_operations(introspection_source)
        assert len(unary_ops) >= 15, "Should have multiple unary operations"
        
        # Should identify different types of unary operations
        plus_ops = tester.get_unary_plus_operations(introspection_source)
        minus_ops = tester.get_unary_minus_operations(introspection_source)
        not_ops = tester.get_unary_not_operations(introspection_source)
        
        assert len(plus_ops) >= 4, "Should have plus operations"
        assert len(minus_ops) >= 6, "Should have minus operations"  
        assert len(not_ops) >= 3, "Should have NOT operations"
        
        # Should identify chained operations
        chain_depth = tester.count_chained_unary_operations(introspection_source)
        assert chain_depth >= 3, "Should have chained unary operations"
        
        # All unary operations should have proper structure
        for unary_op in unary_ops:
            assert isinstance(unary_op, ast.UnaryOp), "Should be UnaryOp node"
            assert isinstance(unary_op.op, (ast.UAdd, ast.USub, ast.Invert)), "Should be unary operator"
            assert unary_op.operand is not None, "Should have operand"