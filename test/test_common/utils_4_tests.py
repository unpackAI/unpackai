from difflib import unified_diff
from pathlib import Path
from typing import Union

import pytest
from pytest import LogCaptureFixture

TEST_DIR = Path(__file__).parent.parent
IMG_DIR = TEST_DIR / "img"
DATA_DIR = TEST_DIR / "test_data"

PathStr = Union[Path, str]


def compare_strings(
    exp: str,
    obt: str,
    name_exp: str = "Expected [string #1]",
    name_obt: str = "Obtained [string #2]",
) -> str:
    """Get unified diff of 2 string"""
    exp_lines = exp.splitlines(keepends=True)
    obt_lines = obt.splitlines(keepends=True)
    differences = unified_diff(exp_lines, obt_lines, fromfile=name_exp, tofile=name_obt)
    return "".join(differences)


def diff_files(exp: PathStr, obt: PathStr, encoding="utf-8", show=False) -> str:
    """Get unified diff of 2 files"""
    exp_str = Path(exp).read_text(encoding=encoding)
    obt_str = Path(obt).read_text(encoding=encoding)
    diff = compare_strings(exp_str, obt_str, name_exp=str(exp), name_obt=str(obt))
    if show:
        print(diff)
    return diff


def check_only_warning(caplog: LogCaptureFixture, sub_str: str):
    """Check that logging only contain warning and it contains a given substring"""
    assert caplog.records, f"There shall be at least one logged message"
    assert all(
        r.levelname == "WARNING" for r in caplog.records
    ), f"There shall be only warning (got {caplog.record_tuples})"
    assert sub_str in caplog.text, f"{sub_str} not found in {caplog.text}"


def check_no_log(caplog: LogCaptureFixture):
    """Check that there is nothing in logging"""
    assert (
        not caplog.records
    ), f"There should be no message but got {caplog.record_tuples}"
