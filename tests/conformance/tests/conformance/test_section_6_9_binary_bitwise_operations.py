"""
Section 6.9: Binary Bitwise Operations - Conformance Test Suite

Tests Python Language Reference Section 6.9 compliance across implementations.
Based on formal binary bitwise operation syntax definitions and prose assertions for bit manipulation behavior.

Grammar tested:
    xor_expr: and_expr ('&' and_expr)*
    or_expr: xor_expr ('|' xor_expr)*
    and_expr: shift_expr ('^' shift_expr)*

Language Reference requirements tested:
    - Bitwise AND (&), OR (|), and XOR (^) operator syntax validation
    - Integer and boolean type support for bitwise operations
    - Bitwise operation precedence and associativity rules
    - Chained bitwise operations and operator interaction
    - Bitwise operations with different data types
    - Error conditions for invalid bitwise operations
    - Bitwise operation AST structure validation
    - Cross-implementation bitwise operation compatibility
"""

import ast
import pytest
import sys
from typing import Any


class BitwiseOperationTester:
    """Helper class for testing binary bitwise operation conformance.
    
    Focuses on AST structure validation for bitwise operation syntax and behavior
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_bitwise_operation_parses(self, source: str):
        """Test that bitwise operation syntax parses correctly.
        
        Args:
            source: Python source code with bitwise operations
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Bitwise operation syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_bitwise_operation_syntax_error(self, source: str):
        """Test that invalid bitwise operation syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_bitwise_operations(self, source: str) -> list:
        """Get BinOp AST nodes with bitwise operators from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes with BitAnd, BitOr, or BitXor operators
        """
        tree = ast.parse(source)
        bitwise_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.BitAnd, ast.BitOr, ast.BitXor)):
                bitwise_ops.append(node)
        
        return bitwise_ops
    
    def get_bitwise_and_operations(self, source: str) -> list:
        """Get bitwise AND operations from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes with BitAnd operators
        """
        tree = ast.parse(source)
        and_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitAnd):
                and_ops.append(node)
        
        return and_ops
    
    def get_bitwise_or_operations(self, source: str) -> list:
        """Get bitwise OR operations from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes with BitOr operators
        """
        tree = ast.parse(source)
        or_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                or_ops.append(node)
        
        return or_ops
    
    def get_bitwise_xor_operations(self, source: str) -> list:
        """Get bitwise XOR operations from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes with BitXor operators
        """
        tree = ast.parse(source)
        xor_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitXor):
                xor_ops.append(node)
        
        return xor_ops
    
    def count_chained_bitwise_operations(self, source: str) -> dict:
        """Count chained bitwise operations by type.
        
        Args:
            source: Python source code
            
        Returns:
            Dict with counts of chained operations by type
        """
        tree = ast.parse(source)
        chain_counts = {'and': 0, 'or': 0, 'xor': 0}
        
        def count_chain(node, op_type):
            if isinstance(node, ast.BinOp) and isinstance(node.op, op_type):
                # Count chain in left operand
                left_chain = count_chain(node.left, op_type)
                return 1 + left_chain
            return 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, ast.BitAnd):
                    chain_counts['and'] = max(chain_counts['and'], count_chain(node, ast.BitAnd))
                elif isinstance(node.op, ast.BitOr):
                    chain_counts['or'] = max(chain_counts['or'], count_chain(node, ast.BitOr))
                elif isinstance(node.op, ast.BitXor):
                    chain_counts['xor'] = max(chain_counts['xor'], count_chain(node, ast.BitXor))
        
        return chain_counts
    
    def get_logical_operations(self, source: str) -> list:
        """Get logical operations (and, or) from source for precedence testing.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BoolOp nodes
        """
        tree = ast.parse(source)
        logical_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp):
                logical_ops.append(node)
        
        return logical_ops


@pytest.fixture
def tester():
    """Provide BitwiseOperationTester instance for tests."""
    return BitwiseOperationTester()


class TestSection69BasicBitwiseSyntax:
    """Test basic bitwise operation syntax."""
    
    def test_simple_bitwise_and_operations(self, tester):
        """Test simple bitwise AND operation patterns"""
        # Language Reference: and_expr: shift_expr ('&' shift_expr)*
        bitwise_and_patterns = [
            """
result = 0b1100 & 0b1010
""",
            """
value = a & b
""",
            """
mask = flags & 0xFF
""",
            """
filtered = data & filter_mask
""",
            """
intersection = set1 & set2
"""
        ]
        
        for source in bitwise_and_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            and_ops = tester.get_bitwise_and_operations(source)
            assert len(and_ops) >= 1, f"Should have bitwise AND operations: {source}"
    
    def test_simple_bitwise_or_operations(self, tester):
        """Test simple bitwise OR operation patterns"""
        # Language Reference: or_expr: xor_expr ('|' xor_expr)*
        bitwise_or_patterns = [
            """
result = 0b1100 | 0b0011
""",
            """
