.ONESHELL:
SHELL := /bin/bash
SRC = $(wildcard nbs/*.ipynb)

.PHONY: all all_and_docs sync docs_serve conda_release pypi clean install

# For generating content
all: unpackai test
all_and_docs: all docs

install: unpackai
	pip install -e .

unpackai: $(SRC) settings.ini setup.py
	nbdev_build_lib
	nbdev_clean_nbs.exe
	touch unpackai

test: $(SRC)
	python test/test_extractor.py
	touch test

sync:
	nbdev_update_lib


docs: $(SRC)
	nbdev_build_docs --mk_readme False
	touch docs


# For Release
docs_serve: docs
	cd docs && bundle exec jekyll serve

release: pypi conda_release
	nbdev_bump_version

conda_release:
	fastrelease_conda_package

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel
	@echo "==Checking the build=="
	twine check dist/*

clean:
	rm -rf dist