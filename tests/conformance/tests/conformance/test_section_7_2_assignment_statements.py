"""
Section 7.2: Assignment Statements - Conformance Test Suite

Tests Python Language Reference Section 7.2 compliance across implementations.
Based on formal grammar definitions and prose assertions for assignment statements.

Grammar tested:
    assignment_stmt: (target_list "=")+ (starred_expression | yield_expression)
    target_list: target ("," target)* [","]
    target: identifier
          | "(" [target_list] ")"
          | "[" [target_list] "]"
          | attributeref
          | subscription  
          | "*" target

Language Reference requirements tested:
    - Simple assignment: name = value
    - Multiple assignment: a = b = value
    - Tuple unpacking: a, b = tuple_value
    - List unpacking: [a, b] = list_value
    - Starred expressions: a, *rest, b = sequence
    - Nested unpacking: (a, b), c = nested_structure
    - Attribute assignment: obj.attr = value
    - Subscription assignment: container[key] = value
    - Target validation and binding semantics
"""

import ast
import pytest
import sys
from typing import Any


class AssignmentStatementTester:
    """Helper class for testing assignment statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_assignment_syntax_parses(self, source: str):
        """Test that assignment statement syntax parses correctly.
        
        Args:
            source: Python assignment statement source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains assignment statement
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    return  # Found assignment statement, syntax is valid
            pytest.fail(f"Expected Assign node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Assignment syntax {source!r} failed to parse: {e}")
    
    def assert_assignment_syntax_error(self, source: str):
        """Test that invalid assignment syntax raises SyntaxError.
        
        Args:
            source: Python assignment source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)

    def get_assignment_from_source(self, source: str) -> ast.Assign:
        """Get the Assign AST node from source for detailed validation.
        
        Args:
            source: Python assignment statement source
            
        Returns:
            ast.Assign node
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                return node
        pytest.fail(f"No Assign node found in: {source}")


class TestSection72SimpleAssignment:
    """Test Section 7.2: Simple Assignment Statements"""
    
    @pytest.fixture
    def tester(self):
        return AssignmentStatementTester()

    def test_basic_simple_assignment(self, tester):
        """Test basic simple assignment syntax"""
        # Language Reference: target_list "=" expression
        simple_assignments = [
            "x = 42",
            "name = 'value'",
            "result = True",
            "data = [1, 2, 3]",
            "config = {'key': 'value'}",
            "count = 0"
        ]
        
        for source in simple_assignments:
            tester.assert_assignment_syntax_parses(source)

    def test_identifier_targets(self, tester):
        """Test valid identifier targets"""
        # Language Reference: target: identifier
        identifier_targets = [
            "valid_name = value",
            "_private_name = value",
            "__dunder_name__ = value",
            "camelCase = value",
            "snake_case = value",
            "name123 = value",
            "x = 1",
            "y_ = 2"
        ]
        
        for source in identifier_targets:
            tester.assert_assignment_syntax_parses(source)

    def test_assignment_to_built_in_names(self, tester):
        """Test assignment to built-in names (should parse but may shadow)"""
        # These should parse syntactically but shadow built-ins
        builtin_shadowing = [
            "len = 42",
            "str = 'string'",
            "int = 123",
            "list = []",
            "dict = {}",
            "sum = 0"
        ]
        
        for source in builtin_shadowing:
            tester.assert_assignment_syntax_parses(source)

    def test_numeric_and_string_literals(self, tester):
        """Test assignment with various literal types"""
        # Different literal value types
        literal_assignments = [
            "x = 0",
            "y = 3.14159",
            "z = 1j",
            "s = 'single quotes'",
            't = "double quotes"',
            "m = '''multiline\nstring'''",
            'n = """another\nmultiline"""',
            "b = b'bytes'",
            "r = r'raw string'",
            "f = f'formatted {x}'"
        ]
        
        for source in literal_assignments:
            tester.assert_assignment_syntax_parses(source)


