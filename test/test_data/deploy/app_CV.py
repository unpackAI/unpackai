from pathlib import Path

import streamlit as st


from unpackai.deploy.cv import get_image, get_learner, dummy_function


st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("Is it a cat?")
st.write("*by Jeff*")
st.write("---")

is_cat = dummy_function

learn = get_learner(Path(__file__).parent / "model.pkl")
vocab = learn.dls.vocab


def display_prediction(pic):
    img = get_image(pic)
    with learn.no_bar():
        prediction, idx, probabilities = learn.predict(img)
    col_img, col_pred = st.columns(2)
    col_img.image(img, caption=getattr(pic, "name", None))
    col_pred.write(f"### {prediction}")
    col_pred.metric(f"Probability", f"{probabilities[idx].item()*100:.2f}%")


select = st.sidebar.radio("How to load images?", ["from files", "from URL"])
st.sidebar.write("---")

if select == "from URL":
    url = st.sidebar.text_input("url")
    if url:
        display_prediction(url)

else:
    files = st.sidebar.file_uploader("Choose images", accept_multiple_files=True)
    for file in files:  # type:ignore # this is an iterable
        display_prediction(file)

st.sidebar.write("---")
st.sidebar.button("Show Balloons", on_click=st.balloons)
