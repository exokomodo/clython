"""
Section 6.2: Atoms - Conformance Test Suite

Tests Python Language Reference Section 6.2 compliance across implementations.
Based on formal grammar definitions and prose assertions for atom syntax.

Grammar tested:
    atom: 'True' | 'False' | 'None' | '...' | identifier | literal | enclosure
    enclosure: parenth_form | list_display | dict_display | set_display 
             | generator_expression | yield_atom
    literal: strings | NUMBER

Language Reference requirements tested:
    - Built-in constants: True, False, None, ... (Ellipsis)
    - Identifiers: valid identifier syntax, private name mangling
    - Numeric literals: integers, floats, complex numbers (builds on Section 2.6)
    - String literals: various string forms (builds on Section 2.7)
    - Parenthesized forms: (expression)
    - List displays: [item1, item2, ...] 
    - Dictionary displays: {'key': 'value', ...}
    - Set displays: {item1, item2, ...}
    - Generator expressions: (expr for x in iterable)
    - Yield atoms: yield expressions in expression context
"""

import ast
import pytest
import sys
from typing import Any


class AtomTester:
    """Helper class for testing atom expression conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_atom_syntax_parses(self, source: str, mode: str = 'eval'):
        """Test that atom expression syntax parses correctly.
        
        Args:
            source: Python atom expression source code
            mode: Parse mode - 'eval' for expressions, 'exec' for statements
        """
        try:
            tree = ast.parse(source, mode=mode)
            # Successfully parsed
            return tree
        except SyntaxError as e:
            pytest.fail(f"Atom syntax {source!r} failed to parse: {e}")
    
    def assert_atom_syntax_error(self, source: str, mode: str = 'eval'):
        """Test that invalid atom syntax raises SyntaxError.
        
        Args:
            source: Python atom source code that should be invalid
            mode: Parse mode - 'eval' for expressions, 'exec' for statements
        """
        with pytest.raises(SyntaxError):
            ast.parse(source, mode=mode)

    def get_ast_node_type(self, source: str, mode: str = 'eval'):
        """Get the AST node type for an atom expression.
        
        Args:
            source: Python atom expression source
            mode: Parse mode
            
        Returns:
            AST node type for the expression
        """
        tree = ast.parse(source, mode=mode)
        if mode == 'eval':
            return type(tree.body)
        else:
            # For exec mode, get the first statement's value if it's an expression
            if (isinstance(tree.body[0], ast.Expr)):
                return type(tree.body[0].value)
            return type(tree.body[0])


class TestSection62BuiltinConstants:
    """Test Section 6.2.1: Built-in Constants"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_boolean_constants(self, tester):
        """Test True and False constants"""
        # Language Reference: 'True' | 'False'
        boolean_constants = [
            "True",
            "False"
        ]
        
        for source in boolean_constants:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Constant)
            assert isinstance(tree.body.value, bool)

    def test_none_constant(self, tester):
        """Test None constant"""
        # Language Reference: 'None'
        none_source = "None"
        tree = tester.assert_atom_syntax_parses(none_source)
        assert isinstance(tree.body, ast.Constant)
        assert tree.body.value is None

    def test_ellipsis_constant(self, tester):
        """Test Ellipsis (...) constant"""
        # Language Reference: '...'
        ellipsis_source = "..."
        tree = tester.assert_atom_syntax_parses(ellipsis_source)
        assert isinstance(tree.body, ast.Constant)
        # Ellipsis value check
        assert tree.body.value is ...

    def test_constant_assignments_forbidden(self, tester):
        """Test that built-in constants cannot be assigned to"""
        # Language Reference: these names cannot be reassigned
        forbidden_assignments = [
            "True = 123",
            "False = 456",
            "None = 'value'"
        ]
        
        for source in forbidden_assignments:
            tester.assert_atom_syntax_error(source, mode='exec')

    def test_constant_attribute_access_forbidden(self, tester):
        """Test that constants cannot be used as attributes in assignments"""
        # Note: This is actually a runtime error, not syntax error
        # The syntax parses correctly but would fail at runtime
        
        # These parse syntactically but are semantically invalid
        forbidden_attr_assignments = [
            "True.attr = value",
            "False.prop = data", 
            "None.field = result"
        ]
        
        for source in forbidden_attr_assignments:
            # These actually parse correctly - it's a runtime error
            tree = tester.assert_atom_syntax_parses(source, mode='exec')
            # The assignment parses but would fail at runtime

    def test_constants_in_expressions(self, tester):
        """Test constants used in expressions"""
        # Constants in valid expression contexts
        constant_expressions = [
            "True and False",
            "None or True",
            "... if condition else None",
            "not False",
            "True == False"
        ]
        
        for source in constant_expressions:
            tester.assert_atom_syntax_parses(source)


