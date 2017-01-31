<font color='red'>This repo is deprecated.</font>

<font color='red'>For Kinto loadtests, please see:</font>

http://github.com/Kinto/kinto-loadtests




# ailoads-kinto

Kinto loadtest based on ailoads

## Requirements

- Python 3.4


## How to run the loadtest?

### For stage

    make test

or for a longer one:

    make test-heavy

### You can change the destination URL

    make test -e KINTO_SERVER_URL=https://kinto.dev.mozaws.net:443


## How to build the docker image?

    make docker-build


## How to run the docker image?

    make docker-run


## How to clean the repository?

    make clean
