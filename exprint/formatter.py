from __future__ import annotations

import io
from abc import ABC, abstractmethod
from itertools import islice
from typing import Any, Callable, Iterable, Protocol, Sized, TypeAlias

__all__ = ["Formatter", "Format"]

ToString: TypeAlias = Any


class IterableAndSized(Iterable[Any], Sized, Protocol):
    pass


class Format(ABC):
    def __init__(self, formatter: Formatter):
        self.formatter = formatter

    # @abstractmethod
    def width(self) -> int: ...

    @abstractmethod
    def finish(self, stream: io.TextIOBase) -> str: ...


class FormatTuple(Format):
    def __init__(self, formatter: Formatter):
        super().__init__(formatter)
        # TODO: think differently
        self._values = []

    def field(self, value: Any) -> FormatTuple:
        self._values.append(value)
        return self

    def finish(self, stream: io.TextIOBase):
        pass


def width_list(cols: int, col_widths: list[int], indent: int):
    return sum(col_widths) + (cols - 1) * 2 + indent + 1


def estimate_list_widths(
    widths: list[int], indentation: int, max_width: int, columns: int = 10
) -> tuple[int, list[int]]:
    columns = min(len(widths), columns)
    for cols in range(columns, 0, -1):
        rows, els = divmod(len(widths), cols)
        col_widths = [
            max([widths[cols * i + c] for i in range(rows + int(c < els))])
            for c in range(cols)
        ]
        width = width_list(cols, col_widths, indentation)
        if width < max_width:
            break
    return cols, col_widths


class FormatList(Format):
    def __init__(self, formatter: Formatter):
        super().__init__(formatter)
        self._values = []
        self._widths = []
        self._length = 0
        self._cache = None

    def value(self, value: Any) -> FormatList:
        return self.value_with(lambda f: f.format_any(value))

    def value_with(self, value_fmt: Callable[[Formatter], Format]) -> FormatList:
        if len(self._widths) < self.formatter.max_elements():
            value = value_fmt(self.formatter)
            self._widths.append(value.width())
            self._values.append(value)
        self._length += 1
        return self

    def values(self, values: IterableAndSized) -> FormatList:
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
            self._cache = estimate_list_widths(
                self._widths,
                self.formatter.indent(),
                self.formatter.width(),
            )
        cols, col_widths = self._cache
        return width_list(cols, col_widths, self.formatter.indent())

    def finish(self, stream: io.TextIOBase):
        if len(self._values) == 0:
            stream.write("[]")
            return
        m = self.formatter.max_elements()
        widths = self._widths
        inline_width = sum(widths) + len(widths) * 2 + self.formatter.indent()
        if len(self._values) > m or inline_width > self.formatter.width():
            indent = self.formatter.indent()
            fixed_indent = self.formatter.fixed_indent()
            if self._cache is None:
                self._cache = estimate_list_widths(
                    widths,
                    indent,
                    self.formatter.width(),
                )
            n, col_widths = self._cache
            seq = self._values
            q, r = divmod(len(seq), n)

            if n == 1:
                stream.write("[\n")
                imax = len(self._values)
                stream.write(" " * indent)
                for i, value in enumerate(seq):
                    value.finish(stream)
                    if i + 1 != imax:
                        stream.write(",\n")
                        stream.write(" " * indent)
                    else:
                        stream.write(",\n")
                if self._length > m:
                    stream.write(" " * indent)
                    stream.write(f"... {self._length - m} more items\n")
                stream.write(" " * (indent - fixed_indent) + "]")
                return

            def format_row(subseq: list[Format]):
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

            stream.write("[\n")
            for i in range(q):
                format_row(seq[n * i : n * (i + 1)])
            if r > 0:
                format_row(seq[n * (i + 1) : n * (i + 1) + r])
            if self._length > m:
                stream.write(" " * indent)
                stream.write(f"... {self._length - m} more items\n")
            stream.write(" " * (indent - fixed_indent))
            stream.write("]")
            return

        stream.write("[ ")
        imax = len(self._values)
        for i, value in enumerate(self._values):
            value.finish(stream)
            if i + 1 != imax:
                stream.write(", ")
        stream.write(" ]")


