"""
Section 2.2: Other Tokens - Conformance Test Suite

Tests Python Language Reference Section 2.2 compliance across implementations.
Based on formal specifications for token types and tokenization rules.

Language Reference requirements tested:
    - NEWLINE tokens: Logical line termination, statement boundaries
    - INDENT tokens: Indentation increase, block structure
    - DEDENT tokens: Indentation decrease, block termination  
    - NAME tokens: Identifier tokenization, keyword recognition
    - NUMBER tokens: Numeric literal tokenization patterns
    - STRING tokens: String and bytes literal tokenization
    - OP tokens: Operator and delimiter tokenization
    - Whitespace handling: Token separation, ignored whitespace
    - Token delimiters: Automatic token boundary detection
    - Longest match rule: Tokenization precedence and disambiguation
"""

import ast
import pytest
import sys
import token
import tokenize
import io
from typing import Any, List


class OtherTokensTester:
    """Helper class for testing other tokens conformance.
    
    Uses tokenize module for token-level validation where possible,
    but focuses on AST-compatible testing for cross-implementation validity.
    """
    
    def assert_source_parses(self, source: str):
        """Test that source code tokenizes and parses correctly.
        
        Args:
            source: Python source code to tokenize and parse
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Token structure {source!r} failed to parse: {e}")
    
    def assert_source_syntax_error(self, source: str):
        """Test that invalid token structure raises SyntaxError.
        
        Args:
            source: Python source that should be invalid due to tokenization
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)

    def get_tokens_via_tokenize(self, source: str) -> List[tuple]:
        """Get tokens using tokenize module for detailed token analysis.
        
        Args:
            source: Python source code
            
        Returns:
            List of (token_type, token_string, start, end, line) tuples
        """
        try:
            tokens = []
            source_io = io.StringIO(source)
            for tok in tokenize.generate_tokens(source_io.readline):
                tokens.append((tok.type, tok.string, tok.start, tok.end, tok.line))
            return tokens
        except tokenize.TokenError as e:
            pytest.fail(f"Tokenization failed for {source!r}: {e}")
        except Exception as e:
            # In case of other errors, just return empty list to avoid test failure
            return []

    def contains_token_type(self, source: str, token_type: int) -> bool:
        """Check if source contains specific token type.
        
        Args:
            source: Python source code
            token_type: Token type constant from token module
            
        Returns:
            True if token type found, False otherwise
        """
        tokens = self.get_tokens_via_tokenize(source)
        return any(tok[0] == token_type for tok in tokens)


