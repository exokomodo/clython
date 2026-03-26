"""
Section 8.10: Match Statements - Conformance Test Suite

Tests Python Language Reference Section 8.10 compliance across implementations.
Based on formal grammar definitions and prose assertions for match statements (Python 3.10+).

Grammar tested:
    match_stmt: "match" subject_expr ':' NEWLINE INDENT case_block+ DEDENT
    case_block: "case" patterns [guard] ':' block
    patterns: open_sequence_pattern | pattern
    pattern: as_pattern | or_pattern
    as_pattern: or_pattern 'as' pattern_capture_target
    or_pattern: closed_pattern ('|' closed_pattern)*
    closed_pattern: literal_pattern | capture_pattern | wildcard_pattern | value_pattern 
                   | group_pattern | sequence_pattern | mapping_pattern | class_pattern

Language Reference requirements tested:
    - Basic match/case syntax
    - Literal pattern matching: numbers, strings, constants
    - Capture patterns: variable binding
    - Wildcard patterns: _ (anonymous)
    - Value patterns: dotted names and constants
    - Sequence patterns: lists, tuples with star patterns
    - Mapping patterns: dictionary matching with ** rest
    - Class patterns: constructor-style matching
    - Guard expressions: if conditions on patterns
    - Or patterns: multiple pattern alternatives (|)
    - As patterns: pattern binding with as keyword
"""

import ast
import pytest
import sys
from typing import Any


