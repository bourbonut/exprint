---
hide:
    - navigation
---

# Default format functions

## `None`

```py
def format_none(obj: None, f: Formatter) -> Format:
    return f.format_value().value(obj)
```

## `bool`

```py
def format_bool(obj: bool, f: Formatter) -> Format:
    return f.format_color(ANSIColors.YELLOW).value(f.format_value().value(obj))
```

## `float`

```py
def format_float(obj: float, f: Formatter) -> Format:
    return f.format_color(ANSIColors.YELLOW).value(f.format_value().value(obj))
```

## `int`

```py
def format_int(obj: int, f: Formatter) -> Format:
    return f.format_color(ANSIColors.YELLOW).value(f.format_value().value(obj))
```

## `str`

```py
def format_str(obj: str, f: Formatter) -> Format:
    return f.format_color(ANSIColors.GREEN).value(f.format_value().value(f'"{obj}"'))
```

## `bytes`

```py
def format_bytes(obj: int, f: Formatter) -> Format:
    return f.format_color(ANSIColors.GREEN).value(f.format_value().value(obj))
```

## `list`

```py
def format_list(obj: list, f: Formatter) -> Format:
    if f.depth() <= 0:
        return f.format_color(ANSIColors.CYAN).value(f.format_value().value("[list]"))
    return f.format_list().values(obj)
```

## `tuple`

```py
def format_tuple(obj: tuple, f: Formatter) -> Format:
    if f.depth() <= 0:
        return f.format_color(ANSIColors.CYAN).value(f.format_value().value("(tuple)"))
    return f.format_tuple().values(obj)
```

## `set`

```py
def format_set(obj: set, f: Formatter) -> Format:
    if f.depth() <= 0:
        return f.format_color(ANSIColors.CYAN).value(f.format_value().value("{set}"))
    return f.format_set().values(obj)
```

## `dict`

```py
def format_dict(obj: dict, f: Formatter) -> Format:
    if f.depth() <= 0:
        return f.format_color(ANSIColors.CYAN).value(f.format_value().value("{dict}"))
    return f.format_dict().items(obj.items())
```

## `"recursion"`

```py
def format_recursion(obj: Any, f: Formatter) -> Format:
    return f.format_color(ANSIColors.MAGENTA).value(
        f.format_value().value("[recursion]")
    )
```

## `"dataclass"`

```py
def format_dataclass(obj: Any, f: Formatter) -> Format:
    fclass = f.format_class(obj.__class__.__name__)
    for name, value in asdict(obj).items():
        fclass.field(name, value)
    return fclass
```

## `"class"`

```py
def format_class(obj: Any, f: Formatter) -> Format:
    fclass = f.format_class(obj.__class__.__name__)
    for name, value in obj.__dict__.items():
        fclass.field(name, value)
    return fclass
```
