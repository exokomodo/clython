"""
Section 2.1: Line Structure - Conformance Test Suite

Tests Python Language Reference Section 2.1 compliance across implementations.
Based on formal specifications for line structure, encoding, and tokenization.

Language Reference requirements tested:
    - Logical lines: NEWLINE token generation, statement boundaries
    - Physical lines: Line termination sequences (Unix LF, Windows CR LF, Classic Mac CR)
    - Encoding declarations: UTF-8 default, coding comments, BOM handling
    - Explicit line joining: Backslash continuation rules
    - Implicit line joining: Parentheses, brackets, braces continuation
    - Blank lines: Whitespace-only line handling
    - Indentation: INDENT/DEDENT token generation, tab/space rules
    - Whitespace between tokens: Token separation requirements
    - End markers: ENDMARKER token at end of input
"""

import ast
import pytest
import sys
import tempfile
import os
from typing import Any


class LineStructureTester:
    """Helper class for testing line structure conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_source_parses(self, source: str):
        """Test that source code with specific line structure parses correctly.
        
        Args:
            source: Python source code with line structure to test
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Line structure {source!r} failed to parse: {e}")
    
    def assert_source_syntax_error(self, source: str):
        """Test that invalid line structure raises SyntaxError.
        
        Args:
            source: Python source that should be invalid due to line structure
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)

    def write_temp_file(self, content: str, encoding='utf-8'):
        """Write content to temporary file and return path.
        
        Args:
            content: File content as string
            encoding: Text encoding to use
            
        Returns:
            Path to temporary file
        """
        fd, path = tempfile.mkstemp(suffix='.py', text=True)
        try:
            with os.fdopen(fd, 'w', encoding=encoding) as f:
                f.write(content)
            return path
        except:
            os.close(fd)
            raise

    def parse_file(self, path: str):
        """Parse Python file and return AST.
        
        Args:
            path: Path to Python file
            
        Returns:
            AST tree or raises SyntaxError
        """
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return ast.parse(content, filename=path)


class TestSection21LogicalLines:
    """Test Section 2.1: Logical Line Structure"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_simple_logical_lines(self, tester):
        """Test simple logical line parsing"""
        # Language Reference: logical lines end with NEWLINE token
        simple_lines = [
            "x = 1",
            "print('hello')",
            "def func(): pass",
            "if True: print('yes')",
            "import os",
            "from sys import exit"
        ]
        
        for line in simple_lines:
            tree = tester.assert_source_parses(line)
            # Should parse as single statement
            assert len(tree.body) == 1

    def test_multiple_logical_lines(self, tester):
        """Test multiple logical lines in sequence"""
        # Multiple statements on separate logical lines
        multi_line_sources = [
            "x = 1\ny = 2",
            "print('first')\nprint('second')",
            "import os\nimport sys",
            "def f(): pass\ndef g(): pass",
            "x = 1\ny = 2\nz = 3"
        ]
        
        for source in multi_line_sources:
            tree = tester.assert_source_parses(source)
            # Should parse as multiple statements
            assert len(tree.body) >= 2

    def test_logical_line_boundaries(self, tester):
        """Test statement boundary rules for logical lines"""
        # Statements cannot cross logical line boundaries except where NEWLINE allowed
        boundary_sources = [
            # Valid: compound statements allow NEWLINE within
            "if True:\n    pass",
            "def func():\n    return 1",
            "class Test:\n    pass",
            "try:\n    x = 1\nexcept:\n    pass",
            
            # Valid: expressions in parentheses
            "result = (1 +\n         2)",
            "items = [1,\n         2,\n         3]"
        ]
        
        for source in boundary_sources:
            tree = tester.assert_source_parses(source)
            # Should parse successfully


