# Section 7.1: Expression Statements - Conformance Test Documentation

**Test File:** `test_section_7_1_expression_statements.py`
**Language Reference:** [Section 7.1 Expression Statements](https://docs.python.org/3/reference/simple_stmts.html#expression-statements)
**Implementation Status:** [DONE] COMPLETE

## Overview

This test suite validates Python implementation conformance to **Python Language Reference Section 7.1: Expression Statements**. It covers all expression statement forms including literals, names, function calls, operations, conditionals, lambdas, and comprehensions that can be evaluated as standalone statements.

## Expression Statement Features Tested

### Simple Expression Statements
- **Literal expressions**: integers, floats, strings, constants (`True`, `False`, `None`)
- **Name expressions**: variables, functions, classes, modules
- **Constant expressions**: built-in constants and `__debug__`
- **Expression vs assignment distinction**: proper categorization

### Function Call Statements
- **Simple calls**: `func()`, `process(data)`, `calculate(x, y)`
- **Method calls**: `obj.method()`, `instance.process(data)`
- **Chained calls**: `builder.add().build()`, `query.filter().execute()`
- **Nested calls**: `print(str(value))`, `validate(parse(input))`

### Attribute Access Statements
- **Simple attributes**: `obj.attr`, `instance.value`, `module.function`
- **Chained attributes**: `app.config.database.host`, `service.client.status`
- **Mixed with subscripts**: `obj.items[0]`, `data[key].value`

### Subscript Statements
- **Simple subscripts**: `array[0]`, `dict[key]`, `items[index]`
- **Chained subscripts**: `matrix[row][col]`, `nested[a][b][c]`
- **Slice expressions**: `array[1:5]`, `text[:10]`, `sequence[::-1]`

### Binary Operation Statements
- **Arithmetic operations**: `x + y`, `a * b`, `x ** y`, `x @ y` (Python 3.5+)
- **Comparison operations**: `x == y`, `a < b`, `x in y`, `a is not b`
- **Logical operations**: `x and y`, `a or b`, `not (x and y)`
- **Bitwise operations**: `x | y`, `a & b`, `x ^ y`, `a << 2`

### Unary Operation Statements
- **Arithmetic unary**: `+x`, `-x`, `+42`, `-variable`
- **Logical unary**: `not x`, `not function()`, `not (x and y)`
- **Bitwise unary**: `~x`, `~flags`, `~(a | b)`

### Conditional Expression Statements
- **Ternary conditionals**: `x if condition else y`, `value if test else default`
- **Nested conditionals**: `a if x else b if y else c`
- **Complex conditions**: `obj.method() if obj else fallback()`

### Lambda Expression Statements
- **Simple lambdas**: `lambda: None`, `lambda x: x`, `lambda x, y: x + y`
- **Complex lambdas**: `lambda x: x if x > 0 else 0`, `lambda *args: sum(args)`
- **Default arguments**: `lambda x=default: x * 2`

### Comprehension Statements
- **List comprehensions**: `[x for x in items]`, `[x*2 for x in range(10) if x > 0]`
- **Set comprehensions**: `{x for x in items}`, `{item.lower() for item in strings}`
- **Dict comprehensions**: `{k: v for k, v in items}`, `{x: x**2 for x in range(5)}`
- **Generator expressions**: `(x for x in items)`, `(item.strip() for item in lines)`

## Test Class Summary

### `TestSection71SimpleExpressionStatements`
- Simple expression statement validation (literals, names, constants)
- Expression statement identification and categorization

### `TestSection71FunctionCallStatements`
- Function call statement validation (simple, method, chained, nested)
- Call expression type verification

### `TestSection71AttributeAccessStatements`
- Attribute access statement validation (simple, chained, mixed)
- Attribute expression type verification

### `TestSection71SubscriptStatements`
- Subscript statement validation (simple, chained, slices)
- Subscript expression type verification

### `TestSection71BinaryOperationStatements`
- Binary operation statement validation (arithmetic, comparison, logical, bitwise)
- Operation expression type verification

### `TestSection71UnaryOperationStatements`
- Unary operation statement validation (arithmetic, logical, bitwise)
- Unary expression type verification

### `TestSection71ConditionalExpressionStatements`
- Conditional expression statement validation (ternary, nested)
- Conditional expression type verification

### `TestSection71LambdaExpressionStatements`
- Lambda expression statement validation (simple, complex, defaults)
- Lambda expression type verification

### `TestSection71ComprehensionStatements`
- Comprehension statement validation (list, set, dict, generator)
- Comprehension expression type verification

### `TestSection71ErrorConditions`
- Invalid expression statement syntax detection
- Malformed operator and comprehension validation

### `TestSection71CrossImplementationCompatibility`
- Complex expression statement pattern testing
- AST structure validation for expression statements
- Edge case and distinction validation
- Expression vs assignment categorization

## Grammar Coverage

Tests complete expression statement grammar from Language Reference:
- `expression_stmt`: Expression list as statement
- All expression forms that can appear as statements
- Expression evaluation context and precedence
- Statement-level expression termination

## Version-Aware Coverage

- **Python 3.5+**: Matrix multiplication operator (`@`)
- **Python 3.6+**: F-string expressions (context-dependent)
- **All versions**: Core expression statement syntax and evaluation

## Validation Commands

```bash
pytest tests/conformance/test_section_7_1_expression_statements.py -v
pytest tests/conformance/test_section_7_1_expression_statements.py::TestSection71FunctionCallStatements -v
pytest tests/conformance/test_section_7_1_expression_statements.py::TestSection71ComprehensionStatements -v
```

## Notes

- Tests expression parsing in statement context (not assignment context)
- Validates proper AST structure for expression statement nodes (`ast.Expr`)
- Covers all expression forms specified in Language Reference
- Tests expression vs assignment statement distinction
- Includes comprehensive error condition validation
- Validates expression type detection within statements
- Tests complex expression combinations and nesting patterns
- Covers advanced expression forms (lambdas, comprehensions, conditionals)