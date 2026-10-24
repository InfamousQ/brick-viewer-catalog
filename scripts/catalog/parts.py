"""parts.json and categories.json, copied verbatim from parts.csv and part_categories.csv."""
from .download import read_csv
from .output import byte_key

PARTS_COLUMNS = ['part_num', 'name', 'category_id', 'material']
CATEGORIES_COLUMNS = ['id', 'name']


def build_parts(raw_dir):
    rows = [[r['part_num'], r['name'], int(r['part_cat_id']), r['part_material']]
            for r in read_csv(raw_dir, 'parts')]
    return sorted(rows, key=lambda row: byte_key(row[0]))


def build_categories(raw_dir):
    rows = [[int(r['id']), r['name']] for r in read_csv(raw_dir, 'part_categories')]
    return sorted(rows)