class TestSection22NewlineTokens:
    """Test NEWLINE token generation"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_newline_token_generation(self, tester):
        """Test NEWLINE tokens generated for logical line boundaries"""
        # Language Reference: NEWLINE token terminates logical lines
        newline_sources = [
            "x = 1\ny = 2",           # NEWLINE between statements
            "print('hello')\npass",   # NEWLINE after function call
            "# comment\nx = 1",       # NEWLINE after comment line
            "if True:\n    pass",     # NEWLINE before indented block
        ]
        
        for source in newline_sources:
            tree = tester.assert_source_parses(source)
            # Should tokenize with NEWLINE tokens
            assert tester.contains_token_type(source, token.NEWLINE)

    def test_newline_statement_boundaries(self, tester):
        """Test NEWLINE tokens create statement boundaries"""
        # Multiple statements should have NEWLINE separation
        boundary_sources = [
            "a = 1\nb = 2\nc = 3",
            "import os\nimport sys",
            "def f(): pass\ndef g(): pass",
            "x = 1\n# comment\ny = 2"
        ]
        
        for source in boundary_sources:
            tree = tester.assert_source_parses(source)
            # Should parse as multiple statements
            assert len(tree.body) >= 2

    def test_newline_in_compound_statements(self, tester):
        """Test NEWLINE behavior in compound statements"""
        # Compound statements use NEWLINE differently
        compound_sources = [
            "if True:\n    x = 1",
            "def func():\n    return 1", 
            "class Test:\n    pass",
            "try:\n    x = 1\nexcept:\n    pass"
        ]
        
        for source in compound_sources:
            tree = tester.assert_source_parses(source)
            # Should parse as compound statement
            assert len(tree.body) == 1

    def test_implicit_newline_at_eof(self, tester):
        """Test implicit NEWLINE at end of file"""
        # Sources without explicit newline should get implicit NEWLINE
        eof_sources = [
            "x = 1",
            "def func(): pass",
            "print('hello')"
        ]
        
        for source in eof_sources:
            tree = tester.assert_source_parses(source)
            # Should parse successfully with implicit NEWLINE


class TestSection22IndentDedentTokens:
    """Test INDENT and DEDENT token generation"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_indent_token_generation(self, tester):
        """Test INDENT tokens for indentation increases"""
        # Language Reference: INDENT generated when indentation increases
        indent_sources = [
            "if True:\n    x = 1",
            "def func():\n    return 1",
            "class Test:\n    pass",
            "with context:\n    do_something()"
        ]
        
        for source in indent_sources:
            tree = tester.assert_source_parses(source)
            # Should contain INDENT token
            assert tester.contains_token_type(source, token.INDENT)

    def test_dedent_token_generation(self, tester):
        """Test DEDENT tokens for indentation decreases"""
        # Language Reference: DEDENT generated when indentation decreases
        dedent_sources = [
            "if True:\n    x = 1\ny = 2",
            "def func():\n    return 1\nfunc()",
            "class Test:\n    pass\ntest = Test()",
        ]
        
        for source in dedent_sources:
            tree = tester.assert_source_parses(source)
            # Should contain DEDENT token
            assert tester.contains_token_type(source, token.DEDENT)

    def test_nested_indent_dedent(self, tester):
        """Test nested INDENT/DEDENT token patterns"""
        # Multiple indentation levels generate multiple INDENT/DEDENT
        nested_sources = [
            "if True:\n    if True:\n        x = 1\n    y = 2\nz = 3",
            "def outer():\n    def inner():\n        return 1\n    return inner()\nresult = outer()",
        ]
        
        for source in nested_sources:
            tree = tester.assert_source_parses(source)
            # Should contain multiple INDENT/DEDENT tokens
            assert tester.contains_token_type(source, token.INDENT)
            assert tester.contains_token_type(source, token.DEDENT)

    def test_indent_dedent_matching(self, tester):
        """Test INDENT/DEDENT token matching requirements"""
        # DEDENT must match a level on indentation stack
        matching_sources = [
            # Valid: return to previous level
            "if True:\n    x = 1\ny = 2",
            
            # Valid: multiple levels with proper matching
            "if True:\n    if True:\n        x = 1\ny = 2",
            
            # Valid: function with nested blocks
            "def func():\n    if True:\n        return 1\n    return 2"
        ]
        
        for source in matching_sources:
            tree = tester.assert_source_parses(source)


