.PHONY: help lint format type-check sort-imports check-files fix-files check-all clean

# Default target
help:
	@echo "Available targets:"
	@echo "  lint          - Run ruff linter"
	@echo "  format        - Run ruff formatter"
	@echo "  type-check    - Run mypy type checker"
	@echo "  sort-imports  - Run isort to sort imports"
	@echo "  check-files   - Check for trailing whitespace, end-of-file, large files"
	@echo "  fix-files     - Fix trailing whitespace and end-of-file issues"
	@echo "  check-all     - Run all checks (lint, type-check, sort-imports, check-files)"
	@echo "  fix-all       - Run all fixes (format, sort-imports, fix-files)"
	@echo "  clean         - Remove __pycache__ and .pyc files"

# Linting with ruff
lint:
	ruff check .

# Formatting with ruff
format:
	ruff format .

# Type checking with mypy
type-check:
	mypy .

# Sort imports with isort
sort-imports:
	isort .

# Check for file issues (trailing whitespace, end-of-file, large files)
check-files:
	@echo "Checking for trailing whitespace..."
	@! grep -r '[[:space:]]$$' --exclude-dir=".venv" --include="*.py" --include="*.yaml" --include="*.yml" --include="*.md" --include="*.txt" . || (echo "Found trailing whitespace" && exit 1)
	@echo "Checking for files without final newline..."
	@find . -not -path "./.venv/*" \( -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" -o -name "*.txt" \) | while read file; do \
		if [ -s "$$file" ] && [ "$$(tail -c1 "$$file" | wc -l)" -eq 0 ]; then \
			echo "File missing final newline: $$file"; \
			exit 1; \
		fi; \
	done
	@echo "Checking for large files..."
	@find . -not -path "./.venv/*" -type f -size +500k -not -path "./.git/*" -not -path "./__pycache__/*" | while read file; do \
		echo "Large file found: $$file"; \
		exit 1; \
	done || true

# Fix file issues (trailing whitespace and end-of-file)
fix-files:
	@echo "Fixing trailing whitespace..."
	@find . -not -path "./.venv/*" \( -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" -o -name "*.txt" \) | xargs sed -i 's/[[:space:]]*$$//'
	@echo "Fixing end-of-file newlines..."
	@find . -not -path "./.venv/*" \( -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" -o -name "*.txt" \) | while read file; do \
		if [ -s "$$file" ] && [ "$$(tail -c1 "$$file" | wc -l)" -eq 0 ]; then \
			echo "" >> "$$file"; \
		fi; \
	done

# Run all checks
check-all: lint type-check check-files
	@echo "All checks completed"

# Run all fixes
fix-all: format sort-imports fix-files
	@echo "All fixes applied"

# Clean up Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
