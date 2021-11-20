from pathlib import Path

import streamlit as st
from unpackai.deploy.cv import get_image, get_learner

st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("Image Classification for cat")
st.write("*by Jeff*")
st.write("---")

# is_cat is the function used in original model for labelling
# Trying to load the model without it defined would lead to an error.
# We can just assign to a dummy function (using an implementation provided by unpackai)
# ... the same might apply to custom functions / classes, or elements defined in fastai
# is_cat = dummy_function

learn = get_learner(Path(__file__).with_name("model.pkl"))
vocab = learn.dls.vocab


def display_prediction(pic):
    img = get_image(pic)
    with learn.no_bar():
        prediction, idx, probabilities = learn.predict(img)
    col_img, col_pred = st.columns(2)
    col_img.image(img, caption=getattr(pic, "name", None))
    col_pred.write(f"### {prediction}")
    col_pred.metric(f"Probability", f"{probabilities[idx].item()*100:.2f}%")


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
