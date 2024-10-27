.PHONY: help clean format test lint

help:
	@echo "make lint    - type checking by mypy"
	@echo "make format  - format the code by autopep8"
	@echo "make clean   - remove unused imports by autoflake"
	@echo "make test    - run tests by pytest"

lint:
	mypy --config-file mypy.ini .

format:
	autopep8 --recursive --in-place --aggressive --exclude 'env' -v -v .

clean:
	autoflake --recursive --in-place --remove-unused-variables --remove-all-unused-imports --exclude "env" -v -v ./

test:
	pytest tests/*py
