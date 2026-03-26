# Section 6.2: Atoms - Conformance Test Documentation

**Test File:** `test_section_6_2_atoms.py`
**Language Reference:** [Section 6.2 Atoms](https://docs.python.org/3/reference/expressions.html#atoms)
**Implementation Status:** [DONE] COMPLETE

## Overview

This test suite validates Python implementation conformance to **Python Language Reference Section 6.2: Atoms**. It covers the most basic elements of expressions including constants, identifiers, literals, and enclosures (parentheses, lists, dicts, sets, generators).

## Grammar Coverage

```text
atom: 'True' | 'False' | 'None' | '...' | identifier | literal | enclosure
enclosure: parenth_form | list_display | dict_display | set_display 
         | generator_expression | yield_atom
literal: strings | NUMBER
```

## Major Areas Tested

- Built-in constants: `True`, `False`, `None`, `...` (Ellipsis)
- Identifiers: valid naming patterns, Unicode support, private name mangling
- Numeric literals: integers, floats, complex (builds on Section 2.6)
- String literals: various string forms (builds on Section 2.7)
- Parenthesized forms: `(expression)`
- List displays: `[item1, item2, ...]`
- Dictionary displays: `{'key': 'value', ...}`
- Set displays: `{item1, item2, ...}`
- Generator expressions: `(expr for x in iterable)`
- Yield atoms: `yield` expressions in expression context
- Invalid syntax validation
- Cross-implementation compatibility

## Test Class Summary

### `TestSection62BuiltinConstants`
- Boolean constants (`True`, `False`)
- None constant
- Ellipsis constant (`...`)
- Constant assignment/attribute access forbidden
- Constants in expressions

### `TestSection62Identifiers`
- Simple identifier atom syntax
- Valid identifier naming patterns
- Unicode identifier support
- Private name mangling patterns (`__name`)
- Special identifier patterns
- Invalid identifier syntax
- Keyword identifier restrictions

### `TestSection62Literals`
- Numeric literal atoms (builds on Section 2.6)
- String literal atoms (builds on Section 2.7)
- String literal concatenation
- Negative numbers as expressions (not literals)

### `TestSection62ParenthesizedForms`
- Simple parenthesized expressions
- Complex expressions in parentheses
- Nested parentheses
- Empty parentheses tuple `()`
- Single element tuples `(item,)`

### `TestSection62ListDisplays`
- Simple list display syntax `[1, 2, 3]`
- Complex element expressions
- Nested list structures
- Trailing comma handling

### `TestSection62DictDisplays`
- Simple dictionary display syntax `{'key': 'value'}`
- Complex key/value expressions
- Dict comprehensions vs displays distinction
- Trailing comma handling

### `TestSection62SetDisplays`
- Simple set display syntax `{1, 2, 3}`
- Complex element expressions
- Set vs dict distinction `{1}` vs `{}`
- Set comprehensions vs displays

### `TestSection62GeneratorExpressions`
- Simple generator syntax `(x for x in range(10))`
- Generators with conditions
- Nested generator structures
- Complex generator expressions

### `TestSection62YieldAtoms`
- Simple yield expressions in function context
- `yield from` expressions
- Yield in expression contexts

### `TestSection62ErrorConditions`
- Invalid literal syntax
- Invalid string literals
- Invalid enclosure syntax
- Yield outside function errors

### `TestSection62CrossImplementationCompatibility`
- Large numeric literals
- Complex nested structures
- Atoms in complex expressions
- Literal identity behavior (AST-level)
- Unicode atom support
- Edge case combinations

## Version-Aware Coverage

- **Python 3.0+**: Unicode identifiers (tested with fallback)
- **Python 3.3+**: `yield from` syntax
- **All versions**: Core atom syntax requirements

## Validation Commands

```bash
pytest tests/conformance/test_section_6_2_atoms.py -v
pytest tests/conformance/test_section_6_2_atoms.py::TestSection62BuiltinConstants -v
pytest tests/conformance/test_section_6_2_atoms.py::TestSection62Identifiers -v
```

## Notes

- Uses AST-based validation for cross-implementation portability.
- Builds on Section 2.6 (Numeric Literals) and Section 2.7 (String/Bytes Literals).
- Tests both expression mode (`eval`) and statement mode (`exec`) parsing.
- Covers fundamental expression building blocks used throughout Python.
- Validates proper distinction between similar syntax forms (sets vs dicts, displays vs comprehensions).