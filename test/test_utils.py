"""Testing code generated by nbdev in unpackai/utils.py"""
# Generated automatically from notebook nbs/10_utils.ipynb

from unpackai.utils import *

# Test Cell
# For Test Cases (might have duplicate import because it will be in a dedicated file)
import requests
from datetime import datetime, timedelta
from pathlib import Path
from shutil import copy, rmtree
from typing import List

import graphviz
import numpy as np
import pandas as pd
import pytest
from PIL import Image
from test_common.utils_4_tests import DATA_DIR, IMG_DIR, check_no_log, check_only_warning

# Test Cell
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


# Test Cell
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
    (sub1 / "file12 haha.jpg").write_text("fake image")
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


# Test Cell
def test_find_static():
    error_report_html = STATIC / "html" / "bug" / "error_report.html"
    assert (error_report_html).is_file(), f"'{STATIC}' is not a valid static path"


# Test Cell
@pytest.mark.parametrize(
    "size,exp",
    [
        (0, "0.00 B"),
        (1, "1.00 B"),
        (1024, "1.00 KB"),
        (1024 ** 2, "1.00 MB"),
        (1024 ** 3 * 3.14, "3.14 GB"),
    ],
)
def test_friendly_size(size, exp):
    """Test computation of friendly size (human readable)"""
    assert friendly_size(size) == exp


# Test Cell
@pytest.fixture
def populated_tmp_dir(tmpdir):
    """Create files to test `ls` function"""
    tmpdir = Path(tmpdir)
    for dir_ in ["dir1/subdir1", "dir1/subdir2", "dir2"]:
        (tmpdir / dir_).mkdir(parents=True)
    for file in ["at_root.txt", "dir1/subdir1/at_subdir.txt", "dir2/at_dir.txt"]:
        (tmpdir / file).write_text("unpackai")
    (tmpdir / "dir1" / "subdir2" / "some_pickle.pkl").write_bytes(b"3141590000")

    return tmpdir


import numpy as np

exp_columns = [
    "Name",
    "Parent",
    "Path",
    "Level",
    "Last_Modif",
    "FileDir",
    "Extension",
    "Type",
    "Size",
    "Friendly_Size",
]


def test_ls(populated_tmp_dir):
    """Test DataFrame generated by `ls` function"""
    df = ls(populated_tmp_dir)
    now = datetime.now()
    assert list(df.columns) == exp_columns, "Incorrect columns in DF"

    # We want to copy the list of expecgted columns to keep it intact
    columns = exp_columns[:]

    assert all(now - timedelta(minutes=5) < date < now for date in df["Last_Modif"])
    df.drop("Last_Modif", axis=1, inplace=True)
    columns.remove("Last_Modif")

    # We check the file "at_root.txt" and do some cleanup
    at_root = df[df["Name"] == "at_root.txt"].iloc[0]
    assert Path(at_root["Path"]) == populated_tmp_dir.absolute() / "at_root.txt"
    assert at_root["Friendly_Size"] == friendly_size(at_root["Size"])
    df.drop(["Path", "Friendly_Size"], axis=1, inplace=True)
    columns.remove("Path")
    columns.remove("Friendly_Size")

    print("===TRUNCATED DF FOR LIST OF FILES/DIR===")
    print(df)
    print("=" * 20)

    exp_root_dir = populated_tmp_dir.name
    df_exp = pd.DataFrame(
        [
            ("at_root.txt", exp_root_dir, 0, "File", ".txt", "text/plain", 8.0),
            ("dir1", exp_root_dir, 0, "Dir", np.NaN, np.NaN, np.NaN),
            ("subdir1", "dir1", 1, "Dir", np.NaN, np.NaN, np.NaN),
            ("at_subdir.txt", "subdir1", 2, "File", ".txt", "text/plain", 8.0),
            ("subdir2", "dir1", 1, "Dir", np.NaN, np.NaN, np.NaN),
            ("some_pickle.pkl", "subdir2", 2, "File", ".pkl", None, 10.0),
            ("dir2", exp_root_dir, 0, "Dir", np.NaN, np.NaN, np.NaN),
            ("at_dir.txt", "dir2", 1, "File", ".txt", "text/plain", 8.0),
        ],
        columns=columns,
    )
    print("===EXPECTED DF FOR LIST OF FILES/DIR===")
    print(df_exp)
    print("=" * 20)

    compare_df = df.reset_index(drop=True).compare(df_exp.reset_index(drop=True))
    assert compare_df.empty, f"Differences found when checking DF:\n{compare_df}"


