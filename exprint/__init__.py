import importlib.metadata

from .colors import ANSIColors
from .exprint import dispatch_generic, dispatch_obj, dispatch_repr, exprint
from .formatter import Format, Formatter

__version__ = importlib.metadata.version(__package__)  # type: ignore

__all__ = [
    "ANSIColors",
    "Format",
    "Formatter",
    "dispatch_generic",
    "dispatch_obj",
    "dispatch_repr",
    "exprint",
]
