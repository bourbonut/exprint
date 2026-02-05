# exprint

`exprint` helps you explore data quickly by pretty-printing values with a flexible API.

# Features

- Pretty print with autoformat with colors

```py
from exprint import exprint

seq = [
    index + 1.174298 if index == 10 or index == 9 or index == 8 else float(index + 1)
    for index in range(1000)
]
exprint(seq)
```

```
[
        1.0,  2.0,  3.0,  4.0,  5.0,  6.0,  7.0,  8.0, 9.174298, 10.174298,
  11.174298, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0,     19.0,      20.0,
       21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0,     29.0,      30.0,
       31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0,     39.0,      40.0,
       41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 47.0, 48.0,     49.0,      50.0,
       51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 58.0,     59.0,      60.0,
       61.0, 62.0, 63.0, 64.0, 65.0, 66.0, 67.0, 68.0,     69.0,      70.0,
       71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0,     79.0,      80.0,
       81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0,     89.0,      90.0,
       91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 97.0, 98.0,     99.0,     100.0,
  ... 900 more items
]
```

- Flexible API

```py
from exprint import Format, Formatter, dispatch_obj, exprint

class Example:
    __slots__ = "foo", "bar"

    def __init__(self, foo: str, bar: int):
        self.foo = foo
        self.bar = bar


def format_example(obj: Example, f: Formatter) -> Format:
    return f.format_class("Example").field("foo", obj.foo).field("bar", obj.bar)

# Assiocate the format function to its type
dispatch_obj(Example, format_example)

exprint(Example("Hello", 10))
# Output:
# Example { foo: 'Hello', bar: 10 }
```

# Examples

- Simple list

- JSON data

```python
import json
from exprint import exprint

# https://github.com/topojson/us-atlas?tab=readme-ov-file#counties-10m.json
with open("./counties-10m.json") as file:
    data = json.load(file)

exprint(data, max_elements=10)
```

In your terminal, you will have a colored output.
```
{
  'type': 'Topology',
  'bbox': [ -179.14733999999999, -14.552548999999999, 179.77847, 71.352561 ],
  'transform': {
    'scale': [ 0.003589293992939929, 0.0008590596905969058 ],
    'translate': [ -179.14733999999999, -14.552548999999999 ],
  },
  'objects': {
    'counties': { 'type': 'GeometryCollection', 'geometries': [list] },
    'states': { 'type': 'GeometryCollection', 'geometries': [list] },
    'nation': { 'type': 'GeometryCollection', 'geometries': [list] },
  },
  'arcs': [
    [ [list], [list] ],
    [ [list], [list], [list] ],
    [ [list], [list] ],
    [ [list], [list], [list], [list] ],
    [ [list], [list] ],
    [ [list], [list] ],
    [ [list], [list] ],
    [ [list], [list], [list], [list], [list], [list], [list], [list], [list], [list] ],
    [ [list], [list] ],
    [ [list], [list], [list], [list], [list], [list], [list], [list], [list], [list] ],
    ... 9859 more items
  ],
}
```