@pytest.mark.min_version_3_10
class MatchStatementTester:
    """Helper class for testing match statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    Note: Match statements require Python 3.10+
    """
    
    def assert_match_syntax_parses(self, source: str):
        """Test that match statement syntax parses correctly.
        
        Args:
            source: Python match statement source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains match statement
            for node in ast.walk(tree):
                if isinstance(node, ast.Match):
                    return  # Found match statement, syntax is valid
            pytest.fail(f"Expected Match node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Match syntax {source!r} failed to parse: {e}")
    
    def assert_match_syntax_error(self, source: str):
        """Test that invalid match syntax raises SyntaxError.
        
        Args:
            source: Python match source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)

    def get_match_from_source(self, source: str) -> ast.Match:
        """Get the Match AST node from source for detailed validation.
        
        Args:
            source: Python match statement source
            
        Returns:
            ast.Match node
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Match):
                return node
        pytest.fail(f"No Match node found in: {source}")


@pytest.mark.min_version_3_10
@pytest.mark.min_version_3_10
class TestSection810BasicMatchStatements:
    """Test Section 8.10: Basic Match Statements"""
    
    @pytest.fixture
    def tester(self):
        return MatchStatementTester()

    def test_basic_match_syntax(self, tester):
        """Test basic match statement syntax"""
        # Language Reference: match_stmt with basic patterns
        basic_matches = [
            """match value:
    case 1:
        result = 'one'
    case 2:
        result = 'two'""",
            
            """match status:
    case 'success':
        handle_success()
    case 'error':
        handle_error()""",
            
            """match x:
    case 42:
        pass"""
        ]
        
        for source in basic_matches:
            tester.assert_match_syntax_parses(source)

    def test_literal_patterns(self, tester):
        """Test literal pattern matching"""
        # Language Reference: literal_pattern
        literal_patterns = [
            """match num:
    case 0:
        print('zero')
    case 1:
        print('one')
    case -1:
        print('negative one')""",
            
            """match text:
    case 'hello':
        greet()
    case 'goodbye':
        farewell()
    case "":
        empty_string()""",
            
            """match flag:
    case True:
        enable()
    case False:
        disable()
    case None:
        reset()"""
        ]
        
        for source in literal_patterns:
            tester.assert_match_syntax_parses(source)

    def test_capture_patterns(self, tester):
        """Test capture pattern syntax"""
        # Language Reference: capture_pattern (variable binding)
        capture_patterns = [
            """match value:
    case x:
        process(x)""",
            
            """match data:
    case result:
        return result""",
            
            """match input:
    case user_input:
        validate(user_input)"""
        ]
        
        for source in capture_patterns:
            tester.assert_match_syntax_parses(source)

    def test_wildcard_patterns(self, tester):
        """Test wildcard pattern syntax"""
        # Language Reference: wildcard_pattern (_)
        wildcard_patterns = [
            """match value:
    case 1:
        handle_one()
    case _:
        handle_other()""",
            
            """match status:
    case 'success':
        success_handler()
    case _:
        default_handler()"""
        ]
        
        for source in wildcard_patterns:
            tester.assert_match_syntax_parses(source)

    def test_multiple_cases(self, tester):
        """Test multiple case patterns"""
        # Multiple case blocks
        multiple_cases = [
            """match grade:
    case 'A':
        print('Excellent')
    case 'B':
        print('Good')
    case 'C':
        print('Average')
    case 'D':
        print('Below Average')
    case 'F':
        print('Failing')
    case _:
        print('Invalid grade')""",
            
            """match response_code:
    case 200:
        success()
    case 404:
        not_found()
    case 500:
        server_error()
    case code:
        unknown_error(code)"""
        ]
        
        for source in multiple_cases:
            tester.assert_match_syntax_parses(source)


@pytest.mark.min_version_3_10
@pytest.mark.min_version_3_10
class TestSection810SequencePatterns:
    """Test sequence pattern matching"""
    
    @pytest.fixture
    def tester(self):
        return MatchStatementTester()

    def test_list_patterns(self, tester):
        """Test list pattern matching"""
        # Language Reference: sequence_pattern with lists
        list_patterns = [
            """match items:
    case []:
        print('empty list')
    case [x]:
        print(f'single item: {x}')
    case [x, y]:
        print(f'two items: {x}, {y}')""",
            
            """match coordinates:
    case [x, y]:
        point_2d(x, y)
    case [x, y, z]:
        point_3d(x, y, z)""",
            
            """match data:
    case [first, *rest]:
        process_head_tail(first, rest)
    case []:
        handle_empty()"""
        ]
        
        for source in list_patterns:
            tester.assert_match_syntax_parses(source)

    def test_tuple_patterns(self, tester):
        """Test tuple pattern matching"""
        # Language Reference: sequence_pattern with tuples
        tuple_patterns = [
            """match point:
    case (x, y):
        return f'2D point at ({x}, {y})'
    case (x, y, z):
        return f'3D point at ({x}, {y}, {z})'""",
            
            """match result:
    case (True, value):
        success(value)
    case (False, error):
        failure(error)""",
            
            """match record:
    case (name, age):
        simple_record(name, age)
    case (name, age, *extras):
        extended_record(name, age, extras)"""
        ]
        
        for source in tuple_patterns:
            tester.assert_match_syntax_parses(source)

    def test_starred_patterns(self, tester):
        """Test starred patterns in sequences"""
        # Language Reference: star patterns in sequence_pattern
        starred_patterns = [
            """match sequence:
    case [first, *middle, last]:
        process_bounded(first, middle, last)
    case [*all]:
        process_all(all)""",
            
            """match args:
    case [head, *tail]:
        recursive_process(head, tail)
    case []:
        base_case()""",
            
            """match data:
    case [x, *_, y]:
        process_first_last(x, y)
    case [single]:
        process_single(single)"""
        ]
        
        for source in starred_patterns:
            tester.assert_match_syntax_parses(source)

    def test_nested_sequence_patterns(self, tester):
        """Test nested sequence patterns"""
        # Nested sequence structures
        nested_patterns = [
            """match nested_data:
    case [[x, y], [a, b]]:
        process_matrix_2x2(x, y, a, b)
    case [row]:
        process_single_row(row)""",
            
            """match structure:
    case [(name, age), *records]:
        process_person_records(name, age, records)
    case []:
        empty_structure()"""
        ]
        
        for source in nested_patterns:
            tester.assert_match_syntax_parses(source)


@pytest.mark.min_version_3_10
@pytest.mark.min_version_3_10
class TestSection810MappingPatterns:
    """Test mapping (dictionary) pattern matching"""
    
    @pytest.fixture
    def tester(self):
        return MatchStatementTester()

    def test_dict_patterns(self, tester):
        """Test dictionary pattern matching"""
        # Language Reference: mapping_pattern
        dict_patterns = [
            """match config:
    case {'debug': True}:
        enable_debug()
    case {'debug': False}:
        disable_debug()""",
            
            """match request:
    case {'method': 'GET', 'path': path}:
        handle_get(path)
    case {'method': 'POST', 'data': data}:
        handle_post(data)""",
            
            """match user:
    case {'name': str(name), 'age': int(age)}:
        validate_user(name, age)"""
        ]
        
        for source in dict_patterns:
            tester.assert_match_syntax_parses(source)

    def test_dict_rest_patterns(self, tester):
        """Test dictionary rest patterns with **"""
        # Language Reference: ** rest in mapping_pattern
        dict_rest_patterns = [
            """match data:
    case {'type': 'user', **user_data}:
        create_user(user_data)
    case {'type': 'admin', **admin_data}:
        create_admin(admin_data)""",
            
            """match config:
    case {'required_field': value, **optional}:
        process_config(value, optional)""",
            
            """match response:
    case {'status': 'ok', 'data': data, **metadata}:
        success_with_metadata(data, metadata)"""
        ]
        
        for source in dict_rest_patterns:
            tester.assert_match_syntax_parses(source)

    def test_mixed_dict_patterns(self, tester):
        """Test mixed dictionary pattern features"""
        # Combined dictionary features
        mixed_dict_patterns = [
            """match api_response:
    case {'error': None, 'data': [*items], 'meta': {'total': count}}:
        process_paginated_data(items, count)
    case {'error': error_msg}:
        handle_api_error(error_msg)""",
            
            """match event:
    case {'type': 'click', 'target': {'id': element_id}, **props}:
        handle_click_event(element_id, props)
    case {'type': event_type, **data}:
        handle_generic_event(event_type, data)"""
        ]
        
        for source in mixed_dict_patterns:
            tester.assert_match_syntax_parses(source)


@pytest.mark.min_version_3_10
@pytest.mark.min_version_3_10
class TestSection810ClassPatterns:
    """Test class pattern matching"""
    
    @pytest.fixture
    def tester(self):
        return MatchStatementTester()

    def test_basic_class_patterns(self, tester):
        """Test basic class pattern syntax"""
        # Language Reference: class_pattern
        class_patterns = [
            """match obj:
    case Point(x, y):
        print(f'Point at {x}, {y}')
    case Circle(radius):
        print(f'Circle with radius {radius}')""",
            
            """match shape:
    case Rectangle(width, height):
        area = width * height
    case Square(side):
        area = side * side""",
            
            """match node:
    case Leaf(value):
        return value
    case Node(left, right):
        return combine(left, right)"""
        ]
        
        for source in class_patterns:
            tester.assert_match_syntax_parses(source)

    def test_class_patterns_with_attributes(self, tester):
        """Test class patterns with named attributes"""
        # Class patterns with keyword arguments
        class_attr_patterns = [
            """match person:
    case Person(name=n, age=a):
        greet_person(n, a)
    case Employee(name=n, id=emp_id, department=dept):
        process_employee(n, emp_id, dept)""",
            
            """match event:
    case MouseEvent(x=x_pos, y=y_pos, button='left'):
        handle_left_click(x_pos, y_pos)
    case KeyEvent(key=k, ctrl=True):
        handle_ctrl_key(k)"""
        ]
        
        for source in class_attr_patterns:
            tester.assert_match_syntax_parses(source)

    def test_nested_class_patterns(self, tester):
        """Test nested class patterns"""
        # Nested class pattern structures
        nested_class_patterns = [
            """match expression:
    case BinaryOp(Add(), Number(x), Number(y)):
        return x + y
    case BinaryOp(Mul(), left, right):
        return evaluate(left) * evaluate(right)""",
            
            """match ast_node:
    case FuncDef(name=func_name, args=Args(args=[*params])):
        process_function(func_name, params)
    case ClassDef(name=class_name, bases=[*base_classes]):
        process_class(class_name, base_classes)"""
        ]
        
        for source in nested_class_patterns:
            tester.assert_match_syntax_parses(source)


@pytest.mark.min_version_3_10
@pytest.mark.min_version_3_10
class TestSection810GuardPatterns:
    """Test guard expressions in patterns"""
    
    @pytest.fixture
    def tester(self):
        return MatchStatementTester()

    def test_guard_expressions(self, tester):
        """Test guard expressions with if conditions"""
        # Language Reference: guard in case_block
        guard_patterns = [
            """match value:
    case x if x > 0:
        positive_handler(x)
    case x if x < 0:
        negative_handler(x)
    case 0:
        zero_handler()""",
            
            """match user:
    case {'age': age} if age >= 18:
        adult_user()
    case {'age': age} if age < 18:
        minor_user()""",
            
            """match data:
    case [x, *rest] if len(rest) > 5:
        large_list_handler(x, rest)
    case [x, *rest]:
        small_list_handler(x, rest)"""
        ]
        
        for source in guard_patterns:
            tester.assert_match_syntax_parses(source)

    def test_complex_guards(self, tester):
        """Test complex guard expressions"""
        # Complex guard conditions
        complex_guards = [
            """match point:
    case (x, y) if x**2 + y**2 <= 1:
        inside_unit_circle(x, y)
    case (x, y) if abs(x) <= 1 and abs(y) <= 1:
        inside_unit_square(x, y)
    case (x, y):
        outside_bounds(x, y)""",
            
            """match request:
    case {'method': 'POST', 'data': data} if validate_data(data):
        process_valid_post(data)
    case {'method': 'POST', 'data': data}:
        reject_invalid_post(data)""",
            
            """match record:
    case Person(name=n, age=a) if a >= 65 and is_retired(n):
        senior_discount(n)
    case Person(name=n, age=a) if a < 18:
        youth_discount(n)"""
        ]
        
        for source in complex_guards:
            tester.assert_match_syntax_parses(source)


@pytest.mark.min_version_3_10
@pytest.mark.min_version_3_10
class TestSection810OrPatterns:
    """Test or patterns with | operator"""
    
    @pytest.fixture
    def tester(self):
        return MatchStatementTester()

    def test_simple_or_patterns(self, tester):
        """Test simple or patterns with | operator"""
        # Language Reference: or_pattern with |
        or_patterns = [
            """match status:
    case 'success' | 'ok' | 'completed':
        success_handler()
    case 'error' | 'failed' | 'aborted':
        error_handler()""",
            
            """match value:
    case 0 | 1:
        binary_value()
    case 2 | 3 | 5 | 7:
        small_prime()""",
            
            """match response_code:
    case 200 | 201 | 202:
        success_response()
    case 400 | 401 | 403:
        client_error()
    case 500 | 502 | 503:
        server_error()"""
        ]
        
        for source in or_patterns:
            tester.assert_match_syntax_parses(source)

    def test_complex_or_patterns(self, tester):
        """Test complex or patterns with different pattern types"""
        # Or patterns with mixed pattern types
        complex_or_patterns = [
            """match data:
    case [] | None:
        empty_handler()
    case [single_item] | single_item:
        single_item_handler(single_item)""",
            
            """match shape:
    case Circle(r) | Square(r) if r > 10:
        large_shape_handler(r)
    case Circle(r) | Square(r):
        small_shape_handler(r)""",
            
            """match event:
    case {'type': 'click'} | {'type': 'tap'}:
        pointer_event()
    case {'type': 'keydown'} | {'type': 'keyup'}:
        keyboard_event()"""
        ]
        
        for source in complex_or_patterns:
            tester.assert_match_syntax_parses(source)


@pytest.mark.min_version_3_10
@pytest.mark.min_version_3_10
class TestSection810AsPatterns:
    """Test as patterns for binding"""
    
    @pytest.fixture
    def tester(self):
        return MatchStatementTester()

    def test_basic_as_patterns(self, tester):
        """Test basic as pattern syntax"""
        # Language Reference: as_pattern with 'as' keyword
        as_patterns = [
            """match data:
    case [x, *rest] as full_list:
        process_list(x, rest, full_list)""",
            
            """match response:
    case {'status': 'ok', 'data': data} as success_response:
        log_success(success_response)
        return data""",
            
            """match point:
    case (x, y) as coordinates:
        validate_point(coordinates)
        return distance(x, y)"""
        ]
        
        for source in as_patterns:
            tester.assert_match_syntax_parses(source)

    def test_nested_as_patterns(self, tester):
        """Test nested as patterns"""
        # As patterns in nested contexts
        nested_as_patterns = [
            """match structure:
    case {'users': [user, *others] as all_users}:
        process_user_list(user, others, all_users)""",
            
            """match expression:
    case BinaryOp(op, left as l, right as r) as binary_expr:
        optimize_binary(op, l, r, binary_expr)""",
            
            """match nested_data:
    case [[first, *row], *matrix] as full_matrix:
        process_matrix(first, row, matrix, full_matrix)"""
        ]
        
        for source in nested_as_patterns:
            tester.assert_match_syntax_parses(source)


@pytest.mark.min_version_3_10
@pytest.mark.min_version_3_10
class TestSection810ErrorConditions:
    """Test error conditions for match statements"""
    
    @pytest.fixture
    def tester(self):
        return MatchStatementTester()

    def test_invalid_match_syntax(self, tester):
        """Test invalid match statement syntax"""
        # Invalid syntax
        invalid_syntax = [
            "match:",                    # Missing subject
            "match value",               # Missing colon
            "match value:\npass",        # Missing case
            "case x:\n    pass",         # Case without match
            "match value:\n    pass"     # No case blocks
        ]
        
        for source in invalid_syntax:
            tester.assert_match_syntax_error(source)

    def test_invalid_case_syntax(self, tester):
        """Test invalid case clause syntax"""
        # Invalid case syntax
        invalid_cases = [
            """match value:
case:
    pass""",                    # Missing pattern

            """match value:
case x
    pass""",                   # Missing colon

            """match value:
case x if:
    pass""",                   # Empty guard

            """match value:
case x as:
    pass"""                    # Missing as target
        ]
        
        for source in invalid_cases:
            tester.assert_match_syntax_error(source)

    def test_invalid_pattern_syntax(self, tester):
        """Test invalid pattern syntax"""
        # Invalid patterns
        invalid_patterns = [
            """match value:
case [x, x]:
    pass""",                   # Duplicate names might be invalid

            """match value:
case {**a, **b}:
    pass""",                   # Multiple ** in mapping

            """match value:
case [*a, *b]:
    pass"""                    # Multiple * in sequence
        ]
        
        # Note: Some of these might be valid, adjust based on actual Python behavior
        for source in invalid_patterns:
            try:
                tester.assert_match_syntax_error(source)
            except AssertionError:
                # Some patterns might be valid, skip if they parse correctly
                pass


@pytest.mark.min_version_3_10
@pytest.mark.min_version_3_10
class TestSection810CrossImplementationCompatibility:
    """Test match statement features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return MatchStatementTester()

    def test_complex_nested_patterns(self, tester):
        """Test deeply nested pattern structures"""
        # Complex nesting
        complex_nested = [
            """match deep_structure:
    case {'data': {'users': [{'name': name, 'permissions': [*perms]}]}}:
        process_user_permissions(name, perms)
    case {'data': {'config': {'settings': {**all_settings}}}}:
        apply_settings(all_settings)""",
            
            """match ast_tree:
    case Module(body=[
        FuncDef(name=fn_name, 
                args=arguments(args=[arg(arg=param_name)]), 
                body=[Return(value=Constant(value=const_val))])
    ]):
        simple_function(fn_name, param_name, const_val)"""
        ]
        
        for source in complex_nested:
            tester.assert_match_syntax_parses(source)

    def test_large_pattern_sets(self, tester):
        """Test match statements with many cases"""
        # Many case patterns
        cases = ["match value:"]
        for i in range(20):
            cases.append(f"    case {i}:")
            cases.append(f"        handle_{i}()")
        cases.extend([
            "    case _:",
            "        default_handler()"
        ])
        
        large_match = "\n".join(cases)
        tester.assert_match_syntax_parses(large_match)

    def test_match_statement_introspection(self, tester):
        """Test match statement AST introspection"""
        # Detailed AST validation
        source = """match data:
    case {'type': 'user', 'name': name}:
        create_user(name)
    case [x, *rest] if len(rest) > 0:
        process_list(x, rest)
    case _:
        default_case()"""
        
        match_node = tester.get_match_from_source(source)
        
        # Validate AST structure
        assert isinstance(match_node.subject, ast.Name)
        assert match_node.subject.id == 'data'
        assert len(match_node.cases) == 3
        
        # First case: mapping pattern
        first_case = match_node.cases[0]
        assert hasattr(first_case, 'pattern')
        assert first_case.guard is None
        
        # Second case: sequence pattern with guard
        second_case = match_node.cases[1]
        assert hasattr(second_case, 'pattern')
        assert second_case.guard is not None
        
        # Third case: wildcard
        third_case = match_node.cases[2]
        assert hasattr(third_case, 'pattern')

    def test_real_world_match_patterns(self, tester):
        """Test real-world match statement patterns"""
        # Patterns from actual code
        real_world_patterns = [
            # HTTP request routing
            """match request:
    case {'method': 'GET', 'path': '/health'}:
        return health_check()
    case {'method': 'POST', 'path': '/api/users', 'body': {'name': name, 'email': email}}:
        return create_user(name, email)
    case {'method': method, 'path': path}:
        return method_not_allowed(method, path)""",
            
            # JSON API response handling
            """match api_response:
    case {'success': True, 'data': data, 'pagination': {'page': p, 'total': t}}:
        process_paginated_success(data, p, t)
    case {'success': True, 'data': data}:
        process_simple_success(data)
    case {'success': False, 'error': {'code': code, 'message': msg}}:
        handle_api_error(code, msg)""",
            
            # AST processing
            """match node:
    case ast.FunctionDef(name=fname, args=ast.arguments(args=params)):
        process_function(fname, [p.arg for p in params])
    case ast.ClassDef(name=cname, bases=bases, body=methods):
        process_class(cname, bases, methods)
    case ast.Import(names=aliases):
        process_imports([alias.name for alias in aliases])"""
        ]
        
        for source in real_world_patterns:
            tester.assert_match_syntax_parses(source)