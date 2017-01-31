HERE = $(shell pwd)
BIN = $(HERE)/venv/bin
PYTHON = $(BIN)/python3

INSTALL = $(BIN)/pip install

KINTO_SERVER_URL = https://webextensions-settings.stage.mozaws.net:443
# KINTO_SERVER_URL = https://webextensions.settings.services.mozilla.com:443

.PHONY: all test build

all: build test

$(PYTHON):
	virtualenv --python python3 $(VTENV_OPTS) venv
	$(BIN)/pip install requests requests_hawk flake8
	$(BIN)/pip install molotov
build: $(PYTHON)

test: build
	bash -c "KINTO_SERVER_URL=$(KINTO_SERVER_URL) $(BIN)/molotov loadtest.py -c -v -d 10"
	$(BIN)/flake8 loadtest.py

test-heavy: build
	bash -c "KINTO_SERVER_URL=$(KINTO_SERVER_URL) $(BIN)/molotov loadtest.py -p 10 -w 200 -d 60 -qx"

clean:
	rm -fr venv/ __pycache__/ *.pyc

docker-build:
	docker build -t chartjes/kinto-loadtests .

docker-run: loadtest.env
	bash -c "docker run -e KINTO_DURATION=600 -e KINTO_NB_USERS=10 -e KINTO_SERVER_URL=$(KINTO_SERVER_URL) chartjes/kinto-loadtests"

configure: build
	@bash kinto.tpl

docker-export:
	docker save "chartjes/kint-loadtests:latest" | bzip2> kinto-latest.tar.bz2
