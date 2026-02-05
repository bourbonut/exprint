---
hide:
    - toc
    - navigation
---

# Welcome

Welcome to the [exprint](https://github.com/bourbonut/exprint) documentation.

## What is exprint ?

`exprint` is a small Python package for helping you to explore easly and quickly your data by pretty-printing values with a flexible API. `exprint` is inspired by [NodeJS](https://nodejs.org/) pretty-printing and [Formatter](https://doc.rust-lang.org/std/fmt/struct.Formatter.html) API in [Rust](https://rust-lang.org/).

<div class="grid cards" markdown>

- :material-check-bold: __Easy to use__

    ---

    Implements concise code to explore your data

- :octicons-package-dependencies-16: __No dependencies__

    ---

    `exprint` requires no dependencies and is written 100% in Python.

- :material-scale-balance: __Open Source__

    ---

    `exprint` is licensed under MIT.

</div>

## Installation

`exprint` is available on PyPi.

```bash
pip install exprint
```

## Example

```python
import json
from exprint import exprint

# https://github.com/topojson/us-atlas?tab=readme-ov-file#counties-10m.json
with open("./counties-10m.json") as file:
    data = json.load(file)

exprint(data, max_elements=10)
```

In your terminal, you will have a 
<span class="colored">
    <span style="animation-delay:0s;">c</span>
    <span style="animation-delay:0.1s;">o</span>
    <span style="animation-delay:0.2s;">l</span>
    <span style="animation-delay:0.3s;">o</span>
    <span style="animation-delay:0.4s;">r</span>
    <span style="animation-delay:0.5s;">e</span>
    <span style="animation-delay:0.6s;">d</span>
</span>
output.

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
