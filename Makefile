VENV_PATH ?= .venv
BUILD_ID ?= latest
TEST_IMAGE = localhost/neo4jbatcher-test:$(BUILD_ID)
TEST_CONTAINER = tmp-neo4jbatcher-test-$(BUILD_ID)

default: lint test


# running stuff locally in a venv
$(VENV_PATH):
	python3.6 -m venv $(VENV_PATH)
	$(VENV_PATH)/bin/pip install -r requirements-dev.txt

lint: $(VENV_PATH)
	$(VENV_PATH)/bin/flake8

test: $(VENV_PATH)
	$(VENV_PATH)/bin/pytest -v

dist: $(VENV_PATH)
	$(VENV_PATH)/bin/python setup.py sdist bdist_wheel

publish: dist
	$(VENV_PATH)/bin/twine upload dist/*


# running tests in docker
build-test-image:
	docker build -f Dockerfile-test --tag $(TEST_IMAGE) .

run-test-image: build-test-image
	docker run --rm -t --name $(TEST_CONTAINER) $(TEST_IMAGE)
