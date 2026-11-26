#!/usr/bin/env python3
"""Génère site/3d.html (français) et site/3d-en.html (anglais) : le gabarit viewer3d_site.html + la liste des zones (zlist.json)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('QD_ROOT', os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'map'))
import i18n_en as EN
from lizard_bags import inline_lizard_bags
tpl = open(os.path.join(HERE, 'viewer3d_site.html'), encoding='utf-8').read()
tpl = inline_lizard_bags(tpl, json.load(open(os.path.join(ROOT, 'map', 'data.json'), encoding='utf-8')))
zl = json.load(open(os.path.join(HERE, 'zlist.json'), encoding='utf-8'))
site = os.path.join(ROOT, 'map', 'site'); os.makedirs(site, exist_ok=True)
fr = tpl.replace('__ZONES__', json.dumps(zl, ensure_ascii=False))
open(os.path.join(site, '3d.html'), 'w', encoding='utf-8').write(fr)
zl_en = [dict(z, label=EN.ZONES.get(z['id'], z['label'])) for z in zl]
en = EN.page_3d(tpl).replace('__ZONES__', json.dumps(zl_en, ensure_ascii=False))
data = {'zones': EN.ZONES, 'cats': EN.CATS, 'poi': [[a, b] for a, b in EN.POI]}
en = en.replace('/*__L10N_APPLY__*/', EN.L10N_JS % json.dumps(data, ensure_ascii=False))
open(os.path.join(site, '3d-en.html'), 'w', encoding='utf-8').write(en)
print('3d.html, 3d-en.html')
