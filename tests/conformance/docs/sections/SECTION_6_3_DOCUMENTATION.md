# Section 6.3: Primary Expressions - Conformance Test Documentation

**Test File:** `test_section_6_3_primary_expressions.py`
**Language Reference:** [Section 6.3 Primary Expressions](https://docs.python.org/3/reference/expressions.html#primaries)
**Implementation Status:** [DONE] COMPLETE

## Overview

This test suite validates Python implementation conformance to **Python Language Reference Section 6.3: Primary Expressions**. It covers all primary expression forms including attribute references, subscriptions, slicing, function calls, and their complex combinations that form the foundation of Python's expression evaluation system.

## Primary Expression Features Tested

### Attribute References
- **Simple attribute access**: `obj.attr`, `instance.method`
- **Chained attribute access**: `obj.attr.subattr.value`
- **Attribute on call results**: `func().attr`, `obj.method().result`
- **Mixed with subscripts**: `obj.items[0].field`, `data[key].value`
- **Identifier patterns**: private, dunder, camelCase, snake_case naming

### Subscriptions (Indexing)
- **Simple subscripts**: `obj[key]`, `array[index]`, `dict['name']`
- **Multiple subscripts**: `matrix[row][col]`, `nested[a][b][c]`
- **Complex index expressions**: `array[i + 1]`, `lookup[hash(key) % size]`
- **Various key types**: integers, strings, variables, function calls, expressions

### Slicing
- **Simple slices**: `seq[start:stop]`, `array[:]`, `text[:10]`
- **Extended slices**: `seq[::2]`, `array[1::2]`, `text[::-1]`
- **Negative slicing**: `seq[-1]`, `array[-5:]`, `data[-10:-5]`
- **Multidimensional slices**: `matrix[1:3, 2:4]`, `tensor[::2, 1:, :-1]`
- **Complex slice expressions**: `buffer[offset:offset + size]`

### Function Calls
- **Simple calls**: `func()`, `process(data)`, `calculate(x, y)`
- **Keyword arguments**: `func(arg=value)`, `connect(host='localhost', port=8080)`
- **Variable arguments**: `func(*args)`, `process(**kwargs)`, `call(*args, **kwargs)`
- **Method calls**: `obj.method()`, `instance.process(data)`
- **Chained calls**: `builder.add(item).build()`, `query.filter().order().limit()`

### Complex Combinations
- **Mixed expressions**: `obj.method()[key].attr`, `func().data[index].process()`
- **Nested calls**: `outer(inner())`, `process(transform(data))`
- **Complex subscripts**: `matrix[func(row), col + offset]`
- **Attribute-method chains**: `service.client.request(endpoint).json()['data']`
- **Precedence validation**: Left-to-right evaluation order testing

### Call Arguments
- **Positional arguments**: `func(1, 2, 3)`, `process(obj, method, params)`
- **Keyword arguments**: `func(a=1, b=2)`, `configure(debug=False, timeout=30)`
- **Mixed arguments**: `func(pos_arg, keyword=value)`
- **Complex argument expressions**: `func(other_func(x))`, `func(obj.method(param))`
- **Generator arguments**: `func(x for x in items)`, `sum(x*x for x in range(10))`

## Test Class Summary

### `TestSection63AttributeReferences`
- Simple and chained attribute access validation
- Attribute access on function call results
- Mixed attribute and subscript operations
- Various identifier naming pattern validation

### `TestSection63Subscriptions`
- Simple and multiple subscription validation
- Complex index expression testing
- Various key type pattern validation
- Chained subscription operation testing

### `TestSection63Slicing`
- Simple and extended slice syntax validation
- Negative indexing and multidimensional slicing
- Complex slice expression validation
- Step parameter and range testing

### `TestSection63FunctionCalls`
- Simple function call syntax validation
- Keyword and variable argument patterns
- Method call and chaining validation
- Complex argument expression testing

### `TestSection63ComplexExpressions`
- Mixed primary expression combinations
- Nested function call validation
- Complex subscript and slice patterns
- Attribute-method combination testing
- Precedence and associativity validation

### `TestSection63CallArguments`
- Positional and keyword argument validation
- Mixed argument pattern testing
- Complex argument expression validation
- Generator expression argument testing

### `TestSection63ErrorConditions`
- Invalid attribute reference syntax
- Invalid subscription and slice syntax
- Invalid function call patterns
- Malformed expression detection

### `TestSection63CrossImplementationCompatibility`
- Comprehensive primary expression pattern testing
- AST structure validation for complex expressions
- Edge case and corner scenario validation
- Operator context integration testing

## Grammar Coverage

Tests complete primary expression grammar from Language Reference:
- `attributeref`: Primary attribute access (`obj.attr`)
- `subscription`: Primary subscript access (`obj[key]`)
- `slicing`: Slice notation with start:stop:step
- `call`: Function/method call with argument lists
- `primary`: All primary expression forms and combinations
- Expression precedence and left-to-right associativity

## Version-Aware Coverage

- **Python 3.0+**: Starred expressions in function calls (`*args`, `**kwargs`)
- **All versions**: Core primary expression syntax and evaluation
- **Cross-implementation**: AST structure validation across Python variants

## Validation Commands

```bash
pytest tests/conformance/test_section_6_3_primary_expressions.py -v
pytest tests/conformance/test_section_6_3_primary_expressions.py::TestSection63FunctionCalls -v
pytest tests/conformance/test_section_6_3_primary_expressions.py::TestSection63ComplexExpressions -v
```

## Notes

- Uses dual-mode AST parsing (`eval` and `exec`) for expression context handling
- Tests syntax parsing and AST structure, not runtime expression evaluation
- Covers all primary expression patterns specified in Language Reference
- Validates proper AST structure for primary expression nodes
- Tests both simple and complex expression combinations
- Includes comprehensive error condition validation
- Validates expression precedence through parser behavior
- Tests chained operations and method call patterns
- Covers advanced argument patterns including generators