def estimate_dict_width(
    keys: list[Format],
    values: list[Format],
    max_width: int,
    indent: int,
    max_elements: int,
) -> tuple[bool, int]:
    m = max_elements
    kwidths = [k.width() for k in keys]
    vwidths = [v.width() for v in values]
    inline_width = sum(kwidths) + sum(vwidths) + 2 * len(values) + indent + 4
    if inline_width <= max_width:
        return False, inline_width
    width = max([kw + vw + 2 + indent for kw, vw in zip(kwidths[:m], vwidths[:m])])
    return True, width


class FormatDict(Format):
    def __init__(self, formatter: Formatter):
        super().__init__(formatter)
        self._keys = []
        self._values = []
        self._cache = None

    def key(self, key: Any) -> FormatDict:
        return self.key_with(lambda f: f.format_any(key))

    def key_with(self, key_fmt: Callable[[Formatter], Format]) -> FormatDict:
        self._keys.append(key_fmt(self.formatter))
        return self

    def value(self, value: Any) -> FormatDict:
        return self.value_with(lambda f: f.format_any(value))

    def value_with(self, value_fmt: Callable[[Formatter], Format]) -> FormatDict:
        self._values.append(value_fmt(self.formatter))
        return self

    def item(self, key: Any, value: Any) -> FormatDict:
        return self.key(key).value(value)

    def items(self, values: Iterable[tuple[Any, Any]]) -> FormatDict:
        for key, value in values:
            self.item(key, value)
        return self

    def width(self) -> int:
        lkeys = len(self._keys)
        lvalues = len(self._values)
        if lkeys < lvalues:
            raise ValueError(
                f"Missing keys (length keys: {lkeys}, length values: {lvalues})"
            )
        if lkeys > lvalues:
            raise ValueError(
                f"Missing values (length keys: {lkeys}, length values: {lvalues})"
            )
        if self._cache is None:
            self._cache = estimate_dict_width(
                self._keys,
                self._values,
                self.formatter.width(),
                self.formatter.indent(),
                self.formatter.max_elements(),
            )
        return self._cache[1]

    def finish(self, stream: io.TextIOBase):
        lkeys = len(self._keys)
        lvalues = len(self._values)
        if lkeys < lvalues:
            raise ValueError(
                f"Missing keys (length keys: {lkeys}, length values: {lvalues})"
            )
        if lkeys > lvalues:
            raise ValueError(
                f"Missing values (length keys: {lkeys}, length values: {lvalues})"
            )
        if self._cache is None:
            self._cache = estimate_dict_width(
                self._keys,
                self._values,
                self.formatter.width(),
                self.formatter.indent(),
                self.formatter.max_elements(),
            )
        multiple_lines = self._cache[0]
        indent = self.formatter.indent()
        fixed_indent = self.formatter.fixed_indent()
        m = self.formatter.max_elements()
        if multiple_lines:
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
            return
        stream.write("{ ")
        imax = len(self._values)
        for i, (key, value) in enumerate(zip(self._keys, self._values)):
            key.finish(stream)
            stream.write(": ")
            value.finish(stream)
            if i + 1 != imax:
                stream.write(", ")
        stream.write(" }")


