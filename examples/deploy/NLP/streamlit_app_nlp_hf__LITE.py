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

# ---

PathOrURL = Union[Path, str]


@st.cache
def get_text(context: PathOrURL) -> str:
    """Cached version to get text only once"""
    # We will extract the text from path or URL
    if isinstance(context, Path):
        return Path(__file__).parent.joinpath(context).read_text(encoding="utf-8")
    elif isinstance(context, str):
        return context
    else:
        raise AttributeError(f"Incorrect context: {context}")


def make_nlp_predictions(input_text: str):
    """Make and display predictions"""
    # === TO BE IMPLEMENTED ===
    # We will use the a default context but it can be customized
    context = Path(__file__).with_name("Economics_Wikipedia.txt")
    text = get_text(context)
    sentences = text.splitlines()

    found_sentences = [
        (i, s) for i, s in enumerate(sentences) if input_text.lower() in s.lower()
    ]
    # === END OF CUSTOM IMPLEMENTATION ===

    for i, sentence in found_sentences:
        with st.expander(f"Sentence #{i+1}: {shorten(sentence, width=80)}"):
            st.caption("".join(s for s in sentences[max(0, i - 2) : i]))
            st.write(f"**{sentence}**")
            st.caption("".join(s for s in sentences[i + 1 : i + 3]))


# === END CUSTOM IMPLEM ===


st.subheader("Search")
input_text = st.text_input("Enter your question")

st.write("---")

st.subheader("Results")
if input_text:
    make_nlp_predictions(input_text=input_text)