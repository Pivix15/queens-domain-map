#!/usr/bin/env python3
"""Assemble site/index.html : template.html + data.json + le plan de chaque zone (site/tiles/<zone>/meta.json)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MIN_GAP = 900.0   # deux sols à moins de 9 m l'un de l'autre = paliers d'un même étage

def merge_floors(floors, gap=MIN_GAP):
    out = []
    for f in floors:
        lv = f['lvl'] if f['lvl'] is not None else f['z0']
        if out:
            p = out[-1]
            plv = p['lvl'] if p['lvl'] is not None else p['z0']
            if lv - plv < gap:
                p['z1'] = f['z1']
                if p['lvl'] is None:
                    p['lvl'] = f['lvl']
                continue
        out.append(dict(f))
    return out

def main():
    d = json.load(open('data.json', encoding='utf-8'))
    for z in d['zones']:
        p = 'site/tiles/%s/meta.json' % z['id']
        if not os.path.exists(p):
            continue
        meta = json.load(open(p))
        n = len(meta['floors'])
        meta['floors'] = merge_floors(meta['floors'], meta.get('mergeGap', MIN_GAP))
        meta['dir'] = 'tiles/%s/' % z['id']
        z['plan'] = meta
        print('%-18s %d étages (%d avant fusion), %d images' % (z['id'], len(meta['floors']), n, len(meta['bands'])))
    t = open('template.html', encoding='utf-8').read()
    for lang in ('fr', 'en'):
        build(d, t, lang)

def build(d, t, lang):
    import copy, html as _h
    from collections import Counter
    import i18n_en as EN
    if lang == 'en':
        d = copy.deepcopy(d)
        for c in d['cats']: c['label'] = EN.CATS.get(c['id'], c['label'])
        for z in d['zones']:
            z['label'] = EN.ZONES.get(z['id'], z['label'])
            for p in z['pois']: p[4] = EN.poi_name(p[4])
        t = EN.page_2d(t)
    cnt = Counter(p[0] for z in d['zones'] for p in z['pois'])
    skip = {'enemy', 'consum', 'npc', 'lizard'}
    word = 'items' if lang == 'en' else 'objets'
    pages = 'worlds/' if lang == 'en' else 'mondes/'   # une page fixe par monde (pages_seo.py)
    zl = ''.join('<li><a href="%s%s.html">%s</a> (%d %s)</li>' % (pages, z['id'], _h.escape(z['label']), sum(1 for p in z['pois'] if p[0] not in skip), word) for z in d['zones'])
    cl = ''.join('<li>%s%s%d</li>' % (_h.escape(c['label']), ': ' if lang == 'en' else ' : ', cnt[c['id']]) for c in d['cats'] if c['id'] not in skip and cnt[c['id']])
    t = t.replace('__SEO_ZONES__', zl).replace('__SEO_CATS__', cl)
    s = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    html = t.replace('__DATA__', s)
    out = 'site/index.html' if lang == 'fr' else 'site/en.html'
    open(out, 'w', encoding='utf-8').write(html)
    if lang == 'fr': open('_check.js', 'w').write(html[html.rindex('<script>') + 8:html.rindex('</script>')])
    else: open('_check_en.js', 'w').write(html[html.rindex('<script>') + 8:html.rindex('</script>')])
    print('%s %.2f Mo' % (out, len(html) / 1e6))

if __name__ == '__main__':
    main()
