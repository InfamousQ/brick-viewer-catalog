"""manifest.json: catalog version, source files and checksums, and the output file list."""
import hashlib
import json

from .download import BASE_URL

# Placeholder wording until the exact terms are copied in (see docs/licensing.md).
ATTRIBUTION = 'Catalog data from Rebrickable (https://rebrickable.com/).'


def version_for(download_date):
    return download_date.replace('-', '.')


def build(record, contents, rows, subset_name=None):
    """contents: file name -> serialised text; rows: file name -> row count."""
    manifest = {
        'format': 1,
        'version': version_for(record['downloaded']),
        'source': {
            'name': 'Rebrickable',
            'url': 'https://rebrickable.com/downloads/',
            'download_url': BASE_URL,
            'downloaded': record['downloaded'],
            'files': record['files'],
        },
        'attribution': ATTRIBUTION,
    }
    if subset_name:
        manifest['subset'] = subset_name
    manifest['files'] = {}
    for name, text in contents.items():
        data = text.encode('utf-8')
        manifest['files'][name] = {
            'rows': rows[name],
            'bytes': len(data),
            'sha256': 'sha256:' + hashlib.sha256(data).hexdigest(),
        }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + '\n'
