"""
Section 2.6 Numeric Literals Conformance Test Suite

Tests Python Language Reference Section 2.6 compliance across implementations.
Based on formal grammar definitions and prose assertions from:
https://docs.python.org/3/reference/lexical_analysis.html#numeric-literals

Grammar tested:
    NUMBER: integer | floatnumber | imagnumber
    integer: decinteger | bininteger | octinteger | hexinteger | zerointeger
    floatnumber: digitpart "." [digitpart] [exponent] | "." digitpart [exponent] | digitpart exponent
    imagnumber: (floatnumber | digitpart) ("j" | "J")

Prose requirements tested:
    - Underscore placement rules: "can only occur between digits"
    - Leading zero restrictions: "not allowed in non-zero decimal numbers"
    - Base prefix requirements: 0b/0B, 0o/0O, 0x/0X
    - Case sensitivity rules for prefixes and imaginary suffix
"""

import pytest
import ast
import sys
from typing import Union, Any


class NumericLiteralTester:
    """Helper class for testing numeric literal parsing"""
    
    def parse_literal(self, literal: str) -> Union[int, float, complex]:
        """Parse a numeric literal using Python's AST parser"""
        try:
            # Parse as expression and extract the literal value
            tree = ast.parse(literal, mode='eval')
            if isinstance(tree.body, ast.Constant):
                return tree.body.value
            elif isinstance(tree.body, ast.Num):  # Python < 3.8 compatibility
                return tree.body.n
            else:
                raise SyntaxError(f"Not a simple literal: {literal}")
        except SyntaxError as e:
            raise SyntaxError(f"Invalid literal '{literal}': {e}")
    
    def assert_parses_correctly(self, literal: str, expected: Union[int, float, complex]):
        """Assert that literal parses to expected value"""
        result = self.parse_literal(literal)
        assert result == expected, f"Expected {expected}, got {result}"
        
    def assert_syntax_error(self, literal: str):
        """Assert that literal raises SyntaxError"""
        with pytest.raises(SyntaxError):
            self.parse_literal(literal)


@pytest.fixture
def tester():
    """Provide NumericLiteralTester instance"""
    return NumericLiteralTester()


class TestSection26IntegerLiterals:
    """Test Section 2.6.1: Integer literals"""
    
    def test_decimal_integers(self, tester):
        """Test basic decimal integer parsing"""
        # Simple decimal integers
        tester.assert_parses_correctly("0", 0)
        tester.assert_parses_correctly("1", 1)
        tester.assert_parses_correctly("123", 123)
        tester.assert_parses_correctly("2147483647", 2147483647)
        
        # Large integers (no built-in limit per Language Reference)
        large_int = "7922816251426433759354395033679228162514264337593543950336"
        tester.assert_parses_correctly(large_int, int(large_int))
    
    def test_leading_zeros_forbidden(self, tester):
        """Test: 'Leading zeros in a non-zero decimal number are not allowed'"""
        # From Language Reference prose
        tester.assert_syntax_error("01")
        tester.assert_syntax_error("0123")
        tester.assert_syntax_error("0999")
        
        # Zero itself is allowed
        tester.assert_parses_correctly("0", 0)
        tester.assert_parses_correctly("00", 0)  # Multiple zeros allowed
    
    def test_binary_integers(self, tester):
        """Test binary integer literals with 0b/0B prefix"""
        # Basic binary literals
        tester.assert_parses_correctly("0b0", 0)
        tester.assert_parses_correctly("0B0", 0)
        tester.assert_parses_correctly("0b1", 1)
        tester.assert_parses_correctly("0B1", 1)
        tester.assert_parses_correctly("0b1010", 10)
        tester.assert_parses_correctly("0B1111", 15)
        
        # Invalid binary digits
        tester.assert_syntax_error("0b2")
        tester.assert_syntax_error("0b8")
        tester.assert_syntax_error("0ba")
        
        # Missing digits
        tester.assert_syntax_error("0b")
        tester.assert_syntax_error("0B")
    
    def test_octal_integers(self, tester):
        """Test octal integer literals with 0o/0O prefix"""
        # Basic octal literals  
        tester.assert_parses_correctly("0o0", 0)
        tester.assert_parses_correctly("0O0", 0)
        tester.assert_parses_correctly("0o7", 7)
        tester.assert_parses_correctly("0o77", 63)
        tester.assert_parses_correctly("0o177", 127)
        tester.assert_parses_correctly("0O377", 255)
        
        # Invalid octal digits
        tester.assert_syntax_error("0o8")
        tester.assert_syntax_error("0o9")
        tester.assert_syntax_error("0oa")
        
        # Missing digits
        tester.assert_syntax_error("0o")
        tester.assert_syntax_error("0O")
    
    def test_hexadecimal_integers(self, tester):
        """Test hexadecimal integer literals with 0x/0X prefix"""
        # Basic hex literals
        tester.assert_parses_correctly("0x0", 0)
        tester.assert_parses_correctly("0X0", 0)
        tester.assert_parses_correctly("0xf", 15)
        tester.assert_parses_correctly("0XF", 15)
        tester.assert_parses_correctly("0xdeadbeef", 3735928559)
        tester.assert_parses_correctly("0XDeadBeef", 3735928559)
        
        # Case insensitive hex digits
        tester.assert_parses_correctly("0xabc", 0xABC)
        tester.assert_parses_correctly("0XABC", 0xabc)
        
        # Invalid hex characters
        tester.assert_syntax_error("0xg")
        tester.assert_syntax_error("0xz")
        
        # Missing digits
        tester.assert_syntax_error("0x")
        tester.assert_syntax_error("0X")
    
    def test_underscore_grouping_valid(self, tester):
        """Test valid underscore placement: 'between digits'"""
        # Decimal with underscores
        tester.assert_parses_correctly("1_000", 1000)
        tester.assert_parses_correctly("1_000_000", 1000000)
        tester.assert_parses_correctly("100_000_000_000", 100000000000)
        
        # Binary with underscores
        tester.assert_parses_correctly("0b_1010_1010", 0b10101010)
        tester.assert_parses_correctly("0b1010_1010", 0b10101010)
        
        # Octal with underscores
        tester.assert_parses_correctly("0o_177", 0o177)
        tester.assert_parses_correctly("0o1_7_7", 0o177)
        
        # Hex with underscores
        tester.assert_parses_correctly("0x_dead_beef", 0xdeadbeef)
        tester.assert_parses_correctly("0xdead_beef", 0xdeadbeef)
        
        # Underscore after base specifier (allowed)
        tester.assert_parses_correctly("0x_1f", 0x1f)
        tester.assert_parses_correctly("0b_10", 0b10)
        tester.assert_parses_correctly("0o_17", 0o17)
    
    def test_underscore_grouping_invalid(self, tester):
        """Test invalid underscore placement per Language Reference"""
        # Leading underscores not allowed
        tester.assert_syntax_error("_123")
        tester.assert_syntax_error("_0x123")
        
        # Trailing underscores not allowed  
        tester.assert_syntax_error("123_")
        tester.assert_syntax_error("0x123_")
        
        # Double underscores not allowed
        tester.assert_syntax_error("123__456")
        tester.assert_syntax_error("0x__123")
        
        # Underscore immediately after base specifier forbidden
        tester.assert_syntax_error("0_x123")
        tester.assert_syntax_error("0_b101")
        tester.assert_syntax_error("0_o123")


