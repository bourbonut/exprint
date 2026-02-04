from __future__ import annotations

import io
from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
from itertools import islice
from typing import Any, Callable, Iterable, Iterator, Protocol, Sized

from exprint.colors import ANSIColors

__all__ = ["Formatter", "Format"]


class ToString(Protocol):
    def __str__(self) -> str: ...


class SizedIterable(Iterable[Any], Sized, Protocol):
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Any]: ...


class Format(ABC):
    """
    Abstract class dealing with format classes.

    Attributes
    ----------
    formatter : Formatter
        Formatter class.
    """

    def __init__(self, formatter: Formatter):
        self.formatter = formatter

    @abstractmethod
    def width(self) -> int:
        """
        Returns the width of formatted text.

        Returns
        -------
        int
            Width of the formatted text.
        """
        ...

    @abstractmethod
    def finish(self, stream: io.TextIOBase):
        """
        Formats the content and outputs it into the specified text stream.

        Parameters
        ----------
        stream : io.TextIOBase
            Text stream in which the text content is written.
        """
        ...


def width_seq(cols: int, col_widths: list[int], indent: int) -> int:
    """
    Returns the width of a sequence formatted in multiple lines.

    Parameters
    ----------
    cols : int
        Number of columns.
    col_widths : list[int]
        List of widths of each column.
    indent : int
        Current indentation.

    Returns
    -------
    int
        Width of the sequence.
    """
    return sum(col_widths) + (cols - 1) * 2 + indent + 1


def estimate_seq_widths(
    widths: list[int], indentation: int, max_width: int, columns: int = 10
) -> tuple[int, list[int]]:
    """
    Computes the minimum number of columns required for formatting the sequence
    into multiple lines.

    Parameters
    ----------
    widths : list[int]
        Computed widths of each `Format` elements.
    indentation : int
        Current indentation.
    max_width : int
        Maximum width allowed.
    columns : int
        Initial number of columns.

    Returns
    -------
    tuple[int, list[int]]
        Number of columns and list of widths of each column

    Notes
    -----
    This function is quite expensive due to its computing complexity.
    """
    columns = min(len(widths), columns)
    for cols in range(columns, 0, -1):
        rows, els = divmod(len(widths), cols)
        col_widths = [
            max([widths[cols * i + c] for i in range(rows + int(c < els))])
            for c in range(cols)
        ]
        width = width_seq(cols, col_widths, indentation)
        if width < max_width:
            break
    return cols, col_widths


class SeqFormatter:
    def __init__(self, format_seq: FormatSeq):
        self.formatter = format_seq.formatter
        self._values = format_seq._values
        self._length = format_seq._length
        self._head = format_seq._head
        self._tail = format_seq._tail

    def format_row(
        self,
        stream: io.TextIOBase,
        subseq: list[Format],
        indent: int,
        col_widths: list[int],
    ):
        stream.write(" " * indent)
        imax = len(subseq)
        for i, (col_width, value) in enumerate(zip(col_widths, subseq)):
            width = value.width()
            stream.write((col_width - width) * " ")
            value.finish(stream)
            if i + 1 == imax:
                stream.write(",")
            else:
                stream.write(", ")
        stream.write("\n")

    def inline(self, stream: io.TextIOBase):
        stream.write(self._head)
        stream.write(" ")
        imax = len(self._values)
        for i, value in enumerate(self._values):
            value.finish(stream)
            if i + 1 != imax:
                stream.write(", ")
        stream.write(" ")
        stream.write(self._tail)

    def monocolumn(self, stream: io.TextIOBase):
        indent = self.formatter.indent()
        fixed_indent = self.formatter.fixed_indent()
        m = self.formatter.max_elements()

        stream.write(self._head)
        stream.write("\n")
        imax = len(self._values)
        stream.write(" " * indent)
        for i, value in enumerate(self._values):
            value.finish(stream)
            if i + 1 != imax:
                stream.write(",\n")
                stream.write(" " * indent)
            else:
                stream.write(",\n")
        if self._length > m:
            stream.write(" " * indent)
            stream.write(f"... {self._length - m} more items\n")
        stream.write(" " * (indent - fixed_indent))
        stream.write(self._tail)

    def multicolumns(self, stream: io.TextIOBase, n: int, col_widths: list[int]):
        indent = self.formatter.indent()
        fixed_indent = self.formatter.fixed_indent()
        m = self.formatter.max_elements()

        seq = self._values
        q, r = divmod(len(seq), n)
        stream.write(self._head)
        stream.write("\n")
        for i in range(q):
            self.format_row(stream, seq[n * i : n * (i + 1)], indent, col_widths)
        if r > 0:
            self.format_row(
                stream, seq[n * (i + 1) : n * (i + 1) + r], indent, col_widths
            )
        if self._length > m:
            stream.write(" " * indent)
            stream.write(f"... {self._length - m} more items\n")
        stream.write(" " * (indent - fixed_indent))
        stream.write(self._tail)
        return


