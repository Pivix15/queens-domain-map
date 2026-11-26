#!/usr/bin/env python3
"""Ajoute à chaque objet de data.json (champ 8) les clés qui permettent de le retrouver dans World0.sav :
   'G<hex>'  GUID de SavableActorStates (objet ramassé, coffre ouvert, mur cassé, boss vaincu…)
   'N<nom>'  entrée de NamedSaveData (défis réussis, pièces remises au scientifique)
   'O<nom>'  cristal de sauvegarde visité / téléporteur débloqué.
   Une seule clé de la liste suffit ; une clé 'A&B&C' demande A, B et C (porte qui s'ouvre avec plusieurs runes)."""
import os as _os
ROOT = _os.environ.get('QD_ROOT', _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))  # dossier du dépôt
import json, glob, os, struct, re, collections
MAPS = ROOT + '/all/RuinsLevel/Maps/'
def g2hex(g): return b''.join(struct.pack('<I', int(x, 16)) for x in g.split('-')).hex()
lv = {}
for f in glob.glob(MAPS + '*.json'):
    try: L = json.load(open(f, encoding='utf-8-sig'))
    except Exception: continue
    if not isinstance(L, list): continue
    b = os.path.basename(f)[:-5]
    for o in L:
        if (o.get('Outer') or {}).get('ObjectName', '').endswith("PersistentLevel'"): lv[(b, o['Name'])] = o
# objets rangés dans un coffre : le jeu enregistre l'ouverture du coffre, pas le ramassage de l'objet
inchest = collections.defaultdict(list)
for (b, n), o in lv.items():
    pr = o.get('Properties') or {}
    for ref in pr.get('ActorsToActivateOnOpen') or []:
        if isinstance(ref, dict) and 'PersistentLevel.' in ref.get('ObjectName', ''):
            item = ref['ObjectName'].split('PersistentLevel.')[-1].rstrip("'")
            inchest[(b, item)] += ['G' + g2hex(g) for g in pr.get('GUIDs', [])]
# passages « activables » : ouverts par un autre acteur (mur, levier, interrupteur…) dont l'état est enregistré à leur place
refby = collections.defaultdict(set)
def _refs(v, out):
    if isinstance(v, dict):
        on = v.get('ObjectName', '')
        if 'PersistentLevel.' in on:
            nm = on.split('PersistentLevel.')[-1].rstrip("'")
            if '.' not in nm: out.add(nm)
        for x in v.values(): _refs(x, out)
    elif isinstance(v, list):
        for x in v: _refs(x, out)
for (b, n), o in lv.items():
    pr = o.get('Properties') or {}
    for k, v in pr.items():
        if not re.search(r'Activat|Target|Door|Open|Trigger', k): continue
        out = set(); _refs(v, out)
        for t in out:
            if t != n: refby[(b, t)].add(n)
def trigger_keys(b, n, depth=0):
    keys = []
    for src in refby.get((b, n), ()):
        so = lv.get((b, src))
        if not so: continue
        sp = so.get('Properties') or {}
        keys += ['G' + g2hex(g) for g in sp.get('GUIDs', [])]
        if depth < 3: keys += trigger_keys(b, src, depth + 1)
    return keys
# portes qui demandent plusieurs activations (ActivationCountRequirement, ou le compte d'un ActivationTrigger) : toutes
# leurs clés à la fois. Seuls les liens d'activation comptent : la porte d'entrée d'un boss (FrontDoor) ne l'ouvre pas.
activators = collections.defaultdict(set)
for (b, n), o in lv.items():
    for k, v in (o.get('Properties') or {}).items():
        if k not in ('ActivatableTargets', 'ActivationTargets', 'ThingsToActivate'): continue
        out = set(); _refs(v, out)
        for t in out:
            if t != n: activators[(b, t)].add(n)
def needed(pr): return int(pr.get('ActivationCountRequirement') or pr.get('Required Activation Count') or 1)
def condition(b, n, depth=0):
    """Clés d'ouverture si plusieurs activations sont requises quelque part en amont, sinon None."""
    need = needed((lv.get((b, n)) or {}).get('Properties') or {})
    parts, several = [], need > 1
    for src in sorted(activators.get((b, n), ())):
        sp = (lv.get((b, src)) or {}).get('Properties') or {}
        sub = condition(b, src, depth + 1) if depth < 3 and needed(sp) > 1 else None
        if sub: parts += sub; several = True
        elif sp.get('GUIDs'): parts.append('G' + g2hex(sp['GUIDs'][0]))
    if not several: return None
    if need == 1: return parts
    if len(parts) != need: raise ValueError('%s/%s : %d déclencheurs pour %d activations' % (b, n, len(parts), need))
    return ['&'.join(parts)]