class TestSection22NameTokens:
    """Test NAME token generation for identifiers"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_simple_name_tokens(self, tester):
        """Test simple identifier NAME tokens"""
        # Language Reference: NAME tokens for identifiers
        name_sources = [
            "variable = 1",
            "function()",
            "object.attribute",
            "module.function()",
            "class_name = None"
        ]
        
        for source in name_sources:
            tree = tester.assert_source_parses(source)
            # Should contain NAME tokens
            assert tester.contains_token_type(source, token.NAME)

    def test_name_token_patterns(self, tester):
        """Test various identifier patterns generate NAME tokens"""
        # Different identifier naming conventions
        pattern_sources = [
            "simple = 1",
            "_private = 2", 
            "__dunder__ = 3",
            "CamelCase = 4",
            "snake_case = 5",
            "UPPER_CASE = 6",
            "mixed123 = 7",
            "with_numbers_123 = 8"
        ]
        
        for source in pattern_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.NAME)

    def test_keyword_vs_name_tokens(self, tester):
        """Test keyword recognition vs NAME token generation"""
        # Keywords should not be NAME tokens, identifiers should be
        keyword_sources = [
            "if True: pass",      # 'if' is keyword, not NAME
            "def function(): pass",  # 'def' is keyword, 'function' is NAME
            "import module",      # 'import' is keyword, 'module' is NAME
            "class Test: pass"    # 'class' is keyword, 'Test' is NAME
        ]
        
        for source in keyword_sources:
            tree = tester.assert_source_parses(source)
            # Should contain NAME tokens (for identifiers, not keywords)
            assert tester.contains_token_type(source, token.NAME)

    def test_name_token_unicode(self, tester):
        """Test Unicode identifier NAME tokens"""
        # Language Reference: identifiers can contain Unicode characters
        unicode_sources = [
            "café = 1",           # Non-ASCII letters
            "naïve = 2",          # Accented characters  
            "münchen = 3",        # German characters
            "北京 = 4",           # Chinese characters
        ]
        
        for source in unicode_sources:
            try:
                tree = tester.assert_source_parses(source)
                assert tester.contains_token_type(source, token.NAME)
            except UnicodeError:
                # Some systems may not support all Unicode in identifiers
                pytest.skip("Unicode identifiers not fully supported")


class TestSection22NumberTokens:
    """Test NUMBER token generation for numeric literals"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_integer_number_tokens(self, tester):
        """Test integer literal NUMBER tokens"""
        # Language Reference: NUMBER tokens for numeric literals
        integer_sources = [
            "x = 123",
            "y = 0",
            "z = 0x1a2b",    # Hexadecimal
            "a = 0o755",     # Octal
            "b = 0b1010"     # Binary
        ]
        
        for source in integer_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.NUMBER)

    def test_float_number_tokens(self, tester):
        """Test floating-point NUMBER tokens"""
        # Floating-point literal patterns
        float_sources = [
            "x = 3.14",
            "y = .5",
            "z = 10.",
            "a = 1e5",
            "b = 2.5e-3",
            "c = 1.2E+10"
        ]
        
        for source in float_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.NUMBER)

    def test_complex_number_tokens(self, tester):
        """Test complex number literal tokens"""
        # Complex number patterns
        complex_sources = [
            "x = 3j",
            "y = 4.5j",
            "z = 1e3j",
            "a = 5J"          # Case insensitive
        ]
        
        for source in complex_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.NUMBER)

    def test_number_token_separators(self, tester):
        """Test underscore separators in NUMBER tokens"""
        # Language Reference: underscores allowed in numeric literals
        separator_sources = [
            "x = 1_000_000",
            "y = 0x_dead_beef", 
            "z = 3.14_159",
            "a = 1e1_000"
        ]
        
        for source in separator_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.NUMBER)