class TestSection26FloatingPointLiterals:
    """Test Section 2.6.2: Floating-point literals"""
    
    def test_basic_float_syntax(self, tester):
        """Test basic floating-point literal parsing"""
        # Integer and fraction parts
        tester.assert_parses_correctly("3.14", 3.14)
        tester.assert_parses_correctly("2.0", 2.0)
        tester.assert_parses_correctly("77.01", 77.01)
        
        # Leading zeros allowed in floats (unlike integers)
        tester.assert_parses_correctly("077.010", 77.01)
        tester.assert_parses_correctly("01.5", 1.5)
    
    def test_optional_components(self, tester):
        """Test optional integer/fraction parts per grammar"""
        # Missing integer part (decimal point + fraction)
        tester.assert_parses_correctly(".5", 0.5)
        tester.assert_parses_correctly(".001", 0.001)
        tester.assert_parses_correctly(".123456", 0.123456)
        
        # Missing fraction part (integer + decimal point)  
        tester.assert_parses_correctly("10.", 10.0)
        tester.assert_parses_correctly("5.", 5.0)
        tester.assert_parses_correctly("0.", 0.0)
    
    def test_exponent_notation(self, tester):
        """Test scientific notation with e/E exponent"""
        # Basic exponent syntax
        tester.assert_parses_correctly("1e3", 1000.0)
        tester.assert_parses_correctly("1E3", 1000.0)  # Case insensitive
        tester.assert_parses_correctly("2e-3", 0.002)
        tester.assert_parses_correctly("1.5e2", 150.0)
        
        # Exponent with explicit positive sign
        tester.assert_parses_correctly("1e+3", 1000.0)
        tester.assert_parses_correctly("6.02214076e+23", 6.02214076e+23)
        
        # Integer with exponent (no decimal point)
        tester.assert_parses_correctly("1e10", 1e10)
        tester.assert_parses_correctly("0e0", 0.0)
    
    def test_underscore_in_floats(self, tester):
        """Test underscore grouping in floating-point literals"""
        # Underscores in integer part
        tester.assert_parses_correctly("1_000.5", 1000.5)
        
        # Underscores in fraction part
        tester.assert_parses_correctly("3.14_15_93", 3.141593)
        tester.assert_parses_correctly("96_485.332_123", 96485.332123)
        
        # Underscores in exponent
        tester.assert_parses_correctly("1e1_000", 1e1000)
        tester.assert_parses_correctly("1.5e-1_0", 1.5e-10)
        
        # Complex float with underscores everywhere
        tester.assert_parses_correctly("1_234.567_8e1_0", 1234.5678e10)