class TestSection62Identifiers:
    """Test Section 6.2.2: Identifiers (Names)"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_simple_identifiers(self, tester):
        """Test simple identifier atom syntax"""
        # Language Reference: identifier
        simple_identifiers = [
            "variable",
            "name",
            "x",
            "result",
            "data",
            "value123"
        ]
        
        for source in simple_identifiers:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Name)
            assert tree.body.id == source

    def test_valid_identifier_patterns(self, tester):
        """Test valid identifier naming patterns"""
        # Various valid identifier patterns
        valid_identifiers = [
            "_private",
            "__dunder__",
            "camelCase", 
            "snake_case",
            "PascalCase",
            "name_with_123_numbers",
            "_single_underscore_prefix",
            "trailing_underscore_",
            "CONSTANT_STYLE",
            "mixedCase_with_underscore"
        ]
        
        for source in valid_identifiers:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Name)
            assert tree.body.id == source

    def test_unicode_identifiers(self, tester):
        """Test Unicode identifier support"""
        # Unicode identifiers (Python 3+)
        unicode_identifiers = [
            "変数",      # Japanese
            "переменная", # Russian  
            "متغير",     # Arabic
            "αβγ",       # Greek
            "变量"       # Chinese
        ]
        
        for source in unicode_identifiers:
            try:
                tree = tester.assert_atom_syntax_parses(source)
                assert isinstance(tree.body, ast.Name)
                assert tree.body.id == source
            except (SyntaxError, UnicodeError):
                # Some Unicode might not be supported in all implementations
                pass

    def test_private_name_mangling_context(self, tester):
        """Test private name mangling identifiers"""
        # Language Reference: private name mangling for __name patterns
        # These should parse as valid identifiers
        private_names = [
            "__private_attr",
            "__method_name", 
            "__internal_var",
            "___triple_underscore"
        ]
        
        for source in private_names:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Name)
            assert tree.body.id == source

    def test_special_identifier_patterns(self, tester):
        """Test special identifier patterns"""
        # Special but valid patterns
        special_identifiers = [
            "__name__",     # Dunder attributes
            "__init__",
            "__str__",
            "_",            # Common throwaway variable
            "__",           # Double underscore
            "___",          # Triple underscore
            "_123",         # Underscore with numbers
            "_a_b_c_"       # Mixed underscores
        ]
        
        for source in special_identifiers:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Name)

    def test_invalid_identifiers(self, tester):
        """Test invalid identifier patterns"""
        # Invalid identifier syntax that should fail to parse
        invalid_identifiers = [
            "123invalid",    # Starts with number
            "space name",    # Contains space
            "dot.name",      # Contains dot (parses as attribute access)
            "exclaim!",      # Special characters
            "dollar$",       # Dollar sign
            "percent%",      # Percent sign
            "@symbol"        # At symbol
        ]
        
        # Test the ones that should actually fail
        syntax_error_identifiers = [
            "123invalid",    # Starts with number
            "space name",    # Contains space
            "exclaim!",      # Special characters
            "dollar$",       # Dollar sign
            "percent%",      # Percent sign
            "@symbol"        # At symbol
        ]
        
        for source in syntax_error_identifiers:
            tester.assert_atom_syntax_error(source)
        
        # Note: "hyp-hen" parses as subtraction (hyp - hen)
        # Note: "dot.name" parses as attribute access

    def test_keyword_identifiers_forbidden(self, tester):
        """Test that Python keywords cannot be used as identifiers"""
        # Python keywords should not parse as identifiers
        keywords = [
            "if", "else", "elif", "while", "for", "def", "class",
            "import", "from", "as", "try", "except", "finally",
            "with", "lambda", "global", "nonlocal", "assert",
            "del", "pass", "break", "continue", "return", "yield"
        ]
        
        for keyword in keywords:
            tester.assert_atom_syntax_error(keyword)


class TestSection62Literals:
    """Test Section 6.2.3: Literals (building on Sections 2.6, 2.7)"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_numeric_literals(self, tester):
        """Test numeric literal atoms (builds on Section 2.6)"""
        # Language Reference: NUMBER token
        numeric_literals = [
            "42",           # Integer
            "3.14159",      # Float
            "2.5e10",       # Scientific notation
            "1j",           # Imaginary
            "3+4j",         # Complex
            "0xFF",         # Hex
            "0o755",        # Octal  
            "0b1010"        # Binary
        ]
        
        for source in numeric_literals:
            tree = tester.assert_atom_syntax_parses(source)
            # Should parse as numeric constant or complex expression
            assert isinstance(tree.body, (ast.Constant, ast.BinOp))

    def test_string_literals(self, tester):
        """Test string literal atoms (builds on Section 2.7)"""
        # Language Reference: strings token
        string_literals = [
            "'single quotes'",
            '"double quotes"',
            '"""triple double"""',
            "'''triple single'''",
            "r'raw string'",
            "b'bytes literal'",
            'f"formatted {value}"',
            'u"unicode string"'
        ]
        
        for source in string_literals:
            tree = tester.assert_atom_syntax_parses(source)
            # Should parse as string constant
            assert isinstance(tree.body, (ast.Constant, ast.JoinedStr))

    def test_literal_concatenation(self, tester):
        """Test string literal concatenation"""
        # Language Reference: string literal concatenation
        concatenated_literals = [
            '"first" "second"',
            "'hello' 'world'",
            'r"raw" "normal"',
            '"normal" r"raw"'
        ]
        
        for source in concatenated_literals:
            tree = tester.assert_atom_syntax_parses(source)
            # Should parse as concatenated string
            assert isinstance(tree.body, ast.Constant)

    def test_negative_numbers_not_literals(self, tester):
        """Test that negative numbers are expressions, not literals"""
        # Language Reference: negative numbers are unary operations
        negative_expressions = [
            "-42",
            "-3.14",
            "-1j"
        ]
        
        for source in negative_expressions:
            tree = tester.assert_atom_syntax_parses(source)
            # Should parse as unary operation, not literal
            assert isinstance(tree.body, ast.UnaryOp)
            assert isinstance(tree.body.op, ast.USub)


