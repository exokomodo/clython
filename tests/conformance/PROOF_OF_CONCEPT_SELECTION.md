# Proof of Concept Section Selection

## Decision: Section 2.6 - Numeric Literals

After thorough analysis of the Python Language Reference structure and current testing landscape, **Section 2.6 (Numeric Literals)** has been selected for the initial proof of concept implementation.

## Justification

### 1. Clear Testable Assertions
**Formal grammar provided:** Section 2.6 includes complete BNF definitions for all numeric literal types:
```
NUMBER: integer | floatnumber | imagnumber
integer: decinteger | bininteger | octinteger | hexinteger | zerointeger
floatnumber: digitpart "." [digitpart] [exponent] | "." digitpart [exponent] | digitpart exponent
imagnumber: (floatnumber | digitpart) ("j" | "J")
```

**Explicit rules:** Every aspect has concrete validation criteria:
- Underscore placement restrictions
- Base prefix requirements  
- Character validity rules
- Case sensitivity specifications

### 2. Manageable Scope
**Three distinct subtypes:** Integer, float, and imaginary literals can be tackled incrementally
**Finite rule set:** Unlike syntax parsing, numeric literal validation has bounded complexity
**Clear boundaries:** Well-defined separation from other language features

### 3. Foundational Importance
**Universal implementation requirement:** Every Python implementation must handle numeric literals correctly
**Cross-implementation consistency critical:** Differences in number parsing break program portability  
**Early parsing stage:** Lexical analysis happens before syntax parsing, making errors here catastrophic

### 4. Specification vs Implementation Testing Gap
**Current CPython tests:** Focus on implementation correctness and edge cases
**Missing specification tests:** No systematic validation against Language Reference prose
**Clear compliance criteria:** Unambiguous pass/fail for conformance testing

## Detailed Analysis of Section 2.6

### 2.6.1 Integer Literals
**Testable assertion categories:**

#### Base Prefix Validation
- `0b` / `0B` prefix requires binary digits (0-1)  
- `0o` / `0O` prefix requires octal digits (0-7)
- `0x` / `0X` prefix requires hex digits (0-9, a-f, A-F)
- Leading zeros forbidden in decimal (e.g., `0123` is invalid)

#### Underscore Grouping Rules
- "Underscores can only occur between digits"
- Forbidden patterns: `_123`, `123_`, `123__321`, `0x_`, `0_x123`
- Allowed patterns: `1_000_000`, `0x_dead_beef`, `0b_1010_1010`

#### Character Set Validation
- Decimal: digits 0-9 only
- Binary: digits 0-1 only  
- Octal: digits 0-7 only
- Hexadecimal: digits 0-9, letters A-F (case insensitive)

### 2.6.2 Floating-Point Literals
**Testable assertion categories:**

#### Component Requirements
- Integer part, decimal point, fraction part - any two can be omitted, not all three
- Valid: `10.`, `.001`, `1e3`, `3.14`, `2.0e-5`
- Invalid: `.`, `e5` (missing both integer and fraction)

#### Exponent Notation Rules
- `e` or `E` followed by optional `+` or `-` and digit sequence
- Case insensitivity: `1e3` ≡ `1E3`
- Sign requirement: `1e+5` and `1e-5` both valid

#### Underscore Placement
- Same rules as integers apply to all numeric parts
- Valid: `3.14_15_93`, `1e1_000`, `1_000.5_00`

### 2.6.3 Imaginary Literals  
**Testable assertion categories:**

#### Suffix Requirements
- `j` or `J` suffix (case insensitive)
- Must be immediately attached: `3j` valid, `3 j` invalid
- Can follow integer or float syntax: `5j`, `3.14j`, `1e10j`

#### Base Number Parsing
- Number before `j` follows float literal rules exactly
- Valid: `4.2j`, `10.j`, `.001j`, `1e100j`
- Decimal point omission allowed with integer: `10j` ≡ `10.j`

## Test Extraction Plan

