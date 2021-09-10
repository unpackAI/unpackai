# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/40_nlp.ipynb (unless otherwise specified).

__all__ = ['Textual', 'InterpEmbeddings', 'InterpEmbeddingsTokenizer']

# Cell
from bs4 import BeautifulSoup
import requests
import logging
from ipywidgets import interact, interact_manual, FileUpload
from pathlib import Path
from forgebox.html import DOM

import numpy as np
import pandas as pd
from .cosine import CosineSearch
from typing import Dict, List

# Cell
class Textual:
    """
    Obtain and manage textual data
    """

    def __init__(self, text: str):
        self.text = text.replace("\n", " ").replace("\r", "")

    def __repr__(self) -> str:
        return f"""Text ({len(self.text)} chars), textual(),
    train_path, val_path = textual.create_train_val()"""

    def __call__(self, page_size: int = 1000) -> None:
        """
        Previewing the first 200(or less) pages
        - page_size: character number each page
        """
        logging.info(f"Previewing the first 200 pages")

        @interact
        def show_text(page=(0, min(len(self.text)//page_size-1, 200), 1)):
            display(self.text[page*page_size: (page+1)*page_size])

    @classmethod
    def from_url(cls, url: str):
        res = requests.get(url)
        if res.status_code == 200:
            res.encoding = 'utf-8'
            headers = res.headers
            if "html" in str(headers).lower():
                text = BeautifulSoup(res.text).text
            else:
                text = res.text
            obj = cls(text)
            obj.path = "./text_data.txt"
            with open(obj.path, "w") as f:
                f.write(obj.text)
            return obj
        else:
            raise ConnectionError(f"Error downloading: {url}")

    @classmethod
    def from_path(cls, path: Path):
        """
        Load a textual object from system path
        """
        if Path(path).exists() == False:
            raise FileExistsError(f"Can not find {path}")
        with open(path, ) as f:
            obj = cls(f.read())
            obj.path = path
            return obj

    @classmethod
    def from_upload(
        cls,
        path: Path = Path("./uploaded_file.txt")
    ):
        """
        Load textual with interactive upload button
        """
        DOM("🗃 Please upload a text file ended in .txt", "h4")()
        my_manual = interact_manual.options(manual_name="Upload")
        @my_manual
        def create_upload(btn_upload = FileUpload(description="Choose File")):
            text = list(btn_upload.values())[-1]['content'].decode()
            with open(path, "w") as f:
                f.write(text)
            return path
        def uploaded():
            result = create_upload.widget.result
            if result is None:
                raise FileExistsError(
                    "You have to upload the txt file first")
            return cls.from_path(result)
        return uploaded


    def create_train_val(
            self,
            valid_ratio=.2,
            train_path="./train_text.txt",
            val_path="./val_text.txt"):
        """
        create 2 files:
        - ./train_text.txt
        - ./val_text.txt
        """
        split = int(len(self.text)*(valid_ratio))
        with open(train_path, "w") as f:
            f.write(self.text[split:])
        with open(val_path, "w") as f:
            f.write(self.text[:split])
        return train_path, val_path

# Cell
class InterpEmbeddings:
    """
    interp = InterpEmbeddings(embedding_matrix, vocab_dict)

    interp.search("computer")

    # visualize the embedding with tensorboard
    interp.visualize_in_tb()
    """

    def __init__(
        self,
        embedding_matrix: np.ndarray,
        vocab: Dict[int, str]
    ):
        """
        embedding_matrix: np.ndarray, embedding matrix of shape:
            (num_items, hidden_size)
        """
        self.base = embedding_matrix
        self.cosine = CosineSearch(embedding_matrix)
        self.vocab = vocab
        self.c2i = dict((v, k) for k, v in vocab.items())

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        return f"{cls} with\n\t{self.cosine}"

    def search(
        self,
        category: str,
        top_k: int = 20,
    ) -> pd.DataFrame:
        """
        search for similar words with embedding and vocabulary dictionary
        """
        token_id = self.c2i.get(category)
        if token_id is None:
            match_list = []
            for token_id, token in self.vocab.items():
                if category.lower() in str(token).lower():
                    match_list.append({"token": token, "token_id": token_id})
            if len(match_list)==0:
                raise KeyError(
                    f"[UnpackAI] category: {category} not in vocabulary")
            else:
                match_df = pd.DataFrame(match_list)
                DOM("Search with the following categories","h3")()
                display(match_df)
                token_ids = list(match_df.token_id)
        else:
            DOM(f"Search with token id {token_id}","h3")()
            token_ids = [token_id,]

        # combine multiple tokens into 1
        vec = self.base[token_ids].mean(0)

        # distance search
        closest, similarity = self.cosine.search(vec, return_similarity=True)

        closest = closest[:top_k]
        similarity = similarity[:top_k]
        tokens = list(self.vocab.get(idx) for idx in closest)
        return pd.DataFrame({
            "tokens": tokens,
            "idx": closest,
            "similarity": similarity})

    def visualize_in_tb(
        self,
        log_dir:str="./logs",
        selection: np.ndarray=None,
        first_k:int=500,
    ) -> None:
        """
        Visualize the embedding in tensorboard
        For now this function is only supported on colab
        """
        # since this won't be excute too many times within a notebook
        # in large chances... so to avoid missing library when import
        # other function under this module: we import related stuff here
        from torch.utils.tensorboard import SummaryWriter
        # this version's pd has vc for quick value counts
        from forgebox.imports import pd
        import tensorflow as tf
        import tensorboard as tb
        import os

        # possible tensorflow version error
        tf.io.gfile = tb.compat.tensorflow_stub.io.gfile
        os.system(f"rm -rf {log_dir}")
        writer = SummaryWriter(log_dir=log_dir,)
        self.i2c = dict((v,k) for k,v in self.c2i.items())
        tokens = list(self.i2c.get(i) for i in range(len(self.i2c)))

        if selection is None:
            vecs = self.base[:first_k]
            tokens = tokens[:first_k]
        else:
            selection = np.array(selection).astype(dtype=np.int64)
            # select a pool of tokens for visualizaiton
            tokens = list(np.array(tokens)[selection][:first_k])
            vecs = self.base[selection][:first_k]
        writer.add_embedding(vecs, metadata=tokens,)
        # prompts for next step
        print(f"Please run the the following command in a cell")
        print("%load_ext tensorboard")
        print(f"%tensorboard  --logdir {log_dir}")


class InterpEmbeddingsTokenizer(InterpEmbeddings):
    def __init__(self,
                 embedding_matrix,
                 tokenizer):
        """
        embedding_matrix: np.ndarray, embedding matrix of shape:
            (num_items, hidden_size)
        tokenizer: a huggingface tokenizer
        """
        super().__init__(
            embedding_matrix,
            dict((v, k) for k, v in tokenizer.vocab.items()))
        self.tokenizer = tokenizer

    def search(
        self,
        word: str,
        filter_special_token: bool = True,
        top_k: int = 20,
    ) -> pd.DataFrame:
        """
        search for similar words with embedding and
            tokenizer's encode/ decode
        """
        token_ids = self.tokenizer.encode(word)
        if filter_special_token:
            token_ids = list(t for t in token_ids if t > 110)

        # combine multiple tokens into 1
        vec = self.base[token_ids].mean(0)

        # distance search
        closest, similarity = self.cosine.search(vec, return_similarity=True)
        tokens = self.tokenizer.convert_ids_to_tokens(closest)
        return pd.DataFrame({
            "tokens": tokens,
            "idx": closest,
            "similarity": similarity}).head(top_k)