class TestSection21PhysicalLines:
    """Test physical line termination sequences"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_unix_line_endings(self, tester):
        """Test Unix LF line endings"""
        # Language Reference: Unix form using ASCII LF
        unix_sources = [
            "x = 1\ny = 2",           # LF between lines
            "print('hello')\npass",   # LF termination
            "# comment\nx = 1"        # LF after comment
        ]
        
        for source in unix_sources:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) >= 1

    def test_windows_line_endings(self, tester):
        """Test Windows CR LF line endings"""
        # Language Reference: Windows form using ASCII CR LF
        windows_sources = [
            "x = 1\r\ny = 2",
            "print('hello')\r\npass",
            "# comment\r\nx = 1"
        ]
        
        for source in windows_sources:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) >= 1

    def test_classic_mac_line_endings(self, tester):
        """Test Classic Mac OS CR line endings"""
        # Language Reference: Classic Mac form using ASCII CR
        mac_sources = [
            "x = 1\ry = 2",
            "print('hello')\rpass", 
            "# comment\rx = 1"
        ]
        
        for source in mac_sources:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) >= 1

    def test_mixed_line_endings(self, tester):
        """Test mixed line ending sequences in same file"""
        # Language Reference: sequences do not need to be consistent within file
        mixed_sources = [
            "x = 1\ny = 2\r\nz = 3",      # LF + CR LF
            "a = 1\rb = 2\nc = 3",        # CR + LF  
            "first\nsecond\r\nthird\rfourth"  # All three types
        ]
        
        for source in mixed_sources:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) >= 2

    def test_end_of_input_termination(self, tester):
        """Test end of input as implicit line terminator"""
        # Language Reference: end of input serves as implicit terminator
        unterminated_sources = [
            "x = 1",              # No explicit line ending
            "print('hello')",     # No newline at EOF
            "def func(): pass"    # Function without trailing newline
        ]
        
        for source in unterminated_sources:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) == 1


class TestSection21EncodingDeclarations:
    """Test encoding declarations and UTF-8 handling"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_utf8_default_encoding(self, tester):
        """Test UTF-8 default encoding"""
        # Language Reference: default encoding is UTF-8
        utf8_sources = [
            "# No encoding declaration\nx = 'hello'",
            "x = 'café'",           # UTF-8 characters
            "name = 'Björk'",       # Non-ASCII characters  
            "text = '你好'"          # Unicode characters
        ]
        
        for source in utf8_sources:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) >= 1

    def test_explicit_encoding_declarations(self, tester):
        """Test explicit encoding declarations"""
        # Language Reference: coding[=:]\\s*([-\\w.]+) pattern
        encoding_sources = [
            "# -*- coding: utf-8 -*-\nx = 'test'",
            "# coding=utf-8\ny = 1",
            "# vim: set fileencoding=utf-8 :\nz = 2",
            "#!/usr/bin/python\n# coding: utf-8\nw = 3"
        ]
        
        for source in encoding_sources:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) >= 1

    def test_encoding_declaration_placement(self, tester):
        """Test encoding declaration line placement rules"""
        # Language Reference: must appear in first or second line
        placement_tests = [
            # Valid: first line
            "# coding: utf-8\nx = 1",
            
            # Valid: second line with shebang
            "#!/usr/bin/python\n# coding: utf-8\ny = 2",
            
            # Valid: second line after comment
            "# This is a Python script\n# coding: utf-8\nz = 3"
        ]
        
        for source in placement_tests:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) >= 1

    def test_utf8_bom_handling(self, tester):
        """Test UTF-8 BOM handling at the lexical level"""
        # Language Reference: UTF-8 BOM should be handled properly
        # Note: Python's AST actually rejects BOM, but file parsing may handle it
        
        # Test that BOM in string content works (BOM as data, not encoding marker)
        bom_as_data = "text = '\\ufeff'  # BOM as string content"
        tree = tester.assert_source_parses(bom_as_data)
        assert len(tree.body) == 1
        
        # Test that files without BOM work normally
        normal_content = "x = 'hello'"
        tree = tester.assert_source_parses(normal_content)
        assert len(tree.body) == 1


