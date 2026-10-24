"""Cut a full build down to a curated subset, for development and testing.

A subset file lists one entry per line; '#' starts a comment:

    3001            a part_num
    category:11     every part in a category

Every listed part pulls in its whole mold group, so groups stay complete. Categories and
colors are cut to the ones the remaining parts and pairs use, plus the special colors.
"""
from .colors import SPECIAL


def read(path):
    parts, categories = set(), set()
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        entry = line.split('#', 1)[0].strip()
        if not entry:
            continue
        if entry.startswith('category:'):
            categories.add(int(entry.removeprefix('category:')))
        elif ' ' in entry or ':' in entry:
            raise SystemExit(f'{path}:{number}: cannot read {entry!r}')
        else:
            parts.add(entry)
    return parts, categories


def apply(catalog, path):
    wanted_parts, wanted_categories = read(path)
    known = {row[0] for row in catalog['parts']}
    missing = sorted(wanted_parts - known)
    if missing:
        raise SystemExit(f'{path}: parts not in parts.csv: {", ".join(missing)}')
    known_categories = {row[0] for row in catalog['categories']}
    missing = sorted(wanted_categories - known_categories)
    if missing:
        raise SystemExit(f'{path}: categories not in part_categories.csv: {", ".join(map(str, missing))}')

    keep = wanted_parts | {row[0] for row in catalog['parts'] if row[2] in wanted_categories}
    groups = [g for g in catalog['mold_groups'] if keep.intersection(g)]
    for g in groups:
        keep.update(g)

    parts = [row for row in catalog['parts'] if row[0] in keep]
    pairs = [row for row in catalog['part_colors'] if row[0] in keep]
    used_categories = {row[2] for row in parts}
    used_colors = {row[1] for row in pairs} | SPECIAL
    return {
        'parts': parts,
        'categories': [row for row in catalog['categories'] if row[0] in used_categories],
        'mold_groups': groups,
        'colors': [row for row in catalog['colors'] if row[0] in used_colors],
        'part_colors': pairs,
    }