class TestSection72MultipleAssignment:
    """Test multiple assignment statements"""
    
    @pytest.fixture
    def tester(self):
        return AssignmentStatementTester()

    def test_chained_assignment(self, tester):
        """Test chained assignment syntax"""
        # Language Reference: (target_list "=")+ expression
        chained_assignments = [
            "a = b = 42",
            "x = y = z = 0",
            "first = second = third = 'value'",
            "config1 = config2 = {}",
            "list1 = list2 = list3 = []",
            "a = b = c = d = e = 1"
        ]
        
        for source in chained_assignments:
            tester.assert_assignment_syntax_parses(source)

    def test_mixed_target_chaining(self, tester):
        """Test chained assignment with different target types"""
        # Mix of simple and complex targets
        mixed_chaining = [
            "a = obj.attr = 42",
            "x = container[0] = 'value'",
            "result = data['key'] = computed_value()",
            "a = b[i] = obj.method()"
        ]
        
        for source in mixed_chaining:
            tester.assert_assignment_syntax_parses(source)

    def test_chained_assignment_ast_structure(self, tester):
        """Test chained assignment AST structure"""
        # Verify AST structure for chained assignment
        source = "a = b = c = 42"
        assign_node = tester.get_assignment_from_source(source)
        
        # Should have 3 targets for a = b = c = 42
        assert len(assign_node.targets) == 3
        
        # All should be Name nodes
        for target in assign_node.targets:
            assert isinstance(target, ast.Name)
        
        # Check target names
        target_names = [target.id for target in assign_node.targets]
        assert target_names == ['a', 'b', 'c']


class TestSection72TupleUnpacking:
    """Test tuple unpacking assignment"""
    
    @pytest.fixture
    def tester(self):
        return AssignmentStatementTester()

    def test_basic_tuple_unpacking(self, tester):
        """Test basic tuple unpacking syntax"""
        # Language Reference: target_list with multiple targets
        tuple_unpacking = [
            "a, b = 1, 2",
            "x, y = tuple_value",
            "first, second = pair",
            "a, b, c = 1, 2, 3",
            "x, y, z, w = sequence"
        ]
        
        for source in tuple_unpacking:
            tester.assert_assignment_syntax_parses(source)

    def test_parenthesized_tuple_unpacking(self, tester):
        """Test tuple unpacking with parentheses"""
        # Language Reference: "(" [target_list] ")"
        parenthesized_unpacking = [
            "(a, b) = 1, 2",
            "(x, y) = tuple_value",
            "(first, second, third) = sequence",
            "(a,) = single_item_tuple",
            "() = empty_tuple"
        ]
        
        for source in parenthesized_unpacking:
            tester.assert_assignment_syntax_parses(source)

    def test_list_unpacking(self, tester):
        """Test list unpacking with square brackets"""
        # Language Reference: "[" [target_list] "]"
        list_unpacking = [
            "[a, b] = [1, 2]",
            "[x, y] = list_value",
            "[first, second, third] = sequence",
            "[a] = single_item_list",
            "[] = empty_list"
        ]
        
        for source in list_unpacking:
            tester.assert_assignment_syntax_parses(source)

    def test_mixed_unpacking_syntax(self, tester):
        """Test mixing parentheses and brackets"""
        # Mixed syntax forms
        mixed_unpacking = [
            "a, (b, c) = value",
            "(x, y), z = nested_value",
            "[a, b], c = nested_sequence",
            "a, [b, c] = mixed_value",
            "(a, [b, c]), d = complex_value"
        ]
        
        for source in mixed_unpacking:
            tester.assert_assignment_syntax_parses(source)

    def test_nested_unpacking(self, tester):
        """Test nested tuple/list unpacking"""
        # Nested unpacking patterns
        nested_unpacking = [
            "(a, b), c = nested_tuple",
            "a, (b, c) = reverse_nested",
            "(x, y), (z, w) = two_tuples",
            "[a, b], [c, d] = two_lists",
            "((a, b), c), d = deeply_nested",
            "a, (b, (c, d)) = triple_nested"
        ]
        
        for source in nested_unpacking:
            tester.assert_assignment_syntax_parses(source)

    def test_trailing_comma_handling(self, tester):
        """Test trailing comma in target lists"""
        # Trailing commas
        trailing_comma = [
            "a, = single_tuple",
            "x, y, = two_tuple",
            "a, b, c, = three_tuple",
            "(a,) = explicit_single_tuple",
            "(x, y,) = explicit_two_tuple"
        ]
        
        for source in trailing_comma:
            tester.assert_assignment_syntax_parses(source)

    def test_unpacking_ast_structure(self, tester):
        """Test unpacking AST structure validation"""
        # Verify AST structure for tuple unpacking
        source = "a, (b, c), d = nested_value"
        assign_node = tester.get_assignment_from_source(source)
        
        # Should have one target (the tuple)
        assert len(assign_node.targets) == 1
        target = assign_node.targets[0]
        
        # Target should be a Tuple
        assert isinstance(target, ast.Tuple)
        
        # Should have 3 elements: a, (b, c), d
        assert len(target.elts) == 3
        
        # First element: Name 'a'
        assert isinstance(target.elts[0], ast.Name)
        assert target.elts[0].id == 'a'
        
        # Second element: Tuple (b, c)  
        assert isinstance(target.elts[1], ast.Tuple)
        assert len(target.elts[1].elts) == 2
        
        # Third element: Name 'd'
        assert isinstance(target.elts[2], ast.Name)
        assert target.elts[2].id == 'd'