class FormatSeq(Format):
    def __init__(self, formatter: Formatter, bracket_head: str, bracket_tail: str):
        super().__init__(formatter)
        self._values = []
        self._widths = []
        self._length = 0
        self._cache = None
        self._head = bracket_head
        self._tail = bracket_tail

    def value(self, value: Any) -> FormatSeq:
        """
        Adds a value to the sequence output.

        Parameters
        ----------
        value : Any
            Value to add.

        Returns
        -------
        FormatSeq
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> f.format_list().value(seq[0])
        """
        return self.value_with(lambda f: f.format_any(value))

    def value_with(self, value_fmt: Callable[[Formatter], Format]) -> FormatSeq:
        """
        Adds a value to the sequence output. Equivalent to `FormatSeq.value`
        but formats the value using a function.

        Parameters
        ----------
        value_fmt : Callable[[Formatter], Format]
            Value function.

        Returns
        -------
        FormatSeq
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> f.format_list().value_with(lambda f: f.format_any(seq[0]))
        """
        if len(self._widths) < self.formatter.max_elements():
            value = value_fmt(self.formatter)
            self._widths.append(value.width())
            self._values.append(value)
        self._length += 1
        return self

    def values(self, values: SizedIterable) -> FormatSeq:
        """
        Adds all values to the sequence output.

        Parameters
        ----------
        values : SizedIterable
            Sequence of values which must be iterable and sized.

        Returns
        -------
        FormatSeq
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> f.format_list().values(seq)
        """
        self._length += len(values)
        offset = self.formatter.max_elements() - len(self._widths)
        values = [self.formatter.format_any(value) for value in islice(values, offset)]
        self._widths.extend(value.width() for value in values)
        self._values.extend(values)
        return self

    def width(self) -> int:
        if len(self._values) == 0:
            return 2
        if self._cache is None:
            self._cache = estimate_seq_widths(
                self._widths,
                self.formatter.indent(),
                self.formatter.width(),
            )
        cols, col_widths = self._cache
        return width_seq(cols, col_widths, self.formatter.indent())

    def finish(self, stream: io.TextIOBase):
        if len(self._values) == 0:
            stream.write(self._head)
            stream.write(self._tail)
            return
        m = self.formatter.max_elements()
        max_width = self.formatter.width()
        indent = self.formatter.indent()
        seq_formatter = SeqFormatter(self)
        widths = self._widths
        inline_width = sum(widths) + len(widths) * 2 + indent
        if self._length > m or inline_width > max_width:
            if self._cache is None:
                self._cache = estimate_seq_widths(widths, indent, max_width)
            n, col_widths = self._cache
            if n == 1:
                return seq_formatter.monocolumn(stream)
            else:
                return seq_formatter.multicolumns(stream, n, col_widths)
        return seq_formatter.inline(stream)


class FormatList(FormatSeq):
    """Class for formatting list of items."""

    def __init__(self, formatter: Formatter):
        super().__init__(formatter, "[", "]")


class FormatTuple(FormatSeq):
    """Class for formatting tuple of items."""

    def __init__(self, formatter: Formatter):
        super().__init__(formatter, "(", ")")


class FormatSet(FormatSeq):
    """Class for formatting set of items."""

    def __init__(self, formatter: Formatter):
        super().__init__(formatter, "{", "}")


