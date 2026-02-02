import io
from dataclasses import dataclass

from exprint import exprint


@dataclass
class SimpleDataclass:
    foo: float
    bar: str


@dataclass
class NestedDataclass:
    simple: SimpleDataclass


def test_simple_dataclass():
    stream = io.StringIO()
    exprint(SimpleDataclass(10.2, "Hello"), stream=stream, with_color=False)
    assert stream.getvalue() == 'SimpleDataclass { foo: 10.2, bar: "Hello" }\n'


def test_nested_dataclass():
    stream = io.StringIO()
    exprint(
        NestedDataclass(SimpleDataclass(10.2, "Hello")), stream=stream, with_color=False
    )
    assert (
        stream.getvalue()
        == 'NestedDataclass { simple: { "foo": 10.2, "bar": "Hello" } }\n'
    )
