# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/51_deploy_app.ipynb (unless otherwise specified).

__all__ = ['deploy_app', 'load_module', 'import_from_module', 'blackify', 'StreamlitApp', 'StreamlitAppCustom']

# Cell
import json
import requests
from dataclasses import dataclass, field
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path
from textwrap import dedent
from typing import Any, Union

from black import Mode, format_file_contents
from jinja2 import Template, DebugUndefined

from ..utils import IS_JUPYTER

# Internal Cell
PathStr = Union[Path, str]

# Cell
def deploy_app(app: PathStr = "app.py"):
    """Deploy a streamlit app using ngrok"""
    if not Path(app).is_file():
        print(f"ERROR: the app {app} does not exist!")
        return

    def show_url(public: str, port: str):
        print(f"Tunnel created for port {port} to: {public}")
        print("... click on the link to launch the app")
        if IS_JUPYTER:
            print("... Note: the output of streamlit is stored in nohup.out")

    if IS_JUPYTER:
        try:
            get_ipython().system_raw("ngrok http 8501 &")
            resp = requests.get("http://localhost:4040/api/tunnels")
        except Exception as e:
            print(f"Met error when trying to connect: {e}")
            print("🧙‍♂️This might happen: run the cell again ▶️ and it should work!")
            return

        tunnel = json.loads(resp.content)["tunnels"][0]
        local = tunnel["config"]["addr"]
        port = local.split(":")[-1]
        public = tunnel["public_url"]

        show_url(public, port)
        Path("nohup.out").write_text("")
        get_ipython().system_raw(f"nohup streamlit run {app}")
    else:
        raise NotImplementedError(f"Deployment outside jupyter currently not supported")


# Cell
def load_module(module_path: PathStr, module_name="module") -> Any:
    """Load and return a module"""
    module_path = Path(module_path)
    if not (module_path.is_file() and module_path.suffix == ".py"):
        raise AttributeError(f"Module {module_path} not found or not a .py file")
    loader = SourceFileLoader(module_name, str(module_path))
    spec = spec_from_loader(loader.name, loader)
    if not spec:
        raise AttributeError(f"Empty module spec from {module_path}")
    module = module_from_spec(spec)
    loader.exec_module(module)
    return module


def import_from_module(module_path: PathStr, name: str, module_name="module") -> Any:
    """Import a list of names from a module from its path"""
    module = load_module(module_path, module_name=module_name)
    try:
        return getattr(module, name)
    except AttributeError:
        raise AttributeError(f"Name {name} not found in {module_path}") from None


# Cell
def blackify(code:str) -> str:
    """Run "black" on a code passed as string"""
    return format_file_contents(code, mode=Mode(), fast=False)

# Internal Cell
TEMPLATE_FLOW = """
from pathlib import Path

import streamlit as st

{{ specific_import }}
{{ custom_import }}

st.set_page_config(page_title="ML deployment, by unpackAI", page_icon="🚀")
st.image("https://unpackai.github.io/unpackai_logo.svg")
st.title("{{ title }}")
st.write("*by {{ author }}*")
st.write("---")

{{ load_model }}

{{ post_process_code }}

{{ display_prediction }}

{{ input_2_prediction }}
"""


@dataclass
class TemplateCode:
    specific_import: str = ""
    load_model: str = ""
    display_prediction: str = ""
    input_2_prediction: str = """\
        select = st.sidebar.radio("How to load {{ input }}?", ["from file{% if multiple %}s{% endif %}", "from URL"])
        st.sidebar.write("---")

        if select == "from URL":
            url = st.sidebar.text_input("url")
            if url:
                display_prediction(url)

        else:
            {% if multiple -%}
            files = st.sidebar.file_uploader("Choose {{ input }}", accept_multiple_files=True)
            for file in files:  # type:ignore # this is an iterable
                display_prediction(file)
            {% else -%}
            file = st.sidebar.file_uploader("Choose {{ input }}")
            if file:
                display_prediction(file)
            {% endif %}
    """


# Internal Cell

# NOTE: We need re-implementation of elements defined during loading