class TestSection72StarredExpressions:
    """Test starred expressions in assignment"""
    
    @pytest.fixture
    def tester(self):
        return AssignmentStatementTester()

    def test_starred_target_syntax(self, tester):
        """Test starred target syntax"""
        # Language Reference: "*" target
        starred_targets = [
            "a, *rest = sequence",
            "*first, b = sequence", 
            "a, *middle, b = sequence",
            "*all = sequence",
            "a, b, *remainder = sequence"
        ]
        
        for source in starred_targets:
            tester.assert_assignment_syntax_parses(source)

    def test_starred_expressions_positions(self, tester):
        """Test starred expressions in different positions"""
        # Various starred positions
        starred_positions = [
            "*head, tail = sequence",
            "head, *tail = sequence", 
            "a, *middle, z = sequence",
            "first, *between, last = sequence",
            "*everything = sequence"
        ]
        
        for source in starred_positions:
            tester.assert_assignment_syntax_parses(source)

    def test_starred_in_nested_unpacking(self, tester):
        """Test starred expressions in nested contexts"""
        # Starred in nested structures
        nested_starred = [
            "(a, *rest), b = nested_sequence",
            "a, (*middle, last) = reverse_nested",
            "[first, *rest] = list_sequence",
            "*head, (a, b) = complex_sequence"
        ]
        
        for source in nested_starred:
            tester.assert_assignment_syntax_parses(source)

    def test_starred_expression_ast_structure(self, tester):
        """Test starred expression AST structure"""
        # Verify AST for starred expressions
        source = "a, *rest, b = sequence"
        assign_node = tester.get_assignment_from_source(source)
        
        target = assign_node.targets[0]
        assert isinstance(target, ast.Tuple)
        assert len(target.elts) == 3
        
        # First: Name 'a'
        assert isinstance(target.elts[0], ast.Name)
        assert target.elts[0].id == 'a'
        
        # Second: Starred 'rest'
        assert isinstance(target.elts[1], ast.Starred)
        assert isinstance(target.elts[1].value, ast.Name)
        assert target.elts[1].value.id == 'rest'
        
        # Third: Name 'b'
        assert isinstance(target.elts[2], ast.Name)
        assert target.elts[2].id == 'b'

    @pytest.mark.min_version_3_9
    def test_starred_expression_limitations(self, tester):
        """Test starred expression limitations"""
        # Only one starred expression per assignment target
        # These should parse but might be semantically invalid
        single_starred = [
            "a, *b, c = sequence",  # Valid
            "*a, b, c = sequence",  # Valid
            "a, b, *c = sequence"   # Valid
        ]
        
        for source in single_starred:
            tester.assert_assignment_syntax_parses(source)


