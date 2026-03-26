SHELL := /bin/bash
.SHELLFLAGS = -e -c
.DEFAULT_GOAL := help
.ONESHELL:
.SILENT:
MAKEFLAGS += --no-print-directory

SBCL := sbcl --noinform --non-interactive --eval '(require :asdf)' --eval '(push (truename ".") asdf:*central-registry*)'

.PHONY: help
help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: setup
setup: ## Install SBCL and Python dependencies
	@echo "Checking SBCL..."
	@which sbcl >/dev/null 2>&1 || (echo "SBCL not found. Install with: sudo apt install sbcl" && exit 1)
	@echo "SBCL: $$(sbcl --version)"
	@echo "Checking Python..."
	@which python3 >/dev/null 2>&1 || (echo "Python3 not found." && exit 1)
	@echo "Python: $$(python3 --version)"
	@if [ -f tests/conformance/pyproject.toml ]; then \
		cd tests/conformance && pip install -e . 2>/dev/null || pip install --user -e . ; \
	fi
	@echo "Setup complete."

.PHONY: build
build: ## Load and compile Clython
	$(SBCL) --eval '(asdf:load-system :clython)' --eval '(quit)'

.PHONY: test
test: ## Run unit tests
	$(SBCL) --eval '(asdf:test-system :clython)' --eval '(quit)'

.PHONY: conformance-cpython
conformance-cpython: ## Run conformance test suite against CPython (baseline)
	@cd tests/conformance && python3 -m pytest tests/ -v --tb=short --ignore=tests/conformance/test_clython_smoke.py

.PHONY: conformance-clython
conformance-clython: ## Run conformance test suite against Clython
	@cd tests/conformance && CLYTHON_BIN=$(CURDIR)/bin/clython python3 -m pytest tests/conformance/test_clython_smoke.py -v --tb=short

.PHONY: repl
repl: ## Start interactive Clython REPL
	$(SBCL) --eval '(asdf:load-system :clython)' --eval '(clython:repl)'

.PHONY: clean
clean: ## Remove build artifacts
	@find . -name "*.fasl" -delete
	@echo "Cleaned."
