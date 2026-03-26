SHELL := /bin/bash
.SHELLFLAGS = -e -c
.DEFAULT_GOAL := help
.ONESHELL:
.SILENT:
MAKEFLAGS += --no-print-directory

# Include .env if present
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

##@ Setup and Installation

.PHONY: setup
setup: ## Install dependencies and initialize environment
	python -m pip install --user -r requirements.txt
	mkdir -p data/pep_cache data/results tests/conformance
	echo '{"last_check": "2024-01-01T00:00:00"}' > data/last_check.json
	echo "✅ Environment setup complete"

.PHONY: clean
clean: ## Clean generated files and cache
	rm -rf data/pep_cache/* data/results/* tests/conformance/pep_*.py
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	echo "✅ Cleaned generated files"

##@ PEP Processing

.PHONY: check-peps
check-peps: ## Check for new PEPs since last run
	echo "🔍 Checking for new PEPs..."
	python scripts/fetch_new_peps.py

.PHONY: process-pep
process-pep: ## Process specific PEP (usage: make process-pep PEP=701)
	ifndef PEP
		$(error PEP number required: make process-pep PEP=701)
	endif
	echo "📋 Processing PEP $(PEP)..."
	python scripts/parse_pep_changes.py $(PEP) > data/pep_$(PEP)_changes.json
	python scripts/format_for_ai.py data/pep_$(PEP)_changes.json > data/pep_$(PEP)_prompt.txt
	echo "✅ PEP $(PEP) formatted for AI processing"
	echo "📄 Prompt saved to: data/pep_$(PEP)_prompt.txt"

.PHONY: process-new-peps
process-new-peps: ## Process all new PEPs found
	echo "🔄 Processing all new PEPs..."
	for pep in $$(python scripts/fetch_new_peps.py | jq -r '.[].number'); do \
		echo "Processing PEP $$pep..."; \
		$(MAKE) process-pep PEP=$$pep; \
	done
	echo "✅ All new PEPs processed"

##@ Testing

.PHONY: test
test: ## Run conformance test suite
	echo "🧪 Running conformance tests..."
	python scripts/run_conformance_tests.py | tee data/results/latest_results.json

.PHONY: test-section
test-section: ## Run tests for specific section (usage: make test-section SECTION=2.6)
	ifndef SECTION
		$(error Section required: make test-section SECTION=2.6)
	endif
	echo "🧪 Running tests for Section $(SECTION)..."
	python -m pytest tests/conformance/section_$(subst .,_,$(SECTION))*.py -v

.PHONY: benchmark
benchmark: ## Run implementation benchmarks
	echo "⚡ Running benchmarks..."
	python scripts/benchmark_implementations.py

##@ Development Workflow

.PHONY: weekly-check
weekly-check: ## Full weekly PEP check and test generation (for heartbeat)
	echo "📅 Starting weekly PEP processing..."
	$(MAKE) check-peps
	$(MAKE) process-new-peps
	$(MAKE) test
	$(MAKE) benchmark
	echo "✅ Weekly check complete"

.PHONY: generate-tests
generate-tests: ## Generate tests from processed PEP (usage: make generate-tests PEP=701)
	ifndef PEP
		$(error PEP number required: make generate-tests PEP=701)
	endif
	echo "🔨 Ready to generate tests for PEP $(PEP)"
	echo "📄 Use this prompt file: data/pep_$(PEP)_prompt.txt"
	echo "📁 Save generated tests to: tests/conformance/pep_$(PEP)_conformance.py"

.PHONY: validate-tests
validate-tests: ## Validate generated test syntax
	echo "✅ Validating test file syntax..."
	python -m py_compile tests/conformance/*.py
	echo "✅ All test files valid"

##@ Information

.PHONY: status
status: ## Show current status and recent activity
	echo "📊 Python Spec Test Suite Status"
	echo "================================="
	echo "Last check: $$(cat data/last_check.json | jq -r .last_check)"
	echo "Test files: $$(ls tests/conformance/*.py 2>/dev/null | wc -l)"
	echo "Cached PEPs: $$(ls data/pep_cache/ 2>/dev/null | wc -l)"
	echo ""
	if [ -f data/results/latest_results.json ]; then \
		echo "Latest test results:"; \
		cat data/results/latest_results.json | jq '{total_tests, passed, failed, timestamp}'; \
	else \
		echo "No test results yet - run 'make test'"; \
	fi

.PHONY: list-peps
list-peps: ## List processed PEPs
	echo "📋 Processed PEPs:"
	ls data/pep_*_changes.json 2>/dev/null | sed 's/.*pep_\(.*\)_changes.json/- PEP \1/' || echo "No PEPs processed yet"

##@ Utilities

.PHONY: install-dev
install-dev: ## Install development dependencies
	python -m pip install --user pytest pytest-json-report black flake8 mypy
	echo "✅ Dev dependencies installed"

.PHONY: format
format: ## Format code with black
	black scripts/ tests/
	echo "✅ Code formatted"

.PHONY: lint
lint: ## Lint code with flake8
	flake8 scripts/ tests/
	echo "✅ Code linted"

.PHONY: help
help: ## Display this help
	awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)