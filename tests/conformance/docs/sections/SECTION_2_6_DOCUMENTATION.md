# Section 2.6 Numeric Literals Conformance Tests

## Overview

This test suite validates Python implementation conformance to **Python Language Reference Section 2.6: Numeric Literals**. It tests the formal grammar rules and prose requirements specified in the official documentation.

## Language Reference Mapping

### Formal Grammar Tested

```
NUMBER: integer | floatnumber | imagnumber
integer: decinteger | bininteger | octinteger | hexinteger | zerointeger  
floatnumber: digitpart "." [digitpart] [exponent] | "." digitpart [exponent] | digitpart exponent
imagnumber: (floatnumber | digitpart) ("j" | "J")
```

### Prose Requirements Validated

| Requirement | Test Class | Test Methods |
|------------|------------|--------------|
| "Leading zeros in a non-zero decimal number are not allowed" | `TestSection26IntegerLiterals` | `test_leading_zeros_forbidden` |
| "Underscores can only occur between digits" | `TestSection26IntegerLiterals` | `test_underscore_grouping_invalid` |
| Valid underscore placement patterns | `TestSection26IntegerLiterals` | `test_underscore_grouping_valid` |
| Binary digit validation (0-1 only) | `TestSection26IntegerLiterals` | `test_binary_integers` |
| Octal digit validation (0-7 only) | `TestSection26IntegerLiterals` | `test_octal_integers` |
| Hex digit validation (0-9, a-f, A-F) | `TestSection26IntegerLiterals` | `test_hexadecimal_integers` |
| Float component optionality | `TestSection26FloatingPointLiterals` | `test_optional_components` |
| Exponent case insensitivity (e/E) | `TestSection26FloatingPointLiterals` | `test_exponent_notation` |
| Imaginary suffix case insensitivity (j/J) | `TestSection26ImaginaryLiterals` | `test_basic_imaginary_syntax` |
| No memory-based integer limits | `TestSection26CrossImplementationCompatibility` | `test_large_number_limits` |

## Test Structure

### Core Test Classes

1. **`TestSection26IntegerLiterals`** - Integer literal parsing (decimal, binary, octal, hex)
2. **`TestSection26FloatingPointLiterals`** - Float literal parsing including scientific notation  
3. **`TestSection26ImaginaryLiterals`** - Complex number literal parsing
4. **`TestSection26ErrorConditions`** - Invalid syntax and error cases
5. **`TestSection26CrossImplementationCompatibility`** - Implementation-specific behavior

### Test Strategy

**Positive Tests:** Valid literals that should parse successfully
- Basic syntax variations
- All grammar rule combinations  
- Valid underscore placement patterns
- Case sensitivity variations
- Large/small value edge cases

**Negative Tests:** Invalid literals that should raise `SyntaxError`
- Invalid digits for number bases
- Invalid underscore placement  
- Malformed syntax
- Forbidden leading zeros

**Cross-Implementation Tests:** Behavior that might vary
- Very large integer parsing
- Floating-point precision limits
- Version-specific features (Python 3.6+ underscores)

## Test Coverage Metrics

### Grammar Rules: 100% Coverage
- ✅ All integer base formats (decimal, binary, octal, hex)
- ✅ All float component variations (integer.fraction, .fraction, integer.)  
- ✅ All exponent notations (e/E, +/-, with/without decimal)
- ✅ All imaginary suffix variations (j/J with integer/float base)

### Prose Requirements: 100% Coverage  
- ✅ Leading zero restrictions tested
- ✅ Underscore placement rules validated
- ✅ Case sensitivity requirements verified
- ✅ Error condition specifications tested

### Edge Cases: Comprehensive
- ✅ Very large integers (1000+ digits)
- ✅ Very small/large floating-point values
- ✅ Complex underscore patterns
- ✅ All valid/invalid base prefix combinations
- ✅ Whitespace and formatting restrictions

## Running the Tests

### Prerequisites

```bash
pip install pytest
```

### Basic Execution

```bash
# Run all Section 2.6 tests
python -m pytest tests/conformance/section_2_6_numeric_literals.py -v

# Run specific test class
python -m pytest tests/conformance/section_2_6_numeric_literals.py::TestSection26IntegerLiterals -v

# Run with detailed output
python -m pytest tests/conformance/section_2_6_numeric_literals.py -v --tb=short
```

### Cross-Implementation Testing

```bash
# Test with different Python implementations
python3.10 -m pytest tests/conformance/section_2_6_numeric_literals.py
python3.11 -m pytest tests/conformance/section_2_6_numeric_literals.py
pypy3 -m pytest tests/conformance/section_2_6_numeric_literals.py
```

## Expected Results

### CPython (Reference Implementation)
All tests should pass. Any failures indicate either:
- Test bugs (incorrect expectations)
- CPython bugs (deviation from Language Reference)

### Alternative Implementations (PyPy, Jython, etc.)
Test failures indicate specification compliance issues:
- **FAIL**: Implementation doesn't conform to Language Reference
- **SKIP**: Feature not supported in this implementation version
- **PASS**: Implementation correctly follows specification

## Test Methodology 

### AST-Based Parsing
Tests use Python's `ast` module to parse literals:
```python
def parse_literal(self, literal: str) -> Union[int, float, complex]:
    tree = ast.parse(literal, mode='eval')
    return tree.body.value
```

**Why AST over `eval()`:**
- Security: No arbitrary code execution
- Precision: Only tests literal parsing, not evaluation
- Clarity: Direct access to parsed token values

### Error Detection Strategy
```python  
def assert_syntax_error(self, literal: str):
    with pytest.raises(SyntaxError):
        self.parse_literal(literal)
```

Tests verify that invalid literals raise `SyntaxError` during parsing, not runtime.

## Validation Against Language Reference

Each test maps directly to Language Reference requirements:

### Example: Underscore Rules
**Language Reference:** *"Underscores can only occur between digits"*

**Test Implementation:**
```python
def test_underscore_grouping_invalid(self, tester):
    # Leading underscores not allowed
    tester.assert_syntax_error("_123")        
    # Trailing underscores not allowed
    tester.assert_syntax_error("123_")        
    # Double underscores not allowed
    tester.assert_syntax_error("123__456")    
```

### Example: Base Prefix Validation  
**Language Reference:** *Binary integers use 0b or 0B prefix with binary digits only*

**Test Implementation:**
```python
def test_binary_integers(self, tester):
    # Valid binary literals
    tester.assert_parses_correctly("0b1010", 10)
    tester.assert_parses_correctly("0B1111", 15)
    # Invalid binary digits  
    tester.assert_syntax_error("0b2")  # 2 not valid in binary
    tester.assert_syntax_error("0ba")  # a not valid in binary
```

## Future Extensions

This test suite provides the foundation for expanding to other Language Reference sections:

### Section 2.7: Operators and Delimiters
- Similar formal grammar approach
- Token recognition validation
- Precedence and associativity testing

### Section 6: Expressions  
- Build on literal parsing
- Add expression evaluation validation
- Operator precedence conformance

### Section 7-8: Statements
- Syntax parsing for simple/compound statements  
- Semantic behavior validation
- Error condition testing

The patterns established in Section 2.6 (formal grammar + prose requirements + comprehensive edge cases) apply systematically across the entire Language Reference.