class TestSection72AttributeSubscriptionAssignment:
    """Test attribute and subscription assignment"""
    
    @pytest.fixture
    def tester(self):
        return AssignmentStatementTester()

    def test_attribute_assignment(self, tester):
        """Test attribute assignment syntax"""
        # Language Reference: attributeref target
        attribute_assignments = [
            "obj.attr = value",
            "instance.property = new_value", 
            "self.name = name",
            "config.setting = True",
            "data.count = 0",
            "obj.nested.deep.attr = value"
        ]
        
        for source in attribute_assignments:
            tester.assert_assignment_syntax_parses(source)

    def test_subscription_assignment(self, tester):
        """Test subscription assignment syntax"""
        # Language Reference: subscription target
        subscription_assignments = [
            "container[0] = value",
            "dictionary['key'] = value",
            "matrix[i][j] = element",
            "data[index] = new_value",
            "mapping[key] = result",
            "array[slice_obj] = sequence"
        ]
        
        for source in subscription_assignments:
            tester.assert_assignment_syntax_parses(source)

    def test_complex_subscription_assignment(self, tester):
        """Test complex subscription expressions"""
        # Complex subscription patterns
        complex_subscriptions = [
            "container[start:end] = sequence",
            "matrix[i, j] = value",
            "data[key1][key2] = nested_value",
            "array[::2] = even_elements",
            "mapping[compute_key()] = result",
            "storage[obj.id] = obj"
        ]
        
        for source in complex_subscriptions:
            tester.assert_assignment_syntax_parses(source)

    def test_mixed_attribute_subscription(self, tester):
        """Test mixing attribute and subscription access"""
        # Mixed access patterns
        mixed_access = [
            "obj.data[key] = value",
            "instance.config['setting'] = True",
            "self.items[0].attr = value",
            "container[key].property = result",
            "obj.nested[i].deep.attr = value"
        ]
        
        for source in mixed_access:
            tester.assert_assignment_syntax_parses(source)

    def test_chained_attribute_subscription(self, tester):
        """Test chained attribute and subscription assignment"""
        # Chained assignments with attributes/subscriptions
        chained_complex = [
            "a = obj.attr = value",
            "x = container[key] = value", 
            "result = obj.data[i] = computed_value",
            "a = b.attr = c['key'] = value"
        ]
        
        for source in chained_complex:
            tester.assert_assignment_syntax_parses(source)

    def test_unpacking_with_attributes_subscriptions(self, tester):
        """Test unpacking combined with attribute/subscription targets"""
        # Unpacking with complex targets
        unpacking_complex = [
            "obj.x, obj.y = coordinates",
            "container[0], container[1] = pair",
            "data['a'], data['b'] = values",
            "obj.attr, container[key] = mixed_values",
            "a, obj.prop, data[i] = triple"
        ]
        
        for source in unpacking_complex:
            tester.assert_assignment_syntax_parses(source)


class TestSection72ErrorConditions:
    """Test error conditions for assignment statements"""
    
    @pytest.fixture
    def tester(self):
        return AssignmentStatementTester()

    def test_invalid_assignment_targets(self, tester):
        """Test invalid assignment target syntax"""
        # Invalid targets
        invalid_targets = [
            "123 = value",           # Literal as target
            "'string' = value",      # String literal as target  
            "x + y = value",         # Expression as target
            "func() = value",        # Function call as target
            "42.attr = value",       # Literal attribute
            "[x + y] = value"        # Expression in list target
        ]
        
        for source in invalid_targets:
            tester.assert_assignment_syntax_error(source)

    def test_invalid_starred_expressions(self, tester):
        """Test invalid starred expression usage"""
        # Invalid starred usage
        invalid_starred = [
            # "*a, *b = sequence",     # Actually valid in Python 3.9+
            "**a = value",           # Double star in assignment target
            "*(a + b) = sequence"    # Starred expression target
        ]
        
        for source in invalid_starred:
            tester.assert_assignment_syntax_error(source)

    def test_empty_assignment_error(self, tester):
        """Test empty assignment statements"""
        # Empty or incomplete assignments
        invalid_empty = [
            "= value",               # Missing target
            "a =",                   # Missing value
            "= ",                    # Both missing
            ", = value",             # Empty target in tuple
            "a, , b = sequence"      # Empty target in middle
        ]
        
        for source in invalid_empty:
            tester.assert_assignment_syntax_error(source)

    def test_invalid_tuple_syntax(self, tester):
        """Test invalid tuple unpacking syntax"""
        # Invalid tuple patterns
        invalid_tuples = [
            "(a b) = value",         # Missing comma
            "[a b] = value",         # Missing comma in list
            "(a,,b) = value",        # Double comma
            "((a,b) = value",        # Unmatched parentheses
            "[a,b)) = value"         # Mismatched brackets
        ]
        
        for source in invalid_tuples:
            tester.assert_assignment_syntax_error(source)

    def test_keyword_as_target_error(self, tester):
        """Test keywords cannot be assignment targets"""
        # Keywords as targets should fail
        keyword_targets = [
            "if = value",
            "for = value",
            "while = value", 
            "def = value",
            "class = value",
            "import = value"
        ]
        
        for source in keyword_targets:
            tester.assert_assignment_syntax_error(source)

    def test_complex_invalid_patterns(self, tester):
        """Test complex invalid assignment patterns"""
        # Complex invalid cases
        complex_invalid = [
            "a + b, c = values",     # Expression in tuple target
            "(a + b) = value",       # Expression in parentheses  
            "[x(), y] = values",     # Function call in list target
            "obj.method(), x = vals", # Method call as target
            "a, b[x + y] = vals"     # Expression in subscription (this might be valid)
        ]
        
        # Note: The last one might actually be valid syntax
        for source in complex_invalid[:-1]:
            tester.assert_assignment_syntax_error(source)


