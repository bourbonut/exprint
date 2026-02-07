---
hide:
    - toc
    - navigation
---

# Guide

`exprint` offers a flexible API for pretty-printing any Python object.

## topojson-rs example

### Introduction

Let's take for example the class `topojson.TopoJSON` from [topojson-rs](https://github.com/bourbonut/topojson-rs), a Python package written in Rust.

```python
import topojson

topology = topojson.read("./counties-10m.json")
print(topology)
```

It outputs:

```
<builtins.TopoJSON object at 0x74134cc51b10>
```

If you try using `exprint`, it will raise an error:

```python
import topojson
from exprint import exprint

topology = topojson.read("./counties-10m.json")
exprint(topology, max_elements=10)
```

It raises:

```
NotImplementedError: No format function found for <class 'builtins.TopoJSON'>
```

### TopoJSON class

That's is because `TopoJSON` is not supported by default by `exprint` (see supported default objects).

In `topojson` package, a `topojson.TopoJSON` has [four attributes](https://topojson-rs.readthedocs.io/en/latest/api/topojson/#topojson.TopoJSON):

- `transform`: `Optional[topojson.Transform]`
- `objects`: `dict[str, Geometry]`
- `bbox`: `list[float]`
- `arcs`: `list[list[list[int]]]`

So we need to create a function for formatting a `topojson.TopoJSON` object.
Since `topojson.TopoJSON` is a class, we are going to use `Formatter.format_class` method to get a `FormatClass` class for formatting the class.

```python
from exprint import Format, Formatter, dispatch_obj

def format_topojson(obj: topojson.TopoJSON, f: Formatter) -> Format:
    return (
        f.format_class("TopoJSON") # (1)!
        .field("transform", obj.transform)
        .field("objects", obj.objects)
        .field("bbox", obj.bbox)
        .field("arcs", obj.arcs)
    )

# Registers the `format_topojson` function
dispatch_obj(topojson.TopoJSON, format_topojson) # (2)!
```

1. See [`FormatClass`][exprint.formatter.FormatClass] for more details.
2. See [`dispatch_obj`][exprint.dispatch_obj] for more details.

Let's try now:

```python
import topojson
from exprint import exprint

topology = topojson.read("./counties-10m.json")
def format_topojson(...):
    # ...

dispatch_obj(topojson.TopoJSON, format_topojson)
exprint(topology, max_elements=10)
```

Again it raises a new error:

```
NotImplementedError: No format function found for <class 'builtins.Transform'>
```

### Transform class

Alright, we need also to create a function for formatting a `topojson.Transform` object.

In `topojson` package, a `topojson.Transform` has [two attributes](https://topojson-rs.readthedocs.io/en/latest/api/transform/#topojson.Transform):

- `scale`: `list[float]`
- `translate`: `list[float]`

```python
def format_transform(obj: topojson.Transform, f: Formatter) -> Format:
    return (
        f.format_class("Transform")
        .field("scale", obj.scale)
        .field("translate", obj.translate)
    )

# Registers the `format_transform` function
dispatch_obj(topojson.Transform, format_transform)
```

Let's try with this new format function:

```
NotImplementedError: No format function found for <class 'builtins.Geometry_GeometryCollection'>
```

### GeometryCollection class

We face a new issue. What is a `Geometry_GeometryCollection` ?
To keep explanation simple, Rust supports [enum](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html) structures which are converted into a range of multiple classes.
In the case of `topojson` package, a `Geometry` is a union of multiple classes (see [documentation](https://topojson-rs.readthedocs.io/en/latest/api/geometry/)).
However, `topojson` does not allow the user to access to the `Geometry` type or more precisely the `Geometry_GeometryCollection` class.

So we are going to create a format function and use `"Geometry_GeometryCollection"` instead of `topojson.Geometry_GeometryCollection`:

```python
def format_geometry_collection(
    obj: "Geometry_GeometryCollection", f: Formatter
) -> Format:
    return f.format_class("GeometryCollection").field("geometries", obj.geometries)

dispatch_obj("Geometry_GeometryCollection", format_geometry_collection)
```

Now we should be done:

```python
import topojson
from exprint import exprint

topology = topojson.read("./counties-10m.json")
def format_topojson(...):
    # ...

def format_transform(...):
    # ...

def format_geometry_collection(...):
    # ...

dispatch_obj(topojson.TopoJSON, format_topojson)
dispatch_obj(topojson.Transform, format_transform)
dispatch_obj("Geometry_GeometryCollection", format_geometry_collection)
exprint(topology, max_elements=10)
```

It worked !

```
TopoJSON {
  transform: Transform {
    scale: [ 0.003589293992939929, 0.0008590596905969058 ],
    translate: [ -179.14734, -14.552549 ],
  },
  objects: {
    "states": GeometryCollection { geometries: [list] },
    "nation": GeometryCollection { geometries: [list] },
    "counties": GeometryCollection { geometries: [list] },
  },
  bbox: [ -179.14734, -14.552549, 179.77847, 71.352561 ],
  arcs: [
    [ [list], [list] ],
    [ [list], [list], [list] ],
    [ [list], [list] ],
    [ [list], [list], [list], [list] ],
    [ [list], [list] ],
    [ [list], [list] ],
    [ [list], [list] ],
    [
      [list], [list], [list], [list], [list], [list], [list], [list], [list], [list],
      ... 18 more items
    ],
    [ [list], [list] ],
    [
      [list], [list], [list], [list], [list], [list], [list], [list], [list], [list],
      ... 2 more items
    ],
    ... 9859 more items
  ],
}
```

!!! info
    As it was introduced, `Geometry` is a union of classes (enumeration in Rust). Thus, other `Geometry` classes (`Geometry_Point`, `Geometry_MultiPoint`, `Geometry_LineString`, `Geometry_MultiLineString`, `Geometry_Polygon` and `Geometry_MultiPolygon`) must have their own format functions if you want to format correctly any `topojson.TopoJSON` class.

## Complete code

```python
import io
import json
import sys

import topojson

from exprint import Format, Formatter, dispatch_obj, exprint

topology = topojson.read("./counties-10m.json")


def format_topojson(obj: topojson.TopoJSON, f: Formatter) -> Format:
    return (
        f.format_class("TopoJSON")
        .field("transform", obj.transform)
        .field("objects", obj.objects)
        .field("bbox", obj.bbox)
        .field("arcs", obj.arcs)
    )


def format_transform(obj: topojson.Transform, f: Formatter) -> Format:
    return (
        f.format_class("Transform")
        .field("scale", obj.scale)
        .field("translate", obj.translate)
    )


def format_geometry_collection(
    obj: "Geometry_GeometryCollection", f: Formatter
) -> Format:
    return f.format_class("GeometryCollection").field("geometries", obj.geometries)


dispatch_obj(topojson.TopoJSON, format_topojson)
dispatch_obj(topojson.Transform, format_transform)
dispatch_obj("Geometry_GeometryCollection", format_geometry_collection)

exprint(topology, max_elements=10)
```