# objets uniques sans trace de ramassage : on regarde l'inventaire (clés 'I<objet>'). Seulement pour eux : beaucoup d'armes
# s'achètent aussi en boutique ou tombent d'ennemis, et l'inventaire cocherait alors l'exemplaire d'un monde jamais visité
ITEMS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'item_names.json')))
ITEM_FIX = {'Torch': ['Torch_Weapon_Item'],   # torche : sans GUID dans le niveau, ni en boutique
            'Knifebelt': ['KnifeBelt_KeyItem'], 'Knight Rusty Sword Pickup': ['!NRustySwordKnightGaveSword'],
            'Skullrod': ['SkullRod_Item'], 'Slashgun': ['SlashGun_ItemData'], 'Wing Crystal': []}
THROWN = re.compile(r'Dagger|Throwing|Spike Ball|Chakram|Needle', re.I)
_ST = {'pickup', 'item', 'data', 'bp', 'dans', 'un', 'coffre', 'the', 'of', '00', 'treasure', 'keyitem', 'key'}
def _toks(t):
    t = re.sub(r'([a-z])([A-Z])', r'\1 \2', t); t = re.sub(r'(\d+)', r' \1 ', t).lower().replace('_', ' ')
    return [x for x in re.split(r'\W+', t) if x and x not in _ST]
def item_keys(label):
    lab = re.sub(r'\s*\(dans un coffre\)', '', label)
    if lab in ITEM_FIX: return [('N' + k[2:]) if k.startswith('!N') else 'I' + k for k in ITEM_FIX[lab]]
    if THROWN.search(lab): return []
    lt = set(_toks(lab))
    c = sorted([i for i in ITEMS if lt and lt <= set(_toks(i)) and not i.endswith('_C') and 'Shop' not in i],
               key=lambda i: (len(set(_toks(i)) - lt), len(i)))
    return ['I' + c[0]] if c else []
d = json.load(open('data.json', encoding='utf-8'))
c = collections.Counter()
for z in d['zones']:
    for p in z['pois']:
        if p[0] == 'bestiaire': continue                 # clés posées par add_bestiary.py
        del p[7:]
        if p[0] == 'enemy': continue                      # les ennemis réapparaissent : rien à cocher
        keys = []
        if p[0] == 'sci':
            k = re.search(r'Unlock_(\d+)', p[6]).group(1)
            keys = ['NWeaponUpgradeUnlock_%02d' % int(k)]     # compte comme fait une fois remise au scientifique
        elif p[0] == 'challenge':
            keys = ['N' + p[4].lower()]
        else:
            level = z['levels'][p[5]]                     # deux niveaux d'une zone peuvent avoir un objet de même nom
            o = lv.get((level, p[6]))
            pr = (o or {}).get('Properties') or {}
            if p[0] in ('save', 'tp'):
                ld = pr.get('LocationData')
                if isinstance(ld, dict): keys = ['O' + ld['ObjectName'].split("'")[1]]
            else:
                # Les lézards sont faits après ramassage du sac, pas dès leur mort.
                prefix = 'T' if p[0] == 'lizard' else 'G'
                keys = [prefix + g2hex(g) for g in pr.get('GUIDs', [])]
                keys += inchest.get((level, p[6]), [])
                if p[0] == 'note' and pr.get('ImportKey'): keys.append('NReadNote_' + pr['ImportKey'])
                if p[0] == 'unique' and not keys: keys = item_keys(p[4])
                if p[0] in ('secret', 'mech') and (pr.get('ActivatableMode') or not keys):
                    opening = condition(level, p[6]) or trigger_keys(level, p[6])
                    keys += [k for k in dict.fromkeys(opening) if k not in keys]
        if keys: p.append(keys); c[p[0]] += 1
        else: c[p[0] + ' (sans clé)'] += 1
