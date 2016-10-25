HERE = $(shell pwd)
BIN = $(HERE)/venv/bin
PYTHON = $(BIN)/python3.4

INSTALL = $(BIN)/pip install

KINTO_SERVER_URL = https://kinto.stage.mozaws.net:443
KINTO_EXISTING_EMAIL =

.PHONY: all test build

all: build test

$(PYTHON):
	$(shell basename $(PYTHON)) -m venv $(VTENV_OPTS) venv
	$(BIN)/pip install requests requests_hawk flake8
	$(BIN)/pip install https://github.com/mozilla/PyFxA/archive/loadtest-tools.zip
	$(BIN)/pip install https://github.com/tarekziade/ailoads/archive/master.zip
build: $(PYTHON)

test: build
	bash -c "KINTO_SERVER_URL=$(KINTO_SERVER_URL) $(BIN)/ailoads -v -d 30"
	$(BIN)/flake8 loadtest.py

test-heavy: build
	bash -c "KINTO_SERVER_URL=$(KINTO_SERVER_URL) $(BIN)/ailoads -v -d 300 -u 10"

clean: refresh
	rm -fr venv/ __pycache__/ *.pyc

docker-build:
	docker build -t kinto/loadtest .

docker-run: loadtest.env
	bash -c "docker run -e KINTO_DURATION=600 -e KINTO_NB_USERS=10 -e KINTO_SERVER_URL=$(KINTO_SERVER_URL) kinto/loadtest"

configure: build
	@bash kinto.tpl

docker-export:
	docker save "kinto/loadtest:latest" | bzip2> kinto-latest.tar.bz2
