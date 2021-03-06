# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/42_nlp_pdf.ipynb (unless otherwise specified).

__all__ = ['PathStr', 'TextualPDF']

# Cell
import re
from pathlib import Path
from typing import List, Union

from pdfminer.high_level import extract_text
from unpackai import utils
from unpackai import nlp

PathStr = Union[Path, str]

# Cell
class TextualPDF(nlp.Textual):
    """Extend Textual for PDF"""

    @classmethod
    def from_url_pdf(
        cls, url: str, password: str = "", page_numbers: List[int] = None, cleanup=True
    ):
        """Create a Textual object from a PDF URL with specific options

        Args:
            url: url of PDF
            password: password, if the PDF is protected
            page_numbers: list of pages to extract (first page = 0)
            cleanup: remove messy characters and line returns (default=True)
        """
        return cls.from_path_pdf(
            utils.download(url),
            password=password,
            page_numbers=page_numbers,
            cleanup=cleanup,
        )

    @classmethod
    def from_path_pdf(
        cls,
        pdf_file: PathStr,
        password: str = "",
        page_numbers: List[int] = None,
        cleanup=True,
    ):
        """Create a Textual object from a PDF

        Args:
            pdf_file: path of PDF
            password: password, if the PDF is protected
            page_numbers: list of pages to extract (first page = 0)
            cleanup: remove messy characters and line returns (default=True)
        """
        txt = extract_text(pdf_file, password=password, page_numbers=page_numbers)
        if cleanup:
            txt = re.sub(r"[\r\n]{2,}", "<line_break>", txt)
            txt = re.sub(r"- *[\n\r]", "", txt)
            txt = txt.replace("\n", " ").replace("<line_break>", "\n\n")

        return cls(txt, Path(pdf_file))

    @classmethod
    def from_path(cls, path: PathStr):
        """Create a Textual object from a path, including PDF"""
        path = Path(path)
        if path.suffix.lower() == ".pdf":
            return cls.from_path_pdf(path)
        else:
            return super().from_path(path)