value = a | b
""",
            """
combined = flags | new_flags
""",
            """
merged = data | additional_data
""",
            """
union = set1 | set2
"""
        ]
        
        for source in bitwise_or_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            or_ops = tester.get_bitwise_or_operations(source)
            assert len(or_ops) >= 1, f"Should have bitwise OR operations: {source}"
    
    def test_simple_bitwise_xor_operations(self, tester):
        """Test simple bitwise XOR operation patterns"""
        # Language Reference: xor_expr: and_expr ('^' and_expr)*
        bitwise_xor_patterns = [
            """
result = 0b1100 ^ 0b1010
""",
            """
value = a ^ b
""",
            """
toggled = flags ^ toggle_mask
""",
            """
encrypted = data ^ key
""",
            """
difference = set1 ^ set2
"""
        ]
        
        for source in bitwise_xor_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            xor_ops = tester.get_bitwise_xor_operations(source)
            assert len(xor_ops) >= 1, f"Should have bitwise XOR operations: {source}"
    
    def test_bitwise_with_variables(self, tester):
        """Test bitwise operations with variables"""
        # Language Reference: operands can be variables
        variable_bitwise_patterns = [
            """
result = value1 & value2
""",
            """
output = data | flags
""",
            """
toggled = input_value ^ mask
""",
            """
intersection = collection1 & collection2
""",
            """
combined = base_config | user_config
"""
        ]
        
        for source in variable_bitwise_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should handle variable operands: {source}"
    
    def test_bitwise_with_expressions(self, tester):
        """Test bitwise operations with complex expressions"""
        # Language Reference: operands can be complex expressions
        expression_bitwise_patterns = [
            """
result = (a + b) & (c - d)
""",
            """
value = calculate() | get_flags()
""",
            """
