# Carte de Neasied — Queen's Domain

Carte interactive non officielle de **Queen's Domain** : tous les mondes en 2D et en 3D, plus de 1 000 objets à trouver, et le suivi de ta progression à partir de ta sauvegarde.

**Site : https://queensdomain.leny15.me**

*[English version below](#english)*

---

## Fonctionnalités

- **Tous les mondes du jeu**, chacun avec un plan 2D texturé par étage et une vue 3D.
- **Les objets** rangés par catégorie :
  - coffres, armes et objets uniques, clés et livres ;
  - améliorations, tickets resto, crânes argentés, collectibles, pièces du scientifique, cellules d'énergie ;
  - murs et portes secrets, boss, bestiaire, notes, runes des dieux, zones de défi, téléporteurs.
- **Lecture de la sauvegarde** (`World0.sav`, `World1.sav`…) : ce que tu as déjà fait est coché automatiquement. Le fichier est lu dans le navigateur et n'est envoyé nulle part.
- **Progression du jeu** : la liste de tous les mondes avec ce qui est fait et ce qui manque. Un clic sur un objet manquant ouvre la carte sur lui. Les notes, les runes et les 16 murs secrets hors succès (`Don'tCountForAchievement` dans le jeu) ne comptent pas dans le 100 %. Un défi compte une fois, même avec plusieurs zones de fin.
- **Vue 3D** (three.js) :
  - étages et plan de coupe ;
  - mondes voisins à leur vraie place (14 mondes, là où ça reste lisible ; pas sur téléphone) : un clic y vole et l'ouvre ;
  - clic sur un objet pour une vue de dessus ;
  - déplacement au clavier (ZQSD ou WASD, A/E ou Q/E, R/F).
- **Lézards et sacs de butin** : les 36 lézards ont une catégorie dédiée, activée par défaut. Avec une sauvegarde, seuls restent les lézards encore vivants et ceux dont le sac est encore au sol, en 2D comme en 3D.
- Recherche, filtres par catégorie et option « Masquer ce qui est déjà fait ». Les réglages sont gardés d'une zone à l'autre.
- **En français et en anglais** : `index.html` / `3d.html` et `en.html` / `3d-en.html`.

## Où trouver sa sauvegarde

Sur PC : `%LOCALAPPDATA%\QueensDomain\Saved\SaveGames\`, puis le dossier à ton numéro Steam. Le fichier s'appelle `World0.sav`, `World1.sav`… selon l'emplacement de ta partie.

## Contenu du dépôt

Le dépôt contient **uniquement le code** : il ne contient **aucun fichier du jeu** (textures, modèles, niveaux). Pour régénérer la carte, il faut exporter soi-même les fichiers de sa copie du jeu avec [FModel](https://fmodel.app).

```
map/
  template.html        carte 2D (HTML + CSS + JS, sans framework)
  data.json            objets de toutes les zones : catégorie, position, nom, clés de sauvegarde
  extract-map-data.js  lit les niveaux exportés par FModel → input/queens-domain-actors.json
  build_data.py        classe les objets par zone et par catégorie → data.json
  add_save_keys.py     ajoute à chaque objet les clés qui le retrouvent dans la sauvegarde
  add_bestiary.py      catégories Bestiaire et Cellules d'énergie
  pack.py              range les images des plans dans map/site/tiles/
  assemble.py          template.html + data.json + plans → map/site/index.html et en.html
  i18n_en.py           traductions anglaises (interface, mondes, catégories)
render/
  render_zone.py       rendu logiciel (numpy) du plan texturé d'une zone, étage par étage
  build3d.py           modèle 3D d'une zone au format glTF (.glb), écrit à la main
  glb.py, place.py     lecture des maillages exportés et placement des acteurs
map3d/
  viewer3d_site.html   vue 3D (three.js)
  place3d.py           range les modèles 3D et ajoute objets et étages → map/site/tiles3d/
  make_neighbours.py   modèles allégés des mondes, montrés autour du monde affiché → voisin.glb
  make_3d_html.py      génère map/site/3d.html et 3d-en.html
input/                 fichiers à fournir soi-même (voir input/README.md)
deploy/                .htaccess (https, cache), favicon.svg, favicon.ico, apple-touch-icon*.png, robots.txt, sitemap.xml
```

### Comment la sauvegarde est lue

`World0.sav` est un fichier GVAS (Unreal Engine 4). Le site en lit cinq listes :

| Liste dans la sauvegarde | Clé dans `data.json` | Sert à |
|---|---|---|
| `SavableActorStates` | `G<guid>` | objets ramassés, coffres ouverts, murs ouverts, boss vaincus |
| `NamedSaveData` | `N<nom>` | notes lues, quêtes, défis |
| `InventoryContents`, `Equipment`, `WeaponLevels`… | `I<objet>` | objets possédés, même obtenus autrement |
| `SavableActorStates` + `ItemDrops` | `T<guid>` | sacs de lézards ramassés : ennemi vaincu et aucun sac restant à son point d’apparition |
| `KilledEnemyCounts` | `K<fiche>` | bestiaire |
| `UnlockedTeleporters`, `SavePointsVisited` | `O<nom>` | téléporteurs et cristaux de sauvegarde |

Un objet est « fait » si **une** de ses clés est présente dans la sauvegarde. Une clé composée `A&B&C` n'est présente que si **toutes** ses parties le sont : une porte qui demande 4 runes n'est pas cochée avec une seule.

## Régénérer la carte

Prérequis : Node.js, Python 3.10+ et `pip install -r requirements.txt`.

1. **Exporter les fichiers du jeu.** Avec FModel (UE 4.27), exporte en JSON les niveaux de `QueensDomain/Content/RuinsLevel/Maps/` dans `all/RuinsLevel/Maps/`, puis les maillages et textures dans `all/` et `meshes/`.
2. **Extraire les objets** :
   ```bash
   node map/extract-map-data.js all/RuinsLevel/Maps input/queens-domain-actors.json
   ```
3. **Construire les données** :
   ```bash
   python3 map/build_data.py
   python3 map/add_save_keys.py
   python3 map/add_bestiary.py
   ```
4. **Rendre les plans 2D**, une zone à la fois (c'est gourmand en mémoire), puis assembler la carte :
   ```bash
   python3 render/render_zone.py ile
   python3 map/pack.py ile
   cd map && python3 assemble.py
   ```
5. **Rendre la vue 3D** :
   ```bash
   python3 render/build3d.py ile map3d/z/ile
   python3 map3d/place3d.py
   python3 map3d/make_neighbours.py   # après place3d.py, qui vide les dossiers des mondes
   python3 map3d/make_3d_html.py
   ```

Les identifiants des zones (`ile`, `marchand`, `aquatique`, `tour-du-savoir`, `mausolee`, `automne`, `chateau`…) sont définis dans `render/render_zone.py`. Par défaut, les scripts travaillent dans le dossier du dépôt ; la variable d'environnement `QD_ROOT` permet d'en choisir un autre.

## Mise en ligne

Envoie le contenu de `map/site/` (`index.html`, `3d.html`, `tiles/`, `tiles3d/`, `og-image.jpg`) et celui de `deploy/` à la racine de ton hébergement. Pense à adapter l'adresse du site dans `robots.txt`, `sitemap.xml` et les balises `og:` de `map/template.html` et `map3d/viewer3d_site.html`. Le site est entièrement statique : pas de serveur, pas de base de données.

## Support

Un problème, un objet mal placé, une idée ? Ouvre une *issue*, ou contacte **Leny15** sur le Discord : https://discord.gg/n5nVh8qafs

## Licence

Le code est sous licence [MIT](LICENSE).

Queen's Domain, ses noms, cartes, textures et modèles appartiennent à **Freshly Baked Games** et **Future Friends Games**. Ce projet est fait par un fan, sans lien avec eux, et ce dépôt ne contient aucun fichier du jeu.

---

<a id="english"></a>

## English

Unofficial interactive map of **Queen's Domain**: every world in 2D and 3D, more than 1,000 items to find, and progress tracking from your save file.

**Website: https://queensdomain.leny15.me/en.html** (also in French)

### Features

- **Every world**, each with a textured 2D floor-by-floor map and a 3D view.
- **Items by category**: chests, unique weapons and items, keys, upgrades, meal tickets, silver skulls, collectibles, the scientist's parts, energy cells, secret walls and doors, bosses, bestiary, notes, god runes, challenge zones, teleporters.
- **Save file reading** (`World0.sav`, `World1.sav`…): everything you've already done is checked automatically. The file is read in your browser and never uploaded.
- **Game progress panel**: every world with what's done and what's missing. Click a missing item to jump to it on the map. Notes, runes and the 16 secret walls the game's achievement ignores don't count toward 100%. A challenge counts once, even with several completion areas.
- **3D view** (three.js): floors, cutting plane, neighbouring worlds at their real position (14 worlds, where it stays readable; not on phones) (click one to fly there), click an item for a top-down view, keyboard movement.

Save location on PC: `%LOCALAPPDATA%\QueensDomain\Saved\SaveGames\<your Steam ID>\`.

### Repository

This repository contains **code only**, **no game files**. To rebuild the map, export the files from your own copy of the game with [FModel](https://fmodel.app), then follow the steps in [Régénérer la carte](#régénérer-la-carte). The commands are the same in any language.

**Lizards & loot bags:** all 36 loot-dropping lizards have a dedicated category, enabled by default. Loading a save keeps only living lizards and those with a bag still on the ground, in both 2D and 3D. Each spawn has its own save GUID; killing one variant does not complete every lizard of that kind.

The shared `map/lizard_bags.js` reader matches persisted bags to the nearest spawn of the same variant within 15 metres. If a bag cannot be matched, it conservatively keeps that variant’s candidates visible. Generated pages embed this helper through `assemble.py` and `make_3d_html.py`. Rebuild 3D zone data with `place3d.py` as well, to refresh marker IDs and save keys.

Run `node --test tests/lizard_bags.test.js` for regression tests. Set `QD_TEST_SAVE` to a local save path to also check the supplied save with both readers and the 2D filter. Save files are not included in the repository.

The save reader (`readSave` in `map/template.html`) parses the GVAS format (Unreal Engine 4) and matches five lists against each item's keys in `data.json`: `G` (actor states), `N` (named data), `I` (inventory), `K` (bestiary), `O` (teleporters and save points).

### Support

Open an issue, or contact **Leny15** on Discord: https://discord.gg/n5nVh8qafs

### License

Code under the [MIT](LICENSE) license. Queen's Domain and all its content belong to Freshly Baked Games and Future Friends Games. This is a fan project, not affiliated with them, and this repository contains no game assets.
