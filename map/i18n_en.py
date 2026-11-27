"""Version anglaise du site : traductions appliquées aux pages françaises au moment de la construction.
Les pages anglaises sont en.html (carte 2D) et 3d-en.html (vue 3D)."""
import re

SITE = 'https://queensdomain.leny15.me/'

ZONES = {
    'ile': 'Isle of Neasied', 'marchand': "Merchant's Isle", 'aquatique': 'Obmuer Temple',
    'tour-du-savoir': 'Tower of Knowledge', 'mausolee': 'Deimpo Mausoleum', 'automne': 'Ancient World',
    'chateau': 'Siraatsu Castle', 'sz-ruines': 'Secret zone: Ruins', 'sz-aquatique': 'Secret zone: Obmuer',
    'sz-tour': 'Secret zone: Tower', 'hod': 'Primeval Shrine', 'prison': 'Underground Prison', 'sz-mausolee': 'Deep Mausoleum',
    'dekanima': 'Overgrown Record of Sin', 'ros': 'Record of Sin', 'marais': 'Rotting Cavern', 'jigeki': 'Jigeki Temple',
    'foret': 'Verdant Hollow', 'jardin-de-pierre': 'Stone Garden', 'zone-finale': 'Final Zone', 'sipeha': "Sipeha's World",
}
CATS = {
    'save': 'Save crystals', 'tp': 'Teleporters', 'chest': 'Chests', 'unique': 'Unique weapons & items',
    'key': 'Keys & books', 'sci': "Scientist's parts", 'upgrade': 'Upgrades', 'ticket': 'Meal tickets', 'skull': 'Silver skulls (Skull Key Relic)',
    'collect': 'Collectibles', 'egg': 'Eggs', 'memento': 'Mementos', 'energy': 'Energy cells', 'bestiaire': 'Bestiary (1 per creature)', 'npc': 'NPCs',
    'note': 'Notes & tablets', 'rune': 'God runes', 'flesh': 'Flesh walls', 'secret': 'Secret walls & doors', 'boss': 'Bosses & unique enemies',
    'challenge': 'Reach challenges', 'lizard': 'Star lizards', 'consum': 'Consumables & coins', 'enemy': 'Enemies',
}
POI = [  # noms d'objets : seules quelques étiquettes ajoutées par le site sont en français
    (r' \(dans un coffre\)', ' (in a chest)'), (r'^Coffre : ', 'Chest: '), (r'^Coffre$', 'Chest'), (r' \(piège\)', ' (trap)'),
    (r' \(fantôme\)', ' (ghost)'), (r'^Mur secret', 'Secret wall'), (r'^Mur de chair', 'Flesh wall'),
    (r'^Crâne argenté \(Skull Key Relic\)', 'Silver skull (Skull Key Relic)'),
    (r'^Porte secrète \(runes des 4 dieux\)', 'Secret door (4 god runes)'),
    (r'^Porte secrète \(6 runes de Puwema\)', 'Secret door (6 Puwema runes)'),
    (r'^Porte secrète \(3 cibles\)', 'Secret door (3 targets)'),
    (r'^Porte secrète \(2 gargouilles\)', 'Secret door (2 gargoyles)'),
    (r"^Noix mystique de l'arbre blanc", 'Mystical Nut of the White Tree'),
    (r'^Ticket resto', 'Meal ticket'), (r'^Souvenir \(', 'Memento ('),
    (r'^Rune de Jigeki', 'Jigeki rune'), (r'^Rune de Puwema', 'Puwema rune'),
    (r'^Rune de Sipeha', 'Sipeha rune'), (r'^Rune de Wodaso', 'Wodaso rune'),
    (r'^Pièce du scientifique n°', "Scientist's part #"), (r'^Zone de défi', 'Challenge zone'), (r'^Point à atteindre \(défi\)$', 'Point to reach (challenge)'),
    # lézards stellaires : nom du bestiaire en français, nom interne en anglais
    (r'^Lézard\ stellaire \(Potion Lizer 01\)$', 'Potion Lizer 01'),
    (r'^Lézard\ stellaire\ aquatique \(Potion Lizer 02\)$', 'Potion Lizer 02'),
    (r'^Lézard\ stellaire\ érudit \(Potion Lizer 03\)$', 'Potion Lizer 03'),
    (r'^Lézard\ stellaire\ des\ tombes \(Potion Lizer 04\)$', 'Potion Lizer 04'),
    (r'^Lézard\ stellaire\ des\ profondeurs \(Potion Lizer 05\)$', 'Potion Lizer 05'),
    (r'^Lézard\ stellaire\ majestueux \(Potion Lizer 06\)$', 'Potion Lizer 06'),
    (r'^Lézard\ stellaire\ reluisant \(Potion Lizer 07\)$', 'Potion Lizer 07'),
]
def poi_name(s):
    for a, b in POI: s = re.sub(a, b, s)
    return s

