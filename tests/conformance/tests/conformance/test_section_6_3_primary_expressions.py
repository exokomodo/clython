"""
Section 6.3: Primary Expressions - Conformance Test Suite

Tests Python Language Reference Section 6.3 compliance across implementations.
Based on formal specifications for primary expression syntax and precedence.

Language Reference requirements tested:
    - Attribute references: primary.identifier
    - Subscriptions: primary[expression_list]
    - Slicing: primary[slice_list] with start:stop:step
    - Function calls: primary(argument_list)
    - Method calls: primary.identifier(argument_list)
    - Call expressions: complex argument patterns
    - Chained expressions: obj.attr[key](args)
    - Expression precedence and associativity
    - Complex primary expression combinations
"""

import ast
import pytest
import sys
from typing import Any


class PrimaryExpressionTester:
    """Helper class for testing primary expression conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_primary_expr_syntax_parses(self, source: str):
        """Test that primary expression syntax parses correctly.
        
        Args:
            source: Python primary expression source code
        """
        try:
            # Parse as expression or statement depending on context
            if not source.strip().endswith(':'):
                tree = ast.parse(source, mode='eval')
            else:
                tree = ast.parse(source, mode='exec')
            return tree
        except SyntaxError as e:
            pytest.fail(f"Primary expression syntax {source!r} failed to parse: {e}")
    
    def assert_primary_expr_syntax_error(self, source: str):
        """Test that invalid primary expression syntax raises SyntaxError.
        
        Args:
            source: Python primary expression source that should be invalid
        """
        with pytest.raises(SyntaxError):
            try:
                ast.parse(source, mode='eval')
            except:
                ast.parse(source, mode='exec')

    def get_expression_nodes_of_type(self, source: str, node_type) -> list:
        """Get nodes of specific type from primary expression.
        
        Args:
            source: Python primary expression source
            node_type: AST node type to search for
            
        Returns:
            List of matching AST nodes
        """
        try:
            tree = ast.parse(source, mode='eval')
        except:
            tree = ast.parse(source, mode='exec')
        
        nodes = []
        for node in ast.walk(tree):
            if isinstance(node, node_type):
                nodes.append(node)
        return nodes

    def contains_node_type(self, source: str, node_type) -> bool:
        """Check if expression contains specific AST node type.
        
        Args:
            source: Python expression source
            node_type: AST node type to check for
            
        Returns:
            True if node type found, False otherwise
        """
        nodes = self.get_expression_nodes_of_type(source, node_type)
        return len(nodes) > 0


class TestSection63AttributeReferences:
    """Test Section 6.3: Attribute Reference Expressions"""
    
    @pytest.fixture
    def tester(self):
        return PrimaryExpressionTester()

    def test_simple_attribute_references(self, tester):
        """Test simple attribute reference syntax"""
        # Language Reference: primary.identifier
        simple_attribute_refs = [
            "obj.attr",
            "self.value",
            "instance.method",
            "module.function",
            "class_name.class_attr",
            "container.items",
            "parser.tokens",
            "config.settings"
        ]
        
        for expr in simple_attribute_refs:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain Attribute node
            assert tester.contains_node_type(expr, ast.Attribute)

    def test_chained_attribute_references(self, tester):
        """Test chained attribute references"""
        # Chained attribute access patterns
        chained_attribute_refs = [
            "obj.attr.subattr",
            "self.config.database.host",
            "instance.handler.logger.level",
            "app.services.auth.provider.settings",
            "data.results.metadata.timestamp.value"
        ]
        
        for expr in chained_attribute_refs:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain multiple Attribute nodes
            attr_nodes = tester.get_expression_nodes_of_type(expr, ast.Attribute)
            assert len(attr_nodes) >= 2

    def test_attribute_with_function_calls(self, tester):
        """Test attribute references on function call results"""
        # Attribute access on call results
        call_attribute_refs = [
            "func().attr",
            "get_object().value",
            "factory().create().name",
            "parser.parse().tokens[0].type",
            "obj.method().result.data"
        ]
        
        for expr in call_attribute_refs:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain both Call and Attribute nodes
            assert tester.contains_node_type(expr, ast.Call)
            assert tester.contains_node_type(expr, ast.Attribute)

    def test_attribute_with_subscripts(self, tester):
        """Test attribute references with subscript operations"""
        # Mixed attribute and subscript access
        mixed_access_patterns = [
            "obj.items[0]",
            "self.data['key'].value",
            "instance.array[index].field",
            "config.sections[name].options['setting']",
            "results.data[0].metadata.tags[tag_name]"
        ]
        
        for expr in mixed_access_patterns:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain both Attribute and Subscript nodes
            assert tester.contains_node_type(expr, ast.Attribute)
            assert tester.contains_node_type(expr, ast.Subscript)

    def test_attribute_identifier_patterns(self, tester):
        """Test various attribute identifier patterns"""
        # Different identifier naming patterns
        identifier_patterns = [
            "obj.simple",
            "obj._private",
            "obj.__dunder__",
            "obj.CamelCase",
            "obj.snake_case",
            "obj.UPPER_CASE",
            "obj.mixed_CamelCase_123",
            "obj.with123numbers"
        ]
        
        for expr in identifier_patterns:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Attribute)


class TestSection63Subscriptions:
    """Test subscription expressions (indexing)"""
    
    @pytest.fixture
    def tester(self):
        return PrimaryExpressionTester()

    def test_simple_subscriptions(self, tester):
        """Test simple subscription syntax"""
        # Language Reference: primary[expression]
        simple_subscriptions = [
            "obj[0]",
            "array[index]",
            "dict[key]",
            "items[i]",
            "data['name']",
            'config["setting"]',
            "matrix[row]",
            "cache[cache_key]"
        ]
        
        for expr in simple_subscriptions:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Subscript)

    def test_multiple_subscriptions(self, tester):
        """Test multiple/chained subscriptions"""
        # Chained subscript operations
        chained_subscriptions = [
            "matrix[row][col]",
            "data[section][key]",
            "nested[a][b][c]",
            "arrays[0][1][2]",
            "tree['root']['children'][0]['value']"
        ]
        
        for expr in chained_subscriptions:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain multiple Subscript nodes
            subscript_nodes = tester.get_expression_nodes_of_type(expr, ast.Subscript)
            assert len(subscript_nodes) >= 2

    def test_subscription_with_expressions(self, tester):
        """Test subscriptions with complex index expressions"""
        # Complex index expressions
        complex_subscriptions = [
            "array[i + 1]",
            "data[len(items) - 1]",
            "matrix[row * cols + col]",
            "lookup[hash(key) % size]",
            "buffer[offset:offset + length]",
            "items[list(func(x) for x in range(10))][0]"  # Fixed: wrapped in list()
        ]
        
        for expr in complex_subscriptions:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Subscript)

    def test_subscription_key_types(self, tester):
        """Test subscriptions with different key types"""
        # Various key type patterns
        key_type_subscriptions = [
            "obj[42]",                    # Integer literal
            "obj['string']",              # String literal
            "obj[variable]",              # Variable name
            "obj[func()]",                # Function call
            "obj[obj.attr]",              # Attribute reference
            "obj[(1, 2, 3)]",             # Tuple literal
            "obj[[1, 2, 3]]",             # List literal
            "obj[{1, 2, 3}]",             # Set literal
        ]
        
        for expr in key_type_subscriptions:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Subscript)


class TestSection63Slicing:
    """Test slicing expressions"""
    
    @pytest.fixture
    def tester(self):
        return PrimaryExpressionTester()

    def test_simple_slices(self, tester):
        """Test simple slice syntax"""
        # Language Reference: primary[start:stop]
        simple_slices = [
            "seq[1:5]",
            "array[start:end]",
            "text[:10]",
            "data[5:]",
            "items[:]",
            "buffer[0:length]"
        ]
        
        for expr in simple_slices:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Subscript)
            # Should contain Slice node
            slice_nodes = tester.get_expression_nodes_of_type(expr, ast.Slice)
            assert len(slice_nodes) >= 1

    def test_extended_slices(self, tester):
        """Test extended slice syntax with step"""
        # Language Reference: primary[start:stop:step]
        extended_slices = [
            "seq[::2]",
            "array[1::2]",
            "text[::-1]",
            "data[::step]",
            "matrix[1:10:3]",
            "items[start:end:stride]"
        ]
        
        for expr in extended_slices:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Subscript)
            slice_nodes = tester.get_expression_nodes_of_type(expr, ast.Slice)
            assert len(slice_nodes) >= 1

    def test_negative_slices(self, tester):
        """Test slices with negative indices"""
        # Negative indexing patterns
        negative_slices = [
            "seq[-1]",
            "array[-5:]",
            "text[:-1]",
            "data[-10:-5]",
            "items[-1::-1]",
            "buffer[:-length]"
        ]
        
        for expr in negative_slices:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Subscript)

    def test_multidimensional_slices(self, tester):
        """Test multidimensional slicing"""
        # Multiple slice dimensions
        multidim_slices = [
            "matrix[1:3, 2:4]",
            "array[:, 0]",
            "tensor[::2, 1:, :-1]",
            "data[start:end, :, step]",
            "grid[row1:row2, col1:col2]"
        ]
        
        for expr in multidim_slices:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Subscript)

    def test_slice_with_expressions(self, tester):
        """Test slices with complex expressions"""
        # Complex slice expressions
        complex_slices = [
            "array[start + 1:end - 1]",
            "data[len(prefix):len(data) - len(suffix)]",
            "seq[func(x):func(y):func(z)]",
            "buffer[offset:offset + size]",
            "matrix[row * size:(row + 1) * size]"
        ]
        
        for expr in complex_slices:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Subscript)


class TestSection63FunctionCalls:
    """Test function call expressions"""
    
    @pytest.fixture
    def tester(self):
        return PrimaryExpressionTester()

    def test_simple_function_calls(self, tester):
        """Test simple function call syntax"""
        # Language Reference: primary(argument_list)
        simple_calls = [
            "func()",
            "function(arg)",
            "process(data)",
            "calculate(x, y)",
            "handler(request, response)",
            "validator(value, schema, options)"
        ]
        
        for expr in simple_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Call)

    def test_function_calls_with_keywords(self, tester):
        """Test function calls with keyword arguments"""
        # Keyword argument patterns
        keyword_calls = [
            "func(arg=value)",
            "process(data, format='json')",
            "connect(host='localhost', port=8080)",
            "create(name=name, value=value, active=True)",
            "configure(debug=False, timeout=30, retries=3)"
        ]
        
        for expr in keyword_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Call)

    def test_function_calls_with_varargs(self, tester):
        """Test function calls with *args and **kwargs"""
        # Variable argument patterns
        varargs_calls = [
            "func(*args)",
            "process(**kwargs)",
            "combine(*sequences)",
            "merge(**dictionaries)",
            "call(fixed, *args, **kwargs)",
            "invoke(arg1, arg2, *rest, key=value, **options)"
        ]
        
        for expr in varargs_calls:
            try:
                tree = tester.assert_primary_expr_syntax_parses(expr)
                assert tester.contains_node_type(expr, ast.Call)
            except AssertionError:
                # Skip if starred expressions not supported
                if sys.version_info < (3, 0):
                    pytest.skip("Starred expressions require Python 3.0+")
                else:
                    raise

    def test_method_calls(self, tester):
        """Test method call expressions"""
        # Method call patterns
        method_calls = [
            "obj.method()",
            "instance.process(data)",
            "self.validate(value)",
            "handler.execute(request)",
            "parser.parse(text, options)",
            "service.call(action, **params)"
        ]
        
        for expr in method_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain both Call and Attribute nodes
            assert tester.contains_node_type(expr, ast.Call)
            assert tester.contains_node_type(expr, ast.Attribute)

    def test_chained_method_calls(self, tester):
        """Test chained method calls"""
        # Method chaining patterns
        chained_calls = [
            "obj.method1().method2()",
            "builder.add(item).build()",
            "query.filter(condition).order(field).limit(10)",
            "text.strip().lower().replace(' ', '_')",
            "data.transform().validate().save()"
        ]
        
        for expr in chained_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain multiple Call nodes
            call_nodes = tester.get_expression_nodes_of_type(expr, ast.Call)
            assert len(call_nodes) >= 2


class TestSection63ComplexExpressions:
    """Test complex primary expression combinations"""
    
    @pytest.fixture
    def tester(self):
        return PrimaryExpressionTester()

    def test_mixed_primary_expressions(self, tester):
        """Test complex combinations of primary expressions"""
        # Mixed expression patterns
        complex_expressions = [
            "obj.method()[key].attr",
            "func().data[index].process()",
            "instance.items[0].transform().result",
            "parser.parse(text).tokens[0].value",
            "service.get(id).data['field'].validate()",
            "factory().create(type).configure(options).build()"
        ]
        
        for expr in complex_expressions:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain multiple primary expression node types
            has_call = tester.contains_node_type(expr, ast.Call)
            has_attr = tester.contains_node_type(expr, ast.Attribute)
            has_subscript = tester.contains_node_type(expr, ast.Subscript)
            
            # Should have at least two different types
            expression_types = sum([has_call, has_attr, has_subscript])
            assert expression_types >= 2

    def test_nested_function_calls(self, tester):
        """Test nested function call expressions"""
        # Nested call patterns
        nested_calls = [
            "outer(inner())",
            "process(transform(data))",
            "validate(parse(normalize(text)))",
            "calculate(add(multiply(x, y), subtract(a, b)))",
            "handler(request, processor(parser(input)))"
        ]
        
        for expr in nested_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain multiple Call nodes
            call_nodes = tester.get_expression_nodes_of_type(expr, ast.Call)
            assert len(call_nodes) >= 2

    def test_complex_subscript_expressions(self, tester):
        """Test complex subscript and slice combinations"""
        # Complex subscript patterns
        complex_subscripts = [
            "matrix[func(row), col + offset]",
            "data[key][subkey][processor(index)]",
            "lookup[hash(key) % size][field]",
            "cache[compute_key(params)].data[section]",
            "buffer[start:start + parse_length(header)]"
        ]
        
        for expr in complex_subscripts:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Subscript)

    def test_attribute_method_combinations(self, tester):
        """Test complex attribute and method access patterns"""
        # Attribute/method combinations
        attr_method_combinations = [
            "obj.config.get('setting').value",
            "instance.services['auth'].authenticate(user)",
            "app.database.users.find({'active': True}).count()",
            "parser.results[-1].tokens[0].normalize().text",
            "service.client.request(endpoint).json()['data']"
        ]
        
        for expr in attr_method_combinations:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should mix attributes, calls, and subscripts
            assert tester.contains_node_type(expr, ast.Attribute)
            assert tester.contains_node_type(expr, ast.Call)

    def test_precedence_and_associativity(self, tester):
        """Test expression precedence and associativity"""
        # Precedence testing expressions
        precedence_expressions = [
            "a.b.c",                      # Left-to-right attribute access
            "f()()",                      # Left-to-right function calls
            "obj[i][j]",                  # Left-to-right subscripts
            "f().g().h()",                # Chained method calls
            "a.b[c].d()",                 # Mixed precedence
            "obj.attr[key](arg).result"   # Complex chaining
        ]
        
        for expr in precedence_expressions:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Just verify they parse correctly
            # Actual precedence validation is done by Python parser


class TestSection63CallArguments:
    """Test function call argument patterns"""
    
    @pytest.fixture
    def tester(self):
        return PrimaryExpressionTester()

    def test_positional_arguments(self, tester):
        """Test positional argument patterns"""
        # Positional argument calls
        positional_calls = [
            "func(1)",
            "func(1, 2)",
            "func(1, 2, 3)",
            "func('hello', 'world')",
            "func(obj, method, params)",
            "func(a, b, c, d, e)"
        ]
        
        for expr in positional_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Call)

    def test_keyword_arguments(self, tester):
        """Test keyword argument patterns"""
        # Keyword argument calls
        keyword_calls = [
            "func(a=1)",
            "func(a=1, b=2)",
            "func(name='value')",
            "func(x=expr, y=other)",
            "func(setting=True, timeout=30)",
            "func(host='localhost', port=8080, debug=False)"
        ]
        
        for expr in keyword_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Call)

    def test_mixed_arguments(self, tester):
        """Test mixed positional and keyword arguments"""
        # Mixed argument patterns
        mixed_calls = [
            "func(1, b=2)",
            "func('hello', name='world')",
            "func(obj, method='GET', headers={})",
            "func(data, format='json', validate=True)",
            "func(x, y, z, option=value, flag=True)"
        ]
        
        for expr in mixed_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Call)

    def test_complex_argument_expressions(self, tester):
        """Test complex expressions as arguments"""
        # Complex argument expressions
        complex_arg_calls = [
            "func(other_func(x))",
            "func(obj.method(param))",
            "func(data[key], options['setting'])",
            "func(x + y, z * w)",
            "func([item for item in collection])",
            "func({'key': compute_value(param)})"
        ]
        
        for expr in complex_arg_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Call)

    def test_generator_arguments(self, tester):
        """Test generator expressions as arguments"""
        # Generator expression arguments
        generator_arg_calls = [
            "func(x for x in items)",
            "sum(x * x for x in range(10))",
            "all(item.valid for item in collection)",
            "max(len(s) for s in strings)",
            "list(process(item) for item in batch)"
        ]
        
        for expr in generator_arg_calls:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            assert tester.contains_node_type(expr, ast.Call)


class TestSection63ErrorConditions:
    """Test error conditions for primary expressions"""
    
    @pytest.fixture
    def tester(self):
        return PrimaryExpressionTester()

    def test_invalid_attribute_syntax(self, tester):
        """Test invalid attribute reference syntax"""
        # Invalid attribute patterns
        invalid_attributes = [
            "obj.",                       # Missing attribute name
            "obj.123",                    # Numeric attribute name
            "obj.'string'",               # String attribute name
            "obj.def",                    # Reserved word attribute
            "obj.class",                  # Reserved word attribute
            "obj..attr",                  # Double dots
        ]
        
        for expr in invalid_attributes:
            tester.assert_primary_expr_syntax_error(expr)

    def test_invalid_subscription_syntax(self, tester):
        """Test invalid subscription syntax"""
        # Invalid subscription patterns
        invalid_subscriptions = [
            "obj[]",                      # Empty subscript
            "obj[",                       # Incomplete subscript
            "obj]",                       # Missing opening bracket
            "obj[1 2]",                   # Missing comma
        ]
        
        for expr in invalid_subscriptions:
            tester.assert_primary_expr_syntax_error(expr)

    def test_invalid_call_syntax(self, tester):
        """Test invalid function call syntax"""
        # Invalid call patterns
        invalid_calls = [
            "func(",                      # Incomplete call
            "func)",                      # Missing opening paren
            "func(,)",                    # Leading comma
            "func(a b)",                  # Missing comma
            "func(=value)",               # Missing keyword name
        ]
        
        for expr in invalid_calls:
            tester.assert_primary_expr_syntax_error(expr)

    def test_invalid_slice_syntax(self, tester):
        """Test invalid slice syntax"""
        # Invalid slice patterns
        invalid_slices = [
            "obj[:]:",                    # Extra colon
            "obj[1:2:3:4]",              # Too many colons
            "obj[::]:",                   # Extra colon after step
        ]
        
        for expr in invalid_slices:
            tester.assert_primary_expr_syntax_error(expr)


class TestSection63CrossImplementationCompatibility:
    """Test primary expression features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return PrimaryExpressionTester()

    def test_comprehensive_primary_expression_patterns(self, tester):
        """Test complex primary expression combinations"""
        # Comprehensive primary expression patterns
        comprehensive_patterns = [
            "service.get_client().request('GET', url, headers=headers).json()['data'][0]['value']",
            "factory(config).create(type='handler').configure(params).process(data).results",
            "parser.parse(input)[0].tokens.filter(lambda t: t.type == 'identifier').map(str)",
            "app.database['users'].find({'active': True}).sort('name').limit(10)[0]['email']",
            "transform(normalize(data.items())[::2]).validate().serialize(format='json')"
        ]
        
        for expr in comprehensive_patterns:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Should contain multiple primary expression types
            has_call = tester.contains_node_type(expr, ast.Call)
            has_attr = tester.contains_node_type(expr, ast.Attribute)
            has_subscript = tester.contains_node_type(expr, ast.Subscript)
            
            # Should have at least two types for complex expressions
            assert sum([has_call, has_attr, has_subscript]) >= 2

    def test_primary_expression_ast_validation(self, tester):
        """Test AST structure validation for primary expressions"""
        # Complex expression for AST validation
        complex_expr = "obj.method(arg)[key].attr(param).result"
        
        tree = tester.assert_primary_expr_syntax_parses(complex_expr)
        
        # Verify specific node types exist
        call_nodes = tester.get_expression_nodes_of_type(complex_expr, ast.Call)
        attr_nodes = tester.get_expression_nodes_of_type(complex_expr, ast.Attribute)
        subscript_nodes = tester.get_expression_nodes_of_type(complex_expr, ast.Subscript)
        
        assert len(call_nodes) >= 2      # Multiple method calls
        assert len(attr_nodes) >= 3      # Multiple attribute accesses
        assert len(subscript_nodes) >= 1 # At least one subscription

    def test_primary_expression_edge_cases(self, tester):
        """Test edge cases in primary expressions"""
        # Edge cases and corner scenarios
        edge_case_expressions = [
            "obj",                        # Simple name
            "obj.attr",                   # Simple attribute
            "obj[0]",                     # Simple subscript
            "func()",                     # Simple call
            "a.b.c.d.e.f",               # Long attribute chain
            "obj[0][1][2][3]",           # Long subscript chain
            "f()()()()",                 # Long call chain
            "(obj.attr)[key](arg)",      # Parenthesized expressions
            "obj.__dict__['__name__']",  # Dunder access
            "_private._attr[_key](_arg)" # Private names
        ]
        
        for expr in edge_case_expressions:
            tree = tester.assert_primary_expr_syntax_parses(expr)
            # Just verify they parse correctly

    def test_primary_expression_with_operators(self, tester):
        """Test primary expressions combined with operators"""
        # Primary expressions in operator contexts (as statements)
        operator_context_statements = [
            "result = obj.method()",
            "value = data[key]",
            "total = sum(items)",
            "flag = obj.attr and other.attr",
            "item = collection[index] or default"
        ]
        
        for stmt in operator_context_statements:
            # Parse as statement instead of expression
            tree = ast.parse(stmt, mode='exec')
            # Should parse successfully with assignment
            assert len(tree.body) == 1