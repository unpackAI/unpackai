import os
import pathlib
import re
import requests
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Union

import streamlit as st
from fastai.learner import load_learner, Learner
from fastai.vision.core import PILImage


PathStr = Union[Path, str]


@contextmanager
def set_posix():
    """To be able to load model in Windows"""
    posix_backup = pathlib.PosixPath
    try:
        if os.name == "nt":
            pathlib.PosixPath = pathlib.WindowsPath
        yield
    finally:
        pathlib.PosixPath = posix_backup


def get_learner(model_path: PathStr) -> Learner:
    try:
        with set_posix():
            return load_learner(model_path)
    except AttributeError as e:
        m_missing_func = re.match(r"Can't get attribute '(.*?)'", str(e))
        if m_missing_func:
            raise AttributeError(
                f"Add in the app the implementation of {m_missing_func.group(1)}"
            )
        else:
            raise


@st.cache
def get_image(img: PathStr) -> PILImage:
    """Get picture from either a path or URL"""
    if str(img).startswith("http"):
        with tempfile.TemporaryDirectory() as tmpdirname:
            dest = Path(tmpdirname) / url.split("?")[0].rpartition("/")[-1]

            # NOTE: to be replaced by download(url, dest=dest) [from unpackai.utils]
            with requests.get(str(img)) as resp:
                resp.raise_for_status()
                dest.write_bytes(resp.content)

            return PILImage.create(dest)
    else:
        return PILImage.create(pic)


is_cat = lambda x: None

st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("Image Classification for cat")
st.write("*by Jeff*")
st.write("---")

learn = get_learner(Path(__file__).with_name("model.pkl"))
vocab = learn.dls.vocab


def display_prediction(pic):
    img = get_image(pic)
    with learn.no_bar():
        prediction, _, probabilities = learn.predict(img)
    col_img, col_pred = st.columns(2)
    col_img.image(img, caption=getattr(pic, "name", None))
    col_pred.write(f"### {prediction}")
    col_pred.metric(f"Probability", f"{probabilities[1].item()*100:.2f}%")


select = st.radio("How to load pictures?", ["from URL", "from files"])
st.write("---")

if select == "from URL":
    url = st.text_input("url")
    if url:
        display_prediction(url)

else:
    pictures = st.file_uploader("Choose pictures", accept_multiple_files=True)
    for pic in pictures:  # type:ignore # this is an iterable
        display_prediction(pic)