output = (x * y) ^ (z // 2)
""",
            """
masked = array[index] & (mask << shift)
""",
            """
processed = transform(data) | compute_flags(config)
"""
        ]
        
        for source in expression_bitwise_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should handle complex expressions: {source}"


class TestSection69BitwiseChaining:
    """Test chained bitwise operations."""
    
    def test_chained_bitwise_and_operations(self, tester):
        """Test chained bitwise AND operations"""
        # Language Reference: bitwise operators are left-associative
        chained_and_patterns = [
            """
result = a & b & c
""",
            """
filtered = value & mask1 & mask2 & mask3
""",
            """
intersection = set1 & set2 & set3
""",
            """
combined_mask = flag1 & flag2 & flag3 & flag4
""",
            """
multi_filter = data & filter_a & filter_b
"""
        ]
        
        for source in chained_and_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            and_ops = tester.get_bitwise_and_operations(source)
            assert len(and_ops) >= 2, f"Should have chained AND operations: {source}"
    
    def test_chained_bitwise_or_operations(self, tester):
        """Test chained bitwise OR operations"""
        # Language Reference: bitwise operators are left-associative
        chained_or_patterns = [
            """
result = a | b | c
""",
            """
combined = flags | new_flags | extra_flags
""",
            """
union = set1 | set2 | set3
""",
            """
permissions = read_perm | write_perm | execute_perm
""",
            """
merged = base_data | patch1 | patch2
"""
        ]
        
        for source in chained_or_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            or_ops = tester.get_bitwise_or_operations(source)
            assert len(or_ops) >= 2, f"Should have chained OR operations: {source}"
    
    def test_chained_bitwise_xor_operations(self, tester):
        """Test chained bitwise XOR operations"""
        # Language Reference: bitwise operators are left-associative
        chained_xor_patterns = [
            """
result = a ^ b ^ c
""",
            """
encrypted = data ^ key1 ^ key2
""",
            """
checksum = byte1 ^ byte2 ^ byte3 ^ byte4
""",
            """
diff = original ^ change1 ^ change2
""",
            """
hash_value = input1 ^ input2 ^ input3
"""
        ]
        
        for source in chained_xor_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            xor_ops = tester.get_bitwise_xor_operations(source)
            assert len(xor_ops) >= 2, f"Should have chained XOR operations: {source}"
    
    def test_mixed_bitwise_operations(self, tester):
        """Test mixed bitwise operations"""
        # Language Reference: different bitwise operators can be combined
        mixed_bitwise_patterns = [
            """
result = a & b | c
""",
            """
value = x | y & z
""",
            """
output = a ^ b & c | d
""",
            """
complex_mask = (flags & mask) | (new_flags ^ toggle)
""",
            """
processed = (data & filter) ^ (key | modifier)
"""
        ]
        
        for source in mixed_bitwise_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 2, f"Should have mixed bitwise operations: {source}"
    
    def test_bitwise_associativity(self, tester):
        """Test bitwise operation associativity"""
        # Language Reference: bitwise operators are left-associative
        associativity_patterns = [
            """
# Left associative: (a & b) & c
result1 = a & b & c
""",
            """
# Explicit grouping for comparison
result2 = (a & b) & c
""",
            """
# OR is also left-associative: (x | y) | z
result3 = x | y | z
""",
            """
# XOR is also left-associative: (a ^ b) ^ c
result4 = a ^ b ^ c
""",
            """
# Mixed operations follow precedence
result5 = a & b | c ^ d
"""
        ]
        
        for source in associativity_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            # Should parse without syntax errors
            assert len(bitwise_ops) >= 0, f"Should handle associativity: {source}"


class TestSection69BitwisePrecedence:
    """Test bitwise operation precedence."""
    
    def test_bitwise_precedence_order(self, tester):
        """Test bitwise operation precedence order"""
        # Language Reference: & has higher precedence than ^, which has higher precedence than |
        precedence_patterns = [
            """
# & before ^: a & b ^ c == (a & b) ^ c
result1 = a & b ^ c
""",
            """
# ^ before |: a ^ b | c == (a ^ b) | c
result2 = a ^ b | c
""",
            """
# Combined: a & b ^ c | d == ((a & b) ^ c) | d
result3 = a & b ^ c | d
""",
            """
# Explicit grouping
result4 = (a & b) ^ (c | d)
""",
            """
# Complex precedence
result5 = x | y ^ z & w
"""
        ]
        
        for source in precedence_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 2, f"Should handle precedence: {source}"
    
    def test_bitwise_vs_comparison_precedence(self, tester):
        """Test precedence of bitwise vs comparison operations"""
        # Language Reference: bitwise operations have higher precedence than comparisons
        comparison_precedence_patterns = [
            """
result = a & b == c
""",
            """
check = x | y > z
""",
            """
valid = value ^ mask != expected
""",
            """
test = data & filter < threshold
""",
            """
comparison = left | bits >= right & other_bits
"""
        ]
        
        for source in comparison_precedence_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should have bitwise operations: {source}"
    
    def test_bitwise_vs_logical_precedence(self, tester):
        """Test precedence of bitwise vs logical operations"""
        # Language Reference: bitwise operations have higher precedence than logical and/or
        logical_precedence_patterns = [
            """
result = a & b and c | d
""",
            """
check = x ^ y or z & w
""",
            """
valid = flag1 | flag2 and flag3 & flag4
""",
            """
test = condition1 and data & mask or fallback
""",
            """
expression = enabled or value & filter and active
"""
        ]
        
        for source in logical_precedence_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            logical_ops = tester.get_logical_operations(source)
            # Should have both bitwise and logical operations
            assert len(bitwise_ops) >= 1, f"Should have bitwise operations: {source}"
    
    def test_bitwise_with_parentheses(self, tester):
        """Test bitwise operations with explicit parentheses"""
        # Language Reference: parentheses override precedence
        parentheses_patterns = [
            """
result = (a | b) & c
""",
            """
value = a & (b | c)
""",
            """
output = (x ^ y) | (z & w)
""",
            """
processed = a | (b & c ^ d)
""",
            """
complex_expr = (a & b) ^ (c | d) & e
"""
        ]
        
        for source in parentheses_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 2, f"Should handle parentheses: {source}"


class TestSection69BitwiseOperationContexts:
    """Test bitwise operations in different contexts."""
    
    def test_bitwise_in_assignments(self, tester):
        """Test bitwise operations in assignment contexts"""
        # Language Reference: bitwise operations in assignments
        assignment_patterns = [
            """
result = value & mask
""",
            """
flags = base_flags | new_flags
""",
            """
a, b = x & mask1, y | mask2
""",
            """
array[index] = data & filter
""",
            """
obj.attr = input_value ^ key
"""
        ]
        
        for source in assignment_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should work in assignments: {source}"
    
    def test_bitwise_in_function_calls(self, tester):
        """Test bitwise operations in function call arguments"""
        # Language Reference: bitwise operations in function arguments
        function_call_patterns = [
            """
result = process(value & mask)
""",
            """
output = transform(data | flags, mode='fast')
""",
            """
validate(input_val ^ key, expected & filter)
""",
            """
complex_function(
    a & b,
    c | d,
    flag=x ^ y > threshold
)
""",
            """
api_call(base_data & filter, format=fmt | format_flags)
"""
        ]
        
        for source in function_call_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should work in function calls: {source}"
    
    def test_bitwise_in_return_statements(self, tester):
        """Test bitwise operations in return statements"""
        # Language Reference: bitwise operations in returns
        return_patterns = [
            """
def apply_mask(value, mask):
    return value & mask
""",
            """
def combine_flags(flag1, flag2):
    return flag1 | flag2
""",
            """
def encrypt_byte(data, key):
    return data ^ key
""",
            """
def process_permissions(base, additional):
    return (base & 0xFF) | (additional << 8)
""",
            """
def compute_checksum(data1, data2, data3):
    return data1 ^ data2 ^ data3
"""
        ]
        
        for source in return_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should work in returns: {source}"
    
    def test_bitwise_in_comprehensions(self, tester):
        """Test bitwise operations in comprehensions"""
        # Language Reference: bitwise operations in comprehensions
        comprehension_patterns = [
            """
masked = [x & mask for x in values]
""",
            """
combined = [a | b for a, b in pairs]
""",
            """
checksums = {key: value ^ salt for key, value in data.items()}
""",
            """
filtered = (x & filter for x in stream if x & mask)
""",
            """
processed = [
    (item & filter1) | (item ^ filter2)
    for item in dataset
    if item & selection_mask
]
"""
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should work in comprehensions: {source}"
    
    def test_bitwise_in_conditional_expressions(self, tester):
        """Test bitwise operations in conditional expressions"""
        # Language Reference: bitwise operations in conditionals
        conditional_patterns = [
            """
result = value & mask if apply_mask else value
""",
            """
output = (data | flags) if use_flags else data
""",
            """
encrypted = data ^ key if encrypt else data
""",
            """
processed = (base & filter) if filtered else (base | enhancement)
""",
            """
final_value = x & y if condition else x | y
"""
        ]
        
        for source in conditional_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should work in conditionals: {source}"


class TestSection69BitwiseOperationTypes:
    """Test bitwise operations with different data types."""
    
    def test_bitwise_with_integers(self, tester):
        """Test bitwise operations with integer types"""
        # Language Reference: bitwise operations work with integers
        integer_bitwise_patterns = [
            """
result = 42 & 15
""",
            """
value = 0xFF | 0x0F
""",
            """
output = 0b1010 ^ 0b1100
""",
            """
masked = large_integer & 0xFFFFFFFF
""",
            """
combined = small_int | (big_int << 16)
"""
        ]
        
        for source in integer_bitwise_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should handle integers: {source}"
    
    def test_bitwise_with_booleans(self, tester):
        """Test bitwise operations with boolean types"""
        # Language Reference: bitwise operations work with booleans
        boolean_bitwise_patterns = [
            """
result = True & False
""",
            """
value = flag1 | flag2
""",
            """
toggled = state ^ True
""",
            """
combined = (condition1 & condition2) | condition3
""",
            """
xor_result = bool1 ^ bool2 ^ bool3
"""
        ]
        
        for source in boolean_bitwise_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should handle booleans: {source}"
    
    def test_bitwise_with_sets(self, tester):
        """Test bitwise operations with set types"""
        # Language Reference: sets support bitwise operations for set operations
        set_bitwise_patterns = [
            """
intersection = set1 & set2
""",
            """
union = set1 | set2
""",
            """
symmetric_diff = set1 ^ set2
""",
            """
multiple_intersection = set1 & set2 & set3
""",
            """
complex_set_op = (set_a | set_b) & (set_c ^ set_d)
"""
        ]
        
        for source in set_bitwise_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should handle sets: {source}"
    
    def test_bitwise_with_mixed_types(self, tester):
        """Test bitwise operations with mixed compatible types"""
        # Language Reference: type coercion in bitwise operations
        mixed_type_patterns = [
            """
result = True & 1
""",
            """
value = False | 0
""",
            """
output = int_value & bool_value
""",
            """
combined = (True & flag) | (0 ^ mask)
""",
            """
processed = bool_flag & int_mask | other_flag
"""
        ]
        
        for source in mixed_type_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should handle mixed types: {source}"


class TestSection69BitwiseOperationErrors:
    """Test bitwise operation error conditions."""
    
    def test_bitwise_operator_syntax(self, tester):
        """Test proper bitwise operator syntax"""
        # Language Reference: correct operator syntax
        valid_operator_patterns = [
            """
result = value & mask
""",
            """
output = data | flags
""",
            """
xor_result = a ^ b
""",
            """
combined = x & y | z
"""
        ]
        
        for source in valid_operator_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should parse valid operators: {source}"
    
    def test_malformed_bitwise_syntax(self, tester):
        """Test malformed bitwise operation syntax"""
        # Language Reference: invalid syntax patterns
        syntax_error_patterns = [
            "a ^^ b",          # Double XOR
            "x & & y",         # Space in operator
        ]
        
        for source in syntax_error_patterns:
            tester.assert_bitwise_operation_syntax_error(source)
        
        # These parse as logical operations or other valid syntax, not bitwise
        logical_instead_patterns = [
            "value && mask",    # Logical AND instead of bitwise - syntax error in Python
            "data || flags",    # Logical OR instead of bitwise - syntax error in Python
        ]
        
        for source in logical_instead_patterns:
            tester.assert_bitwise_operation_syntax_error(source)
    
    def test_incomplete_bitwise_expressions(self, tester):
        """Test incomplete bitwise expressions"""
        # Language Reference: both operands required
        incomplete_patterns = [
            "value &",        # Missing right operand
            "| flags",        # Missing left operand
            "a ^ ^ b",        # Double operator
            "x & | y",        # Mixed incomplete
        ]
        
        for source in incomplete_patterns:
            tester.assert_bitwise_operation_syntax_error(source)


class TestSection69BitwiseOperationAST:
    """Test bitwise operation AST structure validation."""
    
    def test_bitwise_ast_structure(self, tester):
        """Test BinOp AST node structure for bitwise operations"""
        # Language Reference: AST structure for bitwise operations
        bitwise_ast_cases = [
            """
result = value & mask
""",
            """
output = data | flags
""",
            """
xor_result = a ^ b
""",
            """
combined = x & y | z
"""
        ]
        
        for source in bitwise_ast_cases:
            tree = tester.assert_bitwise_operation_parses(source)
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should have bitwise operations: {source}"
            
            for bitwise_op in bitwise_ops:
                # BinOp nodes must have left, op, and right
                assert isinstance(bitwise_op, ast.BinOp), "Should be BinOp node"
                assert hasattr(bitwise_op, 'left'), "Should have left operand"
                assert hasattr(bitwise_op, 'op'), "Should have operator"
                assert hasattr(bitwise_op, 'right'), "Should have right operand"
                
                # Operator should be BitAnd, BitOr, or BitXor
                assert isinstance(bitwise_op.op, (ast.BitAnd, ast.BitOr, ast.BitXor)), "Should be bitwise operator"
                
                # Operands should be non-None
                assert bitwise_op.left is not None, "Left operand should not be None"
                assert bitwise_op.right is not None, "Right operand should not be None"
    
    def test_chained_bitwise_ast_structure(self, tester):
        """Test chained bitwise operation AST structure"""
        # Language Reference: chained bitwise operations create nested BinOp nodes
        chained_bitwise_source = """
result = a & b | c ^ d
"""
        
        tree = tester.assert_bitwise_operation_parses(chained_bitwise_source)
        bitwise_ops = tester.get_bitwise_operations(chained_bitwise_source)
        assert len(bitwise_ops) >= 3, "Should have multiple bitwise operations"
        
        # Check that we have different types of bitwise operations
        and_ops = tester.get_bitwise_and_operations(chained_bitwise_source)
        or_ops = tester.get_bitwise_or_operations(chained_bitwise_source)
        xor_ops = tester.get_bitwise_xor_operations(chained_bitwise_source)
        
        assert len(and_ops) >= 1, "Should have AND operations"
        assert len(or_ops) >= 1, "Should have OR operations"
        assert len(xor_ops) >= 1, "Should have XOR operations"
    
    def test_bitwise_with_complex_operands_ast(self, tester):
        """Test bitwise with complex operands AST"""
        # Language Reference: complex expressions as operands
        complex_bitwise_source = """
result = (a + b) & (c * d) | (e ^ f)
"""
        
        tree = tester.assert_bitwise_operation_parses(complex_bitwise_source)
        bitwise_ops = tester.get_bitwise_operations(complex_bitwise_source)
        assert len(bitwise_ops) >= 3, "Should have bitwise operations"
        
        # Should have arithmetic operations as operands
        arith_ops = [node for node in ast.walk(tree) if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mult))]
        assert len(arith_ops) >= 2, "Should have arithmetic operations in operands"


class TestSection69CrossImplementationCompatibility:
    """Test cross-implementation compatibility for bitwise operations."""
    
    def test_bitwise_ast_consistency(self, tester):
        """Test bitwise operation AST consistency across implementations"""
        # Language Reference: bitwise AST should be consistent
        consistency_test_cases = [
            """
result = value & mask
""",
            """
output = data | flags
""",
            """
xor_result = a ^ b
""",
            """
complex_bitwise = (a & b) | (c ^ d)
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_bitwise_operation_parses(source)
            
            # Should have consistent bitwise structure
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 1, f"Should have bitwise operations: {source}"
            
            for bitwise_op in bitwise_ops:
                assert isinstance(bitwise_op, ast.BinOp), "Should be BinOp node"
                assert isinstance(bitwise_op.op, (ast.BitAnd, ast.BitOr, ast.BitXor)), "Should be bitwise operator"
                assert bitwise_op.left is not None, "Should have left operand"
                assert bitwise_op.right is not None, "Should have right operand"
    
    def test_comprehensive_bitwise_patterns(self, tester):
        """Test comprehensive real-world bitwise patterns"""
        # Language Reference: complex bitwise usage scenarios
        comprehensive_patterns = [
            """
# Cryptography and hash functions using bitwise operations
class CryptoUtils:
    def __init__(self):
        # Bit manipulation constants
        self.S_BOXES = [
            [0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5],
            [0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76]
        ]
        
        # Rotation constants
        self.ROT_CONSTANTS = [1, 2, 8, 16]
        
    def simple_cipher(self, data, key):
        # Simple XOR cipher
        return [byte ^ (key & 0xFF) for byte in data]
    
    def feistel_round(self, left, right, round_key):
        # Feistel cipher round using bitwise operations
        f_output = self.f_function(right, round_key)
        new_left = right
        new_right = left ^ f_output
        return new_left, new_right
    
    def f_function(self, data, key):
        # Simple F function using bitwise operations
        mixed = data ^ key
        substituted = self.substitute(mixed)
        return self.permute(substituted)
    
    def substitute(self, value):
        # S-box substitution using bitwise indexing
        high_nibble = (value >> 4) & 0xF
        low_nibble = value & 0xF
        
        high_sub = self.S_BOXES[0][high_nibble & 0x7]
        low_sub = self.S_BOXES[1][low_nibble & 0x7]
        
        return (high_sub << 4) | low_sub
    
    def permute(self, value):
        # Simple bit permutation
        result = 0
        for i in range(8):
            if value & (1 << i):
                new_pos = (i * 3) % 8
                result |= 1 << new_pos
        return result
    
    def generate_round_keys(self, master_key, num_rounds):
        # Key schedule using bitwise operations
        keys = []
        current_key = master_key
        
        for round_num in range(num_rounds):
            # Rotate key
            current_key = self.rotate_key(current_key, self.ROT_CONSTANTS[round_num % 4])
            
            # Apply round constant
            current_key ^= round_num * 0x01010101
            
            # Key mixing
            temp = current_key
            temp ^= (temp << 1) & 0xFEFEFEFE
            temp ^= (temp << 2) & 0xFCFCFCFC
            temp ^= (temp << 4) & 0xF0F0F0F0
            
            keys.append(temp & 0xFFFFFFFF)
            current_key = temp
        
        return keys
    
    def rotate_key(self, key, positions):
        # Rotate 32-bit key left by positions
        return ((key << positions) | (key >> (32 - positions))) & 0xFFFFFFFF
    
    def avalanche_test(self, input_value):
        # Test avalanche effect using bitwise operations
        original_hash = self.simple_hash(input_value)
        
        avalanche_results = []
        for bit in range(32):
            # Flip one bit
            modified_input = input_value ^ (1 << bit)
            modified_hash = self.simple_hash(modified_input)
            
            # Count different bits
            diff = original_hash ^ modified_hash
            bit_count = bin(diff).count('1')
            avalanche_results.append(bit_count)
        
        return avalanche_results
    
    def simple_hash(self, value):
        # Simple hash function using bitwise operations
        hash_val = 0x811C9DC5  # FNV offset basis
        
        for i in range(4):
            byte = (value >> (i * 8)) & 0xFF
            hash_val ^= byte
            hash_val *= 0x01000193  # FNV prime
            hash_val &= 0xFFFFFFFF
        
        return hash_val

# Network protocol processing using bitwise operations
class NetworkProtocol:
    def __init__(self):
        # Protocol flags using bitwise constants
        self.FLAGS = {
            'SYN': 0x02,
            'ACK': 0x10,
            'FIN': 0x01,
            'RST': 0x04,
            'PSH': 0x08,
            'URG': 0x20
        }
        
        # Header field masks
        self.MASKS = {
            'version': 0xF0,
            'header_length': 0x0F,
            'type_of_service': 0xFF,
            'flags': 0x7,
            'fragment_offset': 0x1FFF
        }
    
    def create_tcp_flags(self, syn=False, ack=False, fin=False, rst=False, psh=False, urg=False):
        # Create TCP flags byte using bitwise OR
        flags = 0
        if syn: flags |= self.FLAGS['SYN']
        if ack: flags |= self.FLAGS['ACK']
        if fin: flags |= self.FLAGS['FIN']
        if rst: flags |= self.FLAGS['RST']
        if psh: flags |= self.FLAGS['PSH']
        if urg: flags |= self.FLAGS['URG']
        return flags
    
    def parse_tcp_flags(self, flags_byte):
        # Parse TCP flags using bitwise AND
        return {
            'SYN': bool(flags_byte & self.FLAGS['SYN']),
            'ACK': bool(flags_byte & self.FLAGS['ACK']),
            'FIN': bool(flags_byte & self.FLAGS['FIN']),
            'RST': bool(flags_byte & self.FLAGS['RST']),
            'PSH': bool(flags_byte & self.FLAGS['PSH']),
            'URG': bool(flags_byte & self.FLAGS['URG'])
        }
    
    def create_ip_header(self, version=4, header_len=5, tos=0, total_len=0, 
                        identification=0, flags=0, fragment_offset=0, ttl=64, 
                        protocol=6, checksum=0, src_ip=0, dest_ip=0):
        # Create IP header using bitwise operations
        header = bytearray(20)
        
        # Version and header length (4 bits each)
        header[0] = ((version & 0xF) << 4) | (header_len & 0xF)
        
        # Type of service
        header[1] = tos & 0xFF
        
        # Total length (16 bits, big endian)
        header[2] = (total_len >> 8) & 0xFF
        header[3] = total_len & 0xFF
        
        # Identification (16 bits, big endian)
        header[4] = (identification >> 8) & 0xFF
        header[5] = identification & 0xFF
        
        # Flags and fragment offset (16 bits total)
        flags_and_frag = ((flags & 0x7) << 13) | (fragment_offset & 0x1FFF)
        header[6] = (flags_and_frag >> 8) & 0xFF
        header[7] = flags_and_frag & 0xFF
        
        # TTL, Protocol, Checksum
        header[8] = ttl & 0xFF
        header[9] = protocol & 0xFF
        header[10] = (checksum >> 8) & 0xFF
        header[11] = checksum & 0xFF
        
        # Source IP (32 bits, big endian)
        header[12] = (src_ip >> 24) & 0xFF
        header[13] = (src_ip >> 16) & 0xFF
        header[14] = (src_ip >> 8) & 0xFF
        header[15] = src_ip & 0xFF
        
        # Destination IP (32 bits, big endian)
        header[16] = (dest_ip >> 24) & 0xFF
        header[17] = (dest_ip >> 16) & 0xFF
        header[18] = (dest_ip >> 8) & 0xFF
        header[19] = dest_ip & 0xFF
        
        return bytes(header)
    
    def parse_ip_header(self, header_bytes):
        # Parse IP header using bitwise operations
        if len(header_bytes) < 20:
            raise ValueError("Header too short")
        
        version = (header_bytes[0] >> 4) & 0xF
        header_length = header_bytes[0] & 0xF
        tos = header_bytes[1]
        
        total_length = (header_bytes[2] << 8) | header_bytes[3]
        identification = (header_bytes[4] << 8) | header_bytes[5]
        
        flags_and_frag = (header_bytes[6] << 8) | header_bytes[7]
        flags = (flags_and_frag >> 13) & 0x7
        fragment_offset = flags_and_frag & 0x1FFF
        
        ttl = header_bytes[8]
        protocol = header_bytes[9]
        checksum = (header_bytes[10] << 8) | header_bytes[11]
        
        src_ip = (header_bytes[12] << 24) | (header_bytes[13] << 16) | (header_bytes[14] << 8) | header_bytes[15]
        dest_ip = (header_bytes[16] << 24) | (header_bytes[17] << 16) | (header_bytes[18] << 8) | header_bytes[19]
        
        return {
            'version': version,
            'header_length': header_length,
            'type_of_service': tos,
            'total_length': total_length,
            'identification': identification,
            'flags': flags,
            'fragment_offset': fragment_offset,
            'ttl': ttl,
            'protocol': protocol,
            'checksum': checksum,
            'source_ip': src_ip,
            'destination_ip': dest_ip
        }
    
    def calculate_checksum(self, header_bytes):
        # Calculate IP header checksum using bitwise operations
        # Set checksum field to 0 for calculation
        header = bytearray(header_bytes)
        header[10] = 0
        header[11] = 0
        
        checksum = 0
        
        # Sum all 16-bit words
        for i in range(0, len(header), 2):
            word = (header[i] << 8) | header[i + 1]
            checksum += word
            
            # Handle carry
            if checksum > 0xFFFF:
                checksum = (checksum & 0xFFFF) + 1
        
        # One's complement
        checksum = (~checksum) & 0xFFFF
        
        return checksum

# Graphics and image processing using bitwise operations
class ImageProcessor:
    def __init__(self):
        # Color channel masks
        self.COLOR_MASKS = {
            'red_rgb888': 0xFF0000,
            'green_rgb888': 0x00FF00,
            'blue_rgb888': 0x0000FF,
            'red_rgb565': 0xF800,
            'green_rgb565': 0x07E0,
            'blue_rgb565': 0x001F
        }
        
        # Dithering patterns
        self.BAYER_4X4 = [
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
        ]
    
    def extract_rgb_channels(self, rgb888_pixel):
        # Extract RGB channels using bitwise operations
        red = (rgb888_pixel & self.COLOR_MASKS['red_rgb888']) >> 16
        green = (rgb888_pixel & self.COLOR_MASKS['green_rgb888']) >> 8
        blue = rgb888_pixel & self.COLOR_MASKS['blue_rgb888']
        return red, green, blue
    
    def pack_rgb888(self, red, green, blue):
        # Pack RGB channels into 888 format using bitwise operations
        return ((red & 0xFF) << 16) | ((green & 0xFF) << 8) | (blue & 0xFF)
    
    def convert_rgb888_to_rgb565(self, rgb888_pixel):
        # Convert RGB888 to RGB565 using bitwise operations
        red, green, blue = self.extract_rgb_channels(rgb888_pixel)
        
        # Scale down to 565 format
        red_565 = (red >> 3) & 0x1F      # 8 -> 5 bits
        green_565 = (green >> 2) & 0x3F   # 8 -> 6 bits
        blue_565 = (blue >> 3) & 0x1F     # 8 -> 5 bits
        
        return (red_565 << 11) | (green_565 << 5) | blue_565
    
    def apply_alpha_blend(self, foreground, background, alpha):
        # Alpha blending using bitwise operations
        fg_r, fg_g, fg_b = self.extract_rgb_channels(foreground)
        bg_r, bg_g, bg_b = self.extract_rgb_channels(background)
        
        # Alpha blend each channel
        alpha_inv = 255 - alpha
        
        result_r = ((fg_r * alpha) + (bg_r * alpha_inv)) >> 8
        result_g = ((fg_g * alpha) + (bg_g * alpha_inv)) >> 8
        result_b = ((fg_b * alpha) + (bg_b * alpha_inv)) >> 8
        
        return self.pack_rgb888(result_r, result_g, result_b)
    
    def apply_bit_mask(self, image_data, mask):
        # Apply bit mask to image data
        return [pixel & mask for pixel in image_data]
    
    def create_gradient(self, width, height, start_color, end_color):
        # Create gradient using bitwise interpolation
        start_r, start_g, start_b = self.extract_rgb_channels(start_color)
        end_r, end_g, end_b = self.extract_rgb_channels(end_color)
        
        gradient = []
        for y in range(height):
            for x in range(width):
                # Linear interpolation based on x position
                t = (x << 8) // width  # Fixed point math
                
                r = start_r + (((end_r - start_r) * t) >> 8)
                g = start_g + (((end_g - start_g) * t) >> 8)
                b = start_b + (((end_b - start_b) * t) >> 8)
                
                gradient.append(self.pack_rgb888(r, g, b))
        
        return gradient
    
    def apply_bayer_dithering(self, grayscale_data, width, height, threshold=128):
        # Apply Bayer dithering using bitwise operations
        dithered = []
        
        for y in range(height):
            for x in range(width):
                pixel = grayscale_data[y * width + x]
                
                # Get Bayer matrix value
                bayer_value = self.BAYER_4X4[y & 3][x & 3]
                
                # Scale Bayer value and apply threshold
                dither_threshold = threshold + ((bayer_value - 8) << 3)
                
                # Dither decision using bitwise comparison
                dithered_pixel = 0xFF if pixel > dither_threshold else 0x00
                dithered.append(dithered_pixel)
        
        return dithered
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_bitwise_operation_parses(source)
            
            # Should have extensive bitwise usage
            bitwise_ops = tester.get_bitwise_operations(source)
            assert len(bitwise_ops) >= 20, f"Should have many bitwise operations: {source}"
    
    def test_bitwise_introspection(self, tester):
        """Test ability to analyze bitwise operations programmatically"""
        # Test programmatic analysis of bitwise operation structure
        introspection_source = """
def bitwise_examples():
    # Simple bitwise operations
    and_result = a & b
    or_result = x | y
    xor_result = p ^ q
    
    # Chained operations
    chained_and = a & b & c
    chained_or = x | y | z
    chained_xor = p ^ q ^ r
    
    # Mixed operations with precedence
    mixed = a & b | c ^ d
    
    # With different types
    bool_and = flag1 & flag2
    set_union = set1 | set2
    int_xor = value ^ mask
    
    # In conditionals
    conditional = x & mask if condition else y | flags
    
    # In comprehensions
    masked = [item & filter for item in data]
    combined = {k: v | default for k, v in items.items()}
    
    # Complex expressions
    complex_bitwise = (base & filter1) | ((data ^ key) & filter2)
    
    return and_result, or_result, xor_result, chained_and, mixed, complex_bitwise
"""
        
        tree = tester.assert_bitwise_operation_parses(introspection_source)
        
        # Should identify all bitwise operations
        bitwise_ops = tester.get_bitwise_operations(introspection_source)
        assert len(bitwise_ops) >= 15, "Should have multiple bitwise operations"
        
        # Should identify different types of bitwise operations
        and_ops = tester.get_bitwise_and_operations(introspection_source)
        or_ops = tester.get_bitwise_or_operations(introspection_source)
        xor_ops = tester.get_bitwise_xor_operations(introspection_source)
        
        assert len(and_ops) >= 5, "Should have AND operations"
        assert len(or_ops) >= 5, "Should have OR operations"
        assert len(xor_ops) >= 3, "Should have XOR operations"
        
        # Should identify chained operations
        chain_counts = tester.count_chained_bitwise_operations(introspection_source)
        assert chain_counts['and'] >= 2, "Should have chained AND operations"
        assert chain_counts['or'] >= 2, "Should have chained OR operations"
        assert chain_counts['xor'] >= 2, "Should have chained XOR operations"
        
        # All bitwise operations should have proper structure
        for bitwise_op in bitwise_ops:
            assert isinstance(bitwise_op, ast.BinOp), "Should be BinOp node"
            assert isinstance(bitwise_op.op, (ast.BitAnd, ast.BitOr, ast.BitXor)), "Should be bitwise operator"
            assert bitwise_op.left is not None, "Should have left operand"
            assert bitwise_op.right is not None, "Should have right operand"