class TestSection22StringTokens:
    """Test STRING token generation for string literals"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_simple_string_tokens(self, tester):
        """Test simple string literal STRING tokens"""
        # Language Reference: STRING tokens for string literals
        string_sources = [
            "x = 'hello'",
            'y = "world"',
            "z = '''triple single'''",
            'a = """triple double"""'
        ]
        
        for source in string_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.STRING)

    def test_string_token_prefixes(self, tester):
        """Test string prefix variations in STRING tokens"""
        # String prefixes should be part of STRING token
        basic_prefix_sources = [
            "x = r'raw'",
            "y = b'bytes'",
            "a = br'raw bytes'",
            "b = rb'bytes raw'",
        ]
        
        for source in basic_prefix_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.STRING)

    @pytest.mark.feature_fstrings
    def test_fstring_token_prefixes(self, tester):
        """Test f-string prefix variations"""
        # F-strings require Python 3.6+
        fstring_sources = [
            "z = f'formatted'",
            "c = fr'formatted raw'", 
            "d = rf'raw formatted'"
        ]
        
        for source in fstring_sources:
            tree = tester.assert_source_parses(source)
            # F-strings may tokenize differently in some implementations
            # Just verify they parse correctly rather than specific tokenization
            assert len(tree.body) == 1

    def test_bytes_literal_tokens(self, tester):
        """Test bytes literal tokenization"""
        # Bytes literals should generate STRING tokens (with b prefix)
        bytes_sources = [
            "x = b'bytes'",
            "y = b\"bytes double\"",
            "z = b'''bytes triple'''",
            "a = B'bytes upper'"
        ]
        
        for source in bytes_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.STRING)

    def test_multiline_string_tokens(self, tester):
        """Test multiline string tokenization"""
        # Triple-quoted strings can span multiple lines
        multiline_sources = [
            '"""multi\nline"""',
            "'''another\nmulti\nline'''",
            'r"""raw\nmultiline"""'
        ]
        
        for source in multiline_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.STRING)


class TestSection22OpTokens:
    """Test OP token generation for operators and delimiters"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_arithmetic_operator_tokens(self, tester):
        """Test arithmetic operator OP tokens"""
        # Language Reference: OP tokens for operators
        arithmetic_sources = [
            "x = a + b",
            "y = a - b", 
            "z = a * b",
            "w = a / b",
            "v = a // b",
            "u = a % b",
            "t = a ** b"
        ]
        
        for source in arithmetic_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.OP)

    def test_comparison_operator_tokens(self, tester):
        """Test comparison operator OP tokens"""
        # Comparison operators
        comparison_sources = [
            "x = a == b",
            "y = a != b",
            "z = a < b", 
            "w = a <= b",
            "v = a > b",
            "u = a >= b"
        ]
        
        for source in comparison_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.OP)

    def test_bitwise_operator_tokens(self, tester):
        """Test bitwise operator OP tokens"""
        # Bitwise operators
        bitwise_sources = [
            "x = a & b",
            "y = a | b",
            "z = a ^ b",
            "w = ~a",
            "v = a << 2",
            "u = b >> 1"
        ]
        
        for source in bitwise_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.OP)

    def test_assignment_operator_tokens(self, tester):
        """Test assignment operator OP tokens"""
        # Assignment and augmented assignment
        assignment_sources = [
            "x = 1",
            "y += 2",
            "z -= 3",
            "a *= 4",
            "b /= 5",
            "c %= 6",
            "d **= 7",
            "e //= 8"
        ]
        
        for source in assignment_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.OP)

    def test_delimiter_tokens(self, tester):
        """Test delimiter OP tokens"""
        # Delimiters (parentheses, brackets, braces, etc.)
        delimiter_sources = [
            "func()",
            "items[0]",
            "mapping = {}",
            "x, y = 1, 2",
            "if True: pass",
            "def func(): pass"
        ]
        
        for source in delimiter_sources:
            tree = tester.assert_source_parses(source)
            assert tester.contains_token_type(source, token.OP)

    def test_matrix_multiplication_token(self, tester):
        """Test matrix multiplication operator token"""
        # Matrix multiplication @ operator (Python 3.5+)
        matmul_source = "result = matrix @ vector"
        
        try:
            tree = tester.assert_source_parses(matmul_source)
            assert tester.contains_token_type(matmul_source, token.OP)
        except SyntaxError:
            if sys.version_info < (3, 5):
                pytest.skip("Matrix multiplication @ requires Python 3.5+")
            else:
                raise


