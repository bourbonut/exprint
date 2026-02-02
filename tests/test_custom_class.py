import io

from exprint import Format, Formatter, dispatch_obj, exprint


class SimpleClass:
    def __init__(self):
        self.foo = 10.2
        self.bar = "Hello"


class SlotsClass:
    __slots__ = "foo", "bar"

    def __init__(self):
        self.foo = 10.2
        self.bar = "Hello"


def test_simple_class():
    stream = io.StringIO()

    exprint(SimpleClass(), stream=stream, with_color=False)
    assert stream.getvalue() == 'SimpleClass { foo: 10.2, bar: "Hello" }\n'


def test_slot_class():
    stream = io.StringIO()

    def format_slotsclass(obj: SlotsClass, f: Formatter) -> Format:
        return f.format_class("SlotsClass").field("foo", obj.foo).field("bar", obj.bar)

    dispatch_obj(SlotsClass, format_slotsclass)
    exprint(SlotsClass(), stream=stream, with_color=False)
    assert stream.getvalue() == 'SlotsClass { foo: 10.2, bar: "Hello" }\n'
