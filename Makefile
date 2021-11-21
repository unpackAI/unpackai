.ONESHELL:
SHELL := /bin/bash
SRC = $(wildcard nbs/*.ipynb)

.PHONY: all build sync docs_serve version conda_release pypi release clean install

# For generating content
build: unpackai test

# We want the default to be just build so all is after it
all: build docs install

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
	nbdev_clean_nbs.exe
	nbdev_build_docs --mk_readme False
	python tools/clean_docs.py
	@touch docs


# For Release
docs/Gemfile.lock:
	@echo "===== INSTALL GEMS & LOCK ====="
	cd docs && bundle install

docs_serve: docs docs/Gemfile.lock
	@echo "===== RUN JEKYLL SERVER ====="
	cd docs && bundle exec jekyll serve

VERSION_PART = 3

version:
	@echo "===== BUMPING VERSION ====="
	git checkout settings.ini
	git checkout unpackai/__init__.py
	nbdev_bump_version --part $(VERSION_PART)

release: version pypi conda_release

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