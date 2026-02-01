import io
import sys
from typing import Any

from .formatter import Formatter

__all__ = ["exprint"]


def exprint(
    obj: Any,
    stream: io.TextIOBase | None = None,
    indentation: int = 2,
    depth: int = 4,
    width: int = 88,
    max_elements: int = 100,
    end: str = "\n",
):
    stream: io.TextIOBase = sys.stdout if stream is None else stream  # type: ignore
    f = Formatter(indentation, depth, width, max_elements)
    f.format_any(obj).finish(stream)
    stream.write(end)
