VIRTUAL_ENV ?= .venv
VENV_PYTHON ?= python3.6
BUILD_ID ?= latest
TEST_IMAGE = localhost/neo4jbatcher-test:$(BUILD_ID)
TEST_CONTAINER = tmp-neo4jbatcher-test-$(BUILD_ID)

default: lint test


# running stuff locally in a venv
$(VIRTUAL_ENV):
	$(VENV_PYTHON) -m venv $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pip install -r requirements-dev.txt

lint: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/flake8

test: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pytest -v

dist: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python setup.py sdist bdist_wheel

publish: dist
	$(VIRTUAL_ENV)/bin/twine upload dist/*


# running tests in docker
build-test-image:
	docker build -f Dockerfile-test --tag $(TEST_IMAGE) .

run-test-image: build-test-image
	docker run --rm -t --name $(TEST_CONTAINER) $(TEST_IMAGE)