DESC_FR = "Carte interactive de Queen's Domain en 2D et 3D : tous les mondes, coffres, crânes argentés, armes, murs secrets et bestiaire. Charge ta sauvegarde pour voir ce qu'il te manque pour le 100 %."
DESC_EN = "Interactive map of Queen's Domain in 2D and 3D: every world, chest, silver skull, weapon, secret wall and bestiary entry. Load your save to see what you're missing for 100%."
DESC3_FR = "Explore Queen's Domain en 3D : chaque monde avec ses étages, ses coffres, crânes argentés et secrets. Clique sur un objet pour le voir de dessus."
DESC3_EN = "Explore Queen's Domain in 3D: every world with its floors, chests, silver skulls and secrets. Click an item to see it from above."

COMMON = [
    ("'Défis atteints : '", "'Challenges reached: '"), ("' · manquent : '", "' · missing: '"),
    ('<span>Dernière sauvegarde : </span>', '<span>Last save: </span>'), ("' · dernière sauvegarde'", "' · last save'"),
    ('<html lang="fr">', '<html lang="en">'),
    ('<meta property="og:locale" content="fr_FR">', '<meta property="og:locale" content="en_GB">'),
    ('<meta property="og:site_name" content="Carte de Neasied">', '<meta property="og:site_name" content="Neasied Map">'),
    ('content="Vue 3D de l\'Île de Neasied avec les objets à trouver"', 'content="3D view of the Isle of Neasied with the items to find"'),
    (SITE + 'og-image.jpg', SITE + 'og-image-en.jpg'),
    ('class="lang" href="en.html" hreflang="en" lang="en"', 'class="lang" href="index.html" hreflang="fr" lang="fr"'),
    ('class="lang" href="3d-en.html" hreflang="en" lang="en"', 'class="lang" href="3d.html" hreflang="fr" lang="fr"'),
    ('>English</a>', '>Français</a>'),
    ("Carte interactive non officielle de Queen's Domain", "Unofficial interactive map of Queen's Domain"),
    ('>Objets de ce monde ›<', '>Items in this world ›<'), ("'mondes/' + ", "'worlds/' + "), ('href="mondes/ile.html"', 'href="worlds/ile.html"'),
    ('>Vue 2D<', '>2D view<'), ('>Vue 3D<', '>3D view<'),
    ('<b>Progression du jeu</b>', '<b>Game progress</b>'),
    ('<label for="zone">Zone</label>', '<label for="zone">World</label>'),
    ('Rechercher un objet', 'Search for an item'),
    ('Skull Rod, coffre, Budaen…', 'Skull Rod, chest, Budaen…'),
    ('<span>Ma sauvegarde</span>', '<span>My save file</span>'),
    ("Charge ton fichier de sauvegarde (<b>World0.sav</b>, <b>World1.sav</b>…) : ce que tu as déjà fait est grisé sur la carte. Le fichier est lu dans ton navigateur et n'est envoyé nulle part.",
     "Load your save file (<b>World0.sav</b>, <b>World1.sav</b>…): everything you've already done is greyed out on the map. The file is read in your browser and never uploaded."),
    ("Charge ton fichier de sauvegarde (<b>World0.sav</b>, <b>World1.sav</b>…) : ce que tu as déjà fait est grisé. Le fichier est lu dans ton navigateur et n'est envoyé nulle part.",
     "Load your save file (<b>World0.sav</b>, <b>World1.sav</b>…): everything you've already done is greyed out. The file is read in your browser and never uploaded."),
    ('>Charger ma sauvegarde<', '>Load my save<'), ("'Charger ma sauvegarde'", "'Load my save'"),
    ('>Oublier<', '>Forget<'), ('Masquer ce qui est déjà fait', 'Hide what is already done'),
    ('Où trouver ce fichier ?', 'Where is this file?'), ('Sur PC, en général : ', 'On PC, usually: '),
    (" puis le dossier à ton numéro Steam. Colle ce chemin dans la barre d'adresse de l'Explorateur Windows. Le fichier s'appelle ",
     " then the folder named after your Steam ID. Paste this path into the address bar of Windows File Explorer. The file is called "),
    ("… selon l'emplacement de ta partie (le premier monde est ", "… depending on your save slot (the first world is "),
    ('). Tu peux aussi glisser le fichier directement sur la carte.', '). You can also drag the file straight onto the map.'),
    ('). Tu peux aussi glisser le fichier directement sur la vue 3D.', '). You can also drag the file straight onto the 3D view.'),
    ('<span>Catégories</span>', '<span>Categories</span>'),
    ('Un problème ou une idée&nbsp;? Contacte <b>Leny15</b> sur Discord&nbsp;:', 'A problem or an idea? Contact <b>Leny15</b> on Discord:'),
    ('>Rejoindre le Discord<', '>Join the Discord<'),
    ('>Tout</button>', '>All</button>'),
    ('<dt>Catégorie</dt>', '<dt>Category</dt>'), ('<dt>Hauteur</dt>', '<dt>Height</dt>'),
    ('aria-label="Zone précédente"', 'aria-label="Previous world"'), ('aria-label="Zone suivante"', 'aria-label="Next world"'),
    ('aria-label="Fermer"', 'aria-label="Close"'),
    ("Dépose ta sauvegarde (World0.sav, World1.sav…) ici", "Drop your save (World0.sav, World1.sav…) here"),
    ("'Lecture impossible : '", "'Could not read the file: '"),
    ("Ce fichier n\\'est pas une sauvegarde Unreal (GVAS).", "This file is not an Unreal save file (GVAS)."),
    ("Pas de liste d\\'objets dans ce fichier : est-ce bien World0.sav ?", "No item list in this file: is it really a World0.sav?"),
    ("'Recharger'", "'Reload'"),
    ("' objets faits sur '", "' items done out of '"),
    ("d.toLocaleDateString('fr-FR') + ' à ' + d.toLocaleTimeString('fr-FR'", "d.toLocaleDateString('en-GB') + ' at ' + d.toLocaleTimeString('en-GB'"),
]