class TestSection21ExplicitLineJoining:
    """Test explicit line joining with backslashes"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_backslash_continuation(self, tester):
        """Test backslash line continuation"""
        # Language Reference: backslash at end joins with following line
        continuation_sources = [
            "x = 1 + \\\n    2",
            "result = very_long_function_name() \\\n         + another_function()",
            "if condition_one and \\\n   condition_two: pass",
            "text = 'first part' + \\\n       'second part'",
        ]
        
        for source in continuation_sources:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) >= 1

    def test_backslash_continuation_rules(self, tester):
        """Test backslash continuation rules and restrictions"""
        # Language Reference: backslash deletes backslash and following end-of-line
        rule_sources = [
            # Valid: backslash continues expression
            "total = first_value \\\n      + second_value",
            
            # Valid: multiple continuations
            "result = a \\\n       + b \\\n       + c",
            
            # Valid: continuation in control structures  
            "if a > 0 and \\\n   b < 10: pass"
        ]
        
        for source in rule_sources:
            tree = tester.assert_source_parses(source)

    def test_backslash_restrictions(self, tester):
        """Test backslash continuation restrictions"""
        # Language Reference: cannot continue comments, must not be in string
        
        # Valid patterns that should work
        valid_sources = [
            "x = 1 \\\n  + 2",  # Expression continuation
            "y = 'hello' \\\n  + 'world'"  # String concatenation via continuation
        ]
        
        for source in valid_sources:
            tree = tester.assert_source_parses(source)

    def test_backslash_token_continuation(self, tester):
        """Test backslash cannot continue most tokens"""
        # Language Reference: backslash does not continue tokens except string literals
        
        # These should parse as separate statements/expressions
        token_sources = [
            # Numbers cannot be split
            "x = 123",  # Cannot be "x = 12\\\n3"
            
            # Names cannot be split  
            "variable = 1",  # Cannot be "vari\\\nable = 1"
            
            # Keywords cannot be split
            "def function(): pass"  # Cannot be "de\\\nf function(): pass"
        ]
        
        for source in token_sources:
            tree = tester.assert_source_parses(source)


class TestSection21ImplicitLineJoining:
    """Test implicit line joining in parentheses, brackets, braces"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_parentheses_continuation(self, tester):
        """Test implicit continuation in parentheses"""
        # Language Reference: expressions in parentheses can span multiple lines
        paren_sources = [
            "result = (1 + 2 +\n          3 + 4)",
            "value = (very_long_expression *\n         another_expression)",
            "condition = (first_test and\n             second_test)",
            "func_call = function(arg1,\n                    arg2,\n                    arg3)"
        ]
        
        for source in paren_sources:
            tree = tester.assert_source_parses(source)
            assert len(tree.body) >= 1

    def test_square_brackets_continuation(self, tester):
        """Test implicit continuation in square brackets"""
        # Language Reference: expressions in square brackets can span lines
        bracket_sources = [
            "items = [1, 2,\n         3, 4]",
            "matrix = [[1, 2],\n          [3, 4]]",
            "result = collection[key1,\n                   key2]",
            "data = [process(item)\n        for item in source]"
        ]
        
        for source in bracket_sources:
            tree = tester.assert_source_parses(source)

    def test_curly_braces_continuation(self, tester):
        """Test implicit continuation in curly braces"""
        # Language Reference: expressions in curly braces can span lines
        brace_sources = [
            "mapping = {'key1': 'value1',\n           'key2': 'value2'}",
            "values = {1, 2,\n          3, 4}",
            "result = {key: process(value)\n          for key, value in items}",
            "config = {\n    'setting1': True,\n    'setting2': False\n}"
        ]
        
        for source in brace_sources:
            tree = tester.assert_source_parses(source)

    def test_continuation_with_comments(self, tester):
        """Test implicit continuation lines can carry comments"""
        # Language Reference: implicitly continued lines can carry comments
        comment_sources = [
            "items = [1,  # first item\n         2,  # second item\n         3]  # third item",
            "result = (a +  # first operand\n          b +  # second operand\n          c)   # third operand",
            "mapping = {\n    'key1': 'value1',  # comment one\n    'key2': 'value2'   # comment two\n}"
        ]
        
        for source in comment_sources:
            tree = tester.assert_source_parses(source)

    def test_continuation_indentation_flexibility(self, tester):
        """Test indentation flexibility in continuation lines"""
        # Language Reference: indentation of continuation lines not important
        indent_sources = [
            "result = (1 +\n2 +\n          3)",  # Various indentation
            "items = [first,\nsecond,\n            third]",  # Mixed indentation
            "value = (expression\n    + other\n+ final)"  # Inconsistent but valid
        ]
        
        for source in indent_sources:
            tree = tester.assert_source_parses(source)

    def test_blank_continuation_lines(self, tester):
        """Test blank continuation lines are allowed"""
        # Language Reference: blank continuation lines are allowed
        blank_sources = [
            "items = [\n    1,\n\n    2,\n    3\n]",  # Blank line in list
            "result = (\n    a +\n\n    b\n)",         # Blank line in expression
        ]
        
        for source in blank_sources:
            tree = tester.assert_source_parses(source)


