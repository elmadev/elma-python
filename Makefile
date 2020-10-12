.PHONY: setup
setup:
	pip install -r requirements.txt

.PHONY: test
test:
	python -m unittest

.PHONY: lint
lint:
	flake8 elma tests

.PHONY: mypy
mypy:
	mypy elma tests