def estimate_struct_width(
    keys: list[Format],
    values: list[Format],
    max_width: int,
    indent: int,
    max_elements: int,
) -> tuple[bool, int]:
    """
    Returns if all pairs of key-values can be written on one line and the
    required width for formatting pairs of key-values.

    Parameters
    ----------
    keys : list[Format]
        List of keys
    values : list[Format]
        List of values
    max_width : int
        Maximum width allowed.
    indent : int
        Current indentation
    max_elements : int
        Maximum of elements allowed.

    Returns
    -------
    tuple[bool, int]
        Boolean which represents multiple lines or inline format and the width
        occupied by the formatted pairs of key-values.
    """
    m = max_elements
    kwidths = [k.width() for k in keys]
    vwidths = [v.width() for v in values]
    inline_width = sum(kwidths) + sum(vwidths) + 2 * len(values) + indent + 4
    if inline_width <= max_width:
        return False, inline_width
    width = max([kw + vw + 2 + indent for kw, vw in zip(kwidths[:m], vwidths[:m])])
    return True, width


class StructFormatter:
    def __init__(
        self,
        formatter: Formatter,
        keys: list[Format],
        values: list[Format],
        class_name: Format | None = None,
    ):
        self.formatter = formatter
        self._keys = keys
        self._values = values
        self._class_name = class_name

    def multilines(self, stream: io.TextIOBase):
        indent = self.formatter.indent()
        fixed_indent = self.formatter.fixed_indent()
        m = self.formatter.max_elements()

        if self._class_name is not None:
            self._class_name.finish(stream)
            stream.write(" ")
        stream.write("{\n")
        for key, value in zip(self._keys[:m], self._values[:m]):
            stream.write(" " * indent)
            key.finish(stream)
            stream.write(": ")
            value.finish(stream)
            stream.write(",\n")
        if len(self._values) > m:
            stream.write(" " * indent + f"... {len(self._values) - m} more items\n")
        stream.write(" " * (indent - fixed_indent))
        stream.write("}")

    def inline(self, stream: io.TextIOBase):
        if self._class_name is not None:
            self._class_name.finish(stream)
            stream.write(" ")
        imax = len(self._values)
        if imax == 0:
            stream.write("{}")
            return
        stream.write("{ ")
        for i, (key, value) in enumerate(zip(self._keys, self._values)):
            key.finish(stream)
            stream.write(": ")
            value.finish(stream)
            if i + 1 != imax:
                stream.write(", ")
        stream.write(" }")


class FormatStruct(Format):
    def __init__(self, formatter: Formatter, class_name: Format | None = None):
        super().__init__(formatter)
        self._keys = []
        self._values = []
        self._class_name = class_name
        self._cache = None

    def width(self) -> int:
        if self._cache is None:
            self._cache = estimate_struct_width(
                self._keys,
                self._values,
                self.formatter.width(),
                self.formatter.indent(),
                self.formatter.max_elements(),
            )
        return self._cache[1]

    def finish(self, stream: io.TextIOBase):
        struct_formatter = StructFormatter(
            self.formatter,
            self._keys,
            self._values,
            self._class_name,
        )

        multiple_lines = self._cache[0]  # type: ignore
        if multiple_lines:
            return struct_formatter.multilines(stream)
        return struct_formatter.inline(stream)


def check_items(length_keys: int, length_values: int):
    """
    Checks if there are as many keys as values.

    Parameters
    ----------
    length_keys : int
        Length of keys
    length_values : int
        Length of values

    Raises
    ------
    ValueError
        If missing keys or missing values
    """
    if length_keys < length_values:
        raise ValueError(
            f"Missing keys (length keys: {length_keys}, length values: {length_values})"
        )
    if length_keys > length_values:
        raise ValueError(
            f"Missing values (length keys: {length_keys}, length values: {length_values})"
        )


