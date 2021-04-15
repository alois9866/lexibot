
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
	DBUSER=postgres DBPASSWORD=password DBHOST=127.0.0.1 BOT_TOKEN_HASH=2ef7674cc6723b5ab3f0bd43b22c66eb00a9ce58f50bcf9fbdf296628db0b8d1 python3 ./server/main.py

run-local-db:
	docker build -t lexibot-local-db --file local_db/Dockerfile .
	docker run --rm -p 5432:5432 --name lexibot-postgres -e POSTGRES_PASSWORD=password -d lexibot-local-db

stop-local-db:
	docker stop $(shell docker ps -a -q --filter="name=lexibot-postgres")

doc_html:
	sphinx-build -M html "./docs"/source "./docs/doc_build"
