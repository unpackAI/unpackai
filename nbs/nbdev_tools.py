import inspect

from nbdev.showdoc import show_doc


def show_doc_methods(cls):
    """Utility for nbdev to generate docs of all public methods of a class"""
    for name, func in inspect.getmembers(cls, predicate=inspect.isroutine):
        if name == name.lstrip("_"):
            try:
                show_doc(func)
            except NameError:
                print(f"Doc will be shown for: {func.__qualname__}.{name}")
