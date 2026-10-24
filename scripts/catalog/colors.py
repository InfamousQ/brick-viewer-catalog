"""colors.json from colors.csv. Drops the num_parts/num_sets popularity counters (see docs/data-model.md)."""
from .download import read_csv

COLUMNS = ['id', 'name', 'rgb', 'is_trans', 'y1', 'y2']
# Special colors, kept in every build (also subsets) so the app can always offer them.
SPECIAL = {-1, 9999}


def _year(value):
    return int(value) if value else None


def _bool(value):
    if value not in ('True', 'False'):
        raise ValueError(f'unexpected is_trans value {value!r} in colors.csv')
    return value == 'True'


def build(raw_dir):
    rows = [[int(r['id']), r['name'], r['rgb'], _bool(r['is_trans']), _year(r['y1']), _year(r['y2'])]
            for r in read_csv(raw_dir, 'colors')]
    return sorted(rows)
