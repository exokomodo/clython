#!/bin/bash
# Build the Clython standalone binary using SBCL
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT="${PROJECT_DIR}/clython"

echo "Building Clython binary..."
sbcl --non-interactive \
  --eval '(require :asdf)' \
  --eval "(push #p\"${PROJECT_DIR}/\" asdf:*central-registry*)" \
  --eval '(asdf:load-system :clython)' \
  --eval "(sb-ext:save-lisp-and-die \"${OUTPUT}\" :toplevel #'clython.cli:main :executable t)"

echo "Built: ${OUTPUT}"