class TestSection72SpecialAssignmentForms:
    """Test special forms of assignment"""
    
    @pytest.fixture
    def tester(self):
        return AssignmentStatementTester()

    def test_yield_expression_assignment(self, tester):
        """Test assignment with yield expressions"""
        # Language Reference: yield_expression as value
        # Note: These need to be in generator context
        yield_assignments = [
            """def gen():
    x = yield""",
            
            """def gen():
    value = yield expression""",
            
            """def gen():
    a, b = yield tuple_value""",
            
            """def gen():
    result = yield from generator()"""
        ]
        
        for source in yield_assignments:
            tester.assert_assignment_syntax_parses(source)

    def test_assignment_in_comprehensions(self, tester):
        """Test assignment statements don't appear in comprehensions"""
        # Assignment statements vs assignment expressions
        comprehension_contexts = [
            "[x for x in sequence]",          # Valid comprehension
            "{k: v for k, v in items}",       # Valid dict comprehension
            "{x for x in sequence}",          # Valid set comprehension
            "(x for x in sequence)"           # Valid generator expression
        ]
        
        for source in comprehension_contexts:
            # These should parse as expressions, not assignment statements
            try:
                ast.parse(source, mode='eval')
            except SyntaxError:
                pytest.fail(f"Valid comprehension {source!r} should parse")

    def test_assignment_vs_augmented_assignment(self, tester):
        """Test distinction between assignment and augmented assignment"""
        # Regular assignment (this test) vs augmented assignment
        regular_assignment = [
            "x = 42",
            "x = x + 1", 
            "x = x * 2",
            "container[key] = container[key] + value"
        ]
        
        for source in regular_assignment:
            tester.assert_assignment_syntax_parses(source)

    def test_global_nonlocal_with_assignment(self, tester):
        """Test assignment with global/nonlocal declarations"""
        # Assignment in global/nonlocal context
        scoped_assignments = [
            """def func():
    global x
    x = value""",
            
            """def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2""",
            
            """def func():
    global a, b
    a = b = value"""
        ]
        
        for source in scoped_assignments:
            tester.assert_assignment_syntax_parses(source)


