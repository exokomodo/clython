# Section 7.2: Assignment Statements - Conformance Test Documentation

**Test File:** `test_section_7_2_assignment_statements.py`
**Language Reference:** [Section 7.2 Assignment Statements](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements)
**Implementation Status:** [DONE] COMPLETE

## Overview

This test suite validates Python implementation conformance to **Python Language Reference Section 7.2: Assignment Statements**. It covers simple assignment, multiple assignment, tuple/list unpacking, starred expressions, attribute/subscription assignment, and error handling.

## Grammar Coverage

```text
assignment_stmt: (target_list "=")+ (starred_expression | yield_expression)
target_list: target ("," target)* [","]
target: identifier
      | "(" [target_list] ")"
      | "[" [target_list] "]"
      | attributeref
      | subscription  
      | "*" target
```

## Major Areas Tested

- Simple assignment: `name = value`
- Multiple/chained assignment: `a = b = value`
- Tuple unpacking: `a, b = tuple_value`
- List unpacking: `[a, b] = list_value`
- Starred expressions: `a, *rest, b = sequence`
- Nested unpacking: `(a, b), c = nested_structure`
- Attribute assignment: `obj.attr = value`
- Subscription assignment: `container[key] = value`
- Invalid assignment targets and syntax errors
- Yield expression assignment in generator context
- Cross-implementation compatibility patterns

## Test Class Summary

### `TestSection72SimpleAssignment`
- Basic simple assignment syntax
- Identifier targets and validation
- Built-in name shadowing (syntactically valid)
- Numeric and string literal assignments

### `TestSection72MultipleAssignment`
- Chained assignment (`a = b = value`)
- Mixed target type chaining
- AST structure validation for multiple targets

### `TestSection72TupleUnpacking`
- Basic tuple unpacking
- Parenthesized and list bracket syntax
- Mixed unpacking syntax
- Nested unpacking patterns
- Trailing comma handling
- AST structure validation

### `TestSection72StarredExpressions`
- Starred target syntax (`*target`)
- Starred expressions in different positions
- Starred in nested unpacking contexts
- AST structure for starred expressions
- Single starred expression limitations

### `TestSection72AttributeSubscriptionAssignment`
- Attribute assignment (`obj.attr = value`)
- Subscription assignment (`container[key] = value`)
- Complex subscription patterns
- Mixed attribute/subscription access
- Chained complex assignments
- Unpacking with complex targets

### `TestSection72ErrorConditions`
- Invalid assignment targets (literals, expressions)
- Invalid starred expression usage
- Empty/incomplete assignment statements
- Invalid tuple unpacking syntax
- Keywords as assignment targets
- Complex invalid patterns

### `TestSection72SpecialAssignmentForms`
- Yield expression assignment in generators
- Assignment vs comprehensions distinction
- Regular vs augmented assignment
- Global/nonlocal scoped assignments

### `TestSection72CrossImplementationCompatibility`
- Large tuple unpacking (100 variables)
- Deeply nested unpacking structures
- Complex chained assignments
- AST introspection validation
- Performance-oriented patterns
- Unicode identifier assignments
- Real-world assignment patterns

## Version-Aware Coverage

- **Python 3.0+**: Starred expressions in unpacking
- **Python 3.0+**: Unicode identifiers (tested with fallback)

## Validation Commands

```bash
pytest tests/conformance/test_section_7_2_assignment_statements.py -v
pytest tests/conformance/test_section_7_2_assignment_statements.py::TestSection72TupleUnpacking -v
pytest tests/conformance/test_section_7_2_assignment_statements.py::TestSection72ErrorConditions -v
```

## Notes

- Uses AST-based validation for cross-implementation portability.
- Tests both syntactic correctness and semantic structure.
- Covers assignment patterns essential for Python language compliance.
- Includes real-world patterns from production code.
- Validates proper target binding and unpacking behavior.