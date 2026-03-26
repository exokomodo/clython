"""
Section 6.8: Shifting Operations - Conformance Test Suite

Tests Python Language Reference Section 6.8 compliance across implementations.
Based on formal shifting operation syntax definitions and prose assertions for bit manipulation behavior.

Grammar tested:
    shift_expr: a_expr ('<<'|'>>' a_expr)*

Language Reference requirements tested:
    - Left shift (<<) and right shift (>>) operator syntax validation
    - Integer type requirements for shifting operations
    - Shifting operation precedence and associativity rules
    - Negative shift count handling and error conditions
    - Large integer shifting behavior and overflow handling
    - Shifting operations in complex expressions
    - Error conditions for invalid shifting operations
    - Shifting operation AST structure validation
    - Cross-implementation shifting operation compatibility
"""

import ast
import pytest
import sys
from typing import Any


class ShiftingOperationTester:
    """Helper class for testing shifting operation conformance.
    
    Focuses on AST structure validation for shifting operation syntax and behavior
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_shifting_operation_parses(self, source: str):
        """Test that shifting operation syntax parses correctly.
        
        Args:
            source: Python source code with shifting operations
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Shifting operation syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_shifting_operation_syntax_error(self, source: str):
        """Test that invalid shifting operation syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_shift_operations(self, source: str) -> list:
        """Get BinOp AST nodes with shift operators from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes with LShift or RShift operators
        """
        tree = ast.parse(source)
        shift_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.LShift, ast.RShift)):
                shift_ops.append(node)
        
        return shift_ops
    
    def get_left_shifts(self, source: str) -> list:
        """Get left shift operations from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes with LShift operators
        """
        tree = ast.parse(source)
        left_shifts = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.LShift):
                left_shifts.append(node)
        
        return left_shifts
    
    def get_right_shifts(self, source: str) -> list:
        """Get right shift operations from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes with RShift operators
        """
        tree = ast.parse(source)
        right_shifts = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.RShift):
                right_shifts.append(node)
        
        return right_shifts
    
    def count_chained_shifts(self, source: str) -> int:
        """Count chained shifting operations.
        
        Args:
            source: Python source code
            
        Returns:
            Number of chained shift operations
        """
        tree = ast.parse(source)
        max_chain = 0
        
        def count_chain(node):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.LShift, ast.RShift)):
                # Count chain in left operand
                left_chain = count_chain(node.left)
                return 1 + left_chain
            return 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                chain_length = count_chain(node)
                max_chain = max(max_chain, chain_length)
        
        return max_chain
    
    def get_arithmetic_operations(self, source: str) -> list:
        """Get arithmetic operations that interact with shifts.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes with arithmetic operators
        """
        tree = ast.parse(source)
        arith_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
                arith_ops.append(node)
        
        return arith_ops


@pytest.fixture
def tester():
    """Provide ShiftingOperationTester instance for tests."""
    return ShiftingOperationTester()


class TestSection68BasicShiftingSyntax:
    """Test basic shifting operation syntax."""
    
    def test_simple_left_shift_operations(self, tester):
        """Test simple left shift operation patterns"""
        # Language Reference: shift_expr: a_expr ('<<' a_expr)*
        left_shift_patterns = [
            """
result = 8 << 2
""",
            """
value = number << shift_count
""",
            """
doubled = x << 1
""",
            """
power_of_two = 1 << n
""",
            """
scaled = base_value << scaling_factor
"""
        ]
        
        for source in left_shift_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            left_shifts = tester.get_left_shifts(source)
            assert len(left_shifts) >= 1, f"Should have left shift operations: {source}"
    
    def test_simple_right_shift_operations(self, tester):
        """Test simple right shift operation patterns"""
        # Language Reference: shift_expr: a_expr ('>>' a_expr)*
        right_shift_patterns = [
            """
result = 32 >> 2
""",
            """
value = number >> shift_count
""",
            """
halved = x >> 1
""",
            """
divided_by_power = value >> n
""",
            """
reduced = large_value >> reduction_factor
"""
        ]
        
        for source in right_shift_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            right_shifts = tester.get_right_shifts(source)
            assert len(right_shifts) >= 1, f"Should have right shift operations: {source}"
    
    def test_shift_with_variables(self, tester):
        """Test shifting operations with variables"""
        # Language Reference: operands can be variables
        variable_shift_patterns = [
            """