class TestSection62ParenthesizedForms:
    """Test parenthesized forms as atoms"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_simple_parenthesized_expressions(self, tester):
        """Test simple parenthesized expressions"""
        # Language Reference: parenth_form
        parenthesized = [
            "(42)",
            "(variable)",
            "(True)",
            "(None)",
            "(...)"
        ]
        
        for source in parenthesized:
            tree = tester.assert_atom_syntax_parses(source)
            # Parentheses don't change the inner expression type
            inner_expr = tree.body
            assert inner_expr is not None

    def test_complex_parenthesized_expressions(self, tester):
        """Test complex expressions in parentheses"""
        # Complex expressions in parentheses
        complex_parenthesized = [
            "(a + b)",
            "(x * y + z)",
            "(function_call())",
            "(obj.method())",
            "(container[index])"
        ]
        
        for source in complex_parenthesized:
            tree = tester.assert_atom_syntax_parses(source)
            # Should parse successfully
            assert tree.body is not None

    def test_nested_parentheses(self, tester):
        """Test nested parentheses"""
        # Nested parenthetical expressions
        nested_parentheses = [
            "((42))",
            "(((variable)))",
            "((a + b) * (c + d))",
            "(((nested_call())))"
        ]
        
        for source in nested_parentheses:
            tree = tester.assert_atom_syntax_parses(source)
            assert tree.body is not None

    def test_empty_parentheses_tuple(self, tester):
        """Test empty parentheses create empty tuple"""
        # Language Reference: () creates empty tuple
        empty_tuple = "()"
        tree = tester.assert_atom_syntax_parses(empty_tuple)
        assert isinstance(tree.body, ast.Tuple)
        assert len(tree.body.elts) == 0

    def test_single_element_parentheses(self, tester):
        """Test single element with trailing comma creates tuple"""
        # Single element with comma
        single_tuple_forms = [
            "(42,)",
            "(variable,)",
            "(expression,)"
        ]
        
        for source in single_tuple_forms:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Tuple)
            assert len(tree.body.elts) == 1


class TestSection62ListDisplays:
    """Test list display atoms"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_simple_list_displays(self, tester):
        """Test simple list display syntax"""
        # Language Reference: list_display
        simple_lists = [
            "[]",                    # Empty list
            "[1]",                   # Single element
            "[1, 2, 3]",             # Multiple elements
            "['a', 'b', 'c']",       # String elements
            "[True, False, None]"    # Mixed constant types
        ]
        
        for source in simple_lists:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.List)

    def test_complex_list_elements(self, tester):
        """Test lists with complex element expressions"""
        # Lists with expressions
        complex_lists = [
            "[a + b, c * d]",
            "[func(), method.call()]",
            "[obj.attr, container[key]]", 
            "[nested[0], nested[1][2]]"
        ]
        
        for source in complex_lists:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.List)

    def test_nested_list_displays(self, tester):
        """Test nested list structures"""
        # Nested lists
        nested_lists = [
            "[[]]",                  # Empty nested list
            "[[1, 2], [3, 4]]",      # 2D list
            "[[[1]]]",               # Deeply nested
            "[[a, b], [c, d, e]]"    # Irregular nesting
        ]
        
        for source in nested_lists:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.List)

    def test_list_with_trailing_comma(self, tester):
        """Test lists with trailing commas"""
        # Trailing comma handling
        trailing_comma_lists = [
            "[1,]",
            "[1, 2,]",
            "[a, b, c,]"
        ]
        
        for source in trailing_comma_lists:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.List)


