VENV_BIN := venv/bin
PORT ?= 8000

.PHONY: deps\:update server\:start test 

# TODO: require python 3.9
venv: requirements/dev.txt
	python3 -m venv venv
	$(VENV_BIN)/pip install -U pip pip-tools
	$(VENV_BIN)/pip install -r requirements/dev.txt
	touch $@ # update timestamp in case the folder already existed

test:
	tox -q

deps\:install:
	$(VENV_BIN)/pip-sync requirements/dev.txt

deps\:update:
	$(VENV_BIN)/pip-compile requirements/lint.in
	$(VENV_BIN)/pip-compile requirements/dev.in
	$(VENV_BIN)/pip-compile requirements/prod.in
	make deps:install

server\:start:
	uvicorn variant_search.app:app --reload --reload-dir variant_search --port $(PORT) --host 0.0.0.0
