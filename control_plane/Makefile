PYTHON ?= python3
PORT ?= 8000

.PHONY: run unit_tests e2e_tests viz help

# Defaults (can be overridden on the make command line)
UTIL ?= 1.0
FORMAT ?= text

run:
	@if [ -z "$(INPUT)" ]; then echo "Error: INPUT is required. Usage: make run INPUT=path/to/file.csv"; exit 1; fi
	$(PYTHON) -m src.main --input $(INPUT) --utilization $(UTIL) --format $(FORMAT)

unit_tests:
	$(PYTHON) -m pytest -q tests

e2e_tests:
	@echo "Running end-to-end test: CSV output comparison"
	$(PYTHON) tests/e2e.py

viz:
	@echo "Starting visualization server on http://localhost:$(PORT)"
	@echo "Press Ctrl+C to stop"
	cd ui && $(PYTHON) -m http.server $(PORT)

help:
	@echo "make run INPUT=path/to/file.csv [UTIL=1.0] [FORMAT=text] - run program (INPUT required)"
	@echo "make unit_tests - run unit tests with pytest"
	@echo "make e2e_tests - run end-to-end tests"
	@echo "make viz [PORT=8000] - start visualization server"