class TestSection26ImaginaryLiterals:
    """Test Section 2.6.3: Imaginary literals"""
    
    def test_basic_imaginary_syntax(self, tester):
        """Test basic imaginary literal parsing with j/J suffix"""
        # Basic imaginary literals
        tester.assert_parses_correctly("1j", 1j)
        tester.assert_parses_correctly("1J", 1j)  # Case insensitive suffix
        tester.assert_parses_correctly("5j", 5j)
        
        # Float-based imaginary  
        tester.assert_parses_correctly("3.14j", 3.14j)
        tester.assert_parses_correctly("2.5J", 2.5j)
        
        # Zero imaginary
        tester.assert_parses_correctly("0j", 0j)
        tester.assert_parses_correctly("0.0j", 0j)
    
    def test_imaginary_with_float_syntax(self, tester):
        """Test imaginary literals using all float syntaxes"""
        # Imaginary with decimal point variations
        tester.assert_parses_correctly("10.j", 10j)
        tester.assert_parses_correctly(".001j", 0.001j)
        
        # Imaginary with exponent
        tester.assert_parses_correctly("1e10j", 1e10j)
        tester.assert_parses_correctly("3.14e-10J", 3.14e-10j)
        tester.assert_parses_correctly("1e100j", 1e100j)
        
        # Complex expressions (very large)  
        tester.assert_parses_correctly("1000000000000000000000000j", 1e+24j)
    
    def test_imaginary_with_underscores(self, tester):
        """Test underscore grouping in imaginary literals"""
        # Underscores in imaginary numbers
        tester.assert_parses_correctly("1_000j", 1000j)
        tester.assert_parses_correctly("3.14_15_93j", 3.141593j)
        tester.assert_parses_correctly("1e1_0j", 1e10j)
    
    def test_imaginary_decimal_point_omission(self, tester):
        """Test decimal point omission rule for imaginary literals"""
        # From Language Reference: decimal point can be omitted for integer part
        tester.assert_parses_correctly("10j", 10j)
        tester.assert_parses_correctly("42J", 42j)
        
        # But result is still float, not integer
        result = tester.parse_literal("10j")
        assert isinstance(result, complex)
        assert result.real == 0.0  # Real part is float zero
        assert result.imag == 10.0  # Imaginary part is float


class TestSection26ErrorConditions:
    """Test error conditions and edge cases"""
    
    def test_invalid_numeric_syntax(self, tester):
        """Test various invalid numeric literal syntaxes"""
        # Empty literals
        tester.assert_syntax_error("")
        
        # Invalid characters
        tester.assert_syntax_error("123abc")
        tester.assert_syntax_error("12.34.56")
        
        # Multiple decimal points
        tester.assert_syntax_error("1.2.3")
        
        # Invalid exponent syntax
        tester.assert_syntax_error("1e")
        tester.assert_syntax_error("1e+")
        tester.assert_syntax_error("1e-")
        tester.assert_syntax_error("1ee2")
    
    def test_whitespace_in_literals(self, tester):
        """Test that whitespace is not allowed within literals"""
        # Spaces not allowed
        tester.assert_syntax_error("1 234")
        tester.assert_syntax_error("3.1 4")
        tester.assert_syntax_error("1e 3")
        tester.assert_syntax_error("5 j")
        
        # Tabs not allowed
        tester.assert_syntax_error("1\t000")
    
    def test_base_prefix_edge_cases(self, tester):
        """Test edge cases for base prefixes"""
        # Mixed case prefixes (should work)
        tester.assert_parses_correctly("0Xf", 15)
        
        # F is not valid in binary - this should fail
        tester.assert_syntax_error("0bF")  # F is not a binary digit
        
    def test_suffix_edge_cases(self, tester):
        """Test edge cases for imaginary suffix"""
        # Suffix must be attached (no space)
        tester.assert_syntax_error("5 j")
        tester.assert_syntax_error("3.14 J")
        
        # Multiple suffixes not allowed
        tester.assert_syntax_error("5jj")
        tester.assert_syntax_error("3jJ")


class TestSection26CrossImplementationCompatibility:
    """Test cases that might vary across Python implementations"""
    
    def test_large_number_limits(self, tester):
        """Test very large numbers for implementation limits"""
        # Language Reference says no limit except memory
        very_large = "9" * 1000  # 1000 digit number
        result = tester.parse_literal(very_large)
        assert isinstance(result, int)
        assert len(str(result)) == 1000
    
    def test_precision_edge_cases(self, tester):
        """Test floating-point precision edge cases"""
        # Very small numbers
        tester.assert_parses_correctly("1e-308", 1e-308)
        
        # Very large exponents
        # Note: May overflow to inf, but should parse successfully
        result = tester.parse_literal("1e308")
        assert isinstance(result, float)
    
    @pytest.mark.min_version_3_6
    @pytest.mark.feature_fstrings
    def test_underscore_version_compatibility(self, tester):
        """Test underscore grouping (added in Python 3.6)"""
        # This should work in Python 3.6+
        tester.assert_parses_correctly("1_000_000", 1000000)


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])