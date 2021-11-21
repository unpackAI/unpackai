import inspect
from typing import Any

from nbdev.showdoc import show_doc


def show_doc_enhanced(element, show_methods=False, **kwargs):
    """Utility for nbdev to generate docs of all public methods of a class"""
    if not show_methods:
        return show_doc(element, **kwargs)

    for name, func in inspect.getmembers(element, predicate=inspect.isroutine):
        if name == name.lstrip("_"):
            try:
                show_doc(func, **kwargs)
            except NameError:
                print(f"Doc will be shown for: {func.__qualname__}.{name}")
