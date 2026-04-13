"""One-time data migration utility

Usage:
    python scripts/migrate_data.py [--apply]

By default the script does a dry-run and prints the planned changes. Use
`--apply` to perform the migration. The script will back up original files
under `data/_backup_<timestamp>/` before overwriting.
"""
from pathlib import Path
import json
from datetime import datetime
import argparse
import shutil


def normalize_places_dict(data: dict) -> dict:
    out = {}
    for city, places in data.items():
        out_places = []
        for p in places:
            if not isinstance(p, dict):
                out_places.append(p)
                continue
            np = dict(p)
            # normalize lat
            lat = np.get('lat')
            if lat is not None:
                try:
                    np['lat'] = float(lat)
                except Exception:
                    np['lat'] = None
            # normalize lon (accept 'lon' or 'lng')
            lon = np.get('lon') if np.get('lon') is not None else np.get('lng')
            if lon is not None:
                try:
                    np['lon'] = float(lon)
                except Exception:
                    np['lon'] = None
            # remove legacy 'lng' key if present
            if 'lng' in np:
                np.pop('lng', None)
            out_places.append(np)
        out[city] = out_places
    return out


def migrate(data_dir: Path, apply: bool = False):
    files = list(data_dir.glob('*.json'))
    if not files:
        print('No JSON files found under', data_dir)
        return 1

    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    backup_dir = data_dir / f'_backup_{timestamp}'

    for f in files:
        name = f.name
        print('Processing', name)
        try:
            obj = json.loads(f.read_text(encoding='utf-8'))
        except Exception as e:
            print('  ERROR reading', name, e)
            continue

        normalized = normalize_places_dict(obj)

        # Compare and show a short summary of changes
        changed = False
        for city, places in obj.items():
            orig_list = places or []
            new_list = normalized.get(city, [])
            if len(orig_list) != len(new_list):
                changed = True
                break
            for o, n in zip(orig_list, new_list):
                if not isinstance(o, dict):
                    continue
                # if 'lng' existed previously and now removed or moved -> change
                if 'lng' in o and 'lng' not in n:
                    changed = True
                    break
                # if numeric casting changed type
                if isinstance(o.get('lat'), (int, float)) and not isinstance(n.get('lat'), (int, float)):
                    changed = True
                    break
        if not changed:
            print('  No structural changes detected')
        else:
            print('  Changes detected (lng->lon normalization and lat/lon casts)')

        if apply and changed:
            # create backup directory once
            if not backup_dir.exists():
                backup_dir.mkdir(parents=True, exist_ok=True)
            # copy original
            shutil.copy2(f, backup_dir / name)
            # write normalized back
            f.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding='utf-8')
            print('  Migrated and backed up to', str(backup_dir / name))

    if apply:
        print('\nMigration complete. Originals are in', str(backup_dir))
    else:
        print('\nDry-run complete. Use --apply to perform migration.')

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Perform migration (writes files).')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    data_dir = root / 'data'
    exit(migrate(data_dir, apply=args.apply) or 0)
