
.PHONY: test lint deps write-deps run-local-db

test:
	python -m pytest

lint:
	pylint --ignore-patterns=test_.*?py bot/ server/

deps:
	pip install -r requirements.txt

# Must be run in virtual environment.
write-deps:
	pip freeze > requirements.txt

run-local-server:
	python3 ./server/main.py -cp ${CONFIG_PATH}

run-local-db:
	docker build -t lexibot-local-db --file local_db/Dockerfile .
	docker run --rm -p 5432:5432 --name lexibot-postgres -e POSTGRES_PASSWORD=password -d lexibot-local-db

stop-local-db:
	docker stop $(shell docker ps -a -q --filter="name=lexibot-postgres")

doc_html:
	sphinx-build -M html "./docs/source" "./docs/doc_build"