# téléporteurs sans LocationData : les utiliser n'écrit rien dans la sauvegarde, on les déduit d'indices qui, eux, y sont
P = {(z['id'], p[6]): p for z in d['zones'] for p in z['pois']}
def ks(zid, *names): return [k for n in names for k in (P[(zid, n)][7] if len(P.get((zid, n), [])) > 7 else [])]
# mini-téléporteur entre le Jardin de pierre et la zone finale : fait dès qu'on est allé dans la zone finale,
# ou qu'on a ouvert le mur secret qui cache le pad du Jardin
fs_tp = ks('zone-finale', 'PigeonFossil_Pickup', 'SecretWall4_2', 'SkullKeyRelic_BP_2') + ks('jardin-de-pierre', 'SecretWall3')
TP_FIX = {('marchand', 'ShopTeleportDestination_2'): ['OGR_ShopIsland_Save', 'NShopUnlockFinished'],   # arrivée sur l'île du marchand
          ('jardin-de-pierre', 'MiniTeleporter2'): fs_tp, ('zone-finale', 'MiniTeleporter_2'): fs_tp}
for (zid, n), keys in TP_FIX.items():
    p = P.get((zid, n))
    if p is not None and keys and len(p) == 7:
        p.append(list(dict.fromkeys(keys))); c[p[0]] += 1; c[p[0] + ' (sans clé)'] -= 1
# objets sans GUID : le jeu enregistre leur état sous un nom (NamedSaveData), dans le bestiaire, ou on le déduit
# - Executioner : sa mort est notée sous ExecutionerKilled et dans le bestiaire
# - œuf de Dekanima (Registre du péché) : l'activer lance l'évènement Dekanima (DekanimaEventState) et ouvre le monde
#   de Dekanima ; y avoir ramassé un objet prouve aussi qu'on l'a activé (GUID seulement : rien qui s'obtienne ailleurs)
dek = [k for k in ks('dekanima', 'SkullKeyRelic_BP23_2', 'SkullKeyRelic_BP2_5', 'OtherWorldSpear_Pickup_2', 'PlasmaRifle_Pickup_2') if k[0] == 'G']
KEY_FIX = {('ile', 'BigNut_SM_2', 'unique'): ['IBigNut'],   # noix : seul l'inventaire dit qu'on l'a prise (pas la mort du golem)
           ('tour-du-savoir', 'ExecutionerMiniboss_Spawner', 'boss'): ['NExecutionerKilled', 'KBoner_ExecutionerMiniboss_Data'],
           ('ros', 'Dekanima_Egg', 'unique'): ['NDekanimaEventState'] + dek,
           # zone finale : la porte aux crânes et le rituel sont notés quand on les termine
           ('zone-finale', 'SecretSkullDoor_NPC_BP_2', 'secret'): ['NSkullDoorQuestDone'],
           ('zone-finale', 'SecretSkullRitual_BP_2', 'secret'): ['NSkullRitualCompleted'],
           # Monde antique : la machine d'amélioration des armes, notée dès la première arme améliorée
           ('automne', 'LabMachine_2', 'upgrade'): ['NHasEverUpgradedWeapon', 'NTotalWeaponsUpgraded']}
for z in d['zones']:
    for p in z['pois']:
        keys = KEY_FIX.get((z['id'], p[6], p[0]))
        if keys and len(p) == 7:
            p.append(list(dict.fromkeys(keys))); c[p[0]] += 1; c[p[0] + ' (sans clé)'] -= 1
# PNJ, fantômes et souvenirs. Un PNJ mort laisse un fantôme : son GUID n'est enregistré qu'une fois le fantôme apparu.
# Le fantôme donne le souvenir de son groupe (inventaire 'I<souvenir>', même à 0 une fois déposé), que l'on dépose
# dans un réceptacle du HOD (GUID du réceptacle). Fantôme et souvenir : faits une fois le souvenir obtenu.
def ghost(level, name): return 'G' + g2hex(lv[(level, name)]['Properties']['GUID'])
def recept(name): return 'G' + g2hex(lv[('730_HOD', name)]['Properties']['GUIDs'][0])
MEMENTO = {'Knight': 'MementoRecepticle_2', 'Fish': 'MementoRecepticle2', 'Raider': 'MementoRecepticle3', 'Librarian': 'MementoRecepticle4',
           'Scientist': 'MementoRecepticle5', 'Chef': 'MementoRecepticle6', 'King': 'MementoRecepticle7', 'BMMC': 'MementoRecepticle8'}
