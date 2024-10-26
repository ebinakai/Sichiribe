.PHONY: help autoremove format test

help:
	@echo "make mypy       - run mypy for type checking"
	@echo "make format     - format the code by autopep8"
	@echo "make autoremove - remove unused imports by autoflake"
	@echo "make test       - run pytest"

mypy:
	mypy --config-file mypy.ini .

format:
	autopep8 -v --in-place --aggressive --exclude 'env/**' **/*.py

autoremove:
	autoflake --recursive --in-place --remove-all-unused-imports --exclude "env" -v -v ./

test:
	pytest tests/*py
