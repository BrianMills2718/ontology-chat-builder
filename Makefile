# Ontology Chat Builder Makefile
#
# Usage: make help

SHELL := /bin/bash
.DEFAULT_GOAL := help

# ─── Development ─────────────────────────────────────────────────────────

.PHONY: lint install

lint:  ## Run ruff linter
	@ruff check . 2>/dev/null || true

install:  ## Install in editable mode
	@pip install -e . 2>/dev/null || true

# ─── Help ────────────────────────────────────────────────────────────────

.PHONY: help

help:  ## Show available targets
	@echo "Ontology Chat Builder"
	@echo ""
	@grep -E '^[a-z][-a-zA-Z0-9_]*:.*## ' $(MAKEFILE_LIST) | \
		awk -F ':.*## ' '{printf "  make %-20s %s\n", $$1, $$2}'
