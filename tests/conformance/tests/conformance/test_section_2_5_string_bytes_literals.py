"""
Section 2.5: String and Bytes Literals - Conformance Test Suite

Tests Python Language Reference Section 2.5 compliance across implementations.
Based on formal string literal syntax definitions and prose assertions for text processing behavior.
"""

import ast
import pytest
import sys


class StringLiteralTester:
    """Helper class for testing string literal conformance."""
    
    def assert_string_literal_parses(self, source: str):
        """Test that string literal syntax parses correctly."""
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"String literal syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_string_literal_syntax_error(self, source: str):
        """Test that invalid string literal syntax raises SyntaxError."""
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_string_literals(self, source: str) -> list:
        """Get string literal AST nodes from source."""
        tree = ast.parse(source)
        string_literals = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                string_literals.append(node)
        
        return string_literals
    
    def get_bytes_literals(self, source: str) -> list:
        """Get bytes literal AST nodes from source."""
        tree = ast.parse(source)
        bytes_literals = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, bytes):
                bytes_literals.append(node)
        
        return bytes_literals
    
    def get_formatted_values(self, source: str) -> list:
        """Get FormattedValue AST nodes from f-strings."""
        tree = ast.parse(source)
        formatted_values = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FormattedValue):
                formatted_values.append(node)
        
        return formatted_values
    
    def get_joinedstr_nodes(self, source: str) -> list:
        """Get JoinedStr AST nodes from f-strings."""
        tree = ast.parse(source)
        joinedstr_nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                joinedstr_nodes.append(node)
        
        return joinedstr_nodes


@pytest.fixture
def tester():
    """Provide StringLiteralTester instance for tests."""
    return StringLiteralTester()


class TestSection25BasicStringLiterals:
    """Test basic string literal syntax."""
    
    def test_simple_string_literals(self, tester):
        """Test simple string literal patterns"""
        simple_string_patterns = [
            'text = "Hello, World!"',
            "message = 'Python is awesome'",
            'empty = ""',
            "also_empty = ''",
            '''apostrophe = "It's a beautiful day"''',
            """quote = 'He said "Hello" to me'"""
        ]
        
        for source in simple_string_patterns:
            tree = tester.assert_string_literal_parses(source)
            string_literals = tester.get_string_literals(source)
            assert len(string_literals) >= 1, f"Should have string literals: {source}"
    
    def test_triple_quoted_strings(self, tester):
        """Test triple-quoted string patterns"""
        triple_quoted_patterns = [
            '''text = """This is a
multiline string
with triple quotes"""''',
            """another = '''Another way
to write multiline
strings'''""",
            '''docstring = """Function documentation
with multiple lines
and examples"""''',
        ]
        
        for source in triple_quoted_patterns:
            tree = tester.assert_string_literal_parses(source)
            string_literals = tester.get_string_literals(source)
            assert len(string_literals) >= 1, f"Should handle triple quotes: {source}"
    
    def test_escape_sequences(self, tester):
        """Test escape sequence handling"""
        escape_sequence_patterns = [
            r'newline = "Line 1\nLine 2"',
            r'tab = "Column 1\tColumn 2"',
            r'backslash = "Path\\to\\file"',
            r'quotes = "She said \"Hello\""',
            r'unicode_escape = "\u03B1\u03B2\u03B3"',
            r'hex_escape = "\x41\x42\x43"'
        ]
        
        for source in escape_sequence_patterns:
            tree = tester.assert_string_literal_parses(source)
            string_literals = tester.get_string_literals(source)
            assert len(string_literals) >= 1, f"Should handle escapes: {source}"
    
    def test_unicode_literals(self, tester):
        """Test Unicode string literals"""
        unicode_patterns = [
            'greek = "αβγδε"',
            'emoji = "🐍🚀✨"',
            'chinese = "你好世界"',
            'mixed = "ASCII and ñ and ▲"'
        ]
        
        for source in unicode_patterns:
            tree = tester.assert_string_literal_parses(source)
            string_literals = tester.get_string_literals(source)
            assert len(string_literals) >= 1, f"Should handle Unicode: {source}"


class TestSection25RawStrings:
    """Test raw string literals."""
    
    def test_raw_string_syntax(self, tester):
        """Test raw string prefix syntax"""
        raw_string_patterns = [
            r'regex = r"\d+\.\d+"',
            r'path = r"C:\Users\Name\Documents"',
            r"raw_text = r'No escape \n processing'",
            r'uppercase_r = R"Uppercase R prefix"'
        ]
        
        for source in raw_string_patterns:
            tree = tester.assert_string_literal_parses(source)
            string_literals = tester.get_string_literals(source)
            assert len(string_literals) >= 1, f"Should handle raw strings: {source}"


