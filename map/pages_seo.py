#!/usr/bin/env python3
"""Pages fixes pour les moteurs de recherche : une page par monde, en français (mondes/<id>.html) et en anglais
(worlds/<id>.html), avec la liste des objets à trouver. La carte elle-même est dessinée en JavaScript : ces pages
donnent à Google du texte à lire et des liens vers chaque monde. Écrit aussi sitemap.xml.

Usage : python pages_seo.py [dossier du site]        (par défaut map/site)
"""
import os, re, sys, json, html, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('QD_ROOT', os.path.dirname(HERE))
sys.path.insert(0, HERE)
import i18n_en as EN

SITE = 'https://queensdomain.leny15.me/'
SKIP = {'enemy', 'consum', 'npc', 'lizard', 'challenge'}
# ordre d'importance pour le résumé des pages (ce que cherchent les joueurs en premier)
WANTED = ['chest', 'unique', 'skull', 'secret', 'key', 'egg', 'ticket', 'upgrade', 'collect', 'memento', 'rune', 'sci', 'energy', 'save', 'tp',
          'boss', 'flesh', 'note', 'bestiaire']          # comme la liste « À propos » de la carte : on ne compte pas ce qui revient
# mondes qui se touchent et que le jeu charge ensemble (listes de chargement du jeu)
LINKS = {
    'ile': ['marchand', 'aquatique', 'tour-du-savoir', 'mausolee', 'sz-ruines'],
    'marchand': ['ile'],
    'aquatique': ['ile', 'sz-aquatique', 'marais'],
    'tour-du-savoir': ['ile', 'sz-tour'],
    'mausolee': ['ile', 'sz-mausolee', 'ros', 'sz-ruines', 'hod', 'automne'],
    'automne': ['chateau', 'mausolee', 'ros'],
    'chateau': ['automne'],
    'sz-ruines': ['ile', 'mausolee', 'prison', 'foret'],
    'sz-aquatique': ['aquatique', 'marais'],
    'sz-tour': ['tour-du-savoir', 'prison'],
    'hod': ['mausolee', 'prison'],
    'prison': ['sz-ruines', 'sz-tour', 'hod', 'foret'],
    'sz-mausolee': ['mausolee', 'ros', 'foret'],
    'ros': ['sz-mausolee', 'foret', 'mausolee', 'automne', 'dekanima'],
    'dekanima': ['ros'],
    'marais': ['jigeki', 'foret', 'jardin-de-pierre', 'sz-aquatique', 'aquatique'],
    'jigeki': ['marais', 'foret', 'jardin-de-pierre'],
    'foret': ['marais', 'jigeki', 'sz-mausolee', 'ros', 'jardin-de-pierre', 'prison', 'sz-ruines'],
    'jardin-de-pierre': ['foret', 'marais', 'jigeki', 'zone-finale'],
    'zone-finale': ['jardin-de-pierre'],
    'sipeha': [],
}
T = {
    'fr': dict(dir='mondes/', map='index.html', map3d='3d.html', home='Carte de Neasied', game="Queen's Domain",
               title="{z} : carte et objets — Queen's Domain",
               h1='{z}', kicker="Monde de Queen's Domain",
               desc="{z} dans Queen's Domain : {list}. Positions en 2D et 3D, suivi du 100 %.",
               intro="{z} est un des {nz} mondes de Queen's Domain couverts par la carte de Neasied. On y trouve {n} objets : {list}.",
               open2d='Ouvrir la carte 2D', open3d='Voir en 3D', save="Charge ta sauvegarde (World0.sav) sur la carte : ce que tu as déjà fait se coche tout seul et la progression liste ce qu'il te manque.",
               near='Mondes reliés', all='Tous les mondes', items='Objets à trouver', crumbs='Mondes', other='English',
               lang_label='Read in English', fan="Projet de fan, sans lien avec Freshly Baked Games ni Future Friends Games. Les noms des objets sont les noms internes du jeu, en anglais.",
               objs='objets', sep=' : ', zone_word='zones de fin', tag='Carte non officielle'),
    'en': dict(dir='worlds/', map='en.html', map3d='3d-en.html', home='Neasied Map', game="Queen's Domain",
               title="{z} map and items — Queen's Domain",
               h1='{z}', kicker="Queen's Domain world",
               desc="{z} in Queen's Domain: {list}. Positions in 2D and 3D, 100% tracking.",
               intro="{z} is one of the {nz} worlds of Queen's Domain covered by the Neasied Map. It holds {n} items: {list}.",
               open2d='Open the 2D map', open3d='View in 3D', save="Load your save (World0.sav) on the map: what you've already done is ticked automatically and the progress panel lists what you're missing.",
               near='Connected worlds', all='All worlds', items='Items to find', crumbs='Worlds', other='Français',
               lang_label='Lire en français', fan="Fan project, not affiliated with Freshly Baked Games or Future Friends Games. Item names are the game's internal names.",
               objs='items', sep=': ', zone_word='completion areas', tag='Unofficial map'),
}
CSS = """:root{color-scheme:dark;--sea:#0f131d;--chart:#161c2a;--chart-2:#1d2434;--line:#2b3347;--ink:#e9e5d8;--dim:#8d95a8;--gold:#e9b949;
--display:"Jacquard 12","Old English Text MT","Times New Roman",serif;--body:"Barlow Semi Condensed","Arial Narrow","Segoe UI",sans-serif}
*{box-sizing:border-box}html{background:var(--sea)}body{margin:0;background:var(--sea);color:var(--ink);font:400 17px/1.5 var(--body)}
a{color:var(--gold)}a:hover{color:#ffd77a}.wrap{max-width:900px;margin:0 auto;padding:24px 16px 48px}
header{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:14px}
.brand{font:400 38px/1 var(--display);color:var(--ink);text-decoration:none}.brand small{display:block;font:500 13px var(--body);color:var(--dim);margin-top:4px}
.lang{font-size:14px;color:var(--dim);text-decoration:none;border:1px solid var(--line);border-radius:3px;padding:4px 9px}.lang:hover{color:var(--ink)}
nav.crumbs{font-size:14px;color:var(--dim);margin:18px 0 6px}nav.crumbs a{color:var(--dim)}
.kicker{margin:0;color:var(--dim);font-size:14px;letter-spacing:.08em;text-transform:uppercase}h1{font:600 38px/1.1 var(--body);margin:4px 0 12px}
h2{font:600 24px/1.2 var(--body);margin:34px 0 10px;padding-top:14px;border-top:1px solid var(--line)}h3{font:600 18px var(--body);margin:20px 0 6px}
.lead{font-size:19px;color:var(--ink)}.muted{color:var(--dim)}
.cta{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}.cta a{flex:1 1 200px;text-align:center;padding:12px 16px;border-radius:6px;border:1px solid var(--line);
font:600 16px var(--body);text-decoration:none;color:var(--ink);background:var(--chart-2)}.cta a.main{background:var(--gold);border-color:var(--gold);color:#111}
.cta a:hover{border-color:var(--gold)}
ul.items{columns:2 260px;column-gap:28px;padding-left:20px;margin:6px 0}ul.items li{break-inside:avoid;margin:2px 0}
.n{color:var(--dim);font-variant-numeric:tabular-nums}ul.worlds{columns:3 200px;padding-left:20px}
.sw{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:8px;vertical-align:0}
footer{margin-top:42px;border-top:1px solid var(--line);padding-top:14px;font-size:14px;color:var(--dim)}
@media (max-width:560px){h1{font-size:30px}.brand{font-size:32px}}"""


