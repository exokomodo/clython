# Clython

A Python interpreter implemented in Common Lisp.

Built by [ExoKomodo](https://github.com/exokomodo), validated against the
[Python Language Reference Conformance Test Suite](https://github.com/soniccyclops-bot-collab/python-spec-test-suite).

## Architecture

```
src/
├── lexer.lisp        # Tokenization
├── parser.lisp       # AST generation
├── ast.lisp          # AST node definitions
├── runtime.lisp      # Python object model + evaluation
├── scope.lisp        # LEGB scoping
├── builtins.lisp     # Python built-in functions
└── clython.lisp      # Main interface + REPL
```

## Target

Clython targets **Python 3.12** semantics. The conformance test suite is pinned
to CPython 3.12.x.

## Requirements

- SBCL (Steel Bank Common Lisp)
- Python 3.12 (for conformance test runner)
- GNU Make

## Usage

```bash
make setup       # Install dependencies
make test        # Run unit tests
make conformance-clython  # Run conformance tests against Clython
make conformance-cpython  # Run conformance tests against CPython (baseline)
make repl        # Interactive Clython REPL
```

## Conformance

The `tests/conformance/` directory contains the Python Language Reference
conformance test suite (1,412 tests). Progress is tracked via GitHub issues
mapped to Language Reference sections.

## License

CC0 1.0 Universal — see [LICENSE](LICENSE).
