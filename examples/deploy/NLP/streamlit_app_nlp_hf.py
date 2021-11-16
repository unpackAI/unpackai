from pathlib import Path

import streamlit as st
from unpackai.deploy import PathStr, dummy_function

st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("Tabular Predictions trained with pycaret")
st.write("*by Jeff*")
st.write("---")


"""
The model shall have been saved with a flow similar to this one:
```python
from pycaret.regression import *

_ = setup(data = date_features=, target = target)
lr = create_model('lr')
lr_final = finalize_model(lr)
save_model(lr_final, 'model')
```
"""

import pandas as pd
from pycaret.regression import load_model, predict_model

model = load_model(Path(__file__).with_name("model.pkl"))

def get_predictions(csv:PathStr):
    df = pd.read_csv(csv)
    predictions = predict_model(model, data = df)
    st.dataframe(predictions)


select = st.radio("How to load CSV?", ["from URL", "from files"])
st.write("---")

if select == "from URL":
    url = st.text_input("url")
    if url:
        get_predictions(url)

else:
    csv = st.file_uploader("Choose CSV file")
    if csv:
        get_predictions(csv)

"""
If you make your model a subclass of PreTrainedModel, then you can use our methods save_pretrained and from_pretrained. Otherwise it’s regular PyTorch code to save and load (using torch.save and torch.load).
"""