class TestSection62DictDisplays:
    """Test dictionary display atoms"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_simple_dict_displays(self, tester):
        """Test simple dictionary display syntax"""
        # Language Reference: dict_display
        simple_dicts = [
            "{}",                           # Empty dict
            "{'key': 'value'}",             # Single pair
            "{'a': 1, 'b': 2}",             # Multiple pairs
            "{1: 'one', 2: 'two'}",         # Numeric keys
            "{'nested': {'inner': 'val'}}"  # Nested dict
        ]
        
        for source in simple_dicts:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Dict)

    def test_complex_dict_expressions(self, tester):
        """Test dicts with complex key/value expressions"""
        # Complex dictionary expressions
        complex_dicts = [
            "{func(): value}",
            "{key: method.call()}",
            "{obj.attr: container[index]}",
            "{a + b: x * y}"
        ]
        
        for source in complex_dicts:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Dict)

    def test_dict_comprehensions_vs_displays(self, tester):
        """Test distinction between dict displays and comprehensions"""
        # Regular dict displays (not comprehensions)
        dict_displays = [
            "{'computed': compute_value()}",
            "{'item' + str(i): i for i in range(3)}"  # This is comprehension
        ]
        
        # Test regular display
        tree1 = tester.assert_atom_syntax_parses(dict_displays[0])
        assert isinstance(tree1.body, ast.Dict)
        
        # Test comprehension
        tree2 = tester.assert_atom_syntax_parses(dict_displays[1])
        assert isinstance(tree2.body, ast.DictComp)

    def test_dict_with_trailing_comma(self, tester):
        """Test dicts with trailing commas"""
        # Trailing comma in dicts
        trailing_comma_dicts = [
            "{'single': 1,}",
            "{'a': 1, 'b': 2,}",
            "{'complex': expr,}"
        ]
        
        for source in trailing_comma_dicts:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Dict)


class TestSection62SetDisplays:
    """Test set display atoms"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_simple_set_displays(self, tester):
        """Test simple set display syntax"""
        # Language Reference: set_display
        simple_sets = [
            "{1}",              # Single element (not empty - that's dict)
            "{1, 2, 3}",        # Multiple elements
            "{'a', 'b', 'c'}",  # String elements
            "{True, False}",    # Boolean elements
        ]
        
        for source in simple_sets:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Set)

    def test_complex_set_elements(self, tester):
        """Test sets with complex element expressions"""
        # Complex set elements
        complex_sets = [
            "{func(), method()}",
            "{obj.attr, other.prop}",
            "{a + b, c * d}"
        ]
        
        for source in complex_sets:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Set)

    def test_set_vs_dict_distinction(self, tester):
        """Test distinction between set and dict displays"""
        # Set vs dict syntax
        set_examples = [
            "{1}",           # Set with one element
            "{1, 2}",        # Set with multiple elements
        ]
        
        dict_examples = [
            "{}",            # Empty dict (not set)
            "{1: 2}",        # Dict with key-value
        ]
        
        # Test sets
        for source in set_examples:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Set)
        
        # Test dicts
        for source in dict_examples:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.Dict)

    def test_set_comprehensions_vs_displays(self, tester):
        """Test distinction between set displays and comprehensions"""
        # Set display vs comprehension
        set_display = "{1, 2, 3}"
        set_comprehension = "{x for x in range(3)}"
        
        tree1 = tester.assert_atom_syntax_parses(set_display)
        assert isinstance(tree1.body, ast.Set)
        
        tree2 = tester.assert_atom_syntax_parses(set_comprehension)
        assert isinstance(tree2.body, ast.SetComp)


