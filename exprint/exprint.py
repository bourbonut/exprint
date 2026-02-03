import io
import sys
from typing import Any, Callable, TypeVar

from .formatter import Format, Formatter

__all__ = ["exprint", "dispatch_generic", "dispatch_obj", "dispatch_repr"]

T = TypeVar("T")


def exprint(
    obj: Any,
    stream: io.TextIOBase | None = None,
    indentation: int = 2,
    depth: int = 4,
    width: int = 88,
    max_elements: int = 100,
    end: str = "\n",
    with_color: bool = True,
):
    stream: io.TextIOBase = sys.stdout if stream is None else stream  # type: ignore
    f = Formatter(indentation, depth, width, max_elements, with_color)
    f.format_any(obj).finish(stream)
    stream.write(end)


def dispatch_repr(obj_type: type[T], format_func: Callable[[T, Formatter], Format]):
    Formatter._dispatch_repr[obj_type.__repr__] = format_func


def dispatch_obj(obj_type: type[T], format_func: Callable[[T, Formatter], Format]):
    Formatter._dispatch_objs[obj_type.__name__] = format_func


def dispatch_generic(gen_key: str, format_func: Callable[[Any, Formatter], Format]):
    Formatter._dispatch_generic[gen_key] = format_func
