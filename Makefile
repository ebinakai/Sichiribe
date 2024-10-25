.PHONY: format test

help:
	@echo "format - format the code"
	@echo "test - run tests"

format:
	autopep8 -v --in-place --aggressive --exclude 'env/**' **/*.py

test:
	pytest tests/*py