TEMPLATE_CV_FASTAI = TemplateCode(
    specific_import="""
        {# The ✨ below is to go around import modification by nbdev #}
        from {# ✨ #}unpackai.deploy.cv import get_image, get_learner
    """
        ,
    load_model="""\
        learn = get_learner(Path(__file__).parent / "{{ model }}")
        vocab = learn.dls.vocab
    """,
    display_prediction="""
        def display_prediction(pic):
            img = get_image(pic)
            with learn.no_bar():
                prediction, idx, probabilities = learn.predict(img)
            col_img, col_pred = st.columns(2)
            col_img.image(img, caption=getattr(pic, "name", None))
            col_pred.write(f"### {prediction}")
            col_pred.metric(f"Probability", f"{probabilities[idx].item()*100:.2f}%")
    """,
)


# Internal Cell

# NOTE: Loading model and prediction depends on the module (e.g. "regression")

TEMPLATE_TABULAR_PYCARET = TemplateCode(
    specific_import="""
        import pandas as pd
        from pycaret.{{ module }} import load_model, predict_model
    """,
    load_model="""model = load_model("{{ model }}")""",
    display_prediction="""
        def display_prediction(csv):
            df = pd.read_csv(csv)
            predictions = predict_model(model, data = df)
            st.dataframe(predictions)
    """,
)


# Internal Cell
TEMPLATE_NLP_HF = TemplateCode(
    specific_import="""
        # TODO
    """,
    load_model="""
        # TODO
    """,
    display_prediction="""
        def display_prediction(csv:PathStr):
            pass # TODO
    """,
)


# Internal Cell

LIST_TEMPLATES = {
    "CV": {"fastai": TEMPLATE_CV_FASTAI},
    "Tabular": {"pycaret": TEMPLATE_TABULAR_PYCARET},
    "NLP": {"hugging_face": TEMPLATE_NLP_HF},
}

# Cell
@dataclass
class StreamlitApp:
    """Class to generate Streamlit App for different applications

    Available applications: "CV", "Tabular", "NLP", and "Custom"
    """

    application: str
    framework: str = field(init=False, default="")
    content: str = field(init=False, default="")
    _title: str = field(init=False, default="Streamlit App")
    _dest: Path = field(init=False, default_factory=Path)

    def __post_init__(self):
        applications = list(LIST_TEMPLATES)
        if self.application not in applications:
            raise AttributeError(
                f"ERROR: Application {self.application} not supported. "
                f"Available applications: {applications}"
            )

    @property
    def template(self) -> Template:
        """Get the template"""
        base_template = Template(TEMPLATE_FLOW, undefined=DebugUndefined)
        try:
            template_framework = LIST_TEMPLATES[self.application][self.framework]
        except KeyError as missing:
            raise AttributeError(f"Element {missing} not found among list of templates")

        return Template(
            base_template.render(
                specific_import=dedent(template_framework.specific_import),
                load_model=dedent(template_framework.load_model),
                display_prediction=dedent(template_framework.display_prediction),
                input_2_prediction=dedent(template_framework.input_2_prediction),
            )
        )

    def _render(
        self,
        framework: str,
        title: str,
        author: str,
        model: PathStr,
        post_process_code: str = "",
        custom_import: str = "",
        **kwargs,
    ):
        """Generic function for rendering"""
        self.framework = framework
        self._title = title
        input_ = {
            "CV": "images",
            "Tabular": "CSV",
            "NLP": "Text",
        }.get(self.application, "input")
        self.content = self.template.render(
            title=title,
            author=author,
            model=model,
            input=input_,
            multiple=(input_.endswith("s")),
            post_process_code=dedent(post_process_code),
            custom_import=dedent(custom_import),
            **kwargs,
        )
        self.content = blackify(self.content)
        return self

    def render_fastai(
        self,
        title: str,
        author: str,
        model: PathStr,
        post_process_code: str = "",
        custom_import: str = "",
    ) -> "StreamlitApp":
        """Render an app based on template

        Args:
            title: title of the App
            author: author of the App
            model: path of .pkl model to load (exported with `learn.export(...)`)
            post_process_mode: optional code to post-process the model after loading
            custom_import: optional code for custom import
        """
        return self._render(
            "fastai",
            title,
            author,
            model,
            post_process_code=post_process_code,
            custom_import=custom_import,
        )

    def render_pycaret(
        self,
        title: str,
        author: str,
        model: PathStr,
        module: str,
        post_process_code: str = "",
        custom_import: str = "",
    ) -> "StreamlitApp":
        """Render an app based on template

        Args:
            title: title of the App
            author: author of the App
            model: path of .pkl model to load (exported with `learn.export(...)`)
            module: regression, classification, etc.
            post_process_mode: optional code to post-process the model after loading
            custom_import: custom import (optional)
        """
        model = Path(model)
        return self._render(
            "pycaret",
            title,
            author,
            model.with_name(model.name.replace(".pkl", "")),
            module=module,
            post_process_code=post_process_code,
            custom_import=custom_import,
        )

    def append(self, content: str) -> "StreamlitApp":
        """Add additional content to the app"""
        self.content += dedent(content)
        return self

    def save(self, dest: PathStr = "app.py", show=False) -> "StreamlitApp":
        """Write the app to a file"""
        self._dest = Path(dest)
        self._dest.write_text(self.content, encoding="utf-8")
        print(f"Saved app '{self._title}' to '{dest}'")
        if show:
            print("-" * 20)
            print(self.content)
        return self

    def deploy(self, dest: PathStr = "app.py") -> None:
        """Deploy the app"""
        if not self._dest:
            raise FileNotFoundError(f"App shall be saved before deployed")
        deploy_app(self._dest)