class TestSection25BytesLiterals:
    """Test bytes literal syntax."""
    
    def test_basic_bytes_literals(self, tester):
        """Test basic bytes literal syntax"""
        bytes_patterns = [
            'data = b"Hello, bytes!"',
            "empty_bytes = b''",
            'ascii_bytes = b"ASCII only content"',
            r'with_escapes = b"Line 1\nLine 2"',
            'uppercase_b = B"Uppercase B prefix"'
        ]
        
        for source in bytes_patterns:
            tree = tester.assert_string_literal_parses(source)
            bytes_literals = tester.get_bytes_literals(source)
            assert len(bytes_literals) >= 1, f"Should have bytes literals: {source}"
    
    def test_raw_bytes_literals(self, tester):
        """Test raw bytes literal combinations"""
        raw_bytes_patterns = [
            r'raw_bytes = br"\literal\backslashes"',
            r'also_raw_bytes = rb"\no\escape\processing"',
            r'uppercase_combo = BR"UPPERCASE\COMBO"',
            r'mixed_case = Rb"Mixed\Case\Prefix"'
        ]
        
        for source in raw_bytes_patterns:
            tree = tester.assert_string_literal_parses(source)
            bytes_literals = tester.get_bytes_literals(source)
            assert len(bytes_literals) >= 1, f"Should handle raw bytes: {source}"


@pytest.mark.min_version_3_6
class TestSection25FStringLiterals:
    """Test f-string literal syntax (Python 3.6+)."""
    
    def test_basic_fstring_syntax(self, tester):
        """Test basic f-string literal syntax"""
        fstring_patterns = [
            '''name = "World"
greeting = f"Hello, {name}!"''',
            '''x = 42
message = f"The answer is {x}"''',
            '''simple_expression = f"Result: {2 + 2}"''',
            '''method_call = f"Length: {len('hello')}"'''
        ]
        
        for source in fstring_patterns:
            tree = tester.assert_string_literal_parses(source)
            joinedstr_nodes = tester.get_joinedstr_nodes(source)
            assert len(joinedstr_nodes) >= 1, f"Should have f-strings: {source}"
    
    def test_fstring_format_specifiers(self, tester):
        """Test f-string format specifiers"""
        format_specifier_patterns = [
            '''pi = 3.14159
formatted = f"Pi: {pi:.2f}"''',
            '''number = 42
hex_format = f"Hex: {number:x}, Binary: {number:b}"''',
            '''text = "hello"
aligned = f"Left: '{text:<10}', Right: '{text:>10}'"'''
        ]
        
        for source in format_specifier_patterns:
            tree = tester.assert_string_literal_parses(source)
            formatted_values = tester.get_formatted_values(source)
            assert len(formatted_values) >= 1, f"Should handle format specs: {source}"


class TestSection25StringLiteralContexts:
    """Test string literals in different contexts."""
    
    def test_string_literals_in_assignments(self, tester):
        """Test string literals in assignment contexts"""
        assignment_patterns = [
            'message = "Hello, World!"',
            '''multiline = """First line
Second line
Third line"""''',
            'a, b, c = "first", "second", "third"'
        ]
        
        for source in assignment_patterns:
            tree = tester.assert_string_literal_parses(source)
            string_literals = tester.get_string_literals(source)
            assert len(string_literals) >= 1, f"Should work in assignments: {source}"
    
    def test_string_literals_in_data_structures(self, tester):
        """Test string literals in data structures"""
        data_structure_patterns = [
            'names = ["Alice", "Bob", "Charlie"]',
            '''person = {
    "first_name": "John",
    "last_name": "Doe"
}''',
            '''mixed_data = [
    "regular string",
    b"bytes data",
    r"raw\\string"
]'''
        ]
        
        for source in data_structure_patterns:
            tree = tester.assert_string_literal_parses(source)
            string_literals = tester.get_string_literals(source)
            assert len(string_literals) >= 1, f"Should work in data structures: {source}"


class TestSection25StringLiteralErrors:
    """Test string literal error conditions."""
    
    def test_unterminated_strings(self, tester):
        """Test unterminated string literals"""
        unterminated_patterns = [
            'text = "Unterminated string',
            "text = 'Also unterminated",
        ]
        
        for source in unterminated_patterns:
            tester.assert_string_literal_syntax_error(source)


