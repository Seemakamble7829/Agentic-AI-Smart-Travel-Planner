"""Generate a folium map for a destination using DataLoader and save as HTML.

This script will try to import folium; if not available it will exit with a message.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data_loader import DataLoader


def main():
    try:
        import folium
    except Exception:
        print('folium not installed; cannot generate map.')
        return 2

    dest = 'Goa'
    data = DataLoader.load_destinations() or {}
    places = data.get(dest, [])
    markers = []
    for p in places:
        if isinstance(p, dict):
            lat = p.get('lat')
            lon = p.get('lon')
            if lat is not None and lon is not None:
                markers.append((p.get('name'), lat, lon, p.get('description', '')))

    if not markers:
        print('No geocoded markers found for', dest)
        return 1

    center = [markers[0][1], markers[0][2]]
    m = folium.Map(location=center, zoom_start=12)
    for name, lat, lon, desc in markers:
        folium.Marker(location=[lat, lon], popup=f"<b>{name}</b><br>{desc}").add_to(m)

    out = ROOT / 'logs'
    out.mkdir(exist_ok=True)
    fname = out / f'map_smoke_{dest}.html'
    m.save(str(fname))
    print('Saved map to', fname)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