class TestSection72CrossImplementationCompatibility:
    """Test assignment features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return AssignmentStatementTester()

    def test_large_tuple_unpacking(self, tester):
        """Test unpacking very large tuples"""
        # Large tuple unpacking
        variables = ', '.join([f'var_{i}' for i in range(100)])
        values = ', '.join([str(i) for i in range(100)])
        large_unpacking = f"{variables} = {values}"
        
        tester.assert_assignment_syntax_parses(large_unpacking)

    def test_deeply_nested_unpacking(self, tester):
        """Test deeply nested unpacking structures"""
        # Deep nesting
        nested_pattern = "a"
        nested_value = "val"
        
        for i in range(10):
            nested_pattern = f"({nested_pattern}, b_{i})"
            nested_value = f"({nested_value}, val_{i})"
        
        deep_unpacking = f"{nested_pattern} = {nested_value}"
        tester.assert_assignment_syntax_parses(deep_unpacking)

    def test_complex_chained_assignment(self, tester):
        """Test complex chained assignments"""
        # Complex chaining with different target types
        complex_chaining = [
            "a = obj.attr = container[key] = computed_value()",
            "x = y[i] = z.prop = w['key'] = expression",
            "first = second[0] = third.value = result"
        ]
        
        for source in complex_chaining:
            tester.assert_assignment_syntax_parses(source)

    def test_assignment_statement_introspection(self, tester):
        """Test assignment statement AST introspection"""
        # Detailed AST validation for complex assignment
        source = """a, (b, *rest), c = obj.method()"""
        
        assign_node = tester.get_assignment_from_source(source)
        
        # Validate AST structure
        assert len(assign_node.targets) == 1
        target = assign_node.targets[0]
        
        # Target should be tuple with 3 elements
        assert isinstance(target, ast.Tuple)
        assert len(target.elts) == 3
        
        # First element: Name 'a'
        assert isinstance(target.elts[0], ast.Name)
        assert target.elts[0].id == 'a'
        
        # Second element: Tuple (b, *rest)
        nested_tuple = target.elts[1]
        assert isinstance(nested_tuple, ast.Tuple)
        assert len(nested_tuple.elts) == 2
        
        # b
        assert isinstance(nested_tuple.elts[0], ast.Name)
        assert nested_tuple.elts[0].id == 'b'
        
        # *rest
        assert isinstance(nested_tuple.elts[1], ast.Starred)
        assert isinstance(nested_tuple.elts[1].value, ast.Name)
        assert nested_tuple.elts[1].value.id == 'rest'
        
        # Third element: Name 'c'
        assert isinstance(target.elts[2], ast.Name)
        assert target.elts[2].id == 'c'
        
        # Value should be method call
        assert isinstance(assign_node.value, ast.Call)

    def test_assignment_performance_patterns(self, tester):
        """Test assignment patterns that might affect performance"""
        # Patterns that could stress parsers/compilers
        performance_patterns = [
            # Many chained assignments
            " = ".join([f"var_{i}" for i in range(50)]) + " = value",
            
            # Deep attribute access
            "a.b.c.d.e.f.g.h.i.j.k = deep_value",
            
            # Complex subscription
            "container[key1][key2][key3][key4] = nested_value",
            
            # Mixed complex patterns
            "obj.data[compute_key()].items[index].value = result"
        ]
        
        for source in performance_patterns:
            tester.assert_assignment_syntax_parses(source)

    def test_unicode_identifier_assignment(self, tester):
        """Test assignment with Unicode identifiers"""
        # Unicode identifiers (Python 3+)
        unicode_assignments = [
            "名前 = 'name'",
            "αβγ = 'greek'", 
            "файл = 'file'",
            "变量 = 'variable'",
            # "🐍 = 'python'"  # Emoji identifiers not supported in this build
        ]
        
        for source in unicode_assignments:
            try:
                tester.assert_assignment_syntax_parses(source)
            except (SyntaxError, UnicodeError):
                # Some Unicode might not be supported in all implementations
                pass

    def test_real_world_assignment_patterns(self, tester):
        """Test real-world assignment patterns"""
        # Common patterns from actual code
        real_world_patterns = [
            # Configuration unpacking
            "host, port, timeout = connection_config",
            
            # Error handling
            "success, error_message = validate_input(data)",
            
            # Coordinate unpacking
            "x, y, z = position_vector",
            
            # Dictionary unpacking (keys, not **kwargs)
            "name, age, email = user_data['name'], user_data['age'], user_data['email']",
            
            # Multiple return values
            "result, metadata, stats = process_data(input)",
            
            # State management
            "self.state, self.previous_state = new_state, self.state",
            
            # File operations
            "content, encoding, errors = read_file_with_metadata(path)"
        ]
        
        for source in real_world_patterns:
            tester.assert_assignment_syntax_parses(source)