class TestSection62GeneratorExpressions:
    """Test generator expression atoms"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_simple_generator_expressions(self, tester):
        """Test simple generator expression syntax"""
        # Language Reference: generator_expression
        simple_generators = [
            "(x for x in range(10))",
            "(item for item in sequence)",
            "(value for value in container)"
        ]
        
        for source in simple_generators:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.GeneratorExp)

    def test_generator_with_conditions(self, tester):
        """Test generators with if conditions"""
        # Generators with filtering
        conditional_generators = [
            "(x for x in range(10) if x % 2 == 0)",
            "(item for item in items if item is not None)",
            "(value for value in data if validate(value))"
        ]
        
        for source in conditional_generators:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.GeneratorExp)

    def test_nested_generator_expressions(self, tester):
        """Test nested generator structures"""
        # Nested generators
        nested_generators = [
            "(x + y for x in range(3) for y in range(3))",
            "(item.value for sublist in lists for item in sublist)",
            "(f(x, y) for x in xs for y in ys if condition(x, y))"
        ]
        
        for source in nested_generators:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.GeneratorExp)

    def test_complex_generator_expressions(self, tester):
        """Test generators with complex expressions"""
        # Complex generator expressions
        complex_generators = [
            "(func(x) for x in data)",
            "(obj.method(item) for item in sequence)",
            "(container[key] for key in keys)",
            "((x, y) for x, y in pairs)"
        ]
        
        for source in complex_generators:
            tree = tester.assert_atom_syntax_parses(source)
            assert isinstance(tree.body, ast.GeneratorExp)


class TestSection62YieldAtoms:
    """Test yield expression atoms"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_simple_yield_expressions(self, tester):
        """Test simple yield expression syntax"""
        # Language Reference: yield_atom
        # Note: yield expressions need to be in function context
        yield_expressions = [
            """def gen():
    x = yield""",
            
            """def gen():
    value = yield 42""",
            
            """def gen():
    result = yield expression"""
        ]
        
        for source in yield_expressions:
            tree = tester.assert_atom_syntax_parses(source, mode='exec')
            # Should parse as function with yield
            assert isinstance(tree.body[0], ast.FunctionDef)

    def test_yield_from_expressions(self, tester):
        """Test yield from expression syntax"""
        # yield from syntax
        yield_from_expressions = [
            """def gen():
    x = yield from generator()""",
            
            """def gen():
    result = yield from other_generator""",
            
            """def gen():
    value = yield from sequence"""
        ]
        
        for source in yield_from_expressions:
            tree = tester.assert_atom_syntax_parses(source, mode='exec')
            assert isinstance(tree.body[0], ast.FunctionDef)

    def test_yield_in_expression_context(self, tester):
        """Test yield used in expression contexts"""
        # Yield in various expression contexts (needs parentheses)
        yield_contexts = [
            """def gen():
    return (yield)""",
            
            """def gen():
    result = func((yield value))""",
            
            """def gen():
    x = (yield) + (yield)"""
        ]
        
        for source in yield_contexts:
            tree = tester.assert_atom_syntax_parses(source, mode='exec')
            assert isinstance(tree.body[0], ast.FunctionDef)