PAGE_2D = [
    ("<title>Carte interactive Queen's Domain — 2D, 3D et 100 % | Carte de Neasied</title>",
     "<title>Queen's Domain interactive map — 2D, 3D & 100% tracker | Neasied Map</title>"),
    ("content=\"Carte interactive Queen's Domain — 2D, 3D et 100 % | Carte de Neasied\"",
     "content=\"Queen's Domain interactive map — 2D, 3D & 100% tracker | Neasied Map\""),
    (DESC_FR, DESC_EN),
    ('<link rel="canonical" href="' + SITE + '">', '<link rel="canonical" href="' + SITE + 'en.html">'),
    ('<meta property="og:url" content="' + SITE + '">', '<meta property="og:url" content="' + SITE + 'en.html">'),
    ('"name": "Carte de Neasied — Queen\'s Domain"', '"name": "Neasied Map — Queen\'s Domain"'),
    ('"name": "Carte de Neasied \\u2014 Queen\'s Domain"', '"name": "Neasied Map \\u2014 Queen\'s Domain"'),
    ('"operatingSystem": "Navigateur web"', '"operatingSystem": "Web browser"'), ('"inLanguage": "fr"', '"inLanguage": "en"'),
    ('"url": "' + SITE + '"', '"url": "' + SITE + 'en.html"'),
    ('<a id="to3d" href="3d.html">', '<a id="to3d" href="3d-en.html">'), ("location.href = '3d.html#'", "location.href = '3d-en.html#'"),
    ('>Tout afficher<', '>Show all<'), ('>Tout masquer<', '>Hide all<'),
    ('Réglage fin de la hauteur', 'Fine height adjustment'), ('<span>Bas</span>', '<span>Low</span>'), ('<span>Haut</span>', '<span>High</span>'),
    ('Afficher toutes les hauteurs', 'Show all heights'),
    ('Positions tirées des fichiers du jeu. Les noms des objets sont les noms internes du jeu, en anglais.', "Positions taken from the game files. Item names are the game's internal names."),
    ('Les objets cochés « trouvé » et la sauvegarde chargée sont gardés dans ce navigateur uniquement.', 'Items ticked as “found” and the loaded save are kept in this browser only.'),
    ('Projet de fan, sans lien avec Freshly Baked Games ni Future Friends Games.', 'Fan project, not affiliated with Freshly Baked Games or Future Friends Games.'),
    ('À propos de cette carte', 'About this map'),
    ('<a href="mondes/index.html">Tous les mondes et leurs objets ›</a>', '<a href="worlds/index.html">All worlds and their items ›</a>'),
    ("<h2>Carte interactive de Queen's Domain</h2>", "<h2>Queen's Domain interactive map</h2>"),
    ("<p>Cette carte non officielle couvre tout <b>Queen's Domain</b> : chaque monde de l'île de Neasied en plan 2D par étage et en vue 3D, avec la position de chaque objet à trouver.</p>",
     "<p>This unofficial map covers all of <b>Queen's Domain</b>: every world of the Isle of Neasied as a floor-by-floor 2D map and in 3D, with the location of every item to find.</p>"),
    ("<p>Pour viser le <b>100 %</b>, charge ta sauvegarde (<code>World0.sav</code>) : ce que tu as déjà fait est coché tout seul, et le panneau « Progression du jeu » liste ce qu'il te manque dans chaque monde.</p>",
     "<p>Going for <b>100%</b>? Load your save (<code>World0.sav</code>): what you've already done is ticked automatically, and the “Game progress” panel lists what you're still missing in each world.</p>"),
    ('<h3>Mondes</h3>', '<h3>Worlds</h3>'), ('<h3>Objets répertoriés</h3>', '<h3>Items listed</h3>'),
    ('<span class="ttl">Étage</span>', '<span class="ttl">Floor</span>'),
    ("title=\"Vue d'ensemble : les salles intérieures sont cachées\"", 'title="Overview: interior rooms are hidden"'),
    ('<h2>Progression</h2>', '<h2>Progress</h2>'), ('Montrer aussi ce qui est déjà fait', 'Also show what is already done'),
    ('Compter les ennemis, PNJ et consommables', 'Count enemies, NPCs and consumables'),
    ('aria-label="Progression de tous les mondes"', 'aria-label="Progress across all worlds"'),
    ('<dt>Niveau</dt>', '<dt>Level</dt>'), ('<dt>Nom interne</dt>', '<dt>Internal name</dt>'),
    ('<span id="cFoundTxt">Trouvé</span>', '<span id="cFoundTxt">Found</span>'),
    ('aria-label="Hauteur minimale"', 'aria-label="Minimum height"'), ('aria-label="Hauteur maximale"', 'aria-label="Maximum height"'),
    ('aria-label="Carte de la zone"', 'aria-label="World map"'), ("aria-label=\"Choix de l'étage\"", 'aria-label="Floor selection"'),
    ('aria-label="Dézoomer"', 'aria-label="Zoom out"'), ('aria-label="Zoomer"', 'aria-label="Zoom in"'),
    ('aria-label="Recentrer la zone"', 'aria-label="Recenter"'), ('title="Recentrer"', 'title="Recenter"'),
    ("' affichés'", "' shown'"), ("' · chargée le '", "' · loaded on '"),
    ("' · plan détaillé'", "' · detailed map'"), ("' · relevé approximatif'", "' · approximate survey'"),
    ("'</b> faits sur tout le jeu · '", "'</b> done across the whole game · '"),
    ('Voir ›', 'View ›'),
    ('Charge ton World0.sav (panneau de gauche) pour comparer avec ta partie. Sans sauvegarde, seuls les objets cochés « Trouvé » comptent.',
     'Load your World0.sav (left panel) to compare with your game. Without a save, only items ticked “Found” count.'),
    ('Clique sur un objet pour aller le voir sur la carte.', 'Click an item to see it on the map.'),
    ("'Pas fait (corrigé à la main)'", "'Not done (fixed by hand)'"),
    ("Fait (d\\'après ta sauvegarde)", 'Done (from your save)'), ("'Trouvé'", "'Found'"),
    ("'Hauteur choisie à la main · '", "'Custom height · '"),
    ('Sauvegarde lue par une ancienne version du site : clique sur « Recharger » et choisis à nouveau ta sauvegarde pour corriger les objets mal reconnus.',
     'Save read by an older version of the site: click “Reload” and choose your save again to fix wrongly detected items.'),
    ('Tout est fait dans ce monde.', 'Everything is done in this world.'),
    ("Vue d\\'ensemble · les salles intérieures sont cachées", 'Overview · interior rooms are hidden'),
    ("'Étage ' + f.idx", "'Floor ' + f.idx"), ("'Étage ' + fl[S.floor].idx + ' sur '", "'Floor ' + fl[S.floor].idx + ' of '"),
    ("(c > 1 ? ' objets' : ' objet')", "(c > 1 ? ' items' : ' item')"),
    ("+ ' à ' +", "+ ' to ' +"),
]