class TestSection25StringLiteralAST:
    """Test string literal AST structure validation."""
    
    def test_string_literal_ast_structure(self, tester):
        """Test string literal AST node structure"""
        string_ast_cases = [
            'simple = "Hello"',
            '''multiline = """Line 1
Line 2"""''',
            r'raw = r"\literal\backslashes"'
        ]
        
        for source in string_ast_cases:
            tree = tester.assert_string_literal_parses(source)
            string_literals = tester.get_string_literals(source)
            if string_literals:
                for string_literal in string_literals:
                    assert isinstance(string_literal, ast.Constant), "Should be Constant node"
                    assert isinstance(string_literal.value, str), "Should have string value"
    
    def test_bytes_literal_ast_structure(self, tester):
        """Test bytes literal AST structure"""
        bytes_ast_source = '''data = b"Binary data"
raw_bytes = rb"\\Raw\\bytes"'''
        
        tree = tester.assert_string_literal_parses(bytes_ast_source)
        bytes_literals = tester.get_bytes_literals(bytes_ast_source)
        assert len(bytes_literals) >= 1, "Should have bytes literals"
        
        for bytes_literal in bytes_literals:
            assert isinstance(bytes_literal, ast.Constant), "Should be Constant node"
            assert isinstance(bytes_literal.value, bytes), "Should have bytes value"


class TestSection25CrossImplementationCompatibility:
    """Test cross-implementation compatibility for string literals."""
    
    def test_string_literal_consistency(self, tester):
        """Test string literal consistency across implementations"""
        consistency_test_cases = [
            'simple = "Basic string"',
            '''multiline = """Multiline
string content"""''',
            r'raw_string = r"\Raw\string"',
            'bytes_literal = b"Bytes content"'
        ]
        
        if sys.version_info >= (3, 6):
            consistency_test_cases.append('fstring = f"Formatted {42} string"')
        
        for source in consistency_test_cases:
            tree = tester.assert_string_literal_parses(source)
    
    def test_comprehensive_string_patterns(self, tester):
        """Test comprehensive real-world string patterns"""
        comprehensive_source = '''
class TextProcessor:
    def __init__(self):
        self.patterns = {
            'email': r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
            'phone': r"\\(?\\d{3}\\)?[-. ]?\\d{3}[-. ]?\\d{4}",
            'url': r"https?://[\\w.-]+(?:/[\\w._~!$&'()*+,;=:@/?-]*)?",
        }
        
        self.greetings = {
            'english': "Hello, World!",
            'spanish': "¡Hola, Mundo!",
            'chinese': "你好，世界！",
            'emoji': "👋🌍🚀"
        }
        
        self.templates = {
            'sql': """
                SELECT u.name, u.email
                FROM users u
                WHERE u.created_at >= ?
            """,
            'html': """
                <!DOCTYPE html>
                <html>
                <head><title>{title}</title></head>
                <body><h1>{header}</h1></body>
                </html>
            """
        }
        
        self.binary_patterns = {
            'png': b'\\x89PNG\\r\\n\\x1a\\n',
            'jpeg': b'\\xff\\xd8\\xff',
            'pdf': b'%PDF-'
        }
'''
        
        tree = tester.assert_string_literal_parses(comprehensive_source)
        string_literals = tester.get_string_literals(comprehensive_source)
        bytes_literals = tester.get_bytes_literals(comprehensive_source)
        
        assert len(string_literals) >= 15, f"Should have many string literals: {len(string_literals)} found"
        assert len(bytes_literals) >= 3, f"Should have bytes literals: {len(bytes_literals)} found"
    
    def test_string_literal_introspection(self, tester):
        """Test ability to analyze string literals programmatically"""
        introspection_source = '''
def string_examples():
    simple = "Basic string"
    multiline = """Triple quoted
    multiline string"""
    raw_path = r"C:\\Windows\\System32"
    binary_data = b"Binary content"
    raw_bytes = rb"\\Raw\\bytes"
    
    if True:  # Version check placeholder
        formatted = f"Hello, {'World'}!"
    
    config = {
        "strings": ["first", "second", "third"],
        "paths": [r"C:\\path1", r"C:\\path2"],
        "binary": [b"data1", b"data2"],
        "template": "Value: {value}"
    }
    
    return simple, multiline, raw_path, binary_data
'''
        
        tree = tester.assert_string_literal_parses(introspection_source)
        string_literals = tester.get_string_literals(introspection_source)
        bytes_literals = tester.get_bytes_literals(introspection_source)
        
        assert len(string_literals) >= 8, "Should have multiple string literals"
        assert len(bytes_literals) >= 2, "Should have bytes literals"
        
        for string_literal in string_literals:
            assert isinstance(string_literal, ast.Constant), "Should be Constant node"
            assert isinstance(string_literal.value, str), "Should have string value"
        
        for bytes_literal in bytes_literals:
            assert isinstance(bytes_literal, ast.Constant), "Should be Constant node"
            assert isinstance(bytes_literal.value, bytes), "Should have bytes value"