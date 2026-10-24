"""Download the Rebrickable bulk CSVs into raw/ and record their checksums.

raw/download.json records the download date and sha256 of each file, so --offline builds
can reuse the same files and still write a correct manifest.
"""
import csv
import datetime
import gzip
import hashlib
import json
import urllib.request

BASE_URL = 'https://cdn.rebrickable.com/media/downloads/'
FILES = [
    'parts.csv.gz',
    'part_categories.csv.gz',
    'part_relationships.csv.gz',
    'colors.csv.gz',
    'elements.csv.gz',
    'inventory_parts.csv.gz',
]
RECORD = 'download.json'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return 'sha256:' + h.hexdigest()


def download(raw_dir):
    """Fetch every source file into raw_dir and return the download record."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        target = raw_dir / name
        tmp = target.with_suffix(target.suffix + '.tmp')
        print(f'Downloading {name}')
        request = urllib.request.Request(BASE_URL + name, headers={'User-Agent': 'brick-viewer-catalog-build'})
        with urllib.request.urlopen(request, timeout=120) as response, open(tmp, 'wb') as f:
            while chunk := response.read(1 << 20):
                f.write(chunk)
        tmp.replace(target)
    record = {
        'downloaded': datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
        'files': {name: sha256(raw_dir / name) for name in FILES},
    }
    (raw_dir / RECORD).write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    return record


def load_record(raw_dir):
    """Return the record of the last download, checking that raw/ still matches it."""
    path = raw_dir / RECORD
    if not path.exists():
        raise SystemExit(f'{path} not found: run once without --offline first')
    record = json.loads(path.read_text(encoding='utf-8'))
    for name in FILES:
        if name not in record['files'] or sha256(raw_dir / name) != record['files'][name]:
            raise SystemExit(f'raw/{name} is missing or changed since the last download: run without --offline')
    return record


def read_csv(raw_dir, name):
    """Yield the rows of raw/<name>.csv.gz as dicts."""
    with gzip.open(raw_dir / f'{name}.csv.gz', 'rt', encoding='utf-8', newline='') as f:
        yield from csv.DictReader(f)