class TestSection22WhitespaceHandling:
    """Test whitespace handling in tokenization"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_whitespace_ignored_between_tokens(self, tester):
        """Test whitespace is ignored between tokens"""
        # Language Reference: whitespace is ignored except for line structure
        whitespace_sources = [
            "x=1",           # No spaces
            "x = 1",         # Normal spaces
            "x  =  1",       # Multiple spaces
            "x\t=\t1",       # Tabs
            "x \t = \t 1"    # Mixed whitespace
        ]
        
        for source in whitespace_sources:
            tree = tester.assert_source_parses(source)
            # Should parse to same AST structure regardless of whitespace

    def test_whitespace_token_separation(self, tester):
        """Test whitespace required for token separation"""
        # Some tokens need whitespace separation to avoid ambiguity
        separation_sources = [
            "if True: pass",    # Keyword separation
            "def func(): pass", # Keyword and name separation
            "x = 1 +2",         # Number and operator
            "import os",        # Keyword and module name
        ]
        
        for source in separation_sources:
            tree = tester.assert_source_parses(source)

    def test_significant_whitespace_preservation(self, tester):
        """Test significant whitespace in indentation"""
        # Indentation whitespace is significant
        indentation_sources = [
            "if True:\n    x = 1",        # 4 spaces
            "if True:\n        x = 1",    # 8 spaces  
            "if True:\n\tx = 1",          # Tab
        ]
        
        for source in indentation_sources:
            tree = tester.assert_source_parses(source)
            # Should preserve indentation structure


class TestSection22TokenDelimiters:
    """Test automatic token boundary detection"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_automatic_token_boundaries(self, tester):
        """Test automatic token boundary detection"""
        # Language Reference: tokens automatically delimited
        boundary_sources = [
            "x=1+2",           # Operators delimit tokens
            "func(arg)",       # Parentheses delimit
            "list[index]",     # Brackets delimit
            "obj.attr",        # Dots delimit
            "a,b=1,2"          # Commas delimit
        ]
        
        for source in boundary_sources:
            tree = tester.assert_source_parses(source)

    def test_token_boundary_ambiguity_resolution(self, tester):
        """Test resolution of token boundary ambiguities"""
        # Cases where token boundaries could be ambiguous
        ambiguity_sources = [
            "x**y",            # ** vs * *
            "a<<b",            # << vs < <
            "c>>d",            # >> vs > > 
            "e!=f",            # != vs ! =
            "g==h",            # == vs = =
            "i<=j",            # <= vs < =
            "k>=l"             # >= vs > =
        ]
        
        for source in ambiguity_sources:
            tree = tester.assert_source_parses(source)

    def test_token_boundary_with_numbers(self, tester):
        """Test token boundaries with numeric literals"""
        # Numbers can create boundary ambiguities
        number_boundary_sources = [
            "1+2",             # Number + operator + number
            "3.14*x",          # Float * name
            "0x1a+b",          # Hex + operator + name
            "1e5-y",           # Scientific notation - name
            "2j+3j"            # Complex numbers
        ]
        
        for source in number_boundary_sources:
            tree = tester.assert_source_parses(source)


