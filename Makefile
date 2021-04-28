
.PHONY: test lint deps write-deps run-local-db l10n

test:
	python -m pytest -v

lint:
	pylint --ignore-patterns=test_.*?py bot/ server/
	pydocstyle bot/ server/

deps:
	pip install -r requirements.txt

# Must be run in virtual environment.
write-deps:
	pip freeze > requirements.txt

run-local-server:
	@echo Running in DEBUG mode, do not use in production!
	DBUSER=postgres DBPASSWORD=password DBHOST=0.0.0.0 python3 ./server/main.py -cp ${CONFIG_PATH}

run-client:
	python -m bot.main -v -cp ${CONFIG_PATH}

run-local-db:
	@echo Running in DEBUG mode, do not use in production!
	docker build -t lexibot-local-db --file local_db/Dockerfile .
	docker run --rm -p 5432:5432 --name lexibot-postgres -e POSTGRES_PASSWORD=password -d lexibot-local-db

stop-local-db:
	docker stop $(shell docker ps -a -q --filter="name=lexibot-postgres")

l10n:
	pybabel compile -D lexibot -i l10n/ru/LC_MESSAGES/lexibot.po -o l10n/ru/LC_MESSAGES/lexibot.mo

doc_html:
	mkdir -p ./docs/source/_static ./docs/source/_templates
	sphinx-build -M html "./docs/source" "./docs/doc_build"

