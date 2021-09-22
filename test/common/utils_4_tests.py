from pathlib import Path
import pytest
from pytest import LogCaptureFixture

IMG_DIR = Path(__file__).parent.parent / "img"


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
