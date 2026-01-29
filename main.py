from __future__ import annotations

import io
import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Sequence, TypeAlias

import orjson

ToString: TypeAlias = Any

with open("./counties-10m.json", "r") as file:
    data = orjson.loads(file.read())


class Format(ABC):
    def __init__(self, formatter: Formatter):
        self._formatter = formatter

    # @abstractmethod
    def width(self) -> int: ...

    @abstractmethod
    def finish(self) -> str: ...


class FormatClass(Format):
    def __init__(self, formatter: Formatter):
        super().__init__(formatter)
        self._names = []
        self._values = []

    def field(self, name: str, value: Any) -> FormatClass:
        return self.field_with(name, lambda f: f.format_any(value))

    def field_with(
        self, name: str, value_fmt: Callable[[Formatter], Format]
    ) -> FormatClass:
        self._names.append(name)
        self._values.append(value_fmt(self._formatter))
        return self

    def finish(self):
        pass


class FormatTuple(Format):
    def __init__(self, formatter: Formatter):
        super().__init__(formatter)
        # TODO: think differently
        self._values = []

    def field(self, value: Any) -> FormatTuple:
        self._values.append(value)
        return self

    def finish(self):
        pass


class FormatList(Format):
    def __init__(self, formatter: Formatter):
        super().__init__(formatter)
        self._values = []
        self._widths = []

    def value(self, value: Any) -> FormatList:
        return self.value_with(lambda f: f.format_any(value))

    def value_with(self, value_fmt: Callable[[Formatter], Format]) -> FormatList:
        value = value_fmt(self._formatter)
        self._widths.append(value.width())
        self._values.append(value)
        return self

    def values(self, values: Sequence[Any]) -> FormatList:
        for value in values:
            self.value(value)
        return self

    def _total_width(self):
        return sum(self._widths) + (len(self._widths) - 1) * 2 + 2

    def width(self) -> int:
        if len(self._widths) == 0:
            return 2
        return min(self._total_width(), self._formatter._width)

    def finish(self):
        max_width = self._formatter.width()
        if self._total_width() > max_width:
            indent = self._formatter.indent()
            values = []
            current_width = indent
            counter = 0
            string = ["["]
            for value, width in zip(self._values, self._widths):
                if counter > self._formatter.max_elements():
                    string.append(
                        " " * indent
                        + f"... {len(self._values) - counter + 1} more items"
                    )
                    values.clear()
                    break
                if current_width + width + 1 > max_width:
                    string.append(
                        " " * indent + ", ".join(v.finish() for v in values) + ", "
                    )
                    values = [value]
                    current_width = indent + width + 2
                else:
                    values.append(value)
                    current_width += width + 2
                counter += 1
            if len(values) > 0:
                string.append(
                    " " * indent + ", ".join(v.finish() for v in values) + ", "
                )
            string.append("]")
            return "\n".join(string)
        return f"[ {', '.join(value.finish() for value in self._values)} ]"


class FormatDict(Format):
    def __init__(self, formatter: Formatter):
        super().__init__(formatter)
        self._keys = []
        self._values = []

    def key(self, key: Any) -> FormatDict:
        self._keys.append(key)
        return self

    def value(self, value: Any) -> FormatDict:
        self._values.append(value)
        return self

    def item(self, key: Any, value: Any) -> FormatDict:
        self._keys.append(key)
        self._values.append(value)
        return self

    def items(self, values: Sequence[tuple[Any, Any]]) -> FormatDict:
        for key, value in values:
            self._keys.append(key)
            self._values.append(value)
        return self

    def finish(self):
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
        pass


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

    def finish(self):
        if self._value is None:
            raise ValueError("Undefined value")
        return self._value


def format_float(obj: float, f: Formatter) -> Format:
    return f.format_value().value(obj)


def format_list(obj: list, f: Formatter) -> Format:
    return f.format_list().values(obj)


class Formatter:
    _dispatch = {
        float.__repr__: format_float,
        list.__repr__: format_list,
    }
    _context = {}

    def __init__(
        self,
        indentation: int = 2,
        depth: int = 2,
        width: int = 88,
        max_elements: int = 100,
    ):
        self._indentation = indentation
        self._depth = depth
        self._width = width
        self._max_elements = max_elements
        self._indent = 0

    def format_dict(self) -> FormatDict:
        return FormatDict(self)

    def format_list(self) -> FormatList:
        return FormatList(self)

    def format_class(self) -> FormatClass:
        return FormatClass(self)

    def format_tuple(self) -> FormatTuple:
        return FormatTuple(self)

    def format_value(self) -> FormatValue:
        return FormatValue(self)

    def format_any(self, obj: Any) -> Format:
        objid = id(obj)
        if objid in self._context:
            return self.format_value().value(
                f"(recursion {type(obj).__name__} on id={objid})"
            )
        format_func = self._dispatch.get(type(obj).__repr__)
        if format_func is None:
            raise NotImplementedError("...")
        else:
            self._context[objid] = 1
            f = format_func(
                obj,
                Formatter(
                    self._indentation,
                    self._depth - 1,
                    self._width,
                    self._max_elements,
                ).increase_indent(),
            )
            del self._context[objid]
            return f

    def increase_indent(self) -> Formatter:
        self._indent += self._indentation
        return self

    def width(self) -> int:
        return self._width

    def depth(self) -> int:
        return self._depth

    def indent(self) -> int:
        return self._indent

    def max_elements(self) -> int:
        return self._max_elements


class Airprint:
    def __init__(
        self,
        stream: io.TextIOBase | None = None,
        indentation: int = 2,
        depth: int = 2,
        width: int = 88,
        max_elements: int = 100,
    ):
        self._stream: io.TextIOBase = sys.stdout if stream is None else stream
        self._formatter = Formatter(
            indentation,
            depth,
            width,
            max_elements,
        ).increase_indent()

    def print(self, obj: Any):
        self._stream.write(self._formatter.format_any(obj).finish())
        self._stream.write("\n")


# Parameters
# - indentation
# - depth
# - max chararacters
# - max displayed elements

# print(data["arcs"][0])
a = Airprint()
a.print([float(x + 1) for x in range(1000)])