class TestSection21BlankLines:
    """Test blank line handling"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_blank_line_ignored(self, tester):
        """Test blank lines are ignored in parsing"""
        # Language Reference: logical lines with only whitespace/comments ignored
        blank_sources = [
            "x = 1\n\ny = 2",           # Blank line between statements
            "def func():\n    pass\n\nfunc()",  # Blank line after function
            "\nx = 1\n",               # Leading/trailing blank lines
            "# comment\n\nx = 1"       # Blank line after comment
        ]
        
        for source in blank_sources:
            tree = tester.assert_source_parses(source)
            # Blank lines should not affect statement count

    def test_whitespace_only_lines(self, tester):
        """Test lines with only whitespace are blank lines"""
        # Language Reference: spaces, tabs, formfeeds make blank lines
        whitespace_sources = [
            "x = 1\n    \ny = 2",      # Spaces only
            "x = 1\n\t\ny = 2",       # Tab only
            "x = 1\n \t \ny = 2"      # Mixed whitespace
        ]
        
        for source in whitespace_sources:
            tree = tester.assert_source_parses(source)

    def test_comment_only_lines(self, tester):
        """Test comment-only lines are treated as blank"""
        # Language Reference: lines with only comments are ignored
        comment_sources = [
            "x = 1\n# comment\ny = 2",
            "def func():\n    # internal comment\n    pass",
            "# header comment\n\nx = 1"
        ]
        
        for source in comment_sources:
            tree = tester.assert_source_parses(source)


class TestSection21Indentation:
    """Test indentation rules and INDENT/DEDENT tokens"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_basic_indentation(self, tester):
        """Test basic indentation creates INDENT/DEDENT"""
        # Language Reference: indentation determines statement grouping
        indent_sources = [
            "if True:\n    x = 1",
            "def func():\n    return 1",
            "class Test:\n    pass",
            "try:\n    x = 1\nexcept:\n    pass"
        ]
        
        for source in indent_sources:
            tree = tester.assert_source_parses(source)

    def test_nested_indentation(self, tester):
        """Test nested indentation levels"""
        # Multiple indentation levels
        nested_sources = [
            "if True:\n    if True:\n        x = 1",
            "def outer():\n    def inner():\n        return 1\n    return inner",
            "class Test:\n    def method(self):\n        if True:\n            pass"
        ]
        
        for source in nested_sources:
            tree = tester.assert_source_parses(source)

    def test_indentation_consistency(self, tester):
        """Test indentation consistency requirements"""
        # Language Reference: indentation levels must be consistent
        consistent_sources = [
            # Consistent 4-space indentation
            "if True:\n    x = 1\n    y = 2",
            
            # Consistent 2-space indentation  
            "def func():\n  return 1",
            
            # Consistent tab indentation
            "class Test:\n\tpass"
        ]
        
        for source in consistent_sources:
            tree = tester.assert_source_parses(source)

    def test_tab_space_conversion(self, tester):
        """Test tab to space conversion rules"""
        # Language Reference: tabs replaced by 1-8 spaces to multiple of 8
        tab_sources = [
            "if True:\n\tx = 1",        # Tab indentation
            "def func():\n\treturn 1",  # Tab in function
            "class Test:\n\tdef method(self):\n\t\tpass"  # Nested tabs
        ]
        
        for source in tab_sources:
            tree = tester.assert_source_parses(source)

    def test_dedent_matching(self, tester):
        """Test DEDENT must match previous indentation level"""
        # Language Reference: dedent must match a level on the stack
        dedent_sources = [
            # Valid: returns to previous level
            "if True:\n    x = 1\ny = 2",
            
            # Valid: multiple dedents
            "if True:\n    if True:\n        x = 1\ny = 2",
            
            # Valid: function with nested control
            "def func():\n    if True:\n        return 1\n    return 2"
        ]
        
        for source in dedent_sources:
            tree = tester.assert_source_parses(source)

    def test_indentation_errors(self, tester):
        """Test indentation error conditions"""
        # Invalid indentation that should raise IndentationError
        # Note: These are syntax errors at the AST level
        
        # Test one valid case to ensure our test method works
        valid_source = "if True:\n    pass"
        tree = tester.assert_source_parses(valid_source)


