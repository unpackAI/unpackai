# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/11_deploy.ipynb (unless otherwise specified).

__all__ = ['deploy', 'get_learner', 'get_image', 'PathStr', 'dummy_function', 'StreamlitApp', 'TEMPLATE_BASE', 'learn',
           'vocab', 'display_prediction', 'StreamlitAppCVClassif', 'TEMPLATE_CV_CLASSIFY', 'select']

# Cell
import json
import os
import pathlib
import re
import requests
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent
from typing import Union, ClassVar

import streamlit as st
from jinja2 import Template
from fastai.learner import load_learner, Learner
from fastai.vision.core import PILImage


# Cell
def deploy(app="app.py", from_jupyter=True):
    """Deploy a streamlit app using ngrok"""
    if from_jupyter:
        get_ipython().system_raw('ngrok http 8501 &')
        resp = requests.get("http://localhost:4040/api/tunnels")
        tunnel = json.loads(resp.content)["tunnels"][0]
        local = tunnel["config"]["addr"]
        public = tunnel["public_url"]
    else:
        raise NotImplementedError(f"Deployment outside jupyter currently not supported")

    print(dedent(f"""\
        1. Create a new cell with: !nohup streamlit run {app}
        2. Run that cell
        3. Click on this link: {public}

      Note: this will link to local address {local}
    """))

# Internal Cell
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


# Cell
PathStr = Union[Path, str]

def get_learner(model_path: PathStr) -> Learner:
    try:
        with set_posix():
            return load_learner(model_path)
    except AttributeError as e:
        m_missing_func = re.match(r"Can't get attribute '(.*?)'", str(e))
        if m_missing_func:
            raise AttributeError(
                f"Add in the app the implementation of '{m_missing_func.group(1)}'"
            )
        else:
            raise


@st.cache
def get_image(img: PathStr) -> PILImage:
    """Get picture from either a path or URL"""
    if str(img).startswith("http"):
        with tempfile.TemporaryDirectory() as tmpdirname:
            dest = Path(tmpdirname) / img.split("?")[0].rpartition("/")[-1]

            # NOTE: to be replaced by download(url, dest=dest) [from unpackai.utils]
            with requests.get(str(img)) as resp:
                resp.raise_for_status()
                dest.write_bytes(resp.content)

            return PILImage.create(dest)
    else:
        return PILImage.create(img)


# Cell
def dummy_function(*args, **kwargs):
    """Function that does absolutely nothing"""
    return None

# Cell
TEMPLATE_BASE = """
from pathlib import Path

import streamlit as st
from .deploy import get_learner, PathStr, dummy_function

st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("{{ title }}")
st.write("*by {{ author }}*")
st.write("---")

{{ implem_4_model }}

learn = get_learner("{{ model }}")
vocab = learn.dls.vocab
"""


@dataclass
class StreamlitApp:
    content: str = field(init=False, default="")
    _title: str = field(init=False, default="Streamlit App")
    TEMPLATE: ClassVar[str] = TEMPLATE_BASE

    def render(
        self, title: str, author: str, model: PathStr, implem_4_model: str
    ) -> "StreamlitApp":
        """Render an app based on template

        Args:
            title: title of the App
            author: author of the App
            model: path of .pkl model to load (exported with `learn.export(...)`)
            implem_4_model: extra implementations needed to load the model
                (e.g. function used for labelling)
        """
        self._title = title
        self.content = Template(self.TEMPLATE).render(
            title=title, author=author, model=model, implem_4_model=implem_4_model
        )
        return self

    def append(self, content:str) -> "StreamlitApp":
        """Add additional content to the app"""
        self.content += content
        return self

    def save(self, dest:PathStr):
        """Write the app to a file"""
        Path(dest).write_text(self.content, encoding="utf-8")
        print(f"Saved app '{self._title}' to '{dest}'")



# Cell
TEMPLATE_CV_CLASSIFY = TEMPLATE_BASE + """

from .deploy import get_image


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

"""

@dataclass
class StreamlitAppCVClassif(StreamlitApp):
    TEMPLATE: ClassVar[str] = TEMPLATE_CV_CLASSIFY