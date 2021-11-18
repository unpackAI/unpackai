from pathlib import Path

import streamlit as st


import pandas as pd
from pycaret.regression import load_model, predict_model


st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("My Mini Tabular App")
st.write("*by Jeff*")
st.write("---")

model = load_model("model")


def display_prediction(csv):
    df = pd.read_csv(csv)
    predictions = predict_model(model, data=df)
    st.dataframe(predictions)


select = st.sidebar.radio("How to load CSV?", ["from file", "from URL"])
st.sidebar.write("---")

if select == "from URL":
    url = st.sidebar.text_input("url")
    if url:
        display_prediction(url)

else:
    file = st.sidebar.file_uploader("Choose CSV")
    if file:
        display_prediction(file)
