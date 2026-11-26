"""Embed shared loot-bag tracking and lizard spawn positions in the static viewers."""
import json
import re
from pathlib import Path


def inline_lizard_bags(template, data):
    points = []
    for zone in data['zones']:
        for poi in zone['pois']:
            if poi[0] != 'lizard':
                continue
            variant = int(re.search(r'Potion Lizer (\d+)', poi[4]).group(1)) - 1
            keys = [key for key in poi[7] if key.startswith('T')] if len(poi) > 7 else []
            if not keys:
                raise ValueError(f"Missing lizard save GUID: {zone['id']}/{poi[6]}")
            points.append([variant, *poi[1:4], keys])
    script = Path(__file__).with_suffix('.js').read_text(encoding='utf-8')
    script = script.replace('/*__LIZARD_POINTS__*/[]', json.dumps(points, separators=(',', ':')))
    return template.replace('/*__LIZARD_BAGS__*/', script)
