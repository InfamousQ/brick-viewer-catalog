"""mold_groups.json: connected components of the undirected Mold (M) graph.

Edge direction carries no reliable meaning (cycles and multiple roots exist), so edges are
treated as undirected. Each group is ordered canonical part first: by set usage (descending),
then shorter part_num, then byte order. See docs/data-model.md.
"""
import collections

from .download import read_csv
from .output import byte_key


def read_mold_edges(raw_dir):
    return [(r['child_part_num'], r['parent_part_num'])
            for r in read_csv(raw_dir, 'part_relationships') if r['rel_type'] == 'M']


def _components(edges):
    neighbours = collections.defaultdict(set)
    for a, b in edges:
        neighbours[a].add(b)
        neighbours[b].add(a)
    seen = set()
    for start in neighbours:
        if start in seen:
            continue
        component, stack = [], [start]
        seen.add(start)
        while stack:
            part = stack.pop()
            component.append(part)
            for other in neighbours[part] - seen:
                seen.add(other)
                stack.append(other)
        yield component


def build(edges, usage):
    def member_key(part):
        return (-usage[part], len(part), byte_key(part))

    groups = [sorted(c, key=member_key) for c in _components(edges)]
    return sorted(groups, key=lambda g: byte_key(g[0]))
