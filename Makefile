.PHONY: help lint format prune test check

help:
	@echo "make lint                  - type checking by mypy"
	@echo "make format                - format the code by black"
	@echo "make prune                 - remove unused imports by autoflake"
	@echo "make test                  - run tests by pytest"
	@echo "make check                 - run all the above commands"

lint:
	mypy --config-file mypy.ini --show-error-context --show-column-numbers --pretty .

format:
	black --exclude 'env' --verbose .

prune:
	autoflake --recursive --in-place --remove-unused-variables --remove-all-unused-imports --exclude "env" -v -v ./

test:
	pytest tests/*py

check:
	mypy --config-file mypy.ini .
	black --exclude 'env' .
	autoflake --recursive --in-place --remove-unused-variables --remove-all-unused-imports --exclude "env" ./
	pytest --quiet tests/*py
