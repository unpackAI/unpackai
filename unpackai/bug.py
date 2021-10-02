# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/12_bug.ipynb (unless otherwise specified).

__all__ = ['BugBook', 'module_not_found_message1', 'module_not_found_message2', 'module_not_found_error_filter',
           'BUGBOOK', 'render_download_button', 'custom_exc', 'itb', 'ishell']

# Cell
from IPython.core.ultratb import AutoFormattedTB
from traceback import format_exc
from datetime import datetime
from forgebox.html import list_group, list_group_kv, HTML
import html
import json
import base64
from jinja2 import Template
from .utils import STATIC
import logging
from inspect import isfunction
from typing import Union, Callable, Dict, Any

# Cell
class BugBook(dict):
    """
    A collection of bugs, and how to handle them
    """

    def __init__(self, **kwargs):
        self.rules = dict(kwargs)

    def __repr__(self): return "Bug Book"

    def __getitem__(
        self, key
    ) -> Dict[str, Any]:
        if isfunction(key):
            return self.rules[key.__name__]
        return self[str(key)]

    def __setitem__(self,
                    key: Union[str, Callable],
                    value: Union[str, Callable]
                    ) -> None:
        if type(key) == str:
            self.rules[key] = {"key": key,
                               "value": value,
                               "keytype": "string"}
        elif isfunction(key):
            self.rules[key.__name__] = {"key": key,
                                        "value": value,
                                        "keytype": "function"}
        else:
            self.rules[str(key)] = {"key": key, "value": value,
                                    "keytype": "unknown"}
        return

    def __call__(self, etype, evalue, tb):
        custom = None
        type_name = etype.__name__
        for d in self.rules.values():
            if d["keytype"] == "function":
                if d['key'](etype, evalue, tb):
                    custom = d["value"]
                    break
        if custom is None:
            if type_name in self.rules:
                custom = self.rules[type_name]["value"]
        if custom is None:
            return None
        else:
            if type(custom) == str:
                return custom
            elif isfunction(custom):
                return custom(etype, evalue, tb)
            else:
                logging.error(
                    f"{type(custom)} is not a valid type for bugbook")
                return None

# Cell
# functions that we can use as value of the rule
def module_not_found_message1(etype, evalue, tb):
    libname = str(evalue).replace("No module named ", "")[1:-1]
    return f'Library "{libname}" not installed, run a cell like "pip install -q {libname}"'

def module_not_found_message2(etype, evalue, tb):
    libname = str(evalue).replace("No module named ", "")[1:-1]
    return f'''
    Are you sure the library name <strong>{libname}</strong> is correct? <br>
    If so run "pip install -q {libname}" to install again📦 <br><br>
    Or ⏯ re-run the cell contains "pip install ..."
    '''

# functions that we can use as key of the fule
def module_not_found_error_filter(etype, evalue, tb):
    if etype.__name__ == "ModuleNotFoundError":
        libname = str(evalue).replace("No module named ", "")[1:-1]
        if libname in ["fastai", "unpackai", "transformers","test_filter"]:
            return True
    return False

# Cell
BUGBOOK = BugBook()

BUGBOOK["ImportError"] = "Make sure all the libraries are installed for the required version🦮🐩"

BUGBOOK["SyntaxError"] ="""
<h5>There is a <strong>grammatic</strong> error in your python code</h5>
<p>Please check the following</p>
<p>Every '(' or '[' or '{' or '"' or ' was closed with properly</p>
<p>':' should follow by the nextline with 1 more <strong>indent</strong> (4 spaces)</p>
<p>or other grammatic errors, please check traceback below for clue, usually <strong>near ^ mark</strong></p>
"""

BUGBOOK["ModuleNotFoundError"] = module_not_found_message2

BUGBOOK[module_not_found_error_filter] = module_not_found_message1

# Cell
itb = AutoFormattedTB(mode = 'Plain', tb_offset = 1)

def render_download_button(
    bytes_data:bytes,
    filename: str,
    description: str="Download",
    color:str = "default"):

    """
    Loads data from buffer into base64 payload
        embedded into a HTML button.
    Recommended for small files only.

    bytes_data: open file object ready for reading.
        A file like object with a read method.
    filename:    str
        The name when it is downloaded.
    description: str
        The text that goes into the button.

    """
    payload = base64.b64encode(bytes_data).decode()

    with open(STATIC/"html"/"download_button.html","r") as f:
        temp = Template(f.read())

    download_button = temp.render(
        filename=filename,
        payload=payload,
        color=color,
        description=description)
    return download_button

def custom_exc(shell, etype, evalue, tb, tb_offset=None, ):
    """
    A customize exception method
    That we can assign to the ishell kernel
    Arguments follow the format of default exeception function
    """
    # gathering data on this error
    # the colorful traceback
    stb = itb.structured_traceback(etype, evalue, tb)
    sstb = itb.stb2text(stb)

    # the plain string of traceback
    traceback_string = format_exc()

    # input_history, sanitized(escape) for html
    input_history = list(html.escape(i)
                for i in ishell.history_manager.input_hist_parsed[-20:])

    # now time stamp
    now_full = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    now = datetime.now().strftime("%m%d_%H%M%S")

    error_data = {
        "error_type_name": etype.__name__,
        "error_value":str(evalue),
        "traceback_string":html.escape(traceback_string),
        "timestamp":now_full,
        "input_history":input_history,
    }

    # custom made error text
    msg = BUGBOOK(etype, evalue, tb)
    if msg is not None:
        error_data.update({"msg":msg})

    error_data = json.dumps(error_data, indent=2)

    # create an error report in html format
    # by rendering a jinja2 template with error_data
    with open(STATIC/"html"/"bug"/"error_report.html","r") as f:
        temp = Template(f.read())

    error_report_page = temp.render(
        data = json.dumps(
            error_data,
        ))

    # create a mini error panel
    # a download button with embedded data
    download_button = render_download_button(
        error_report_page.encode(),
        filename=f"npakai_{etype.__name__}_{now}.html",
        description="🦋 Download Report",
        color="success")

    with open(STATIC/"html"/"bug"/"error_tiny_page.html", "r") as f:
        temp2 = Template(f.read())
        error_tiny_page = temp2.render(
            download_button=download_button,
            error_type_name=etype.__name__,
            msg=msg,
            error_value=str(evalue),
        )
    display(HTML(error_tiny_page))


    print(sstb)

# Cell
ishell = get_ipython()
ishell.set_custom_exc((Exception,), custom_exc)