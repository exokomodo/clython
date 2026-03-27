SHELL := /bin/bash
.SHELLFLAGS = -e -c
.DEFAULT_GOAL := help
.ONESHELL:
.SILENT:
MAKEFLAGS += --no-print-directory

UNAME_S := $(shell uname -s)

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
PYTEST ?= $(PYTHON) -m pytest
VENV ?= $(PYTHON) -m venv
VENV_DIR := venv
SBCL := sbcl --noinform --non-interactive --eval '(require :asdf)' --eval '(push (truename ".") asdf:*central-registry*)'

##@ Environment Setup

.PHONY: setup
setup: setup/python setup/sbcl ## Install all development dependencies

.PHONY: setup/python
setup/python: ## Install Python dependencies for conformance testing
	if ! which -a python3 >/dev/null 2>&1; then
		echo "Python not found. Please install Python >= 3 and try again."
		exit 1
	fi
	if $(VENV) $(VENV_DIR); then
		echo "Created virtual environment in $(VENV_DIR)"
		. $(VENV_DIR)/bin/activate
	fi
	cd tests/conformance
	$(PIP) install -e .

.PHONY: setup/sbcl
setup/sbcl: ## Install SBCL
ifeq ($(UNAME_S),Linux)
	sudo apt update && sudo apt install -y sbcl
else ifeq ($(UNAME_S),Darwin)
	brew install sbcl
else
	$(error "Unsupported OS: $(UNAME_S). Please install SBCL manually.")
endif

##@ Development Tasks

.PHONY: build
build: ## Load and compile Clython
	$(SBCL) --eval '(asdf:load-system :clython)' --eval '(quit)'

.PHONY: clean
clean: ## Remove build artifacts
	find . -name "*.fasl" -delete
	echo "Cleaned"

.PHONY: repl
repl: ## Start interactive Clython REPL
	$(SBCL) --eval '(asdf:load-system :clython)' --eval '(clython:repl)'

.PHONY: test
test: test/unit ## Run CL tests

.PHONY: test/unit
test/unit: ## Run CL unit tests
	$(SBCL) --eval '(asdf:load-system :clython-tests)' --eval '(clython.test:run-all-tests)'

##@ Conformance Testing

.PHONY: conformance-cpython
conformance-cpython: ## Run conformance test suite against CPython (baseline)
	if [[ -f $(VENV_DIR)/bin/activate ]]; then
		. $(VENV_DIR)/bin/activate
	fi
	cd tests/conformance
	$(PYTEST) tests/ -v --tb=short --ignore=tests/conformance/test_clython_smoke.py

.PHONY: conformance-clython
conformance-clython: ## Run conformance test suite against Clython
	if [[ -f $(VENV_DIR)/bin/activate ]]; then
		. $(VENV_DIR)/bin/activate
	fi
	cd tests/conformance
	CLYTHON_BIN=$(CURDIR)/bin/clython $(PYTEST) tests/conformance/test_clython_smoke.py -v --tb=short

##@ Utilities

.PHONY: help
help: ## Show available targets
	awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
