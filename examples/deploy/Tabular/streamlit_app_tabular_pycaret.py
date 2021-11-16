from pathlib import Path

import streamlit as st

st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("Tabular Predictions trained with pycaret")
st.write("*by Jeff*")
st.write("---")

"""
The model shall have been created and saved with a flow similar to this one:
```python
from pycaret.regression import *

_ = setup(data = date_features=, target = target)
lr = create_model('lr')
lr_final = finalize_model(lr)
save_model(lr_final, 'model')
```
"""
st.write("---")

import pandas as pd
from pycaret.regression import load_model, predict_model

model = load_model(Path(__file__).parent / "model")


def get_predictions(csv):
    df = pd.read_csv(csv)
    predictions = predict_model(model, data=df)
    st.dataframe(predictions)


select = st.sidebar.radio("How to load CSV?", ["from file", "from URL"])
st.sidebar.write("---")

if select == "from URL":
    url = st.sidebar.text_input("url")
    if url:
        get_predictions(url)

else:
    csv = st.sidebar.file_uploader("Choose CSV file")
    if csv:
        get_predictions(csv)
