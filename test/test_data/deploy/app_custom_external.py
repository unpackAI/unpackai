from pathlib import Path

import streamlit as st

from unpackai.deploy.app import import_from_module


st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("Custom App")
st.write("*by Jeff*")
st.write("---")


make_predictions = import_from_module(
    Path(__file__).parent / "correct_code_for_custom_app.py",
    "make_predictions",
)
make_predictions()