class FormatDict(FormatStruct):
    """Class for formatting dictionary of items."""

    def __init__(self, formatter: Formatter):
        super().__init__(formatter)

    def key(self, key: Any) -> FormatDict:
        """
        Adds a key to the dictionary output.

        Parameters
        ----------
        key : Any
            Key to add.

        Returns
        -------
        FormatDict
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> key = list(map.keys())[0]
        >>> f.format_dict().key(key)
        """
        return self.key_with(lambda f: f.format_any(key))

    def key_with(self, key_fmt: Callable[[Formatter], Format]) -> FormatDict:
        """
        Adds a key to the dictionary output. Equivalent to `FormatDict.key` but
        formats the value using a function.

        Parameters
        ----------
        key_fmt : Callable[[Formatter], Format]
            Key function.

        Returns
        -------
        FormatDict
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> key = list(map.keys())[0]
        >>> f.format_dict().key_with(lambda f: f.format_any(key))
        """
        self._keys.append(key_fmt(self.formatter))
        return self

    def value(self, value: Any) -> FormatDict:
        """
        Adds a value to the dictionary output.

        Parameters
        ----------
        value : Any
            Value to add.

        Returns
        -------
        FormatDict
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> value = list(map.values())[0]
        >>> f.format_dict().value(value)
        """
        return self.value_with(lambda f: f.format_any(value))

    def value_with(self, value_fmt: Callable[[Formatter], Format]) -> FormatDict:
        """
        Adds a value to the dictionary output. Equivalent to `FormatDict.value`
        but formats the value using a function.

        Parameters
        ----------
        value : Any
            Value to add.

        Returns
        -------
        FormatDict
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> value = list(map.values())[0]
        >>> f.format_dict().value_with(lambda f: f.format_any(value))
        """
        self._values.append(value_fmt(self.formatter))
        return self

    def item(self, key: Any, value: Any) -> FormatDict:
        """
        Adds a pair of key-value to the dictionary output.

        Parameters
        ----------
        key : Any
            Key to add.
        value : Any
            Value to add.

        Returns
        -------
        FormatDict
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> key, value = list(map.items())[0]
        >>> f.format_dict().item(key, value)
        """
        return self.key(key).value(value)

    def items(self, values: Iterable[tuple[Any, Any]]) -> FormatDict:
        """
        Adds all pairs of key-values to the dictionary output.

        Parameters
        ----------
        values : Iterable[tuple[Any, Any]]
            Pair of key-values

        Returns
        -------
        FormatDict
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> f.format_dict().items(map.items())
        """
        for key, value in values:
            self.item(key, value)
        return self

    def width(self) -> int:
        check_items(len(self._keys), len(self._values))
        return super().width()

    def finish(self, stream: io.TextIOBase):
        check_items(len(self._keys), len(self._values))
        if self._cache is None:
            self._cache = estimate_struct_width(
                self._keys,
                self._values,
                self.formatter.width(),
                self.formatter.indent(),
                self.formatter.max_elements(),
            )
        return super().finish(stream)


class FormatClass(FormatStruct):
    """
    Class for formatting classes.

    Parameters
    ----------
    class_name : str
        Class name
    """

    def __init__(self, class_name: str, formatter: Formatter):
        super().__init__(formatter, formatter.format_value().value(class_name))

    def field(self, name: str, value: Any) -> FormatClass:
        """
        Adds a field to the class output.

        Parameters
        ----------
        name : str
            Name of the field.
        value : Any
            Value of the field.

        Returns
        -------
        FormatClass
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> f.format_class("MyClass").field("foo", obj.foo)
        """
        return self.field_with(name, lambda f: f.format_any(value))

    def field_with(
        self, name: str, value_fmt: Callable[[Formatter], Format]
    ) -> FormatClass:
        """
        Adds a field to the class output. Equivalent to `FormatClass.field` but
        formats the value using a function.

        Parameters
        ----------
        name : str
            Name of the field.
        value_fmt : Callable[[Formatter], Format]
            Value function.

        Returns
        -------
        FormatClass
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> f.format_class("MyClass").field_with("foo", lambda f: f.format_any(obj.foo))
        """
        self._keys.append(self.formatter.format_value().value(name))
        self._values.append(value_fmt(self.formatter))
        return self

    def width(self) -> int:
        super().width()
        multiple_lines, width = self._cache  # type: ignore
        if multiple_lines:
            self._cache = (multiple_lines, width)
        else:
            self._cache = (multiple_lines, width + self._class_name.width() + 1)  # type: ignore
        return self._cache[1]

    def finish(self, stream: io.TextIOBase):
        if self._cache is None:
            multiple_lines, width = estimate_struct_width(
                self._keys,
                self._values,
                self.formatter.width(),
                self.formatter.indent(),
                self.formatter.max_elements(),
            )
            if multiple_lines:
                self._cache = (multiple_lines, width)
            else:
                self._cache = (multiple_lines, width + self._class_name.width() + 1)  # type: ignore
        return super().finish(stream)


