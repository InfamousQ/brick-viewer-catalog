"""Checks across all output files (docs/output-format.md). The build writes nothing if any fails."""
from .output import byte_key


def _check_sorted_unique(name, keys, errors):
    for previous, key in zip(keys, keys[1:]):
        if key <= previous:
            errors.append(f'{name}: rows not sorted, or duplicate key, at {key!r}')
            return


def validate(catalog, mold_edges):
    """Return a list of error messages; empty means the catalog is valid."""
    errors = []
    parts = catalog['parts']
    part_nums = {row[0] for row in parts}
    category_ids = {row[0] for row in catalog['categories']}
    color_ids = {row[0] for row in catalog['colors']}

    _check_sorted_unique('parts.json', [byte_key(row[0]) for row in parts], errors)
    _check_sorted_unique('categories.json', [row[0] for row in catalog['categories']], errors)
    _check_sorted_unique('colors.json', [row[0] for row in catalog['colors']], errors)
    _check_sorted_unique('part_colors.json', [(byte_key(r[0]), r[1]) for r in catalog['part_colors']], errors)
    _check_sorted_unique('mold_groups.json', [byte_key(g[0]) for g in catalog['mold_groups']], errors)

    for row in parts:
        if row[2] not in category_ids:
            errors.append(f'parts.json: {row[0]} has unknown category {row[2]}')

    for part, color in catalog['part_colors']:
        if part not in part_nums:
            errors.append(f'part_colors.json: unknown part {part!r}')
        if color not in color_ids:
            errors.append(f'part_colors.json: unknown color {color} for {part!r}')

    group_of = {}
    for index, group in enumerate(catalog['mold_groups']):
        if len(group) < 2:
            errors.append(f'mold_groups.json: group {group} has fewer than 2 parts')
        for part in group:
            if part not in part_nums:
                errors.append(f'mold_groups.json: unknown part {part!r}')
            if part in group_of:
                errors.append(f'mold_groups.json: {part!r} is in more than one group')
            group_of[part] = index

    # A subset may leave both ends of an edge out, but never just one.
    for a, b in mold_edges:
        if a in part_nums or b in part_nums:
            if group_of.get(a) is None or group_of.get(a) != group_of.get(b):
                errors.append(f'mold_groups.json: M edge {a} - {b} is not inside one group')

    return errors[:50] + ([f'... and {len(errors) - 50} more'] if len(errors) > 50 else [])
