from pathlib import Path

import streamlit as st

st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("Question Answering")
st.write("*by Jeff*")
st.write("---")


# === Custom implem ===
from pathlib import Path
from textwrap import shorten
from typing import Union

# Ideally: it would be nice to be able to import text from URL by using unpackai
# from unpackai.utils import url_2_text
# ... temporarily, we will replace by implementation here
# ---
import requests


def url_2_text(url: str) -> str:
    """Extract text content from an URL (textual content for an HTML)"""
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ConnectionError(f"Error when retrieving text content from {url}")

    resp.encoding = "utf-8"
    content_type = resp.headers["Content-Type"]
    return resp.text


# ---

PathOrURL = Union[Path, str]


@st.cache
def get_text(context: PathOrURL) -> str:
    """Cached version to get text only once"""
    # We will extract the text from path or URL
    if str(context).lower().startswith("http"):
        return url_2_text(context)
    elif isinstance(context, Path):
        return (Path(__file__).parent / context).read_text(encoding="utf-8")
    elif isinstance(context, str):
        return context
    else:
        raise AttributeError(f"Incorrect context: {context}")


def make_nlp_predictions(input_text: str, context: PathOrURL = None):
    """Make and display predictions"""
    # We will use the a default context but it can be customized
    if context is None:
        context = Path(__file__).with_name("Economics_Wikipedia.txt")
    text = get_text(context)
    sentences = text.splitlines()

    found_sentences = [
        (i, s) for i, s in enumerate(sentences) if input_text.lower() in s.lower()
    ]
    for i, sentence in found_sentences:
        with st.expander(f"Sentence #{i+1}: {shorten(sentence, width=80)}"):
            st.caption("".join(s for s in sentences[max(0, i - 2) : i]))
            st.write(f"**{sentence}**")
            st.caption("".join(s for s in sentences[i + 1 : i + 3]))


# === END CUSTOM IMPLEM ===

st.subheader("Context")
select = st.radio("How to select context?", ["default", "from file", "from URL", "from text"])

if select == "default":
    context = None
elif select == "from URL":
    context = st.text_input("url")
elif select == "from file":
    file = st.file_uploader("Choose TXT file (with one sentence per line)")
    context = Path(file.name) if file else ""
else:
    context = st.text_area("Enter your text, one sentence per line")

st.write("---")

st.subheader("Search")
input_text = st.text_input("Enter your question")

st.write("---")

st.subheader("Results")
if input_text:
    make_nlp_predictions(input_text=input_text, context=context)
