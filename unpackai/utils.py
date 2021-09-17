# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/10_utils.ipynb (unless otherwise specified).

__all__ = ['check_img', 'clean_error_img']

# Cell
from pathlib import Path
from tqdm.notebook import tqdm
import os
import logging
from typing import Callable, List
from PIL import Image

# Cell
def check_img(
    img: Path,
    formats: List[str] = [".jpg", ".jpeg", ".png", ".bmp"],
) -> None:
    """
    Check on a single image,
    If it's quality is troublesome
        we unlink/ditch the image
    """
    img = Path(img)
    # check if this path is an image
    if img.suffix.lower().split("?")[0] not in formats:
        return

    try:
        # try to open that image
        _ = Image.open(img).load()
    except Exception as e:
        if img.exists():
            img.unlink()
            logging.warning(f"removed error img: {img}")


def clean_error_img(
    path: Path,
    progress: bool = True,
) -> None:
    """
    - path: an image directory
    - progress: do we print out progress bar or not
        default True
    """
    path = Path(path)

    # check directory existence
    if path.exists() == False:
        raise FileExistsError(
            f"""path does not exists on:{path},
    make sure there is a directory "{path.name}".
    under directory "{path.parent}"
    """)

    # create iterator, probably with progress bar
    iterator = tqdm(list(path.iterdir()), leave=False)\
        if progress else path.iterdir()

    for obj in iterator:
        if obj.is_dir():
            # use recursion to clean the sub folder
            clean_error_img(obj, progress=progress)
        else:
            # cheking on a single image
            check_img(obj)