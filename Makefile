.ONESHELL:
SHELL := /bin/bash
SRC = $(wildcard nbs/*.ipynb)

.PHONY: all build sync docs_serve version conda_release pypi release clean install help

# For generating content
build: unpackai test  ## generate code and tests [default command]

# We want the default to be just build so all is after it
all: build docs install  ## generate code, tests, and docs (NOT default)

install: unpackai  ## install unpackai locally
	@echo "===== INSTALL ====="
	pip install -e .

unpackai: $(SRC) settings.ini setup.py  ## generate code
	@echo "===== LIBRARY ====="
	nbdev_build_lib
	nbdev_clean_nbs.exe
	@touch unpackai

test: $(SRC)  ## generate tests
	python tools/test_extractor.py
	@touch test

sync:  ## update library (nbdev_update_lib)
	nbdev_update_lib


docs: $(SRC)  ## generate documentation
	@echo "===== DOCUMENTATION ====="
	nbdev_build_docs --mk_readme False
	python tools/clean_docs.py
	@touch docs


# For Release
docs/Gemfile.lock:
	@echo "===== INSTALL GEMS & LOCK ====="
	cd docs && bundle install

docs_serve: docs docs/Gemfile.lock  ## start Jekyll server
	@echo "===== RUN JEKYLL SERVER ====="
	cd docs && bundle exec jekyll serve

VERSION_PART = 3

version:  ## upgrade version number (use VERSION_PART=2 for major, VERSION_PART=3 for minor [default])
	@echo "===== BUMPING VERSION ====="
	git checkout settings.ini
	git checkout unpackai/__init__.py
	nbdev_bump_version --part $(VERSION_PART)

release: version pypi conda_release  ## push to pypi and conda

conda_release:  ## push to conda
	fastrelease_conda_package

pypi: dist  ## push to pypi
	twine upload --repository pypi dist/*

dist: clean  ## build distribution package
	@echo "===== DISTRIBUTION ====="
	python setup.py sdist bdist_wheel
	@echo "==Checking the build=="
	twine check dist/*

clean:  ## cleanup
	rm -rf dist

help:  ## list all the commands (this message)
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| sed -n 's/^\(.*\): \(.*\)##\(.*\)/* \1#\3/p' \
	| column -t -s '#'  -N "COMMAND, DESCRIPTION"