### Phase 1: Grammar Rule Conversion
**Direct BNF mapping:** Convert formal grammar definitions to parser test cases
```python
def test_integer_binary_prefix():
    """Test binary integer literal parsing per Section 2.6.1"""
    valid_cases = ['0b1010', '0B1111', '0b_1010_1010']
    invalid_cases = ['0b2', '0b_', '_0b1010', '0b']
    
    for case in valid_cases:
        assert parse_number(case).type == "binary_integer"
    
    for case in invalid_cases:
        with pytest.raises(SyntaxError):
            parse_number(case)
```

### Phase 2: Prose Assertion Extraction
**Natural language rules:** Convert English statements to test cases
```python
def test_underscore_placement_rules():
    """Test underscore grouping rules per Section 2.6.1 prose"""
    # From: "Underscores can only occur between digits"
    forbidden = ['_123', '123_', '123__321', '0x__', '0_x123']
    
    for literal in forbidden:
        with pytest.raises(SyntaxError, match="invalid.*underscore"):
            parse_number(literal)
```

### Phase 3: Cross-Implementation Validation  
**Multiple Python implementations:** Test against CPython, PyPy, Jython
```python
@pytest.mark.parametrize("implementation", ["cpython", "pypy", "jython"])
def test_numeric_literal_consistency(implementation):
    """Verify consistent numeric literal behavior across implementations"""
    test_cases = load_conformance_test_suite("section_2_6")
    
    for case in test_cases:
        result = run_on_implementation(implementation, case.code)
        assert result == case.expected_result
```

### Phase 4: Specification Edge Cases
**Boundary conditions:** Test limits mentioned in Language Reference
```python
def test_specification_edge_cases():
    """Test edge cases specifically mentioned in Language Reference"""
    # From: "There is no limit for the length of integer literals 
    # apart from what can be stored in available memory"
    very_large_int = "7922816251426433759354395033679228162514264337593543950336"
    assert isinstance(parse_number(very_large_int), int)
    
    # From: "Leading zeros in a non-zero decimal number are not allowed"
    with pytest.raises(SyntaxError):
        parse_number("0123")
```

## Implementation Framework

### Test Generation Pipeline
1. **Grammar parser:** Convert BNF rules → test case templates
2. **Assertion extractor:** Parse prose → testable requirements  
3. **Example harvester:** Extract code samples → positive test cases
4. **Error mapper:** Map exception specs → negative test cases
5. **Cross-validator:** Run tests against multiple implementations

### Success Criteria
- **Complete coverage:** Every rule in Section 2.6 has corresponding tests
- **Implementation agnostic:** Tests pass on CPython, PyPy, and other implementations  
- **Specification focused:** Tests validate Language Reference compliance, not implementation details
- **Clear failure reporting:** Failed tests clearly indicate which specification rule was violated

## Expected Outcomes

### Proof of Concept Validation
- **Feasibility demonstration:** Prose-to-test conversion works for numeric literals
- **Framework validation:** Test generation pipeline handles formal and informal specifications
- **Quality assessment:** Generated tests catch real implementation differences
- **Scaling readiness:** Approach proven applicable to other Language Reference sections

### Immediate Value
- **Implementation validation:** Verify numeric literal handling across Python implementations
- **Regression prevention:** Test suite catches specification compliance bugs
- **Documentation clarity:** Highlights ambiguities requiring Language Reference clarification  
- **Community contribution:** Reusable test suite for all Python implementation teams

## Next Steps After Proof of Concept

1. **Expand to Section 2.7 (Operators and Delimiters):** Similar formal grammar structure
2. **Tackle Section 6 (Expressions):** More complex but still grammar-heavy
3. **Address Section 3 (Data Model):** Transition to prose-heavy specification
4. **Develop full automation:** Complete prose-to-test extraction pipeline
5. **Integration with Python development:** Contribution to official test infrastructure

Section 2.6 provides the optimal balance of testability, importance, and scope for proving this approach works before scaling to the complete Language Reference.