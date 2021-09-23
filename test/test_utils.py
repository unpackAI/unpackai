from unpackai.utils import *

# Internal Cell
from pathlib import Path
from shutil import copy

import pytest
from test.common.utils_4_tests import IMG_DIR, check_no_log, check_only_warning

# Internal Cell

images_rob = list((IMG_DIR / "robustness").glob("*.*"))

@pytest.mark.parametrize("img", images_rob, ids=[i.name for i in images_rob])
def test_check_img_error(img:Path, tmpdir, caplog):
    """Check check_img with incorrect images"""
    img_copy = tmpdir / img.name
    copy(img, img_copy)
    check_img(img_copy)
    check_only_warning(caplog, img.name)


def test_check_img_empty_wrong_suffix(tmpdir, caplog):
    """Check check_img with wrong image that does not have a correct extension"""
    img = Path(tmpdir) / "empty.txt"
    img.write_bytes(b"")
    check_img(img)
    check_no_log(caplog)