def esc(s):
    return html.escape(str(s), quote=True)


def build(site):
    d = json.load(open(os.path.join(ROOT, 'map', 'data.json'), encoding='utf-8'))
    for a, bs in LINKS.items():
        for b in bs:
            assert a in LINKS[b], 'lien à sens unique : %s -> %s' % (a, b)
    today = datetime.date.today().isoformat()
    zids = [z['id'] for z in d['zones']]
    assert set(zids) == set(LINKS), 'mondes à relier : %s' % (set(zids) ^ set(LINKS))
    names = {'fr': {z['id']: z['label'] for z in d['zones']}, 'en': {z['id']: EN.ZONES.get(z['id'], z['label']) for z in d['zones']}}
    cats = {'fr': {c['id']: c['label'] for c in d['cats']}, 'en': {c['id']: EN.CATS.get(c['id'], c['label']) for c in d['cats']}}
    order = [c['id'] for c in d['cats']]
    urls = []
    for lang, t in T.items():
        os.makedirs(os.path.join(site, t['dir']), exist_ok=True)
        other = 'en' if lang == 'fr' else 'fr'
        for z in d['zones']:
            zid, zn = z['id'], names[lang][z['id']]
            pois = [p for p in z['pois'] if p[0] not in SKIP]
            by = collections.OrderedDict((c, []) for c in order)
            for p in pois:
                by[p[0]].append(p)
            by = collections.OrderedDict((c, v) for c, v in by.items() if v)
            counts = [(c, len(v)) for c, v in by.items()]
            short = lambda c: re.sub(r' \(.*\)', '', cats[lang][c]).lower()
            ranked = sorted(counts, key=lambda x: WANTED.index(x[0]))
            summary = ', '.join('%s (%d)' % (short(c), k) for c, k in ranked)
            parts = []
            for c, k in ranked:                     # description : ce qui tient en 155 caractères
                parts.append('%s (%d)' % (short(c), k))
                if len(t['desc'].format(z=zn, list=', '.join(parts))) > 155:
                    parts.pop()
                    break
            brief = ', '.join(parts)
            n = len(pois)
            url = SITE + t['dir'] + zid + '.html'
            alt = SITE + T[other]['dir'] + zid + '.html'
            fr_url, en_url = (url, alt) if lang == 'fr' else (alt, url)
            title = t['title'].format(z=zn, n=n)
            desc = t['desc'].format(z=zn, list=brief or '—')
            crumbs = [(t['home'], SITE + ('' if lang == 'fr' else 'en.html')), (t['crumbs'], SITE + t['dir'] + 'index.html'), (zn, url)]
            ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': i + 1, 'name': a, 'item': b} for i, (a, b) in enumerate(crumbs)]},
                {'@context': 'https://schema.org', '@type': 'WebPage', 'name': title, 'url': url, 'inLanguage': lang, 'description': desc,
                 'isPartOf': {'@type': 'WebSite', 'name': t['home'], 'url': SITE},
                 'about': {'@type': 'VideoGame', 'name': "Queen's Domain"}}]
            body = []
            body.append('<nav class="crumbs" aria-label="Fil d\'Ariane"><a href="../%s">%s</a> › <a href="index.html">%s</a> › %s</nav>' % (
                t['map'], esc(t['home']), esc(t['crumbs']), esc(zn)))
            body.append('<p class="kicker">%s</p><h1>%s</h1>' % (esc(t['kicker']), esc(t['h1'].format(z=zn))))
            body.append('<p class="lead">%s</p>' % esc(t['intro'].format(z=zn, nz=len(zids), n=n, list=summary or '—')))
            body.append('<div class="cta"><a class="main" href="../%s#%s">%s</a><a href="../%s#%s">%s</a></div>' % (
                t['map'], zid, esc(t['open2d']), t['map3d'], zid, esc(t['open3d'])))
            body.append('<p class="muted">%s</p>' % esc(t['save']))
            if by:
                body.append('<h2>%s</h2>' % esc(t['items']))
            for c, ps in by.items():
                color = next(x['color'] for x in d['cats'] if x['id'] == c)
                body.append('<h3><span class="sw" style="background:%s"></span>%s <span class="n">(%d)</span></h3>' % (esc(color), esc(cats[lang][c]), len(ps)))
                grouped = collections.Counter()
                for p in ps:
                    name = EN.poi_name(p[4]) if lang == 'en' else p[4]
                    if c == 'challenge':
                        name = EN.poi_name('Zone de défi') if lang == 'en' else 'Zone de défi'
                    grouped[name] += 1
                body.append('<ul class="items">' + ''.join('<li>%s%s</li>' % (esc(k), ' <span class="n">×%d</span>' % v if v > 1 else '')
                                                         for k, v in sorted(grouped.items(), key=lambda x: x[0].lower())) + '</ul>')
            near = [x for x in LINKS[zid]]
            if near:
                body.append('<h2>%s</h2><ul class="worlds">%s</ul>' % (esc(t['near']), ''.join(
                    '<li><a href="%s.html">%s</a></li>' % (x, esc(names[lang][x])) for x in near)))
            body.append('<h2>%s</h2><ul class="worlds">%s</ul>' % (esc(t['all']), ''.join(
                '<li>%s</li>' % (esc(names[lang][x]) if x == zid else '<a href="%s.html">%s</a>' % (x, esc(names[lang][x]))) for x in zids)))
            write(site, t, lang, zid, title, desc, url, fr_url, en_url, ld, body, T[other]['dir'] + zid + '.html')
            urls.append((url, fr_url, en_url, '0.7'))
        # sommaire des mondes
        url = SITE + t['dir'] + 'index.html'
        fr_url, en_url = SITE + 'mondes/index.html', SITE + 'worlds/index.html'
        title = ("Tous les mondes de Queen's Domain : cartes et objets" if lang == 'fr'
                 else "All Queen's Domain worlds: maps and items")
        desc = ("Les %d mondes de Queen's Domain et ce qu'il y a à trouver dans chacun : coffres, armes, crânes argentés, murs secrets et plus encore." % len(zids)
                if lang == 'fr' else "All %d worlds of Queen's Domain and what to find in each: chests, weapons, silver skulls, secret walls and more." % len(zids))
        rows = ''.join('<li><a href="%s.html">%s</a> <span class="n">— %d %s</span></li>' % (
            z['id'], esc(names[lang][z['id']]), sum(1 for p in z['pois'] if p[0] not in SKIP), t['objs']) for z in d['zones'])
        body = ['<nav class="crumbs"><a href="../%s">%s</a> › %s</nav>' % (t['map'], esc(t['home']), esc(t['crumbs'])),
                '<p class="kicker">%s</p><h1>%s</h1>' % (esc(t['tag']), esc(title.split(' :')[0].split(':')[0])),
                '<p class="lead">%s</p>' % esc(desc),
                '<div class="cta"><a class="main" href="../%s">%s</a><a href="../%s">%s</a></div>' % (t['map'], esc(t['open2d']), t['map3d'], esc(t['open3d'])),
                '<ul class="worlds">%s</ul>' % rows]
        ld = [{'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': t['home'], 'item': SITE + ('' if lang == 'fr' else 'en.html')},
            {'@type': 'ListItem', 'position': 2, 'name': t['crumbs'], 'item': url}]}]
        write(site, t, lang, 'index', title, desc, url, fr_url, en_url, ld, body, T[other]['dir'] + 'index.html')
        urls.append((url, fr_url, en_url, '0.8'))
    pages = [(SITE, SITE, SITE + 'en.html', '1.0'), (SITE + 'en.html', SITE, SITE + 'en.html', '1.0'),
             (SITE + '3d.html', SITE + '3d.html', SITE + '3d-en.html', '0.8'), (SITE + '3d-en.html', SITE + '3d.html', SITE + '3d-en.html', '0.8')]
    seen = set()
    rows = []
    for u, fr, en, pr in pages + urls:
        if u in seen:
            continue
        seen.add(u)
        rows.append('  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority>\n'
                    '    <xhtml:link rel="alternate" hreflang="fr" href="%s"/>\n'
                    '    <xhtml:link rel="alternate" hreflang="en" href="%s"/>\n'
                    '    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/></url>' % (u, today, pr, fr, en, en))
    open(os.path.join(site, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + '\n'.join(rows) + '\n</urlset>\n')
    print(len(urls), 'pages, sitemap de', len(rows), 'adresses')


def write(site, t, lang, name, title, desc, url, fr_url, en_url, ld, body, other_rel):
    other_lang = 'en' if lang == 'fr' else 'fr'
    page = '''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="fr" href="{fr}">
<link rel="alternate" hreflang="en" href="{en}">
<link rel="alternate" hreflang="x-default" href="{en}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#0f131d">
<link rel="icon" href="../favicon.ico" sizes="any">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{home}">
<meta property="og:locale" content="{locale}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}{img}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jacquard+12&family=Barlow+Semi+Condensed:wght@400;500;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="wrap">
<header><a class="brand" href="../{map}">Neasied<small>{tag} · Queen's Domain</small></a>
<a class="lang" href="../{other_rel}" hreflang="{other_lang}" lang="{other_lang}" title="{lang_label}">{other}</a></header>
<main>
{body}
</main>
<footer><p>{fan}</p></footer>
</div>
</body>
</html>
'''.format(lang=lang, title=esc(title), desc=esc(desc), url=url, fr=fr_url, en=en_url, home=esc(t['home']),
           locale='fr_FR' if lang == 'fr' else 'en_GB', site=SITE, img='og-image.jpg' if lang == 'fr' else 'og-image-en.jpg',
           ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), css=CSS, map=t['map'], tag=esc(t['tag']),
           other_rel=other_rel, other_lang=other_lang, lang_label=esc(t['lang_label']), other=esc(t['other']),
           body='\n'.join(body), fan=esc(t['fan']))
    open(os.path.join(site, t['dir'], name + '.html'), 'w', encoding='utf-8', newline='\n').write(page)


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'map', 'site'))