MKEYS = {m: ['I%s_Memento_Item' % m, recept(r)] for m, r in MEMENTO.items()}
GHOSTS = {**{('100_GR', 'Ghost_' + k): 'Knight' for k in ('Arjaot', 'Budaen', 'Daon', 'Ekonta', 'Imba', 'Ippibi', 'Nu', 'Ujji')},
          ('100_GR', 'Raider_2_Ghost'): 'Raider', ('100_GR', 'Raider_4_Ghost'): 'Raider', ('200_AQ', 'Raider_1_Ghost'): 'Raider',
          ('200_AQ', 'Raider_Captain_Ghost'): 'Raider', ('210_AQ_underground', 'Raider_3_Ghost'): 'Raider',
          ('200_AQ', 'Fishwife_Ghost_BP_2'): 'Fish', ('300_LIB', 'Librarian_Ghost_NPC_BP_2'): 'Librarian',
          ('450_MAUS_darkmaze', 'BMMC_Ghost_NPC_BP_2'): 'BMMC', ('450_MAUS_darkmaze', 'Chef_Ghost_BP_2'): 'Chef',
          ('450_MAUS_darkmaze', 'ChefCrow_Ghost_BP_2'): 'Chef', ('450_MAUS_darkmaze', 'King_Ghost_NPC_BP_2'): 'King',
          ('500_AUT', 'Scientist_Ghost_NPC_BP_2'): 'Scientist'}
# PNJ vivant -> son fantôme (Erma n'a pas de GUID de fantôme : le jeu note qu'elle est vaincue et qu'on a parlé à son fantôme)
ALIVE = {('100_GR', 'Knight_SaddestPose2'): ghost('100_GR', 'Ghost_Arjaot'), ('100_GR', 'Knight_BP_Helmet3_0'): ghost('100_GR', 'Ghost_Ekonta'),
         ('100_GR', 'Knight_Ippibi'): ghost('100_GR', 'Ghost_Ippibi'), ('300_LIB', 'Knight_Budaen_NPC_BP_2'): ghost('100_GR', 'Ghost_Budaen'),
         ('420_MAUS_mid', 'Knight_Nu_NPC_BP_2'): ghost('100_GR', 'Ghost_Nu'), ('450_MAUS_darkmaze', 'Knight_Daon_NPC_BP_2'): ghost('100_GR', 'Ghost_Daon'),
         ('450_MAUS_darkmaze', 'Knight_Imba_NPC_BP_2'): ghost('100_GR', 'Ghost_Imba'),
         ('200_AQ', 'Raider_NPC_BP'): ghost('200_AQ', 'Raider_Captain_Ghost'), ('200_AQ', 'Fishwife_NPC_BP_2'): 'NEvilFishWifeDefeated',
         ('300_LIB', 'Librarian_NPC_BP'): ghost('300_LIB', 'Librarian_Ghost_NPC_BP_2'),
         ('450_MAUS_darkmaze', 'BMMC_NPC_BP'): ghost('450_MAUS_darkmaze', 'BMMC_Ghost_NPC_BP_2'),
         ('450_MAUS_darkmaze', 'King_NPC_BP_2'): ghost('450_MAUS_darkmaze', 'King_Ghost_NPC_BP_2'),
         ('450_MAUS_darkmaze', 'Chef_BP'): ghost('450_MAUS_darkmaze', 'Chef_Ghost_BP_2'), ('100_GR', 'ChefCrowEvent_NPC_2'): ghost('450_MAUS_darkmaze', 'Chef_Ghost_BP_2'),
         ('450_MAUS_darkmaze', 'ChefCrow_NPC'): ghost('450_MAUS_darkmaze', 'ChefCrow_Ghost_BP_2'),
         ('500_AUT', 'Scientist_NPC_BP'): ghost('500_AUT', 'Scientist_Ghost_NPC_BP_2'), ('500_AUT', 'Scientist_Kicked_NPC_2'): ghost('500_AUT', 'Scientist_Ghost_NPC_BP_2')}
for z in d['zones']:
    for p in z['pois']:
        at = (z['levels'][p[5]], p[6])
        if p[0] == 'memento': keys = MKEYS[GHOSTS[(at[0], p[6][:-len('_Souvenir')])]]
        elif p[0] == 'npc' and at in GHOSTS: keys = MKEYS[GHOSTS[at]]
        elif p[0] == 'npc' and at in ALIVE: keys = [ALIVE[at]] + (['NFishwifeGhostTalked'] if p[6] == 'Fishwife_NPC_BP_2' else [])
        else: continue
        del p[7:]; p.append(list(keys)); c[p[0]] += 1
json.dump(d, open('data.json', 'w', encoding='utf-8'), ensure_ascii=False)
for k, v in sorted(c.items()): print(k, v)