class FormatValue(Format):
    """Class for formatting single values."""

    def __init__(self, formatter: Formatter):
        super().__init__(formatter)
        self._value = None
        self._width = 0

    def value(self, value: ToString) -> FormatValue:
        """
        Adds a value to the formatter. The value must have a `__str__` method.

        Parameters
        ----------
        value : ToString
            Value to add.

        Returns
        -------
        FormatValue
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> f.format_value().value(10.286)
        """
        self._value = str(value)
        self._width = len(self._value)
        return self

    def width(self):
        return self._width

    def finish(self, stream: io.TextIOBase):
        if self._value is None:
            raise ValueError("Undefined value")
        stream.write(self._value)


class FormatColor(Format):
    """
    Class for coloring values.

    Parameters
    ----------
    color : ANSIColors
        ANSI color code
    """

    RESET = ANSIColors.RESET.value

    def __init__(self, formatter: Formatter, color: ANSIColors):
        super().__init__(formatter)
        self._color: str = color.value
        self._value: Format = None

    def value(self, value: Format) -> FormatColor:
        """
        Adds the value to the formatter.

        Parameters
        ----------
        value : Format
            Value to add.

        Returns
        -------
        FormatColor
            Itself

        Examples
        --------

        >>> f = Formatter()
        >>> value = f.format_value().value(10.286)
        >>> f.format_color(ANSIColors.BLUE).value(value)
        """
        self._value = value
        return self

    def width(self):
        return self._value.width()

    def finish(self, stream: io.TextIOBase):
        if self.formatter.color():
            stream.write(self._color)
            self._value.finish(stream)
            stream.write(self.RESET)
        else:
            self._value.finish(stream)


def format_none(obj: None, f: Formatter) -> Format:
    return f.format_value().value(obj)


def format_float(obj: float, f: Formatter) -> Format:
    return f.format_color(ANSIColors.YELLOW).value(f.format_value().value(obj))


def format_int(obj: int, f: Formatter) -> Format:
    return f.format_color(ANSIColors.YELLOW).value(f.format_value().value(obj))


def format_str(obj: str, f: Formatter) -> Format:
    return f.format_color(ANSIColors.GREEN).value(f.format_value().value(f'"{obj}"'))


def format_bytes(obj: int, f: Formatter) -> Format:
    return f.format_color(ANSIColors.GREEN).value(f.format_value().value(obj))


def format_list(obj: list, f: Formatter) -> Format:
    if f.depth() <= 0:
        return f.format_color(ANSIColors.CYAN).value(f.format_value().value("[list]"))
    return f.format_list().values(obj)


def format_tuple(obj: tuple, f: Formatter) -> Format:
    if f.depth() <= 0:
        return f.format_color(ANSIColors.CYAN).value(f.format_value().value("(tuple)"))
    return f.format_tuple().values(obj)


def format_set(obj: set, f: Formatter) -> Format:
    if f.depth() <= 0:
        return f.format_color(ANSIColors.CYAN).value(f.format_value().value("{set}"))
    return f.format_set().values(obj)


def format_dict(obj: dict, f: Formatter) -> Format:
    if f.depth() <= 0:
        return f.format_color(ANSIColors.CYAN).value(f.format_value().value("{dict}"))
    return f.format_dict().items(obj.items())


def format_recursion(obj: Any, f: Formatter) -> Format:
    return f.format_color(ANSIColors.MAGENTA).value(
        f.format_value().value("[recursion]")
    )


def format_dataclass(obj: Any, f: Formatter) -> Format:
    fclass = f.format_class(obj.__class__.__name__)
    for name, value in asdict(obj).items():
        fclass.field(name, value)
    return fclass


def format_class(obj: Any, f: Formatter) -> Format:
    fclass = f.format_class(obj.__class__.__name__)
    for name, value in obj.__dict__.items():
        fclass.field(name, value)
    return fclass


