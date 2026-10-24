"""One pass over inventory_parts.csv, the largest source file.

Collects what two outputs need: the (part, color) pairs for part_colors.json and the per-part
set usage that picks the canonical part of each mold group.
"""
import collections

from .download import read_csv


class InventoryScan:
    def __init__(self, pairs, usage):
        self.pairs = pairs  # set of (part_num, color_id)
        self.usage = usage  # Counter: part_num -> number of distinct inventories it appears in


def scan(raw_dir):
    pairs = set()
    inventories = collections.defaultdict(set)
    for r in read_csv(raw_dir, 'inventory_parts'):
        pairs.add((r['part_num'], int(r['color_id'])))
        inventories[r['part_num']].add(r['inventory_id'])
    usage = collections.Counter({part: len(ids) for part, ids in inventories.items()})
    return InventoryScan(pairs, usage)
