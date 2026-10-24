"""Serialise catalog files in the committed format (see docs/output-format.md).

One row per line, UTF-8 with non-ASCII written as is, '\\n' line endings and a trailing newline.
"""
import json

FORMAT = 1


def byte_key(value):
    """Sort key for string keys: UTF-8 byte order, independent of the build machine's locale."""
    return value.encode('utf-8')


def _line(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def _body(lines):
    return '\n' + ',\n'.join(lines) + '\n' if lines else '\n'


def table(columns, rows):
    """A column-oriented file: {"format","columns","rows"}. Rows must already be sorted."""
    head = f'{{"format":{FORMAT},"columns":{_line(columns)},"rows":['
    return head + _body([_line(row) for row in rows]) + ']}\n'


def groups(groups):
    """mold_groups.json: {"format","groups"}, one group per line."""
    return f'{{"format":{FORMAT},"groups":[' + _body([_line(g) for g in groups]) + ']}\n'
