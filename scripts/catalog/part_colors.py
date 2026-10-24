"""part_colors.json: the union of (part, color) pairs from inventory_parts.csv and elements.csv.

Neither source alone is complete (see docs/data-model.md). Pairs that reference a part or color
missing from parts.csv/colors.csv are dropped and reported, since pairs are only hints.
"""
from .download import read_csv
from .output import byte_key

COLUMNS = ['part_num', 'color_id']


def build(raw_dir, inventory, part_nums, color_ids):
    """Return (rows, dropped), where dropped is the sorted list of pairs with an unknown part or color."""
    pairs = set(inventory.pairs)
    pairs.update((r['part_num'], int(r['color_id'])) for r in read_csv(raw_dir, 'elements'))
    rows, dropped = [], []
    for pair in pairs:
        (rows if pair[0] in part_nums and pair[1] in color_ids else dropped).append(list(pair))
    key = lambda row: (byte_key(row[0]), row[1])
    return sorted(rows, key=key), sorted(dropped, key=key)