exp_files = [
    "at_root.txt",
    "dir1",
    "subdir1",
    "at_subdir.txt",
    "subdir2",
    "some_pickle.pkl",
    "dir2",
    "at_dir.txt",
]
exp_dir1 = ["at_root.txt", "dir2", "at_dir.txt"]
exp_dir2 = [
    "at_root.txt",
    "dir1",
    "subdir1",
    "subdir2",
    "at_subdir.txt",
    "some_pickle.pkl",
]
exp_subdir = ["at_root.txt", "dir1", "dir2", "subdir2", "some_pickle.pkl", "at_dir.txt"]
exp_dir2_subdir = ["at_root.txt", "dir1", "subdir2", "some_pickle.pkl"]


def test_ls_path_as_str(populated_tmp_dir):
    """Test `ls` function called with a string for path"""
    df = ls(str(populated_tmp_dir))
    assert sorted(df["Name"]) == sorted(exp_files)


@pytest.mark.parametrize(
    "exclude, exp",
    [
        ([], exp_files),
        (["I am not a Dir"], exp_files),
        (["dir1"], exp_dir1),
        (["dir2"], exp_dir2),
        (["subdir1"], exp_subdir),
        (["subdir1", "dir2"], exp_dir2_subdir),
    ],
)
def test_ls_exclude(exclude, exp, populated_tmp_dir):
    """Test `ls` function with an exclusion of some directories"""
    df = ls(populated_tmp_dir, exclude=exclude)
    assert sorted(df["Name"]) == sorted(exp)


def test_ls_no_info(populated_tmp_dir):
    """Test `ls` function with `hide_info` set to True"""
    df = ls(populated_tmp_dir, hide_info=True)
    assert set(exp_columns) - set(df.columns) == {"Size", "Friendly_Size"}


def test_ls_not_exist():
    """Test `ls` when path does not exist"""
    with pytest.raises(FileNotFoundError):
        ls("this_path_does_not_exist")


def test_not_dir(tmpdir):
    """Test `ls` if root is a file and not a dir"""
    file_path = Path(tmpdir) / "toto.txt"
    file_path.touch(exist_ok=True)
    with pytest.raises(FileNotFoundError):
        ls(file_path)


# Test Cell
@pytest.mark.parametrize("rankdir", [None, "LR", "TD"])
def test_gv(rankdir):
    """Test Graphviz Generation via `gv`"""
    src = "inputs->program->results"
    if rankdir is None:
        graph = gv(src)
        rankdir = "LR"  # default orientation
    else:
        graph = gv(src, rankdir=rankdir)

    assert isinstance(
        graph, graphviz.Source
    ), f"Output shall be a GraphViz Source (but is {type(graph)})"

    gv_src = graph.source
    assert gv_src.startswith("digraph"), f"Source is not a digraph: {gv_src}"
    assert src in gv_src, f"Source input not in Graph Source: {gv_src}"
    assert f'rankdir="{rankdir}"' in gv_src, f"Rankdir {rankdir} not found: {gv_src}"


# Test Cell
GITHUB_TEST_DATA_URL = (
    "https://raw.githubusercontent.com/unpackAI/unpackai/main/test/test_data/"
)
url_raw_txt = f"{GITHUB_TEST_DATA_URL}/to_download.txt"
test_data_txt = (DATA_DIR / "to_download.txt").read_text()


@pytest.fixture(scope="session")
def check_connection_github():
    try:
        with requests.request("HEAD", url_raw_txt, timeout=1) as resp:
            resp.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        pytest.xfail(f"Cannot connect to Github: {e}")


# Test Cell
@pytest.mark.github
def test_get_url_size(check_connection_github):
    assert get_url_size(url_raw_txt) == 264, f"Wrong size for {url_raw_txt}"


@pytest.mark.github
def test_download_dest(check_connection_github, tmpdir):
    """Test download of file to a destination"""
    dest = Path(tmpdir / "to_download.txt")
    download(url_raw_txt, dest)
    assert dest.is_file()
    assert dest.read_text() == test_data_txt


@pytest.mark.github
def test_download_empty(check_connection_github, tmpdir):
    """Test download of file without destination"""
    dest = Path("to_download.txt")
    download(url_raw_txt)
    try:
        assert dest.is_file()
        assert dest.read_text() == test_data_txt
    finally:
        dest.unlink()


@pytest.mark.github
def test_url_2_text(check_connection_github):
    """Test extraction of text from URL"""
    assert url_2_text(url_raw_txt) == test_data_txt


# Test Cell
url_ar = (
    r"https://alaska.usgs.gov/data/landBirds/sewardPeninsula/2012/"
    "avianHabitat_sewardPeninsula_McNew_2012.zip"
)