class Formatter:
    """
    Main class for formatting any type.

    Parameters
    ----------
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
    """

    _dispatch_repr = {
        type(None).__repr__: format_none,
        float.__repr__: format_float,
        int.__repr__: format_int,
        str.__repr__: format_str,
        bytes.__repr__: format_bytes,
        list.__repr__: format_list,
        tuple.__repr__: format_tuple,
        set.__repr__: format_set,
        dict.__repr__: format_dict,
    }

    _dispatch_generic = {
        "recursion": format_recursion,
        "dataclass": format_dataclass,
        "class": format_class,
    }

    _dispatch_objs = {}

    _context = {}

    def __init__(
        self,
        indentation: int = 2,
        depth: int = 4,
        width: int = 88,
        max_elements: int = 100,
        with_color: bool = True,
    ):
        self._fixed_indentation = indentation
        self._depth = depth
        self._width = width
        self._max_elements = max_elements
        self._color = with_color
        self._indent = 0

    def format_dict(self) -> FormatDict:
        """
        Creates a `FormatDict` object designed for dict-like structures.

        Returns
        -------
        FormatDict
            FormatDict object
        """
        return FormatDict(self)

    def format_list(self) -> FormatSeq:
        """
        Creates a `FormatList` object designed for list-like structures.

        Returns
        -------
        FormatList
            FormatList object
        """
        return FormatList(self)

    def format_class(self, class_name: str) -> FormatClass:
        """
        Creates a `FormatClass` object designed for class-like structures.

        Parameters
        ----------
        class_name : str
            Class name

        Returns
        -------
        FormatClass
            FormatClass object
        """
        return FormatClass(class_name, self)

    def format_tuple(self) -> FormatTuple:
        """
        Creates a `FormatTuple` object designed for tuple-like structures.

        Returns
        -------
        FormatTuple
            FormatTuple object
        """
        return FormatTuple(self)

    def format_set(self) -> FormatSet:
        """
        Creates a `FormatSet` object designed for set-like structures.

        Returns
        -------
        FormatSet
            FormatSet object
        """
        return FormatSet(self)

    def format_value(self) -> FormatValue:
        """
        Creates a `FormatValue` object designed for single values which support
        `__str__` method.

        Returns
        -------
        FormatValue
            FormatValue object
        """
        return FormatValue(self)

    def format_color(self, color: ANSIColors) -> FormatColor:
        """
        Creates a `FormatColor` object designed to apply color formatting to
        values.

        Parameters
        ----------
        color : ANSIColors
            Color value

        Returns
        -------
        FormatColor
            FormatColor object
        """
        return FormatColor(self, color)

    def format_any(self, obj: Any) -> Format:
        """
        Formats any object based on registered format functions registered in
        dispatch private attributes.

        Parameters
        ----------
        obj : Any
            Object to format

        Returns
        -------
        Format
            Format object
        """
        objid = id(obj)
        next_formatter = Formatter(
            self._fixed_indentation,
            self._depth - 1,
            self._width,
            self._max_elements,
            self._color,
        ).with_indent(self._indent + self._fixed_indentation)
        if objid in self._context:
            return self._dispatch_generic["recursion"](obj, next_formatter)

        format_func = self._dispatch_repr.get(
            type(obj).__repr__, self._dispatch_objs.get(type(obj).__name__)
        )
        if format_func is None:
            if is_dataclass(obj):
                return self._dispatch_generic["dataclass"](obj, next_formatter)
            if hasattr(obj, "__dict__"):
                return self._dispatch_generic["class"](obj, next_formatter)
            raise NotImplementedError(f"No format function found for {type(obj)}")

        self._context[objid] = 1
        f = format_func(obj, next_formatter)
        del self._context[objid]
        return f

    def with_indent(self, indent: int) -> Formatter:
        """
        Updates the current indentation and returns itself

        Parameters
        ----------
        indent : int
            Indent value

        Returns
        -------
        Formatter
            Itself
        """
        self._indent = indent
        return self

    def width(self) -> int:
        """
        Returns the maximum amount of allowed characters on one line.

        Returns
        -------
        int
            Width value
        """
        return self._width

    def depth(self) -> int:
        """
        Returns the current depth of the nested object.

        Returns
        -------
        int
            Current depth value
        """
        return self._depth

    def indent(self) -> int:
        """
        Returns the indentation of the nested object.

        Returns
        -------
        int
            Current indentation value
        """
        return self._indent

    def fixed_indent(self) -> int:
        """
        Returns the fixed number of spaces used for each indentation level.

        Returns
        -------
        int
            Fixed indentation value
        """
        return self._fixed_indentation

    def max_elements(self) -> int:
        """
        Returns the maximum amount of elements formatted for each object.

        Returns
        -------
        int
            Maximum elements
        """
        return self._max_elements

    def color(self) -> bool:
        """
        Determines if colored output is enabled.

        Returns
        -------
        bool
            Color condition boolean
        """
        return self._color