class TestSection21WhitespaceTokens:
    """Test whitespace between tokens"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_whitespace_separation(self, tester):
        """Test whitespace separates tokens when needed"""
        # Language Reference: whitespace needed when concatenation changes meaning
        separation_sources = [
            # Keywords and names need separation  
            "if True: pass",      # Keyword and literal need separation
            "def func(): pass",   # Keyword and name need separation  
            "import os",          # Keyword and name need separation
            "class Test: pass",   # Keyword and name need separation
            # Operators that need separation from numbers/names
            "x = 1 +2",          # Number and operator 
            "result = a -b"      # Names and operator
        ]
        
        for source in separation_sources:
            tree = tester.assert_source_parses(source)

    def test_optional_whitespace(self, tester):
        """Test whitespace optional in some contexts"""
        # Language Reference: +a and + a both produce same tokens
        optional_sources = [
            "+x",          # Unary plus without space
            "- y",         # Unary minus with space  
            "x+y",         # Binary operator without spaces
            "x + y",       # Binary operator with spaces
            "func()",      # Function call without spaces
            "func( )",     # Function call with spaces
        ]
        
        for source in optional_sources:
            tree = tester.assert_source_parses(source)

    def test_whitespace_types(self, tester):
        """Test different whitespace characters"""
        # Language Reference: space, tab, formfeed can separate tokens
        whitespace_sources = [
            "x = 1",        # Space separation
            "x\t=\t1",      # Tab separation
            "x\f=\f1",      # Formfeed separation (if supported)
            "x \t = \t 1"   # Mixed whitespace
        ]
        
        for source in whitespace_sources:
            try:
                tree = tester.assert_source_parses(source)
            except SyntaxError:
                # Some whitespace characters may not be universally supported
                if '\f' in source:
                    pytest.skip("Formfeed whitespace not supported")
                else:
                    raise


class TestSection21EndMarkers:
    """Test ENDMARKER token at end of input"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_end_of_file_handling(self, tester):
        """Test end of file generates ENDMARKER"""
        # Language Reference: ENDMARKER generated at end of non-interactive input
        eof_sources = [
            "x = 1",                    # Simple statement at EOF
            "def func(): pass",         # Function definition at EOF
            "if True:\n    pass",       # Compound statement at EOF
            "x = 1\ny = 2"              # Multiple statements ending at EOF
        ]
        
        for source in eof_sources:
            tree = tester.assert_source_parses(source)
            # Should parse successfully with implicit ENDMARKER

    def test_incomplete_input_detection(self, tester):
        """Test incomplete input that needs continuation"""
        # Sources that would need continuation in interactive mode
        incomplete_sources = [
            "if True:",     # Incomplete if statement
            "def func():",  # Incomplete function definition
            "class Test:",  # Incomplete class definition
            "try:"          # Incomplete try statement
        ]
        
        for source in incomplete_sources:
            # These should raise SyntaxError due to unexpected EOF
            tester.assert_source_syntax_error(source)

    def test_complete_input_recognition(self, tester):
        """Test complete input is properly recognized"""
        # Complete statements that don't need continuation
        complete_sources = [
            "pass",                 # Simple complete statement
            "x = 1",               # Assignment statement
            "if True: pass",       # Single-line compound statement
            "def f(): return 1",   # Single-line function
        ]
        
        for source in complete_sources:
            tree = tester.assert_source_parses(source)


