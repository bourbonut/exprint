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
    """
    Pretty prints the obj by formatting it recursively and writes the content
    into a text stream.

    Parameters
    ----------
    obj : Any
        Object to format.
    stream : io.TextIOBase | None
        Text stream.
    indentation : int
        Number of spaces used for each indentation level
    depth : int
        For nested objects, this value reflects the depth to which nested
        objects are pretty-printed. For example, when `depth` is less than 0,
        list objects are formatted as `[list]` values and dict objects are
        formatted as `{dict}` values.
    width : int
        The maximum amount of allowed characters on one line.
    max_elements : int
        The maximum amount of elements formatted for each object.
    end : str
        A string added at the end after the formatted object.
    with_color : bool
        If `True`, enables colored output for better readability

    Raises
    ------
    NotImplementedError
        When no associated format function has been found for the object to be
        formatted.
    """
    stream: io.TextIOBase = sys.stdout if stream is None else stream  # type: ignore
    f = Formatter(indentation, depth, width, max_elements, with_color)
    f.format_any(obj).finish(stream)
    stream.write(end)


def dispatch_repr(obj_type: type[T], format_func: Callable[[T, Formatter], Format]):
    """
    Registers format function associated to the `__repr__` method of a type.

    Default registered types:

    - `type(None)`
    - `float`
    - `int`
    - `str`
    - `bytes`
    - `list`
    - `tuple`
    - `set`
    - `dict`

    Parameters
    ----------
    obj_type : type[T]
        Type of the object
    format_func : Callable[[T, Formatter], Format]
        Format function

    Examples
    --------

    >>> def format_float(obj: float, f: Formatter) -> Format:
    ...     return f.format_color(ANSIColors.MAGENTA).value(f.format_value().value(obj))
    >>> dispatch_repr(float, format_float)

    See also
    --------
    dispatch_obj : Format functions for types with `__name__` attribute.
    dispatch_generic : Format functions for generic objects.
    """
    Formatter._dispatch_repr[obj_type.__repr__] = format_func


def dispatch_obj(obj_type: type[T], format_func: Callable[[T, Formatter], Format]):
    """
    Registers format function associated to the `__name__` attribute of an
    object type.

    Parameters
    ----------
    obj_type : type[T]
        Object type
    format_func : Callable[[T, Formatter], Format]
        Format function

    Examples
    --------

    >>> class Example:
    ...     __slots__ = "foo", "bar"
    ...     def __init__(self, foo: str, bar: int):
    ...         self.foo = foo
    ...         self.bar = bar
    >>> def format_example(obj: Example, f: Formatter) -> Format:
    ...     return f.format_class("Example").field("foo", obj.foo).field("bar", obj.bar)
    >>> dispatch_obj(Example, format_example)

    See also
    --------
    dispatch_repr : Format functions for types with `__repr__` method.
    dispatch_generic : Format functions for generic objects.
    """
    Formatter._dispatch_objs[obj_type.__name__] = format_func


def dispatch_generic(gen_key: str, format_func: Callable[[Any, Formatter], Format]):
    """
    Registers format function associated to a generic object.

    Supported generic keys:

    - `"recursion"`
    - `"dataclass"`
    - `"class"`

    Parameters
    ----------
    gen_key : str
        Generic key
    format_func : Callable[[Any, Formatter], Format]
        Format function

    Examples
    --------

    >>> def format_class(obj: Any, f: Formatter) -> Format:
    ...     fclass = f.format_class(obj.__class__.__name__)
    ...     for name, value in obj.__dict__.items():
    ...         fclass.field(name, value)
    ...     return fclass
    >>> dispatch_generic("class", format_class)

    See also
    --------
    dispatch_obj : Format functions for types with `__name__` attribute.
    dispatch_repr : Format functions for types with `__repr__` method.
    """
    Formatter._dispatch_generic[gen_key] = format_func
