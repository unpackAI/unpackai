# Contributing

Welcome! Happy to see you willing to make the project better! 🎉🥳

This is how we generate the code:

1. Code is written inside Jupyter Notebooks to allow exploration (folder **nbs**)

2. Code and Documentation is then generated in folder **unpackai** by using `nbdev`
    * nbdev_build_lib
    * nbdev_clean_nbs
    * nbdev_build_docs --mk_readme False

3. Because `nbdev` does not managed well Test Cases that we want to extract in external files, we need to run a script to move the Test Cases in a dedicated folder:
`python test/extract_tests.py`

4. (not yet implemented) Run `black` (https://github.com/psf/black) on code in **unpackai** and folder **test** to format the code nicely

NOTES:

* [README.md](README.md) is not managed by `nbdev` so it does not have be identical to **docs/index.html**
* Cells with tests in Notebooks shall have the following characteristics:
  * start by a comment `# exporti`
  * either contain `import pytest` or define a test function/class (`def test_xxx` or `class Testxxx`)
