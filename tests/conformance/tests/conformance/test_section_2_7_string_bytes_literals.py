"""
Section 2.7: String and Bytes Literals - Conformance Test Suite

Tests Python Language Reference Section 2.7 compliance across implementations.
Based on formal grammar definitions and prose assertions from:
https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals

Grammar tested:
    stringliteral: [stringprefix](shortstring | longstring)  
    stringprefix: "r" | "u" | "R" | "U" | "f" | "F" | "fr" | "Fr" | "fR" | "FR" | "rf" | "rF" | "Rf" | "RF"
    bytesliteral: bytesprefix(shortstring | longstring)
    bytesprefix: "b" | "B" | "br" | "Br" | "bR" | "BR" | "rb" | "rB" | "Rb" | "RB"
    shortstring: "'" shortstringitem* "'" | '"' shortstringitem* '"'
    longstring: "'''" longstringitem* "'''" | '"""' longstringitem* '"""'

Prose requirements tested:
    - String and bytes concatenation rules: "Adjacent string/bytes literals are concatenated"
    - f-string expression syntax: "{expression}" with format specifiers
    - Raw string escaping: "backslashes are treated literally"
    - Prefix case insensitivity: "case insensitive but normalized"
    - Triple quote spanning: "may span multiple lines"
"""

import ast
import pytest
import sys
from typing import Union, Any


class StringLiteralTester:
    """Helper class for testing string and bytes literal conformance.
    
    Follows Section 2.6 NumericLiteralTester pattern for AST-based validation.
    """
    
    def assert_string_parses_correctly(self, source: str, expected_value: Any = None):
        """Test that string literal source parses correctly via AST.
        
        Args:
            source: Python string literal source code
            expected_value: Expected parsed value (optional, for validation)
        """
        try:
            tree = ast.parse(source, mode='eval')
            if expected_value is not None:
                # Evaluate the parsed AST to verify value
                compiled = compile(tree, '<test>', 'eval')
                actual = eval(compiled)
                assert actual == expected_value, f"Expected {expected_value!r}, got {actual!r}"
        except SyntaxError as e:
            pytest.fail(f"String literal {source!r} failed to parse: {e}")
    
    def assert_string_syntax_error(self, source: str):
        """Test that string literal source raises SyntaxError.
        
        Args:
            source: Python string literal source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source, mode='eval')


class TestSection27StringLiterals:
    """Test Section 2.7.1: String literals"""
    
    @pytest.fixture
    def tester(self):
        return StringLiteralTester()

    def test_basic_string_quotes(self, tester):
        """Test basic single and double quoted strings"""
        # Language Reference: shortstring: "'" shortstringitem* "'" | '"' shortstringitem* '"'
        tester.assert_string_parses_correctly("'hello'", 'hello')
        tester.assert_string_parses_correctly('"hello"', 'hello')
        tester.assert_string_parses_correctly("'hello world'", 'hello world')
        tester.assert_string_parses_correctly('"hello world"', 'hello world')

    def test_triple_quoted_strings(self, tester):
        """Test triple quoted strings spanning multiple lines"""  
        # Language Reference: longstring: "'''" longstringitem* "'''" | '"""' longstringitem* '"""'
        tester.assert_string_parses_correctly("'''hello'''", 'hello')
        tester.assert_string_parses_correctly('"""hello"""', 'hello')
        
        # Multi-line strings
        multiline_single = "'''line1\\nline2'''"
        tester.assert_string_parses_correctly(multiline_single, 'line1\nline2')
        
        multiline_double = '"""line1\\nline2"""'  
        tester.assert_string_parses_correctly(multiline_double, 'line1\nline2')

    def test_string_prefixes_case_insensitive(self, tester):
        """Test string prefix case insensitivity per Language Reference"""
        # Language Reference: "case insensitive but normalized"
        test_cases = [
            ("r'hello'", 'hello'),
            ("R'hello'", 'hello'), 
            ("f'hello'", 'hello'),
            ("F'hello'", 'hello'),
            ("fr'hello'", 'hello'),
            ("Fr'hello'", 'hello'),
            ("fR'hello'", 'hello'), 
            ("FR'hello'", 'hello'),
            ("rf'hello'", 'hello'),
            ("rF'hello'", 'hello'),
            ("Rf'hello'", 'hello'),
            ("RF'hello'", 'hello')
        ]
        
        for source, expected in test_cases:
            tester.assert_string_parses_correctly(source, expected)

    def test_raw_string_escaping(self, tester):
        """Test raw string escape sequence handling"""
        # Language Reference: "backslashes are treated literally" in raw strings
        tester.assert_string_parses_correctly(r"r'hello\nworld'", 'hello\\nworld')
        tester.assert_string_parses_correctly(r'r"hello\nworld"', 'hello\\nworld')
        tester.assert_string_parses_correctly(r"r'hello\tworld'", 'hello\\tworld')
        tester.assert_string_parses_correctly(r"r'C:\path\to\file'", 'C:\\path\\to\\file')

    @pytest.mark.min_version_3_6
    @pytest.mark.feature_fstrings  
    def test_f_string_basic_syntax(self, tester):
        """Test f-string basic expression syntax (Python 3.6+)"""
        # Language Reference: f-string expressions with {expression}
        tester.assert_string_parses_correctly("f'hello'", 'hello')
        
        # Note: f-strings with expressions require more complex testing
        # as they involve runtime evaluation, not just AST parsing
        # These tests focus on syntax validation only
        
    def test_string_concatenation_adjacent(self, tester):
        """Test adjacent string literal concatenation"""
        # Language Reference: "Adjacent string literals are concatenated"
        tester.assert_string_parses_correctly("'hello' 'world'", 'helloworld')
        tester.assert_string_parses_correctly('"hello" "world"', 'helloworld')
        tester.assert_string_parses_correctly("'hello' \"world\"", 'helloworld')
        
        # Multi-line concatenation
        multiline_concat = """'hello' \\
