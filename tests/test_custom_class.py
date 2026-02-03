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


class LongClass:
    def __init__(self):
        self.foo1 = 11.2
        self.foo2 = 12.2
        self.foo3 = 13.2
        self.foo4 = 14.2
        self.foo5 = 15.2
        self.foo6 = 16.2
        self.foo7 = 17.2
        self.foo8 = 18.2
        self.foo9 = 19.2
        self.foo10 = 110.2
        self.foo11 = 111.2
        self.foo12 = 112.2
        self.foo13 = 113.2
        self.foo14 = 114.2
        self.foo15 = 115.2
        self.foo16 = 116.2
        self.foo17 = 117.2
        self.foo18 = 118.2
        self.foo19 = 119.2
        self.foo20 = 120.2
        self.foo21 = 121.2
        self.foo22 = 122.2
        self.foo23 = 123.2
        self.foo24 = 124.2
        self.foo25 = 125.2
        self.foo26 = 126.2
        self.foo27 = 127.2
        self.foo28 = 128.2
        self.foo29 = 129.2
        self.foo30 = 130.2
        self.foo31 = 131.2
        self.foo32 = 132.2
        self.foo33 = 133.2
        self.foo34 = 134.2
        self.foo35 = 135.2
        self.foo36 = 136.2


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


def test_long_class():
    stream = io.StringIO()

    exprint(LongClass(), stream=stream, with_color=False)
    assert stream.getvalue() == "\n".join(
        [
            "LongClass {",
            "  foo1: 11.2,",
            "  foo2: 12.2,",
            "  foo3: 13.2,",
            "  foo4: 14.2,",
            "  foo5: 15.2,",
            "  foo6: 16.2,",
            "  foo7: 17.2,",
            "  foo8: 18.2,",
            "  foo9: 19.2,",
            "  foo10: 110.2,",
            "  foo11: 111.2,",
            "  foo12: 112.2,",
            "  foo13: 113.2,",
            "  foo14: 114.2,",
            "  foo15: 115.2,",
            "  foo16: 116.2,",
            "  foo17: 117.2,",
            "  foo18: 118.2,",
            "  foo19: 119.2,",
            "  foo20: 120.2,",
            "  foo21: 121.2,",
            "  foo22: 122.2,",
            "  foo23: 123.2,",
            "  foo24: 124.2,",
            "  foo25: 125.2,",
            "  foo26: 126.2,",
            "  foo27: 127.2,",
            "  foo28: 128.2,",
            "  foo29: 129.2,",
            "  foo30: 130.2,",
            "  foo31: 131.2,",
            "  foo32: 132.2,",
            "  foo33: 133.2,",
            "  foo34: 134.2,",
            "  foo35: 135.2,",
            "  foo36: 136.2,",
            "}",
            "",
        ]
    )