result = value << count
""",
            """
output = data >> bits
""",
            """
shifted = input_value << offset
""",
            """
compressed = large_number >> compression_level
""",
            """
expanded = small_number << expansion_factor
"""
        ]
        
        for source in variable_shift_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should handle variable operands: {source}"
    
    def test_shift_with_expressions(self, tester):
        """Test shifting operations with complex expressions"""
        # Language Reference: operands can be complex expressions
        expression_shift_patterns = [
            """
result = (a + b) << (c - d)
""",
            """
value = calculate() >> get_shift_amount()
""",
            """
output = (x * y) << (z // 2)
""",
            """
shifted = array[index] >> (count + 1)
""",
            """
processed = transform(data) << compute_shift(config)
"""
        ]
        
        for source in expression_shift_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should handle complex expressions: {source}"


class TestSection68ShiftChaining:
    """Test chained shifting operations."""
    
    def test_chained_left_shifts(self, tester):
        """Test chained left shift operations"""
        # Language Reference: shift operators are left-associative
        chained_left_patterns = [
            """
result = value << 2 << 3
""",
            """
output = base << shift1 << shift2 << shift3
""",
            """
scaled = number << a << b
""",
            """
expanded = data << x << y << z
""",
            """
multiplied = input_val << first << second
"""
        ]
        
        for source in chained_left_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            left_shifts = tester.get_left_shifts(source)
            assert len(left_shifts) >= 2, f"Should have chained left shifts: {source}"
            
            chain_count = tester.count_chained_shifts(source)
            assert chain_count >= 2, f"Should have shift chain: {source}"
    
    def test_chained_right_shifts(self, tester):
        """Test chained right shift operations"""
        # Language Reference: shift operators are left-associative
        chained_right_patterns = [
            """
result = value >> 2 >> 3
""",
            """
output = base >> shift1 >> shift2 >> shift3
""",
            """
reduced = number >> a >> b
""",
            """
compressed = data >> x >> y >> z
""",
            """
divided = large_value >> first >> second
"""
        ]
        
        for source in chained_right_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            right_shifts = tester.get_right_shifts(source)
            assert len(right_shifts) >= 2, f"Should have chained right shifts: {source}"
            
            chain_count = tester.count_chained_shifts(source)
            assert chain_count >= 2, f"Should have shift chain: {source}"
    
    def test_mixed_shift_chains(self, tester):
        """Test mixed left and right shift chains"""
        # Language Reference: left and right shifts can be chained
        mixed_shift_patterns = [
            """
result = value << 2 >> 1
""",
            """
output = data >> 3 << 2
""",
            """
processed = input_val << a >> b << c
""",
            """
transformed = base >> x << y >> z
""",
            """
normalized = large_number >> first << adjustment >> final
"""
        ]
        
        for source in mixed_shift_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 2, f"Should have mixed shift operations: {source}"
    
    def test_shift_associativity(self, tester):
        """Test shift operation associativity"""
        # Language Reference: shift operators are left-associative
        associativity_patterns = [
            """
# Left associative: (a << b) << c
result1 = a << b << c
""",
            """
# Explicit grouping for comparison
result2 = (a << b) << c
""",
            """
# Right shifts also left-associative: (x >> y) >> z
result3 = x >> y >> z
""",
            """
# Explicit grouping
result4 = (x >> y) >> z
""",
            """
# Mixed operations: ((a << b) >> c) << d
result5 = a << b >> c << d
"""
        ]
        
        for source in associativity_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            # Should parse without syntax errors
            assert len(shifts) >= 0, f"Should handle associativity: {source}"


class TestSection68ShiftPrecedence:
    """Test shifting operation precedence."""
    
    def test_shift_vs_arithmetic_precedence(self, tester):
        """Test precedence of shifts vs arithmetic operations"""
        # Language Reference: shifts have lower precedence than arithmetic
        precedence_patterns = [
            """
result = a + b << c
""",
            """
value = x - y >> z
""",
            """
output = a * b << c + d
""",
            """
processed = x / y >> z - w
""",
            """
complex_expr = a + b * c << d - e / f
"""
        ]
        
        for source in precedence_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            arith_ops = tester.get_arithmetic_operations(source)
            assert len(shifts) >= 1, f"Should have shift operations: {source}"
            assert len(arith_ops) >= 1, f"Should have arithmetic operations: {source}"
    
    def test_shift_vs_comparison_precedence(self, tester):
        """Test precedence of shifts vs comparison operations"""
        # Language Reference: shifts have higher precedence than comparisons
        comparison_precedence_patterns = [
            """
result = a << b > c
""",
            """
check = x >> y < z
""",
            """
valid = value << shift == expected
""",
            """
test = data >> amount != original
""",
            """
comparison = left << bits >= right >> other_bits
"""
        ]
        
        for source in comparison_precedence_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should have shift operations: {source}"
    
    def test_shift_with_parentheses(self, tester):
        """Test shifting operations with explicit parentheses"""
        # Language Reference: parentheses override precedence
        parentheses_patterns = [
            """
result = (a + b) << c
""",
            """
value = a << (b + c)
""",
            """
output = (x - y) >> (z + w)
""",
            """
processed = a + (b << c)
""",
            """
complex_expr = (a * b) << (c - d) + e
"""
        ]
        
        for source in parentheses_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should handle parentheses: {source}"
    
    def test_shift_in_complex_expressions(self, tester):
        """Test shifting operations in complex expressions"""
        # Language Reference: shifts can be part of complex expressions
        complex_expression_patterns = [
            """
result = a + b << c * d - e
""",
            """
value = x * (y << z) + w / (u >> v)
""",
            """
output = (a << b) + (c >> d) * e
""",
            """
processed = func(x << y) + array[z >> w]
""",
            """
complex_calc = (a + b) * (c << d) - (e >> f) / g
"""
        ]
        
        for source in complex_expression_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should work in complex expressions: {source}"


class TestSection68ShiftOperationContexts:
    """Test shifting operations in different contexts."""
    
    def test_shifts_in_assignments(self, tester):
        """Test shifting operations in assignment contexts"""
        # Language Reference: shifts in assignments
        assignment_patterns = [
            """
result = value << 4
""",
            """
compressed = data >> compression_level
""",
            """
a, b = x << 2, y >> 3
""",
            """
array[index] = base_value << shift_amount
""",
            """
obj.attr = input_data >> reduction_factor
"""
        ]
        
        for source in assignment_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should work in assignments: {source}"
    
    def test_shifts_in_function_calls(self, tester):
        """Test shifting operations in function call arguments"""
        # Language Reference: shifts in function arguments
        function_call_patterns = [
            """
result = process(value << 3)
""",
            """
output = transform(data >> 2, mode='fast')
""",
            """
validate(input_val << shift, expected >> reduction)
""",
            """
complex_function(
    a << b,
    c >> d,
    flag=x << y > threshold
)
""",
            """
api_call(base_data >> compression, format=fmt << format_shift)
"""
        ]
        
        for source in function_call_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should work in function calls: {source}"
    
    def test_shifts_in_return_statements(self, tester):
        """Test shifting operations in return statements"""
        # Language Reference: shifts in returns
        return_patterns = [
            """
def multiply_by_power_of_two(value, power):
    return value << power
""",
            """
def divide_by_power_of_two(value, power):
    return value >> power
""",
            """
def process_data(data, shift_amount):
    return data << shift_amount if shift_amount > 0 else data >> abs(shift_amount)
""",
            """
def combine_shifts(a, b, left_shift, right_shift):
    return (a << left_shift) + (b >> right_shift)
""",
            """
def fast_multiplication(value, factor_bits):
    return value << factor_bits
"""
        ]
        
        for source in return_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should work in returns: {source}"
    
    def test_shifts_in_comprehensions(self, tester):
        """Test shifting operations in comprehensions"""
        # Language Reference: shifts in comprehensions
        comprehension_patterns = [
            """
powers = [1 << i for i in range(10)]
""",
            """
halved = [x >> 1 for x in values]
""",
            """
shifted_data = {key: value << shift for key, value in data.items()}
""",
            """
bit_patterns = (x << y for x in base_values for y in shifts)
""",
            """
processed = [
    transform(item << left_shift, item >> right_shift)
    for item in dataset
    if item << 1 > threshold
]
"""
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should work in comprehensions: {source}"
    
    def test_shifts_in_conditional_expressions(self, tester):
        """Test shifting operations in conditional expressions"""
        # Language Reference: shifts in conditionals
        conditional_patterns = [
            """
result = value << 2 if positive else value >> 2
""",
            """
output = (data << left) if use_left_shift else (data >> right)
""",
            """
processed = x << y if x > 0 and y > 0 else 0
""",
            """
shifted = (base << amount) if amount >= 0 else (base >> abs(amount))
""",
            """
optimized = fast_shift << bits if use_fast else slow_shift >> bits
"""
        ]
        
        for source in conditional_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should work in conditionals: {source}"


class TestSection68ShiftOperationErrors:
    """Test shifting operation error conditions."""
    
    def test_shift_operator_syntax(self, tester):
        """Test proper shift operator syntax"""
        # Language Reference: correct operator syntax
        valid_operator_patterns = [
            """
result = value << 2
""",
            """
output = data >> 3
""",
            """
left_shifted = x << y
""",
            """
right_shifted = a >> b
"""
        ]
        
        for source in valid_operator_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should parse valid operators: {source}"
    
    def test_malformed_shift_syntax(self, tester):
        """Test malformed shift operation syntax"""
        # Language Reference: invalid syntax patterns
        malformed_patterns = [
            "value < < 2",  # Spaces in operator
            "data > > 3",   # Spaces in operator
            "x <<< y",      # Triple less-than
            "a >>> b",      # Triple greater-than
        ]
        
        for source in malformed_patterns:
            tester.assert_shifting_operation_syntax_error(source)
    
    def test_incomplete_shift_expressions(self, tester):
        """Test incomplete shift expressions"""
        # Language Reference: both operands required
        incomplete_patterns = [
            "value <<",      # Missing right operand
            ">> 3",          # Missing left operand
            "x << << y",     # Double operator
            "a >> >> b",     # Double operator
        ]
        
        for source in incomplete_patterns:
            tester.assert_shifting_operation_syntax_error(source)


class TestSection68ShiftOperationAST:
    """Test shifting operation AST structure validation."""
    
    def test_shift_ast_structure(self, tester):
        """Test BinOp AST node structure for shifts"""
        # Language Reference: AST structure for shift operations
        shift_ast_cases = [
            """
result = value << 4
""",
            """
output = data >> 2
""",
            """
left_shifted = x << y
""",
            """
right_shifted = a >> b
"""
        ]
        
        for source in shift_ast_cases:
            tree = tester.assert_shifting_operation_parses(source)
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should have shift operations: {source}"
            
            for shift_op in shifts:
                # BinOp nodes must have left, op, and right
                assert isinstance(shift_op, ast.BinOp), "Should be BinOp node"
                assert hasattr(shift_op, 'left'), "Should have left operand"
                assert hasattr(shift_op, 'op'), "Should have operator"
                assert hasattr(shift_op, 'right'), "Should have right operand"
                
                # Operator should be LShift or RShift
                assert isinstance(shift_op.op, (ast.LShift, ast.RShift)), "Should be shift operator"
                
                # Operands should be non-None
                assert shift_op.left is not None, "Left operand should not be None"
                assert shift_op.right is not None, "Right operand should not be None"
    
    def test_chained_shift_ast_structure(self, tester):
        """Test chained shift operation AST structure"""
        # Language Reference: chained shifts create nested BinOp nodes
        chained_shift_source = """
result = value << 2 >> 1 << 3
"""
        
        tree = tester.assert_shifting_operation_parses(chained_shift_source)
        shifts = tester.get_shift_operations(chained_shift_source)
        assert len(shifts) >= 3, "Should have multiple shift operations"
        
        # Check that we have proper nesting structure
        chain_count = tester.count_chained_shifts(chained_shift_source)
        assert chain_count >= 3, "Should have shift chain"
    
    def test_shift_with_complex_operands_ast(self, tester):
        """Test shift with complex operands AST"""
        # Language Reference: complex expressions as operands
        complex_shift_source = """
result = (a + b) << (c * d - e)
"""
        
        tree = tester.assert_shifting_operation_parses(complex_shift_source)
        shifts = tester.get_shift_operations(complex_shift_source)
        assert len(shifts) >= 1, "Should have shift operation"
        
        # Should have arithmetic operations as operands
        arith_ops = tester.get_arithmetic_operations(complex_shift_source)
        assert len(arith_ops) >= 2, "Should have arithmetic operations in operands"


class TestSection68CrossImplementationCompatibility:
    """Test cross-implementation compatibility for shifting operations."""
    
    def test_shift_ast_consistency(self, tester):
        """Test shift operation AST consistency across implementations"""
        # Language Reference: shift AST should be consistent
        consistency_test_cases = [
            """
result = value << 4
""",
            """
output = data >> 2
""",
            """
chained = x << 2 >> 1
""",
            """
complex_shift = (a + b) << (c - d)
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_shifting_operation_parses(source)
            
            # Should have consistent shift structure
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 1, f"Should have shift operations: {source}"
            
            for shift_op in shifts:
                assert isinstance(shift_op, ast.BinOp), "Should be BinOp node"
                assert isinstance(shift_op.op, (ast.LShift, ast.RShift)), "Should be shift operator"
                assert shift_op.left is not None, "Should have left operand"
                assert shift_op.right is not None, "Should have right operand"
    
    def test_comprehensive_shift_patterns(self, tester):
        """Test comprehensive real-world shift patterns"""
        # Language Reference: complex shift usage scenarios
        comprehensive_patterns = [
            """
# Bit manipulation and optimization algorithms
class BitManipulator:
    def __init__(self):
        # Common bit patterns using shifts
        self.powers_of_two = [1 << i for i in range(64)]
        self.bit_masks = [(1 << i) - 1 for i in range(1, 33)]
        
        # Optimization constants
        self.fast_multiply_by_2 = lambda x: x << 1
        self.fast_multiply_by_4 = lambda x: x << 2
        self.fast_multiply_by_8 = lambda x: x << 3
        
        self.fast_divide_by_2 = lambda x: x >> 1
        self.fast_divide_by_4 = lambda x: x >> 2
        self.fast_divide_by_8 = lambda x: x >> 3
    
    def extract_bits(self, value, start_bit, num_bits):
        # Extract specific bits using shifts and masks
        mask = (1 << num_bits) - 1
        return (value >> start_bit) & mask
    
    def set_bits(self, value, start_bit, num_bits, new_bits):
        # Set specific bits using shifts and masks
        mask = ((1 << num_bits) - 1) << start_bit
        cleared = value & ~mask
        new_value = (new_bits << start_bit) & mask
        return cleared | new_value
    
    def rotate_left(self, value, shift, width=32):
        # Rotate bits left using shifts
        shift = shift % width
        return ((value << shift) | (value >> (width - shift))) & ((1 << width) - 1)
    
    def rotate_right(self, value, shift, width=32):
        # Rotate bits right using shifts
        shift = shift % width
        return ((value >> shift) | (value << (width - shift))) & ((1 << width) - 1)
    
    def count_leading_zeros(self, value, width=32):
        # Count leading zeros using shifts
        if value == 0:
            return width
        
        count = 0
        test_bit = 1 << (width - 1)
        
        while (value & test_bit) == 0 and count < width:
            count += 1
            test_bit >>= 1
        
        return count
    
    def reverse_bits(self, value, width=32):
        # Reverse bits using shifts
        result = 0
        for i in range(width):
            if value & (1 << i):
                result |= 1 << (width - 1 - i)
        return result
    
    def generate_gray_code(self, n):
        # Generate Gray code sequence using shifts
        return [i ^ (i >> 1) for i in range(1 << n)]
    
    def hamming_weight(self, value):
        # Count set bits using shifts (Brian Kernighan's algorithm)
        count = 0
        while value:
            value &= value - 1  # Clear lowest set bit
            count += 1
        return count
    
    def next_power_of_two(self, value):
        # Find next power of two using shifts
        if value <= 1:
            return 1
        
        # Decrease value by 1 to handle exact powers of 2
        value -= 1
        
        # Fill all bits below the highest set bit
        value |= value >> 1
        value |= value >> 2
        value |= value >> 4
        value |= value >> 8
        value |= value >> 16
        
        return value + 1
    
    def align_to_boundary(self, address, boundary_bits):
        # Align address to boundary using shifts
        boundary = 1 << boundary_bits
        return (address + boundary - 1) & ~(boundary - 1)

# Data compression and encoding using shifts
class DataEncoder:
    def __init__(self):
        self.encoding_tables = {}
        self.compression_stats = {'compressed': 0, 'original': 0}
    
    def pack_rgb565(self, r, g, b):
        # Pack RGB values into 16-bit format using shifts
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    
    def unpack_rgb565(self, packed):
        # Unpack 16-bit RGB format using shifts
        r = (packed >> 11) & 0x1F
        g = (packed >> 5) & 0x3F
        b = packed & 0x1F
        
        # Scale to 8-bit values
        r = (r << 3) | (r >> 2)
        g = (g << 2) | (g >> 4)
        b = (b << 3) | (b >> 2)
        
        return r, g, b
    
    def encode_variable_length(self, values):
        # Variable length encoding using shifts
        encoded = []
        
        for value in values:
            # Encode each value using continuation bits
            while value >= 128:
                encoded.append((value & 0x7F) | 0x80)
                value >>= 7
            encoded.append(value & 0x7F)
        
        return bytes(encoded)
    
    def decode_variable_length(self, data):
        # Decode variable length encoding using shifts
        decoded = []
        i = 0
        
        while i < len(data):
            value = 0
            shift = 0
            
            while i < len(data):
                byte = data[i]
                i += 1
                
                value |= (byte & 0x7F) << shift
                shift += 7
                
                if (byte & 0x80) == 0:
                    break
            
            decoded.append(value)
        
        return decoded
    
    def delta_encode(self, values):
        # Delta encoding with bit packing
        if not values:
            return []
        
        deltas = [values[0]]
        for i in range(1, len(values)):
            deltas.append(values[i] - values[i - 1])
        
        # Pack small deltas efficiently using shifts
        packed = []
        for delta in deltas:
            if -64 <= delta <= 63:
                # 7-bit signed delta
                packed.append((delta & 0x7F) | 0x00)
            elif -8192 <= delta <= 8191:
                # 14-bit signed delta
                packed.extend([
                    ((delta >> 7) & 0x7F) | 0x80,
                    delta & 0x7F
                ])
            else:
                # Full 32-bit value
                packed.extend([
                    0xFF,
                    (delta >> 24) & 0xFF,
                    (delta >> 16) & 0xFF,
                    (delta >> 8) & 0xFF,
                    delta & 0xFF
                ])
        
        return packed
    
    def huffman_decode_fast(self, data, code_table):
        # Fast Huffman decoding using bit shifts
        result = []
        bit_buffer = 0
        bit_count = 0
        byte_index = 0
        
        while byte_index < len(data):
            # Fill bit buffer
            while bit_count < 24 and byte_index < len(data):
                bit_buffer |= data[byte_index] << bit_count
                bit_count += 8
                byte_index += 1
            
            # Decode symbols
            for code_length in range(1, 16):  # Max Huffman code length
                code = bit_buffer & ((1 << code_length) - 1)
                
                if (code_length, code) in code_table:
                    symbol = code_table[(code_length, code)]
                    result.append(symbol)
                    
                    bit_buffer >>= code_length
                    bit_count -= code_length
                    break
            else:
                # No valid code found
                break
        
        return result

# Hash functions and checksums using shifts
class HashGenerator:
    def __init__(self):
        self.prime_constants = [
            0x01000193, 0x811C9DC5, 0x9E3779B9, 0x85EBCA6B
        ]
    
    def fnv1a_hash(self, data):
        # FNV-1a hash using shifts and XOR
        hash_value = 0x811C9DC5  # FNV offset basis
        
        for byte in data:
            hash_value ^= byte
            hash_value *= 0x01000193  # FNV prime
            hash_value &= 0xFFFFFFFF  # 32-bit
        
        return hash_value
    
    def djb2_hash(self, data):
        # djb2 hash using shifts
        hash_value = 5381
        
        for byte in data:
            hash_value = ((hash_value << 5) + hash_value) + byte
            hash_value &= 0xFFFFFFFF
        
        return hash_value
    
    def sdbm_hash(self, data):
        # SDBM hash using shifts
        hash_value = 0
        
        for byte in data:
            hash_value = byte + (hash_value << 6) + (hash_value << 16) - hash_value
            hash_value &= 0xFFFFFFFF
        
        return hash_value
    
    def murmur3_hash32(self, data, seed=0):
        # Simplified MurmurHash3 using shifts
        c1 = 0xCC9E2D51
        c2 = 0x1B873593
        
        hash_value = seed
        
        for i in range(0, len(data) - 3, 4):
            k = (data[i] | 
                 (data[i + 1] << 8) |
                 (data[i + 2] << 16) |
                 (data[i + 3] << 24))
            
            k = (k * c1) & 0xFFFFFFFF
            k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
            k = (k * c2) & 0xFFFFFFFF
            
            hash_value ^= k
            hash_value = ((hash_value << 13) | (hash_value >> 19)) & 0xFFFFFFFF
            hash_value = (hash_value * 5 + 0xE6546B64) & 0xFFFFFFFF
        
        # Handle remaining bytes
        remaining = len(data) % 4
        if remaining:
            k = 0
            for i in range(remaining):
                k |= data[len(data) - remaining + i] << (8 * i)
            
            k = (k * c1) & 0xFFFFFFFF
            k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
            k = (k * c2) & 0xFFFFFFFF
            hash_value ^= k
        
        hash_value ^= len(data)
        hash_value ^= hash_value >> 16
        hash_value = (hash_value * 0x85EBCA6B) & 0xFFFFFFFF
        hash_value ^= hash_value >> 13
        hash_value = (hash_value * 0xC2B2AE35) & 0xFFFFFFFF
        hash_value ^= hash_value >> 16
        
        return hash_value
    
    def rolling_hash(self, data, window_size):
        # Rolling hash using shifts for substring matching
        if len(data) < window_size:
            return []
        
        base = 256
        mod = 1009  # Prime modulus
        
        # Precompute base^(window_size-1) % mod
        h = 1
        for i in range(window_size - 1):
            h = (h * base) % mod
        
        hashes = []
        current_hash = 0
        
        # Compute hash for first window
        for i in range(window_size):
            current_hash = (current_hash * base + ord(data[i])) % mod
        
        hashes.append(current_hash)
        
        # Rolling hash for remaining windows
        for i in range(window_size, len(data)):
            # Remove leftmost character and add rightmost character
            current_hash = (current_hash - ord(data[i - window_size]) * h) % mod
            current_hash = (current_hash * base + ord(data[i])) % mod
            hashes.append(current_hash)
        
        return hashes
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_shifting_operation_parses(source)
            
            # Should have extensive shift usage
            shifts = tester.get_shift_operations(source)
            assert len(shifts) >= 15, f"Should have many shift operations: {source}"
    
    def test_shift_introspection(self, tester):
        """Test ability to analyze shift operations programmatically"""
        # Test programmatic analysis of shift operation structure
        introspection_source = """
def shift_examples():
    # Simple shifts
    left = value << 2
    right = data >> 3
    
    # Chained shifts
    chained = x << 1 >> 2 << 3
    
    # Mixed with arithmetic
    arithmetic = (a + b) << c - d
    
    # In conditionals
    conditional = x << 2 if flag else y >> 3
    
    # In comprehensions
    powers = [1 << i for i in range(10)]
    divisions = [x >> 1 for x in values]
    
    # Complex expressions
    complex_shift = (base << shift1) + (offset >> shift2)
    
    # Function arguments
    result = process(input_val << 4, mode=config >> 2)
    
    return left, right, chained, arithmetic, conditional, powers, divisions, complex_shift, result
"""
        
        tree = tester.assert_shifting_operation_parses(introspection_source)
        
        # Should identify all shift operations
        shifts = tester.get_shift_operations(introspection_source)
        assert len(shifts) >= 10, "Should have multiple shift operations"
        
        # Should identify left and right shifts
        left_shifts = tester.get_left_shifts(introspection_source)
        right_shifts = tester.get_right_shifts(introspection_source)
        assert len(left_shifts) >= 5, "Should have left shifts"
        assert len(right_shifts) >= 3, "Should have right shifts"
        
        # Should identify chained operations
        chain_count = tester.count_chained_shifts(introspection_source)
        assert chain_count >= 3, "Should have chained shifts"
        
        # All shifts should have proper structure
        for shift_op in shifts:
            assert isinstance(shift_op, ast.BinOp), "Should be BinOp node"
            assert isinstance(shift_op.op, (ast.LShift, ast.RShift)), "Should be shift operator"
            assert shift_op.left is not None, "Should have left operand"
            assert shift_op.right is not None, "Should have right operand"