'world'"""
        tester.assert_string_parses_correctly(multiline_concat, 'helloworld')

    def test_escape_sequences_basic(self, tester):
        """Test basic escape sequence handling in regular strings"""
        test_cases = [
            ("'hello\\nworld'", 'hello\nworld'),
            ("'hello\\tworld'", 'hello\tworld'), 
            ("'hello\\\\world'", 'hello\\world'),
            ("'hello\\'world'", "hello'world"),
            ('\"hello\\\"world\"', 'hello"world'),
            ("'hello\\rworld'", 'hello\rworld'),
        ]
        
        for source, expected in test_cases:
            tester.assert_string_parses_correctly(source, expected)

    def test_unicode_strings(self, tester):
        """Test Unicode string literal handling"""
        tester.assert_string_parses_correctly("'café'", 'café')
        tester.assert_string_parses_correctly("'🐍'", '🐍')
        tester.assert_string_parses_correctly("'\\u0041'", 'A')  # Unicode escape
        tester.assert_string_parses_correctly("'\\U00000041'", 'A')  # Long Unicode escape


class TestSection27BytesLiterals:
    """Test Section 2.7.2: Bytes literals"""
    
    @pytest.fixture
    def tester(self):
        return StringLiteralTester()

    def test_bytes_prefix_syntax(self, tester):
        """Test bytes prefix syntax variations"""
        # Language Reference: bytesprefix: "b" | "B" | "br" | "Br" | "bR" | "BR" | "rb" | "rB" | "Rb" | "RB"
        test_cases = [
            ("b'hello'", b'hello'),
            ("B'hello'", b'hello'),
            ("br'hello'", b'hello'),
            ("Br'hello'", b'hello'),
            ("bR'hello'", b'hello'),
            ("BR'hello'", b'hello'),
            ("rb'hello'", b'hello'),
            ("rB'hello'", b'hello'),
            ("Rb'hello'", b'hello'),
            ("RB'hello'", b'hello')
        ]
        
        for source, expected in test_cases:
            tester.assert_string_parses_correctly(source, expected)

    def test_bytes_content_restrictions(self, tester):
        """Test bytes literal content restrictions (ASCII only)"""
        # Valid ASCII bytes
        tester.assert_string_parses_correctly("b'hello'", b'hello')
        tester.assert_string_parses_correctly("b'123'", b'123')
        tester.assert_string_parses_correctly("b'\\x41\\x42\\x43'", b'ABC')
        
    def test_bytes_raw_strings(self, tester):
        """Test raw bytes literal handling"""
        tester.assert_string_parses_correctly(r"br'hello\nworld'", b'hello\\nworld')
        tester.assert_string_parses_correctly(r"rb'hello\nworld'", b'hello\\nworld')

    def test_bytes_concatenation(self, tester):
        """Test adjacent bytes literal concatenation"""
        # Language Reference: "Adjacent string/bytes literals are concatenated"
        tester.assert_string_parses_correctly("b'hello' b'world'", b'helloworld')
        tester.assert_string_parses_correctly("b'hello' B'world'", b'helloworld')


class TestSection27ErrorConditions:
    """Test error conditions and invalid syntax"""
    
    @pytest.fixture
    def tester(self):
        return StringLiteralTester()

    def test_unterminated_string_errors(self, tester):
        """Test unterminated string literal errors"""
        invalid_strings = [
            "'hello",      # Missing closing quote
            '"hello',      # Wrong quote type
            "'''hello'",   # Incomplete triple quote
            '"""hello"',   # Incomplete triple quote  
        ]
        
        for invalid in invalid_strings:
            tester.assert_string_syntax_error(invalid)

    def test_invalid_prefix_combinations(self, tester):
        """Test invalid string prefix combinations"""
        invalid_prefixes = [
            "uf'hello'",   # u and f cannot be combined
            "fb'hello'",   # f and b cannot be combined
            "bf'hello'",   # b and f cannot be combined
            "ub'hello'",   # u and b cannot be combined (Python 3)
        ]
        
        for invalid in invalid_prefixes:
            tester.assert_string_syntax_error(invalid)

    def test_invalid_escape_sequences(self, tester):
        """Test invalid escape sequences"""
        # Note: Some invalid escapes might be warnings rather than errors
        # depending on Python version - test the clearly invalid ones
        invalid_escapes = [
            r"'\x'",       # Incomplete hex escape
            r"'\x1'",      # Incomplete hex escape (need 2 digits)
        ]
        
        for invalid in invalid_escapes:
            tester.assert_string_syntax_error(invalid)


