#!/usr/bin/env python3
"""
Populate default duration_minutes, rating, and description into data/spots_*.json files.
Run from repository root: python scripts/persist_spot_defaults.py
"""
import json
from pathlib import Path

DATA_DIR = Path('data')
FILES = [p for p in DATA_DIR.glob('spots_*.json')]

default_durations = {
    'outdoor': 60,
    'indoor': 90,
    'temple': 45,
    'shopping': 60,
    'museum': 90,
    'food': 60,
}

default_ratings = {
    'outdoor': 4.2,
    'indoor': 4.3,
    'temple': 4.1,
    'shopping': 3.9,
    'museum': 4.5,
    'food': 4.0,
}

explanation_templates = {
    'outdoor': 'Popular outdoor attraction with scenic views and good photo opportunities.',
    'indoor': 'Well-curated indoor spot; expect exhibits or sheltered activities.',
    'temple': 'Historic or religious site, usually quiet and culturally significant.',
    'shopping': 'Shopping area with stores and local vendors; good for browsing.',
    'museum': 'High-quality museum with notable collections; allow more time.',
    'food': 'Recommended local food spot; good for meals and tasting local cuisine.',
}

updated = []
for fp in FILES:
    try:
        data = json.loads(fp.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Failed to read {fp}: {e}")
        continue

    changed = False
    for item in data:
        cat = item.get('category', '')
        name = item.get('name', 'Attraction')
        if 'duration_minutes' not in item or item.get('duration_minutes') is None:
            item['duration_minutes'] = default_durations.get(cat, 60)
            changed = True
        if 'rating' not in item or item.get('rating') is None:
            item['rating'] = default_ratings.get(cat, 4.0)
            changed = True
        # always (re)write a more detailed, name-specific description
        base_expl = explanation_templates.get(cat, 'Popular attraction with local appeal.')
        first_words = ' '.join(name.split()[:2])
        new_desc = (
            f"Typical visit ~{item.get('duration_minutes', default_durations.get(cat,60))} minutes. "
            "Rating reflects typical visitor satisfaction and category averages. "
            "Consider booking tickets in advance for busy seasons."
        )
        if item.get('description') != new_desc:
            item['description'] = new_desc
            changed = True

    if changed:
        fp.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding='utf-8')
        updated.append(fp.name)
        print(f"Updated {fp}")
    else:
        print(f"No changes for {fp}")

print('\nSummary:')
if updated:
    for u in updated:
        print(' -', u)
else:
    print('No files modified.')
