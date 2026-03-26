# Documentation

This directory contains all documentation and specifications for the Python Language Reference Conformance Test Suite.

## Structure

### `sections/`
Section-specific documentation files containing the implementation rationale, Language Reference quotes, and test design decisions for each Python Language Reference section.

**Format:** `SECTION_X_Y_DOCUMENTATION.md` where X.Y matches the Language Reference section number.

**Example sections:**
- `SECTION_2_1_DOCUMENTATION.md` - Line structure and logical lines
- `SECTION_6_2_DOCUMENTATION.md` - Atoms (literals, identifiers, enclosures)
- `SECTION_8_4_DOCUMENTATION.md` - Try statements and exception handling

Each documentation file includes:
- Direct quotes from the Python Language Reference
- Implementation rationale for test design decisions
- Examples of tested syntax patterns
- Cross-references to related Language Reference sections

### Root Documentation

- **`VERSION_AWARE_TESTING.md`** - Methodology for testing Python version-specific features
- **`README.md`** (this file) - Documentation structure overview

## Usage

### For Test Implementation
When implementing tests for a new Language Reference section, first read the corresponding documentation file to understand:
- What aspects of the specification need validation
- How similar patterns were tested in other sections  
- Version compatibility considerations

### For Test Maintenance
When the Python Language Reference changes:
1. Update the appropriate section documentation with new quotes/requirements
2. Implement corresponding test changes based on updated documentation
3. Ensure version-aware testing markers are updated per `VERSION_AWARE_TESTING.md`

### For Cross-Implementation Validation
The documentation explains the AST-based testing approach that enables the test suite to work across multiple Python implementations (CPython, PyPy, GraalPy) without modification.

## Documentation Philosophy

**Specification-First**: Every test traces back to specific Language Reference requirements documented here.

**AI-Assisted Maintenance**: Documentation provides structured context for AI systems to generate and maintain tests while preserving human design decisions.

**Cross-Implementation Focus**: Documentation emphasizes testing approaches that work across Python implementations rather than implementation-specific behaviors.