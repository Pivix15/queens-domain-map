#!/usr/bin/env python3
"""Range les modèles 3D dans le site : site/tiles3d/<zone>/ (morceaux base64 pour l'artefact)
et ovh/tiles3d/<zone>/ (scene.glb direct pour un hébergement classique). Ajoute étages et identifiants des objets."""
import os as _os
ROOT = _os.environ.get('QD_ROOT', _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # dossier du dépôt
import json, os, glob, base64, shutil
SRC = ROOT + '/map3d/z'; SITE = ROOT + '/map/site/tiles3d'; OVH = ROOT + '/map3d/ovh/tiles3d'
data = json.load(open(ROOT + '/map/data.json', encoding='utf-8'))
ZD = {z['id']: z for z in data['zones']}
CH = 7_000_000
order = [z['id'] for z in data['zones'] if os.path.exists(os.path.join(SRC, z['id'], 'scene.glb'))]
for zid in order:
    d = os.path.join(SRC, zid); z = json.load(open(os.path.join(d, 'zone.json'), encoding='utf-8'))
    dz = ZD[zid]
    # identifiants (pour les cases « trouvé ») et clés de sauvegarde à jour
    pts = [p for p in dz['pois']]
    if len(pts) == len(z['pois']):
        for q, p in zip(z['pois'], pts):
            q['id'] = dz['levels'][p[5]] + '/' + p[6] + ('#lizard-bag' if p[0] == 'lizard' else ''); q['k'] = p[7] if len(p) > 7 else []; q['c'] = p[0]; q['n'] = p[4]
    else:   # data.json a changé depuis la génération : on reprend les objets depuis data.json
        z['pois'] = [{'c': p[0], 'x': p[1] / 100, 'y': p[3] / 100, 'z': p[2] / 100, 'n': p[4], 'k': p[7] if len(p) > 7 else [],
                      'id': dz['levels'][p[5]] + '/' + p[6] + ('#lizard-bag' if p[0] == 'lizard' else '')} for p in pts]
    z['cats'] = data['cats']; z['zone'] = dz['label']
    mp = ROOT + '/map/site/tiles/%s/meta.json' % zid
    if os.path.exists(mp):
        m = json.load(open(mp)); z['floors'] = [{'z0': f['z0'] / 100, 'z1': f['z1'] / 100} for f in m['floors']]
    glb = open(os.path.join(d, 'scene.glb'), 'rb').read()
    for out, packed in ((os.path.join(SITE, zid), True), (os.path.join(OVH, zid), False)):
        if os.path.exists(out): shutil.rmtree(out)
        os.makedirs(out)
        zz = dict(z)
        if packed:
            b = base64.b64encode(glb).decode(); parts = [b[i:i + CH] for i in range(0, len(b), CH)]
            for i, p in enumerate(parts): json.dump({'glb': p}, open(os.path.join(out, 'scene%d.json' % i), 'w'))
            zz['parts'] = len(parts)
        else:
            open(os.path.join(out, 'scene.glb'), 'wb').write(glb); zz.pop('parts', None)
        json.dump(zz, open(os.path.join(out, 'zone.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(zid, round(len(glb) / 1e6, 1), 'Mo')
json.dump([{'id': i, 'label': ZD[i]['label']} for i in order], open(ROOT + '/map3d/zlist.json', 'w', encoding='utf-8'), ensure_ascii=False)
