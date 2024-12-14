.PHONY: help lint format prune test docs check

help:
	@echo "make lint                  - type checking by mypy"
	@echo "make format                - format the code by black"
	@echo "make prune                 - remove unused imports by autoflake"
	@echo "make test                  - run tests by pytest"
	@echo "make docs                  - generate documentation by pdoc"
	@echo "make check                 - run all the above commands"

lint:
	mypy --config-file pyproject.toml --show-error-context --show-column-numbers --pretty .

format:
	black --exclude 'env' --verbose .

prune:
	autoflake --recursive --in-place --remove-unused-variables --remove-all-unused-imports --exclude "env" -v -v ./

test:
	pytest --log-level=DEBUG tests/*py

docs:
	mv train _train
	mv tests _tests
	mkdir -p html
	pdoc --template-dir docs_template --html --force .
	rm -rf docs && mv html/sichiribe docs && rm -r html
	cp res/favicon.ico docs
	mv _train train
	mv _tests tests
	
check:
	mypy --config-file pyproject.toml .
	black --exclude 'env' .
	autoflake --recursive --in-place --remove-unused-variables --remove-all-unused-imports --exclude "env" ./
	pytest --quiet tests/*py