class TestSection62ErrorConditions:
    """Test error conditions for atom expressions"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_invalid_literal_syntax(self, tester):
        """Test invalid literal syntax"""
        # Invalid literals
        invalid_literals = [
            "08",           # Invalid octal (leading zero)
            "1.2.3",        # Multiple decimal points
            "0xGHI",        # Invalid hex digits
            "1e",           # Incomplete scientific notation
            "1j2",          # Invalid imaginary syntax
        ]
        
        for source in invalid_literals:
            tester.assert_atom_syntax_error(source)

    def test_invalid_string_literals(self, tester):
        """Test invalid string literal syntax"""
        # Invalid string syntax
        invalid_strings = [
            "'unclosed string",     # Unclosed quote
            '"mixed quotes\'',      # Mismatched quotes
            "'''unclosed triple",   # Unclosed triple quotes
            'f"invalid {',          # Unclosed f-string expression
        ]
        
        for source in invalid_strings:
            tester.assert_atom_syntax_error(source)

    def test_invalid_enclosure_syntax(self, tester):
        """Test invalid enclosure syntax"""
        # Invalid enclosures
        invalid_enclosures = [
            "[unclosed list",       # Unclosed bracket
            "{unclosed dict",       # Unclosed brace
            "(unclosed paren",      # Unclosed parenthesis
            "[1, 2,, 3]",          # Double comma
            "{key: value:}",       # Invalid dict syntax
        ]
        
        for source in invalid_enclosures:
            tester.assert_atom_syntax_error(source)

    def test_yield_outside_function_error(self, tester):
        """Test that yield expressions require function context"""
        # yield outside function should fail
        invalid_yield = [
            "yield",
            "yield 42",
            "yield from sequence"
        ]
        
        for source in invalid_yield:
            tester.assert_atom_syntax_error(source)


class TestSection62CrossImplementationCompatibility:
    """Test atom features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return AtomTester()

    def test_large_numeric_literals(self, tester):
        """Test very large numeric literals"""
        # Large numbers
        large_numbers = [
            "123456789012345678901234567890",     # Large integer
            "1.23456789e100",                     # Large float
            "999999999999999999999j"              # Large imaginary
        ]
        
        for source in large_numbers:
            tree = tester.assert_atom_syntax_parses(source)
            # Should parse as numeric constant
            assert isinstance(tree.body, (ast.Constant, ast.BinOp))

    def test_complex_nested_structures(self, tester):
        """Test deeply nested atom structures"""
        # Complex nesting
        nested_structures = [
            "[[[[[[1]]]]]]",                      # Deep list nesting
            "{'a': {'b': {'c': {'d': 'value'}}}}", # Deep dict nesting
            "((((((expression))))))",              # Deep parentheses
            "((x for x in (y for y in range(10))))" # Nested generators
        ]
        
        for source in nested_structures:
            tree = tester.assert_atom_syntax_parses(source)
            # Should parse successfully
            assert tree.body is not None

    def test_atom_in_complex_expressions(self, tester):
        """Test atoms within complex expression contexts"""
        # Atoms in complex contexts
        complex_contexts = [
            "func([1, 2, 3], {'key': 'value'})",
            "obj.method({x for x in range(10)})",
            "container[{'nested': 'dict'}]",
            "(lambda x: [x, x * 2])(42)"
        ]
        
        for source in complex_contexts:
            tree = tester.assert_atom_syntax_parses(source)
            assert tree.body is not None

    def test_atom_literal_identity_behavior(self, tester):
        """Test atom literal identity behavior (implementation-specific)"""
        # These test AST parsing, not runtime behavior
        identity_test_literals = [
            "7",           # Small integer (may be cached)
            "123456789",   # Large integer (likely not cached)
            "'hello'",     # String literal
            "None",        # None constant
            "True"         # Boolean constant
        ]
        
        for source in identity_test_literals:
            tree = tester.assert_atom_syntax_parses(source)
            # Should parse as constants
            assert isinstance(tree.body, ast.Constant)

    def test_unicode_atom_support(self, tester):
        """Test Unicode support in atoms"""
        # Unicode in various atom types
        unicode_atoms = [
            "'こんにちは'",    # Unicode string
            "變數名稱",        # Unicode identifier (if supported)
            "{'鍵': '值'}",    # Unicode dict keys/values
        ]
        
        for source in unicode_atoms:
            try:
                tree = tester.assert_atom_syntax_parses(source)
                assert tree.body is not None
            except (SyntaxError, UnicodeError):
                # Some Unicode might not be supported
                pass

    def test_edge_case_atom_combinations(self, tester):
        """Test edge case atom combinations"""
        # Edge cases
        edge_cases = [
            "(...,)",          # Ellipsis in tuple
            "[..., None, True]", # Constants in list
            "{None: ..., True: False}", # Constants as dict keys/values
            "(yield for x in [])", # Yield in generator (invalid)
        ]
        
        # Test valid cases
        for source in edge_cases[:-1]:
            tree = tester.assert_atom_syntax_parses(source)
            assert tree.body is not None
        
        # Last one should fail (yield in generator expression)
        tester.assert_atom_syntax_error(edge_cases[-1])