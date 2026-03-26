# Section 2.8: Operators and Delimiters - Conformance Test Documentation

**Test File:** `test_section_2_8_operators_delimiters.py`
**Language Reference:** [Section 2.8 Operators and Delimiters](https://docs.python.org/3/reference/lexical_analysis.html#operators)
**Implementation Status:** [DONE] COMPLETE

## Overview

This test suite validates Python implementation conformance to **Python Language Reference Section 2.8: Operators and Delimiters**. It covers all operator symbols, delimiter syntax, precedence rules, and associativity patterns that form the foundation of Python expression syntax.

## Operator Categories Tested

### Arithmetic Operators
- **Basic arithmetic**: `+`, `-`, `*`, `/`, `//`, `%`, `**`
- **Matrix multiplication**: `@` (Python 3.5+)
- **Unary operators**: `+a`, `-a`, `~a`
- **Precedence testing**: Power, multiplication/division, addition/subtraction
- **Associativity validation**: Left-associative vs right-associative operators

### Bitwise Operators
- **Binary bitwise**: `&`, `|`, `^`, `<<`, `>>`
- **Unary bitwise**: `~` (bitwise NOT)
- **Precedence hierarchy**: `~` > `<<`/`>>` > `&` > `^` > `|`
- **Complex bitwise expressions**

### Comparison Operators
- **Equality/inequality**: `==`, `!=`, `<>` (Python 2 legacy)
- **Ordering**: `<`, `>`, `<=`, `>=`
- **Identity**: `is`, `is not`
- **Membership**: `in`, `not in`
- **Chained comparisons**: `a < b < c`, `a == b != c`

### Logical Operators
- **Binary logical**: `and`, `or`
- **Unary logical**: `not`
- **Precedence**: `not` > `and` > `or`
- **Short-circuit evaluation support**

### Assignment Operators
- **Simple assignment**: `=`
- **Augmented assignment**: `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `**=`, `@=`, `&=`, `|=`, `^=`, `<<=`, `>>=`
- **Annotated assignment**: `variable: type = value` (Python 3.6+)

## Delimiter Categories Tested

### Grouping Delimiters
- **Parentheses**: `()` for grouping and tuples
- **Square brackets**: `[]` for lists and subscripting
- **Curly braces**: `{}` for sets and dictionaries

### Separator Delimiters
- **Comma**: `,` for element separation
- **Colon**: `:` for dictionary key-value pairs, slices
- **Dot**: `.` for attribute access
- **Semicolon**: `;` for statement separation

### Function Delimiters
- **Arrow**: `->` for function return annotations (Python 3.5+)
- **At symbol**: `@` for decorators
- **Lambda colon**: `:` in lambda expressions

## Test Class Summary

### `TestSection28ArithmeticOperators`
- Basic arithmetic operator syntax (`+`, `-`, `*`, `/`, `//`, `%`, `**`)
- Matrix multiplication operator `@` (Python 3.5+)
- Unary operators (`+a`, `-a`, `~a`)
- Precedence and associativity validation

### `TestSection28BitwiseOperators`
- Binary bitwise operators (`&`, `|`, `^`, `<<`, `>>`)
- Unary bitwise operator (`~`)
- Bitwise operator precedence hierarchy

### `TestSection28ComparisonOperators`
- All comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`)
- Identity operators (`is`, `is not`)
- Membership operators (`in`, `not in`)
- Chained comparison syntax

### `TestSection28LogicalOperators`
- Binary logical operators (`and`, `or`)
- Unary logical operator (`not`)
- Logical operator precedence

### `TestSection28AssignmentOperators`
- Simple assignment syntax
- All augmented assignment operators
- Annotated assignment (Python 3.6+)

### `TestSection28Delimiters`
- Grouping delimiters (`()`, `[]`, `{}`)
- Separator delimiters (`,`, `:`, `.`, `;`)
- Function delimiters (`->`, `@`)
- Decorator syntax validation

### `TestSection28ErrorConditions`
- Invalid operator combinations
- Invalid delimiter usage
- Incomplete operator expressions

### `TestSection28CrossImplementationCompatibility`
- Complex multi-operator expressions
- Comprehensive precedence validation
- Nested delimiter structures
- Mixed operand types
- Assignment in various contexts
- AST structure validation

## Grammar Coverage

Tests the complete operator and delimiter grammar from the Language Reference:
- All unary and binary operator symbols
- Operator precedence hierarchy (15 levels)
- Left vs right associativity rules
- Delimiter pairing and nesting rules
- Context-sensitive delimiter usage

## Version-Aware Coverage

- **Python 3.5+**: Matrix multiplication `@`, function annotations `->`
- **Python 3.6+**: Annotated assignments with type hints
- **All versions**: Core operator and delimiter syntax

## Validation Commands

```bash
pytest tests/conformance/test_section_2_8_operators_delimiters.py -v
pytest tests/conformance/test_section_2_8_operators_delimiters.py::TestSection28ArithmeticOperators -v
pytest tests/conformance/test_section_2_8_operators_delimiters.py::TestSection28ComparisonOperators -v
```

## Notes

- Uses AST-based validation for cross-implementation portability
- Tests syntax parsing, not runtime behavior
- Validates complete operator precedence hierarchy
- Covers all delimiter contexts from Language Reference
- Tests both simple and complex operator combinations
- Includes comprehensive error condition validation
- Validates proper AST structure for operator expressions