from unpackai.utils import *

# Internal Cell
# For Test Cases (might have duplicate import because it will be in a dedicated file)
from pathlib import Path
from shutil import copy, rmtree

import pytest
from PIL import Image
from test_common.utils_4_tests import IMG_DIR, check_no_log, check_only_warning

# Internal Cell

images_rob = list((IMG_DIR / "robustness").glob("*.*"))
IMG_RGB = Image.new("RGB", (60, 30), color=(73, 109, 137))
IMG_RGBA = Image.new("RGBA", (60, 30), color=(73, 109, 137, 100))

@pytest.mark.parametrize("img", images_rob, ids=[i.name for i in images_rob])
def test_check_img_error(img: Path, tmpdir, caplog):
    """Test check_img with incorrect images"""
    img_copy = Path(tmpdir) / img.name
    copy(img, img_copy)
    check_img(img_copy)
    check_only_warning(caplog, img.name)
    assert not img_copy.is_file(), f"File {img_copy} not be deleted"


def test_check_img_empty_wrong_suffix(tmpdir, caplog):
    """Test check_img with wrong image that does not have a correct extension"""
    img_path = Path(tmpdir) / "empty.txt"
    img_path.write_bytes(b"")
    check_img(img_path)
    check_no_log(caplog)
    assert img_path.is_file(), f"Image {img_path} not found"


@pytest.mark.parametrize("img", [IMG_RGB, IMG_RGBA])
@pytest.mark.parametrize("ext", ["png", "bmp", "jpg", "jpeg"])
def test_check_img_correct(img: Image, ext: str, tmpdir, caplog):
    """Correct that correct image is not removed"""
    alpha_suffix = "_alpha" if len(img.getcolors()[0][1]) == 4 else ""
    if alpha_suffix and ext.startswith("jp"):
        pytest.skip("JPG does not support RGBA")

    img_path = Path(tmpdir) / f"correct_image_blue{alpha_suffix}.{ext}"
    img.save(img_path)
    check_img(img_path)
    check_no_log(caplog)
    assert img_path.is_file(), f"Image {img_path} not found"


# Internal Cell

def test_clean_error_img(tmpdir, monkeypatch) -> None:
    """Test clean_error_img"""
    for img in images_rob:
        copy(img, Path(tmpdir) / img.name)

    monkeypatch.chdir(tmpdir)
    root = Path(".")

    sub1 = root / "sub1"
    sub2 = root / "sub2"
    sub1.mkdir()
    sub2.mkdir()
    sub3 = sub2 / "sub3"
    sub3.mkdir()


    (sub1 / "file11.BMP").write_text("fake image")
    (sub1/"😱file12 haha.jpg").write_text("fake image")
    (sub1 / "file13 haha.txt").write_text("not image")
    IMG_RGB.save(sub1 / "img14_good.jpg")
    IMG_RGBA.save(sub1 / "img15_good.png")

    (sub2 / "file21.jpg").write_text("fake image")
    (sub2 / "file22.jpeg").write_text("fake image")

    (sub3 / "file31.jpeg").write_text("fake image")
    IMG_RGB.save(sub3 / "img32_good.jpeg")
    IMG_RGBA.save(sub3 / "img33_good.bmp")


    good: List[Path] = list()
    bad: List[Path] = list()

    print("Existing files:")
    for file in root.rglob("*.*"):
        print(f" * {file}")
        if file.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
            (good if "good" in file.name else bad).append(file)

    print(" => CLEANING")
    clean_error_img(root, progress=False)

    good_removed = [f for f in good if not f.is_file()]
    assert not good_removed, f"Good pictures deleted: {good_removed}"

    bad_still_here = [f for f in bad if f.is_file()]
    assert not bad_still_here, f"Bad pictures not deleted: {bad_still_here}"

