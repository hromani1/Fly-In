.PHONY: install run debug lint lint-strict clean

PYTHON := python3

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py

debug:
	$(PYTHON) -m pdb main.py

lint:
	flake8 .
	mypy . --ignore-missing-imports --warn-unused-ignores --check-untyped-defs --warn-return-any --disallow-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict --ignore-missing-imports

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	rm -rf */.mypy_cache
	rm -rf .mypy_cache
	rm -f *.pyc maze.txt validator_out.txt