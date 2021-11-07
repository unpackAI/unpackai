import logging
import re
from pathlib import Path
from typing import Any, Dict, Union

import nbformat
from black import Mode, Report, TargetVersion, WriteBack, reformat_one, reformat_code
from nbdev.export import find_default_export, get_config

PathLike = Union[Path, str]
NoteBook = Dict[str, Any]  # nbformat.NotebookNode
Cell = Dict[str, str]  # nbformat.NotebookNode


def read_nb(path: PathLike) -> NoteBook:
    "Read the notebook from path (improvement of function in nbdev"
    nb_content = Path(path).read_text(encoding="utf8")
    return nbformat.reads(nb_content, as_version=4)


_PAT_EXPORT_TEST = re.compile(r"^\s*#\s*export{1,2}est.*?$", flags=re.M | re.I)
_PAT_TEST = re.compile(r"^(class Test|def test_|import pytest|from pytest)", flags=re.M)


def is_test_export(cell: Cell, idx: int = None) -> bool:
    """Check if a cell shall be exported to Tests"""
    source = cell["source"]
    if _PAT_EXPORT_TEST.search(source):
        return True

    if _PAT_TEST.search(source):
        cell_loc = f"Cell #{idx}" if idx else "Cell"
        lines = source.splitlines()
        max_nb = 5
        if len(lines) > max_nb:
            source = "\n".join(lines[:max_nb]) + "\n[...]"
        logging.warning(
            f"Please check {cell_loc} that contains tests but is not exported."
            f"\n------\n{source}\n------"
        )
    return False


def format_cell_test_code(cell: Cell) -> str:
    """Get the code of cell for Test"""
    # Note: on Windows, we have the EOL \r that we need to remove
    source = _PAT_EXPORT_TEST.sub("", cell["source"]).replace("\r", "")
    return f"# Test Cell\n{source.strip()}"


TEST_TEMPLATE = '''\
"""Testing code generated by nbdev in {module_path}"""
# Generated automatically from notebook {nb_path}

from {module} import *

{test_sources}
'''


def black_format(code_path: Path, line_length=90) -> None:
    """Format code with black formatter"""
    check = False
    diff = False

    write_back = WriteBack.from_configuration(check=check, diff=diff, color=True)
    report = Report(check=check, diff=diff, quiet=False, verbose=True)
    mode = Mode(
        target_versions={TargetVersion.PY37},
        line_length=line_length,
        is_pyi=False,
        is_ipynb=False,
        string_normalization=True,
        magic_trailing_comma=False,
        experimental_string_processing=False,
    )

    reformat_one(
        src=code_path, fast=True, write_back=write_back, mode=mode, report=report
    )
    # TODO: explore how to format a string and return the formatted string
    # (i.e. with reformat_code)


def extract_tests(nb_path: PathLike):
    """Extract Tests from a Notebook for cells containing # exportest"""
    nb = read_nb(nb_path)

    root = get_config().config_path
    TEST_ROOT = root / "test"

    package_root = get_config().path("lib_path")
    package_path = package_root.relative_to(root)
    package = str(package_path)

    default = find_default_export(nb["cells"])
    if default is None:
        print(f"{nb_path}: No export default found => SKIPPED")
        return

    module = f"{package}.{default}"
    module_path = package_path.joinpath(*default.split(".")).with_suffix(".py")

    test_path = TEST_ROOT.joinpath(*default.split("."))
    test_path = test_path.with_name(f"test_{test_path.name}.py")

    test_sources = [
        format_cell_test_code(cell)
        for idx, cell in enumerate(nb["cells"])
        if is_test_export(cell, idx=idx)
    ]

    if not test_sources:
        print(f"{nb_path}: No Test cases => SKIPPED")
        return

    # We need to use "/" in paths to avoid weird excaped characters
    test_code = TEST_TEMPLATE.format(
        module_path=module_path.as_posix(),
        nb_path=Path(nb_path).resolve().relative_to(root).as_posix(),
        module=module,
        test_sources="\n\n".join(test_sources),
    )

    # We need to create the directory and a __init__.py if needed
    # Note: we need __init__.py to allow files with same name in different folders
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.with_name("__init__.py").write_text("")
    test_path.write_text(test_code, encoding="utf-8")
    black_format(test_path)

    print(f"{nb_path}: tests to {test_path.relative_to(root)} => EXTRACTED")


if __name__ == "__main__":
    root = Path(__file__).parent.parent
    nb_dir = root / "nbs"
    for nb_path in nb_dir.glob("*.ipynb"):
        extract_tests(nb_path)
