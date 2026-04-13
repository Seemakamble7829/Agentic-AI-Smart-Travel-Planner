"""Smoke test: build a plan for a known destination and verify routing info.

Run with:
    py -3 scripts\smoke_test.py
"""
import json
import sys
from pathlib import Path

# add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import Controller
from data_loader import DataLoader


def run():
    dest = 'Goa'
    days = 2
    budget = 5000
    interests = 'beach food'

    print('Loading sample data keys:', list(DataLoader.load_destinations().keys()))
    ctrl = Controller()
    plan = ctrl.build_plan(dest, days, budget, interests)

    print('\nPlan keys:', list(plan.keys()))
    itin = plan.get('itinerary', [])
    print(f'Itinerary items: {len(itin)}')
    missing_coords = [i for i in itin if i.get('lat') is None or i.get('lon') is None]
    if missing_coords:
        print('Warning: some itinerary items missing coords:', missing_coords)
    else:
        print('All itinerary items have lat/lon.')

    route = plan.get('route', {})
    print('Route keys:', list(route.keys()))
    legs_by_day = route.get('legs_by_day', {})
    for day, legs in legs_by_day.items():
        print(f' Day {day}: {len(legs)} legs')
        if legs:
            sample = legs[0]
            print('  Sample leg:', sample)

    # Save plan to logs for manual inspection
    logs = ROOT / 'logs'
    logs.mkdir(exist_ok=True)
    out_file = logs / f'smoke_plan_{dest}.json'
    out_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\nSaved plan to', out_file)


if __name__ == '__main__':
    run()
