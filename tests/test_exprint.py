import io

import pytest

from exprint import exprint


def test_end():
    stream = io.StringIO()
    exprint(10.2, stream=stream, with_color=False, end="HelloWorld")
    assert stream.getvalue() == "10.2HelloWorld"


def test_indentation():
    stream = io.StringIO()
    exprint(list(range(100)), stream=stream, with_color=False, indentation=4)
    assert stream.getvalue() == "\n".join(
        [
            "[",
            "     0,  1,  2,  3,  4,  5,  6,  7,  8,  9,",
            "    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,",
            "    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,",
            "    30, 31, 32, 33, 34, 35, 36, 37, 38, 39,",
            "    40, 41, 42, 43, 44, 45, 46, 47, 48, 49,",
            "    50, 51, 52, 53, 54, 55, 56, 57, 58, 59,",
            "    60, 61, 62, 63, 64, 65, 66, 67, 68, 69,",
            "    70, 71, 72, 73, 74, 75, 76, 77, 78, 79,",
            "    80, 81, 82, 83, 84, 85, 86, 87, 88, 89,",
            "    90, 91, 92, 93, 94, 95, 96, 97, 98, 99,",
            "]",
            "",
        ]
    )


@pytest.mark.parametrize("depth", [1, 0])
def test_depth(depth: int):
    stream = io.StringIO()
    exprint(list(range(100)), stream=stream, with_color=False, depth=depth)
    assert stream.getvalue() == "[list]\n"


def test_width():
    stream = io.StringIO()
    seq = list(range(100))
    exprint(seq, stream=stream, with_color=False, width=400)
    c = ", ".join(map(str, seq))
    assert stream.getvalue() == f"[ {c} ]\n"


def test_max_elements():
    stream = io.StringIO()
    exprint(list(range(1000)), stream=stream, with_color=False, max_elements=10)
    assert stream.getvalue() == "\n".join(
        [
            "[",
            "  0, 1, 2, 3, 4, 5, 6, 7, 8, 9,",
            "  ... 990 more items",
            "]",
            "",
        ]
    )
