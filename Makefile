SHELL :=/bin/bash

.PHONY: clean check setup
.DEFAULT_GOAL=help
VENV_DIR = .venv
# Use the system's default python command - critical for Arch Linux
PYTHON_VERSION = python

check: # Ruff check
	@source $(VENV_DIR)/bin/activate && ruff check .
	@echo "✅ Check complete!"

fix: # Fix auto-fixable linting issues
	@source $(VENV_DIR)/bin/activate && ruff check . --fix

clean: # Clean temporary files
	@rm -rf __pycache__ .pytest_cache .ruff_cache $(VENV_DIR)
	@find . -name '*.pyc' -exec rm -r {} +
	@find . -name '__pycache__' -exec rm -r {} +
	@rm -rf build dist
	@find . -name '*.egg-info' -type d -exec rm -r {} +

run: # Run the application
	@source $(VENV_DIR)/bin/activate && streamlit run app.py

setup: # Initial project setup
	@echo "Creating virtual env at: $(VENV_DIR) using $(PYTHON_VERSION)"
	@$(PYTHON_VERSION) -m venv $(VENV_DIR)
	@echo "Installing dependencies..."
	@source $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -r requirements/requirements-dev.txt && pip install -r requirements/requirements.txt
	@echo -e "\n✅ Done.\n🎉 Run the following commands to get started:\n\n ➡️ source $(VENV_DIR)/bin/activate\n ➡️ playwright install-deps\n ➡️ playwright install\n ➡️ make run\n"

help: # Show this help
	@egrep -h '\s#\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'