class FormatClass(Format):
    def __init__(self, class_name: str, formatter: Formatter):
        super().__init__(formatter)
        self._class_name = self.formatter.format_value().value(class_name)
        self._names = []
        self._values = []
        self._cache = None

    def field(self, name: str, value: Any) -> FormatClass:
        return self.field_with(name, lambda f: f.format_any(value))

    def field_with(
        self, name: str, value_fmt: Callable[[Formatter], Format]
    ) -> FormatClass:
        self._names.append(self.formatter.format_value().value(name))
        self._values.append(value_fmt(self.formatter))
        return self

    def width(self) -> int:
        if self._cache is None:
            multiple_lines, width = estimate_dict_width(
                self._names,
                self._values,
                self.formatter.width(),
                self.formatter.indent(),
                self.formatter.max_elements(),
            )
            if multiple_lines:
                self._cache = (multiple_lines, width)
            else:
                self._cache = (multiple_lines, width + self._class_name.width() + 1)
        return self._cache[1]

    def finish(self, stream: io.TextIOBase):
        if self._cache is None:
            multiple_lines, width = estimate_dict_width(
                self._names,
                self._values,
                self.formatter.width(),
                self.formatter.indent(),
                self.formatter.max_elements(),
            )
            if multiple_lines:
                self._cache = (multiple_lines, width)
            else:
                self._cache = (multiple_lines, width + self._class_name.width() + 1)
        multiple_lines = self._cache[0]
        indent = self.formatter.indent()
        fixed_indent = self.formatter.fixed_indent()
        m = self.formatter.max_elements()
        if multiple_lines:
            self._class_name.finish(stream)
            stream.write(" {\n")
            for key, value in zip(self._names[:m], self._values[:m]):
                stream.write(" " * indent)
                key.finish(stream)
                stream.write(": ")
                value.finish(stream)
                stream.write(",\n")
            if len(self._values) > m:
                stream.write(" " * indent + f"... {len(self._values) - m} more items\n")
            stream.write(" " * (indent - fixed_indent))
            stream.write("}")
            return
        self._class_name.finish(stream)
        stream.write(" { ")
        imax = len(self._values)
        for i, (key, value) in enumerate(zip(self._names, self._values)):
            key.finish(stream)
            stream.write(": ")
            value.finish(stream)
            if i + 1 != imax:
                stream.write(", ")
        stream.write(" }")


class FormatValue(Format):
    def __init__(self, formatter: Formatter):
        super().__init__(formatter)
        self._value = None
        self._width = 0

    def value(self, value: ToString) -> FormatValue:
        self._value = str(value)
        self._width = len(self._value)
        return self

    def width(self):
        return self._width

    def finish(self, stream: io.TextIOBase):
        if self._value is None:
            raise ValueError("Undefined value")
        stream.write(self._value)


def format_float(obj: float, f: Formatter) -> Format:
    return f.format_value().value(obj)


def format_int(obj: int, f: Formatter) -> Format:
    return f.format_value().value(obj)


def format_str(obj: str, f: Formatter) -> Format:
    return f.format_value().value(repr(obj))


def format_list(obj: list, f: Formatter) -> Format:
    if f.depth() == 0:
        return f.format_value().value("[list]")
    return f.format_list().values(obj)


def format_dict(obj: dict, f: Formatter) -> Format:
    if f.depth() == 0:
        return f.format_value().value("[dict]")
    return f.format_dict().items(obj.items())


class Formatter:
    _dispatch = {
        float.__repr__: format_float,
        int.__repr__: format_int,
        str.__repr__: format_str,
        list.__repr__: format_list,
        dict.__repr__: format_dict,
    }
    _context = {}

    def __init__(
        self,
        indentation: int = 2,
        depth: int = 4,
        width: int = 88,
        max_elements: int = 100,
    ):
        self._fixed_indentation = indentation
        self._depth = depth
        self._width = width
        self._max_elements = max_elements
        self._indent = 0

    def format_dict(self) -> FormatDict:
        return FormatDict(self)

    def format_list(self) -> FormatList:
        return FormatList(self)

    def format_class(self, class_name: str) -> FormatClass:
        return FormatClass(class_name, self)

    def format_tuple(self) -> FormatTuple:
        return FormatTuple(self)

    def format_value(self) -> FormatValue:
        return FormatValue(self)

    def format_any(self, obj: Any) -> Format:
        objid = id(obj)
        if objid in self._context:
            return self.format_value().value("[Recursion]")
        format_func = self._dispatch.get(type(obj).__repr__)
        if format_func is None:
            raise NotImplementedError("...")
        else:
            self._context[objid] = 1
            f = format_func(
                obj,
                Formatter(
                    self._fixed_indentation,
                    self._depth - 1,
                    self._width,
                    self._max_elements,
                ).with_indent(self._indent + self._fixed_indentation),
            )
            del self._context[objid]
            return f

    def with_indent(self, indent: int) -> Formatter:
        self._indent = indent
        return self

    def width(self) -> int:
        return self._width

    def depth(self) -> int:
        return self._depth

    def indent(self) -> int:
        return self._indent

    def fixed_indent(self) -> int:
        return self._fixed_indentation

    def max_elements(self) -> int:
        return self._max_elements