PAGE_3D = [
    ("'Réessayer'", "'Retry'"), ("' Mo'", "' MB'"),
    ('"name":"Carte de Neasied — Queen\'s Domain en 3D"', '"name":"Neasied Map — Queen\'s Domain in 3D"'),
    ('"url":"https://queensdomain.leny15.me/3d.html"', '"url":"https://queensdomain.leny15.me/3d-en.html"'),
    ('"description":"' + DESC3_FR + '"', '"description":"' + DESC3_EN + '"'),
    ('"operatingSystem":"Navigateur web","inLanguage":"fr"', '"operatingSystem":"Web browser","inLanguage":"en"'),
    ("<title>Queen's Domain en 3D — carte interactive de tous les mondes | Carte de Neasied</title>",
     "<title>Queen's Domain in 3D — interactive map of every world | Neasied Map</title>"),
    ("content=\"Queen's Domain en 3D — carte interactive de tous les mondes | Carte de Neasied\"",
     "content=\"Queen's Domain in 3D — interactive map of every world | Neasied Map\""),
    (DESC3_FR, DESC3_EN),
    ('<link rel="canonical" href="' + SITE + '3d.html">', '<link rel="canonical" href="' + SITE + '3d-en.html">'),
    ('<meta property="og:url" content="' + SITE + '3d.html">', '<meta property="og:url" content="' + SITE + '3d-en.html">'),
    ('<a id="to2d" href="index.html">', '<a id="to2d" href="en.html">'),
    # panneau Progression (mêmes textes que la carte 2D)
    ('<h2>Progression</h2>', '<h2>Progress</h2>'), ('Montrer aussi ce qui est déjà fait', 'Also show what is already done'),
    ('Compter les ennemis, PNJ et consommables', 'Count enemies, NPCs and consumables'),
    ('aria-label="Progression de tous les mondes"', 'aria-label="Progress across all worlds"'),
    ("'</b> faits sur tout le jeu · '", "'</b> done across the whole game · '"), ('Voir ›', 'View ›'),
    ('Charge ton World0.sav (panneau de gauche) pour comparer avec ta partie. Sans sauvegarde, seuls les objets cochés « Trouvé » comptent.',
     'Load your World0.sav (left panel) to compare with your game. Without a save, only items ticked “Found” count.'),
    ('Clique sur un objet pour aller le voir sur la carte.', 'Click an item to see it on the map.'),
    ('Tout est fait dans ce monde.', 'Everything is done in this world.'), ("'Chargement de tous les mondes…'", "'Loading every world…'"),
    ('>Chargement…<', '>Loading…<'), ('<span>Couper à</span>', '<span>Cut at</span>'), ('aria-label="Hauteur de coupe"', 'aria-label="Cut height"'),
    ('>Recentrer<', '>Recenter<'), ('>Vue de dessus<', '>Top view<'),
    ('>Tout afficher<', '>Show all<'), ('>Tout masquer<', '>Hide all<'),
    ('>Cacher les mondes voisins<', '>Hide neighbouring worlds<'), ('>Afficher les mondes voisins<', '>Show neighbouring worlds<'),
    ("' — clique pour y aller'", "' — click to go there'"),
    ('aria-label="Boussole"', 'aria-label="Compass"'), ('data-dir="o">O<', 'data-dir="o">W<'),
    ("<b>Souris</b> : clic gauche tourner · clic droit déplacer · molette zoom · clic sur un point : vue de dessus sur l'objet",
     '<b>Mouse</b>: left click rotate · right click pan · wheel zoom · click a marker: top view of the item'),
    ('<b>Clavier</b> : ZQSD (WASD en QWERTY) ou flèches se déplacer · A / E tourner (Q / E en QWERTY) · R / F zoom · Maj accélère · Espace vue de dessus',
     '<b>Keyboard</b>: WASD (ZQSD on AZERTY) or arrows move · Q / E rotate (A / E on AZERTY) · R / F zoom · Shift faster · Space top view'),
    ("' dans cette zone · '", "' in this world · '"),
    (" · Page préc. / suiv. changer d'étage · Échap tout voir", ' · Page Up / Down change floor · Esc show all'),
    ('<div class="t">Étage</div>', '<div class="t">Floor</div>'),
    ("'chargée le '", "'loaded on '"), (": 'chargée';", ": 'loaded';"), ("'Sauvegarde ' + when", "'Save ' + when"),
    ("'Chargement du modèle… '", "'Loading model… '"), ("'Chargement du modèle…'", "'Loading model…'"),
    ("'Préparation de la scène…'", "'Preparing the scene…'"), ("Le modèle n\\'a pas pu être chargé.", 'The model could not be loaded.'),
    ("' · déjà fait'", "' · already done'"),
    ('<span id="cft">Trouvé</span>', '<span id="cft">Found</span>'),
    ("'Pas fait (corrigé à la main)' : 'Fait (d\\'après ta sauvegarde)') : 'Trouvé'", "'Not done (fixed by hand)' : 'Done (from your save)') : 'Found'"), ("' · étage '", "' · floor '"), ("'Aucun objet trouvé.'", "'No item found.'"),
    ("'étage ' + (f + 1)", "'floor ' + (f + 1)"),
    ("'Étage ' + (i + 1) + ' · ' + Math.round(f.z0) + ' à '", "'Floor ' + (i + 1) + ' · ' + Math.round(f.z0) + ' to '"),
    ("' objets'", "' items'"), ("' — 3D · Carte de Neasied'", "' — 3D · Neasied Map'"), ("'aucune'", "'none'"),
    ('Sauvegarde lue par une ancienne version du site : recharge ta sauvegarde pour corriger les objets mal reconnus.',
     'Save read by an older version of the site: load your save again to fix wrongly detected items.'),
]

def translate(text, pairs, where):
    missing = []
    for fr, en in pairs:
        if fr not in text: missing.append(fr[:70])
        text = text.replace(fr, en)
    if missing: print('[%s] non trouvés :' % where, *missing, sep='\n  ')
    return text

def page_2d(html): return translate(translate(html, COMMON, 'commun (2D)'), PAGE_2D, '2D')
def page_3d(html): return translate(translate(html, COMMON, 'commun (3D)'), PAGE_3D, '3D')

# appliqué par la vue 3D anglaise à zone.json après chargement
L10N_JS = '''const L10N = %s;
zone.zone = L10N.zones[zid] || zone.zone;
zone.cats.forEach(c => { if (L10N.cats[c.id]) c.label = L10N.cats[c.id]; });
zone.pois.forEach(p => { L10N.poi.forEach(([a, b]) => { p.n = p.n.replace(new RegExp(a), b); }); });'''
