# Filler Template Engine

Create text-based file from template.

Standard Django/Jinja compatible format.

Tiny size - less than 200 lines in one file.

No dependencies, not even stdlib - pure python only.

Supports all essential operations:

- Variable/expression expansion {{ a+b }}
- Conditional inclusion (if/elif/else) {% if a<3 %}
- Repetitions {% for var in iterable %}

Block/include tags may be added later.

## Build

Run tests:

```python -m unittest```

Build tarball + wheel:

```python -m build```

## Contacts

Email oda16m@gmail.com