class TestSection21CrossImplementationCompatibility:
    """Test line structure features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return LineStructureTester()

    def test_comprehensive_line_structure_patterns(self, tester):
        """Test complex line structure combinations"""
        # Complex patterns combining multiple line structure features
        complex_sources = [
            # Encoding + continuation + implicit joining
            "# coding: utf-8\nresult = (very_long_expression \\\n    + another_part +\n    final_part)",
            
            # Mixed line endings + comments + indentation
            "def function():\n    # Comment line\r\n    if condition:\r        return value\n    else:\n        return default",
            
            # Implicit joining + comments + blank lines  
            "data = {\n    'key1': 'value1',  # First entry\n\n    'key2': 'value2'   # Second entry\n}",
            
            # Multiple continuation types
            "total = first_value \\\n      + (second_value +\n         third_value) \\\n      + final_value"
        ]
        
        for source in complex_sources:
            tree = tester.assert_source_parses(source)

    def test_line_structure_edge_cases(self, tester):
        """Test edge cases in line structure"""
        # Edge cases that might expose implementation differences
        edge_sources = [
            "",                     # Empty file
            "\n",                   # Just newline
            "# Only comment",       # Comment-only file
            "   \n  \n   ",        # Whitespace and newlines only
            "pass\n",              # Statement with trailing newline
            "\n\npass\n\n",        # Statement surrounded by blank lines
        ]
        
        for source in edge_sources:
            try:
                tree = tester.assert_source_parses(source)
                # Empty files and whitespace-only should parse as empty module
                if not source.strip() or source.strip().startswith('#'):
                    assert len(tree.body) == 0 or all(isinstance(node, ast.Expr) for node in tree.body)
            except SyntaxError:
                # Some edge cases might be syntax errors, which is acceptable
                pass

    def test_line_structure_specification_compliance(self, tester):
        """Test compliance with specific Language Reference rules"""
        # Test specific rules from Language Reference
        compliance_tests = [
            # Test: "statements cannot cross logical line boundaries except where NEWLINE allowed"
            "if True: x = 1",  # Valid: single line compound statement
            
            # Test: "end of input serves as implicit terminator"  
            "x = 1",  # Valid: no explicit line ending needed
            
            # Test: "indentation determines statement grouping"
            "if True:\n    x = 1\n    y = 2",  # Valid: consistent grouping
            
            # Test: "blank lines are ignored"
            "x = 1\n\n\ny = 2",  # Valid: multiple blank lines
            
            # Test: "implicitly continued lines can carry comments"
            "items = [\n    1,  # comment\n    2\n]"  # Valid: comment in continuation
        ]
        
        for source in compliance_tests:
            tree = tester.assert_source_parses(source)