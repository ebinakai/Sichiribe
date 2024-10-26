.PHONY: format test help

help:
	@echo "make format - format the code by autopep8"
	@echo "make test   - run pytest"

format:
	autopep8 -v --in-place --aggressive --exclude 'env/**' **/*.py

test:
	pytest tests/*py