# Internal Cell
TEMPLATE_CUSTOM = TemplateCode(
    specific_import="{{ specific_import }}",
    load_model="",
    display_prediction="",
    input_2_prediction="{{ make_predictions }}"
)

# Cell
@dataclass
class StreamlitAppCustom:
    """Application with custom implementation"""

    content: str = field(init=False, default="")
    _title: str = field(init=False, default="Streamlit App")

    def render(
        self,
        title: str,
        author: str,
        make_predictions: Union[str, Path],
        custom_import: str = "",
    ) -> "StreamlitAppCustom":
        """Render an app based on template

        Args:
            title: title of the App
            author: author of the App
            make_predictions: custom implementations, either code or file path
                if a file is provided, it shall implement the function
                'def make_predictions()'
            custom_import: custom import (optional)
        """
        self._title = title
        base_template = Template(TEMPLATE_FLOW, undefined=DebugUndefined)
        template = Template(
            base_template.render(
                specific_import=dedent(TEMPLATE_CUSTOM.specific_import),
                load_model=dedent(TEMPLATE_CUSTOM.load_model),
                display_prediction=dedent(TEMPLATE_CUSTOM.display_prediction),
                input_2_prediction=dedent(TEMPLATE_CUSTOM.input_2_prediction),
            )
        )

        if isinstance(make_predictions, str) and not make_predictions.endswith(".py"):
            self.content = template.render(
                title=title,
                author=author,
                specific_import="",
                make_predictions=dedent(make_predictions),
                custom_import=custom_import,
            )
        elif isinstance(make_predictions, Path) or make_predictions.endswith(".py"):
            loaded_make_predictions = f"""\
                make_predictions = import_from_module(r"{make_predictions}", "make_predictions")
                make_predictions()
            """
            self.content = template.render(
                title=title,
                author=author,
                specific_import="from unpackai.deploy.app import import_from_module",
                make_predictions=dedent(loaded_make_predictions),
                custom_import=custom_import,
            )
        else:
            raise AttributeError(
                f"Incorrect type for {make_predictions}: shall be code or .py path"
            )

        self.content = blackify(self.content)
        return self

    def save(self, dest: PathStr, show=False):
        """Write the app to a file"""
        Path(dest).write_text(self.content, encoding="utf-8")
        print(f"Saved app '{self._title}' to '{dest}'")
        if show:
            print("-" * 20)
            print(self.content)