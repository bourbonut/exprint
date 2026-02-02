import io
from typing import Any

import pytest

from exprint import ANSIColors, exprint


@pytest.mark.parametrize(
    "input_value, with_color, expected",
    [
        [10, False, "10\n"],
        [
            10,
            True,
            f"{ANSIColors.YELLOW.value}10{ANSIColors.RESET.value}\n",
        ],
        [10.2948209, False, "10.2948209\n"],
        [
            10.2948209,
            True,
            f"{ANSIColors.YELLOW.value}10.2948209{ANSIColors.RESET.value}\n",
        ],
        ["10", False, '"10"\n'],
        [
            "10",
            True,
            f'{ANSIColors.GREEN.value}"10"{ANSIColors.RESET.value}\n',
        ],
        [b"10", False, "b'10'\n"],
        [
            b"10",
            True,
            f"{ANSIColors.GREEN.value}b'10'{ANSIColors.RESET.value}\n",
        ],
    ],
)
def test_builtin(input_value: Any, with_color: bool, expected: str):
    stream = io.StringIO()
    exprint(input_value, stream=stream, with_color=with_color)
    assert stream.getvalue() == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        [[], "[]\n"],
        [[1, 2, 3], "[ 1, 2, 3 ]\n"],
        [[[[[10]]]], "[ [ [ [list] ] ] ]\n"],
        [
            list(range(1000)),
            "\n".join(
                [
                    "[",
                    "   0,  1,  2,  3,  4,  5,  6,  7,  8,  9,",
                    "  10, 11, 12, 13, 14, 15, 16, 17, 18, 19,",
                    "  20, 21, 22, 23, 24, 25, 26, 27, 28, 29,",
                    "  30, 31, 32, 33, 34, 35, 36, 37, 38, 39,",
                    "  40, 41, 42, 43, 44, 45, 46, 47, 48, 49,",
                    "  50, 51, 52, 53, 54, 55, 56, 57, 58, 59,",
                    "  60, 61, 62, 63, 64, 65, 66, 67, 68, 69,",
                    "  70, 71, 72, 73, 74, 75, 76, 77, 78, 79,",
                    "  80, 81, 82, 83, 84, 85, 86, 87, 88, 89,",
                    "  90, 91, 92, 93, 94, 95, 96, 97, 98, 99,",
                    "  ... 900 more items",
                    "]",
                    "",
                ]
            ),
        ],
        [
            [list(range(30)) for _ in range(4)],
            "\n".join(
                [
                    "[",
                    "  [",
                    "     0,  1,  2,  3,  4,  5,  6,  7,  8,  9,",
                    "    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,",
                    "    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,",
                    "  ],",
                    "  [",
                    "     0,  1,  2,  3,  4,  5,  6,  7,  8,  9,",
                    "    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,",
                    "    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,",
                    "  ],",
                    "  [",
                    "     0,  1,  2,  3,  4,  5,  6,  7,  8,  9,",
                    "    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,",
                    "    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,",
                    "  ],",
                    "  [",
                    "     0,  1,  2,  3,  4,  5,  6,  7,  8,  9,",
                    "    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,",
                    "    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,",
                    "  ],",
                    "]",
                    "",
                ]
            ),
        ],
    ],
)
def test_list(input_value: list, expected: str):
    stream = io.StringIO()
    exprint(input_value, stream=stream, with_color=False)
    assert stream.getvalue() == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        [{}, "{}\n"],
        [{"a": 10, "b": 20}, '{ "a": 10, "b": 20 }\n'],
        [{0: {1: {2: {3: 10}}}}, "{ 0: { 1: { 2: {dict} } } }\n"],
        [
            {f"key{i}": i for i in range(10)},
            "\n".join(
                [
                    "{",
                    '  "key0": 0,',
                    '  "key1": 1,',
                    '  "key2": 2,',
                    '  "key3": 3,',
                    '  "key4": 4,',
                    '  "key5": 5,',
                    '  "key6": 6,',
                    '  "key7": 7,',
                    '  "key8": 8,',
                    '  "key9": 9,',
                    "}",
                    "",
                ]
            ),
        ],
    ],
)
def test_dict(input_value: list, expected: str):
    stream = io.StringIO()
    exprint(input_value, stream=stream, with_color=False)
    assert stream.getvalue() == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        [set(), "{}\n"],
        [{1, 2, 3}, "{ 1, 2, 3 }\n"],
        [[[[{1, 2, 3}]]], "[ [ [ {set} ] ] ]\n"],
        [
            set(range(1000)),
            "\n".join(
                [
                    "{",
                    "   0,  1,  2,  3,  4,  5,  6,  7,  8,  9,",
                    "  10, 11, 12, 13, 14, 15, 16, 17, 18, 19,",
                    "  20, 21, 22, 23, 24, 25, 26, 27, 28, 29,",
                    "  30, 31, 32, 33, 34, 35, 36, 37, 38, 39,",
                    "  40, 41, 42, 43, 44, 45, 46, 47, 48, 49,",
                    "  50, 51, 52, 53, 54, 55, 56, 57, 58, 59,",
                    "  60, 61, 62, 63, 64, 65, 66, 67, 68, 69,",
                    "  70, 71, 72, 73, 74, 75, 76, 77, 78, 79,",
                    "  80, 81, 82, 83, 84, 85, 86, 87, 88, 89,",
                    "  90, 91, 92, 93, 94, 95, 96, 97, 98, 99,",
                    "  ... 900 more items",
                    "}",
                    "",
                ]
            ),
        ],
    ],
)
def test_set(input_value: list, expected: str):
    stream = io.StringIO()
    exprint(input_value, stream=stream, with_color=False)
    assert stream.getvalue() == expected


@pytest.mark.parametrize(
    "input_value, expected",
    [
        [tuple(), "()\n"],
        [(1, 10.2), "( 1, 10.2 )\n"],
        [[[[(1, 10.2)]]], "[ [ [ (tuple) ] ] ]\n"],
    ],
)
def test_tuple(input_value: list, expected: str):
    stream = io.StringIO()
    exprint(input_value, stream=stream, with_color=False)
    assert stream.getvalue() == expected
