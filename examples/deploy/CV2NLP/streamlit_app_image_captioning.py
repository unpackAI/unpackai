from pathlib import Path
from typing import Optional

import streamlit as st
import torch
from torch import nn
from tokenizers import Tokenizer
from torchvision import transforms as tfm
from transformers import AutoTokenizer, EncoderDecoderModel
from unpackai.deploy.cv import get_image


st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("Image Captioning")
st.write("*by unpackAI*")
st.write("---")


# name of the folder with pre-trained model for encoder/decoder
NAME_MODEL = "en-de-coder"


class Caption(nn.Module):
    """The caption model is created by combining decoder and encoder [by unpackAI]"""

    def __init__(self, encoder: nn.Module, decoder: nn.Module):
        """
        - encoder: The encoder model that can extract image features
        - decoder: The decoder model that can generate text sequence
            - you have to set add_cross_attention
                to True when instantiate the model
        """
        super().__init__()
        self.encoder_decoder = EncoderDecoderModel(
            encoder=encoder,
            decoder=decoder,
        )

        # update generate documentation
        self.generate.__func__.__doc__ = f"""
        Generate text with image:
        - batch_img: a batch of image tensor
        - other generate kwargs please see following
        {self.encoder_decoder.decoder.generate.__doc__}"""

    def forward(self, inputs):
        x, input_ids = inputs
        # extract image feature with encoder
        # the extracted feature we call them: encoder_outputs
        encoder_outputs = self.encoder_decoder.encoder(x)

        # predict text sequence logits
        # with the encoder_outputs
        seq_out = self.encoder_decoder(
            encoder_outputs=encoder_outputs,
            # decoder_inputs is to help decoders learn better,
            # decoder has mask that allow model to see
            # only the previous text tokens and encoder feature
            decoder_input_ids=input_ids,
            labels=input_ids,
        )
        return seq_out

    def generate(self, batch_img, **generate_kwargs):
        with torch.no_grad():
            # extract image features first
            encoder_outputs = self.encoder_decoder.encoder(pixel_values=batch_img)
            return self.encoder_decoder.decoder.tokenizer.batch_decode(
                # encoder_decoder has a 'generate' function we can use
                self.encoder_decoder.generate(
                    encoder_outputs=encoder_outputs, **generate_kwargs
                ),
            )


@st.cache(hash_funcs={Tokenizer: hash})
def get_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    # tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


@st.cache(suppress_st_warning=True)
def get_model(pretrained: Path):
    with st.empty():
        st.write("Loading model ...")
        encoder_decoder = EncoderDecoderModel.from_pretrained(pretrained)

        tokenizer = get_tokenizer()
        encoder_decoder.decoder.tokenizer = tokenizer

        model = Caption(encoder=encoder_decoder.encoder, decoder=encoder_decoder.decoder)

    st.write("✔️ Model loaded")
    st.write("---")
    st.balloons()

    return model


INPUT_MEAN = [0.5, 0.5, 0.5]
INPUT_STD = [0.5, 0.5, 0.5]


@st.cache
def image_2_caption(img, captioning: Caption) -> str:
    """Get caption from an image (need "model" and "tokenizer")"""
    image_to_batch = tfm.Compose(
        [tfm.Resize((224, 224)), tfm.ToTensor(), tfm.Normalize(INPUT_MEAN, INPUT_STD)]
    )

    batch = image_to_batch(img)[None, :]
    vocab = captioning.encoder_decoder.decoder.tokenizer.vocab

    return captioning.generate(
        batch,
        top_p=0.6,
        do_sample=True,  # text generation strategy
        bos_token_id=vocab[":"],
    )[0].replace("<|endoftext|>", "").strip(": ")


def display_prediction(pic, captioning: Caption):
    img = get_image(pic)
    caption = image_2_caption(img, captioning)
    col_img, col_pred = st.columns(2)
    col_img.image(img, caption=getattr(pic, "name", None))
    col_pred.write(f"### {caption}")


captioning = get_model(Path(__file__).parent / NAME_MODEL)

if captioning:
    select = st.radio("How to load pictures?", ["from files", "from URL"])
    st.write("---")

    if select == "from URL":
        url = st.text_input("url")
        if url:
            display_prediction(url, captioning=captioning)

    else:
        pictures = st.file_uploader("Choose pictures", accept_multiple_files=True)
        for pic in pictures:  # type:ignore # this is an iterable
            display_prediction(pic, captioning=captioning)