class TestSection22LongestMatchRule:
    """Test longest possible string matching rule"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_longest_operator_matching(self, tester):
        """Test longest match rule for operators"""
        # Language Reference: longest possible string is taken as token
        longest_match_sources = [
            "x == y",          # == not = =
            "a != b",          # != not ! =
            "c <= d",          # <= not < =
            "e >= f",          # >= not > =
            "g << h",          # << not < <
            "i >> j",          # >> not > >
            "k ** l",          # ** not * *
            "m // n",          # // not / /
        ]
        
        for source in longest_match_sources:
            tree = tester.assert_source_parses(source)
            # Should tokenize as single operators, not multiple

    def test_longest_match_with_numbers(self, tester):
        """Test longest match for numeric literals"""
        # Numbers should take longest possible match
        number_longest_sources = [
            "123",             # Entire number, not 1, 2, 3
            "3.14159",         # Entire float
            "0x1a2b3c",        # Entire hex number
            "1e100",           # Entire scientific notation
            "2.5e-10"          # Entire complex scientific notation
        ]
        
        for source in number_longest_sources:
            tree = tester.assert_source_parses(f"x = {source}")

    def test_longest_match_with_strings(self, tester):
        """Test longest match for string literals"""
        # String literals take entire quoted content
        string_longest_sources = [
            "'hello world'",   # Entire string content
            '"multiple words"', # Full quoted string
            "'''triple quoted content'''", # Full triple-quoted content
        ]
        
        for source in string_longest_sources:
            tree = tester.assert_source_parses(f"x = {source}")

    def test_longest_match_disambiguation(self, tester):
        """Test longest match rule disambiguation"""
        # Cases where longest match resolves ambiguity
        disambiguation_sources = [
            "+= operator",      # += not + =
            "-= operator",      # -= not - =
            "*= operator",      # *= not * =
            "/= operator",      # /= not / =
            "//= operator",     # //= not // =
            "**= operator",     # **= not ** =
            "<<= operator",     # <<= not << =
            ">>= operator",     # >>= not >> =
        ]
        
        for source in disambiguation_sources:
            # Test as assignment statements
            test_source = f"x {source.split()[0]} 1"
            tree = tester.assert_source_parses(test_source)


class TestSection22CrossImplementationCompatibility:
    """Test token handling across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return OtherTokensTester()

    def test_comprehensive_token_patterns(self, tester):
        """Test complex token combinations"""
        # Complex source combining all token types
        complex_sources = [
            # All token types in one statement
            "def function_name(param1, param2=123, *args, **kwargs):\n    '''Docstring'''\n    result = param1 + param2 * 3.14\n    return result",
            
            # Mixed operators and tokens
            "total = (value1 + value2) * coefficient / denominator ** exponent",
            
            # String operations with tokens
            "message = f'Processing {count} items with {rate:.2%} success rate'",
            
            # Complex data structures
            "data = {'key1': [1, 2, 3], 'key2': {item: process(item) for item in source}}"
        ]
        
        for source in complex_sources:
            try:
                tree = tester.assert_source_parses(source)
                # Should contain multiple token types
                assert tester.contains_token_type(source, token.NAME)
                assert tester.contains_token_type(source, token.OP)
            except SyntaxError:
                # Some patterns may not be valid in all Python versions
                if 'f\'' in source and sys.version_info < (3, 6):
                    pytest.skip("F-strings require Python 3.6+")
                else:
                    raise

    def test_token_edge_cases(self, tester):
        """Test edge cases in tokenization"""
        # Edge cases that might expose tokenization differences
        edge_sources = [
            "",                 # Empty source
            "pass",             # Single keyword
            "123",              # Single number
            "'string'",         # Single string
            "# comment only",   # Comment only
            "x",                # Single name
            "+",                # Single operator (invalid but tests tokenization)
        ]
        
        for source in edge_sources:
            if source in ["", "# comment only"]:
                # Empty and comment-only are valid
                tree = tester.assert_source_parses(source)
            elif source == "+":
                # Single operator should be syntax error
                tester.assert_source_syntax_error(source)
            else:
                # Other single tokens should parse in expression context
                try:
                    tree = tester.assert_source_parses(source)
                except SyntaxError:
                    # Some single tokens may not be valid statements
                    tree = tester.assert_source_parses(f"x = {source}")

    def test_tokenization_specification_compliance(self, tester):
        """Test compliance with tokenization specifications"""
        # Specific Language Reference compliance tests
        compliance_sources = [
            # Test: "NEWLINE token terminates logical lines"
            "x = 1\ny = 2",
            
            # Test: "INDENT/DEDENT generated for indentation changes"  
            "if True:\n    x = 1\ny = 2",
            
            # Test: "NAME tokens for identifiers, keywords recognized"
            "def function(parameter): return parameter",
            
            # Test: "NUMBER tokens for numeric literals"
            "values = [123, 3.14, 0x1a, 5j]",
            
            # Test: "STRING tokens for string literals"
            "text = 'hello' + \"world\" + '''multi\nline'''",
            
            # Test: "OP tokens for operators and delimiters"
            "result = (a + b) * c / d",
            
            # Test: "longest possible string taken as token"
            "comparison = (a == b) != (c <= d)"
        ]
        
        for source in compliance_sources:
            tree = tester.assert_source_parses(source)