@pytest.mark.parametrize("url", [url_ar, url_ar + "?x=123"], ids=["url", "url?x=y"])
@pytest.mark.parametrize("dest", [None, "unzip_dir"], ids=["no dest", "dest"])
def test_download_and_unpack(url, dest, tmpdir):
    """Test download and unzip with `download_and_unpack`"""
    if dest is None:
        dest = Path(url.split("?")[0].rpartition("/")[-1]).stem

    extract_dir = Path(tmpdir / dest)
    download_and_unpack(url, extract_dir=extract_dir)

    df_files = ls(extract_dir)
    obt_files = {k: v for k, v in zip(df_files.Name, df_files.Size)}

    exp_files = {
        "avianHabitat_sewardPeninsula_McNew_2012.csv": 60617,
        "avianHabitat_sewardPeninsula_McNew_2012.html": 22883,
        "avianHabitat_sewardPeninsula_McNew_2012.xml": 14408,
    }
    assert (
        obt_files == exp_files
    ), f"Differences found in list of files:\n{obt_files}\nvs\n{exp_files}"


# Test Cell
LOCAL_ZIP_FLAT = DATA_DIR / "archive.zip"
LOCAL_TAR_FLAT = DATA_DIR / "archive.tar"
LOCAL_GZ_FLAT = DATA_DIR / "archive.tar.gz"
LOCAL_ZIP_FOLDER = DATA_DIR / "archived_folder.zip"
GITHUB_ZIP_FLAT = f"{GITHUB_TEST_DATA_URL}/archive.zip"
GITHUB_ZIP_FOLDER = f"{GITHUB_TEST_DATA_URL}/archived_folder.zip"


@pytest.mark.parametrize(
    "archive,csv",
    [
        (LOCAL_ZIP_FLAT, "100_rows.csv"),
        (LOCAL_TAR_FLAT, "100_rows.csv"),
        (LOCAL_GZ_FLAT, "100_rows.csv"),
        (LOCAL_ZIP_FOLDER, "archived_folder/100_rows (folder).csv"),
        (LOCAL_ZIP_FOLDER, "archived_folder/sub_folder/100_rows (subfolder).csv"),
    ],
    ids=["flat (zip)", "flat (tar)", "flat (tar.gz)", "folder", "subfolder"],
)
def test_read_csv_from_zip_local(archive, csv):
    """Test reading CSV from a local zip with read_csv_from_zip"""
    df = read_csv_from_zip(archive, csv)
    assert isinstance(df, pd.DataFrame), f"Result is not a DataFrame: {df}"
    assert len(df) == 100


@pytest.mark.github
@pytest.mark.parametrize(
    "archive,csv",
    [
        (GITHUB_ZIP_FLAT, "100_rows.csv"),
        (GITHUB_ZIP_FOLDER, "archived_folder/100_rows (folder).csv"),
        (GITHUB_ZIP_FOLDER, "archived_folder/sub_folder/100_rows (subfolder).csv"),
    ],
    ids=["flat", "folder", "subfolder"],
)
def test_read_csv_from_zip_github(archive, csv, check_connection_github):
    """Test reading CSV from a URL zip in GitHub with read_csv_from_zip"""
    df = read_csv_from_zip(archive, csv)
    assert isinstance(df, pd.DataFrame), f"Result is not a DataFrame: {df}"
    assert len(df) == 100


def test_read_csv_from_zip_url():
    """Test reading CSV from a URL zip with read_csv_from_zip"""
    url_ar = (
        r"https://alaska.usgs.gov/data/landBirds/sewardPeninsula/2012/"
        "avianHabitat_sewardPeninsula_McNew_2012.zip"
    )
    df = read_csv_from_zip(url_ar, "avianHabitat_sewardPeninsula_McNew_2012.csv")
    assert isinstance(df, pd.DataFrame), f"Result is not a DataFrame: {df}"
    assert len(df) == 1070


@pytest.mark.parametrize(
    "archive,csv,error",
    [
        ("does_not_exist.zip", "table.csv", FileNotFoundError),
        (LOCAL_ZIP_FLAT, "does_not_exist.csv", FileNotFoundError),
        (LOCAL_TAR_FLAT, "does_not_exist.csv", FileNotFoundError),
        (LOCAL_GZ_FLAT, "does_not_exist.csv", FileNotFoundError),
        (LOCAL_ZIP_FLAT, "not_a_csv.txt", AttributeError),
        (LOCAL_ZIP_FLAT, "not_a_csv", AttributeError),
        (DATA_DIR / "to_download.txt", "table.csv", AttributeError),
    ],
    ids=[
        "zip missing",
        "csv missing (zip)",
        "csv missing (tar)",
        "csv missing (tar.gz)",
        "not csv (extension)",
        "not csv (no extension)",
        "not archive",
    ],
)
def test_read_csv_from_zip_robustness(archive, csv, error):
    """Test robustness of read_csv_from_zip"""
    with pytest.raises(error):
        read_csv_from_zip(archive, csv)