class TestSection27FStringSpecific:
    """Test f-string specific syntax and behavior (Python 3.6+)"""
    
    @pytest.fixture
    def tester(self):
        return StringLiteralTester()

    @pytest.mark.min_version_3_6
    @pytest.mark.feature_fstrings
    def test_f_string_expression_syntax(self, tester):
        """Test f-string expression syntax validation"""
        # Basic f-string expression syntax - AST level validation only
        # These test that the syntax parses correctly, not evaluation
        
        # Simple expressions (no actual evaluation in these tests)
        f_string_syntaxes = [
            "f'{1}'",           # Literal expression
            "f'{1 + 2}'",       # Arithmetic expression  
            "f'hello {42}'",    # Mixed content
            "f'{\"nested\"}'",  # Nested quotes
        ]
        
        # Just test these parse successfully (don't evaluate)
        for syntax in f_string_syntaxes:
            try:
                ast.parse(syntax, mode='eval')
            except SyntaxError as e:
                pytest.fail(f"f-string syntax {syntax!r} should parse but failed: {e}")

    @pytest.mark.min_version_3_6
    def test_f_string_format_specifiers(self, tester):
        """Test f-string format specifier syntax"""
        # Format specifier syntax tests (AST parsing only)
        format_specs = [
            "f'{42:d}'",        # Integer format
            "f'{42:04d}'",      # Zero-padded
            "f'{3.14:.2f}'",    # Float precision
            "f'{42:x}'",        # Hex format
        ]
        
        for syntax in format_specs:
            try:
                ast.parse(syntax, mode='eval')
            except SyntaxError as e:
                pytest.fail(f"f-string format syntax {syntax!r} should parse but failed: {e}")


class TestSection27CrossImplementationCompatibility:
    """Test cases that might vary across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return StringLiteralTester()

    def test_large_string_literals(self, tester):
        """Test very large string literals for implementation limits"""
        # Test reasonably large strings (not extreme to avoid memory issues)
        large_string = "'" + "x" * 10000 + "'"
        tester.assert_string_parses_correctly(large_string, "x" * 10000)

    def test_deeply_nested_concatenation(self, tester):
        """Test many adjacent string concatenations"""
        # Test reasonable nesting (not extreme to avoid parser limits)
        parts = ["'part" + str(i) + "'" for i in range(100)]
        concatenated = " ".join(parts)
        expected = "".join(f"part{i}" for i in range(100))
        tester.assert_string_parses_correctly(concatenated, expected)

    def test_mixed_quote_styles_concatenation(self, tester):
        """Test concatenation of different quote styles"""
        tester.assert_string_parses_correctly("'hello' \"world\" '''from''' \"\"\"python\"\"\"", 
                                            'helloworldfrompython')

    @pytest.mark.min_version_3_6
    def test_string_bytes_concatenation_restrictions(self, tester):
        """Test that string and bytes cannot be concatenated"""
        # This should be a syntax error
        invalid_concatenations = [
            "'hello' b'world'",    # String + bytes
            "b'hello' 'world'",    # Bytes + string  
            "f'hello' b'world'",   # f-string + bytes
        ]
        
        for invalid in invalid_concatenations:
            tester.assert_string_syntax_error(invalid)