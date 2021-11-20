.ONESHELL:
SHELL := /bin/bash
SRC = $(wildcard nbs/*.ipynb)

.PHONY: all all_and_docs sync docs_serve conda_release pypi clean install

# For generating content
build: unpackai test
all: build docs

install: unpackai
	@echo "===== INSTALL ====="
	pip install -e .

unpackai: $(SRC) settings.ini setup.py
	@echo "===== LIBRARY ====="
	nbdev_build_lib
	nbdev_clean_nbs.exe
	@touch unpackai

test: $(SRC)
	python tools/test_extractor.py
	@touch test

sync:
	nbdev_update_lib


docs: $(SRC)
	@echo "===== DOCUMENTATION ====="
	nbdev_build_docs --mk_readme False
	python tools/clean_docs.py
	@touch docs


# For Release
docs_serve: docs
	@echo "===== RUN JEKYLL SERVER ====="
	cd docs && bundle exec jekyll serve

release: pypi conda_release
	nbdev_bump_version

conda_release:
	fastrelease_conda_package

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	@echo "===== DISTRIBUTION ====="
	python setup.py sdist bdist_wheel
	@echo "==Checking the build=="
	twine check dist/*

clean:
	rm -rf dist