#!/usr/bin/env python3
"""Build the catalog from Rebrickable bulk CSVs: download -> skip if unchanged -> transform -> validate -> write.

Usage: python3 scripts/build.py [--offline] [--force] [--subset FILE] [--out DIR]

  --offline       reuse the files already in raw/ instead of downloading
  --force         build even if the source files are unchanged since the last build in --out
  --subset FILE   build only the parts listed in FILE (see scripts/catalog/subset.py), e.g. subsets/sample.txt
  --out DIR       where to write the catalog files and manifest.json (default: data/)

Nothing is written unless every validation check passes. Committing and tagging the new
version is a separate step (see docs/refresh.md).
"""
import argparse
import json
import pathlib
import sys

from catalog import colors, download, inventory, manifest, mold_groups, output, part_colors, parts, subset
from catalog.validate import validate

ROOT = pathlib.Path(__file__).resolve().parent.parent


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--subset', type=pathlib.Path)
    parser.add_argument('--out', type=pathlib.Path, default=ROOT / 'data')
    parser.add_argument('--raw', type=pathlib.Path, default=ROOT / 'raw', help=argparse.SUPPRESS)
    return parser.parse_args()


def subset_name(path):
    return path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else path.name


def unchanged(out_dir, record, subset_label):
    path = out_dir / 'manifest.json'
    if not path.exists():
        return False
    previous = json.loads(path.read_text(encoding='utf-8'))
    return previous['source']['files'] == record['files'] and previous.get('subset') == subset_label


def transform(raw_dir):
    print('Reading parts, categories and colors')
    catalog = {
        'parts': parts.build_parts(raw_dir),
        'categories': parts.build_categories(raw_dir),
        'colors': colors.build(raw_dir),
    }
    print('Reading inventory_parts (the slow one)')
    scan = inventory.scan(raw_dir)
    edges = mold_groups.read_mold_edges(raw_dir)
    catalog['mold_groups'] = mold_groups.build(edges, scan.usage)
    catalog['part_colors'], dropped = part_colors.build(
        raw_dir, scan, {row[0] for row in catalog['parts']}, {row[0] for row in catalog['colors']})
    if dropped:
        sample = ', '.join(f'{p}/{c}' for p, c in dropped[:5])
        print(f'Dropped {len(dropped)} part-color pairs with an unknown part or color (e.g. {sample})')
    return catalog, edges


def serialise(catalog):
    contents = {
        'parts.json': output.table(parts.PARTS_COLUMNS, catalog['parts']),
        'categories.json': output.table(parts.CATEGORIES_COLUMNS, catalog['categories']),
        'mold_groups.json': output.groups(catalog['mold_groups']),
        'colors.json': output.table(colors.COLUMNS, catalog['colors']),
        'part_colors.json': output.table(part_colors.COLUMNS, catalog['part_colors']),
    }
    rows = {f'{name}.json': len(value) for name, value in catalog.items()}
    return contents, rows


def main():
    args = parse_args()
    record = download.load_record(args.raw) if args.offline else download.download(args.raw)
    subset_label = subset_name(args.subset) if args.subset else None
    if not args.force and unchanged(args.out, record, subset_label):
        print(f'Source files unchanged since the build in {args.out}; nothing to do (use --force to rebuild)')
        return

    catalog, edges = transform(args.raw)
    if args.subset:
        catalog = subset.apply(catalog, args.subset)

    errors = validate(catalog, edges)
    if errors:
        print('Validation failed, nothing written:', *errors, sep='\n  ', file=sys.stderr)
        sys.exit(1)

    contents, rows = serialise(catalog)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in contents.items():
        (args.out / name).write_text(text, encoding='utf-8', newline='\n')
    # Written last, so a manifest always describes complete files.
    (args.out / 'manifest.json').write_text(
        manifest.build(record, contents, rows, subset_label), encoding='utf-8', newline='\n')

    summary = ', '.join(f'{rows[name]} {name.removesuffix(".json")}' for name in contents)
    print(f'Built catalog {manifest.version_for(record["downloaded"])} in {args.out}: {summary}')


if __name__ == '__main__':
    main()
