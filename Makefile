
.PHONY: test lint deps write-deps

test:
	pytest

lint:
	pylint bot/ server/

deps:
	pip install -r requirements.txt

# Must be run in virtual environment.
write-deps:
	pip freeze > requirements.txt
