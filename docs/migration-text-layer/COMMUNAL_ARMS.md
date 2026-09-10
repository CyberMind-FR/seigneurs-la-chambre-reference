# Armoiries communales — registre, mécanisme et procédure (2026-09-10)

## Statut

**MÉCANISME LIVRÉ, AUCUNE ARMOIRIE COMPOSÉE.** Demande du propriétaire : « lister les communes,
renseigner les armoiries de chaque commune quand elles sont présentes et récupérer les images,
compléter le guide, et mettre leurs armoiries en lieu et place de celles de La Chambre en haut à
gauche des pages des villes ». Depuis l'environnement de travail, toutes les sources héraldiques
sont bloquées par le proxy de sortie (fr.wikipedia.org, commons.wikimedia.org et son serveur de
fichiers upload.wikimedia.org, armorialdefrance.fr, heraldry-wiki.com, tchinggiz.org, wikidata,
dbpedia, sites des mairies). Seuls des extraits de moteur de recherche ont pu être lus : ils
identifient des fichiers et rapportent des blasonnements, mais ne sont pas des sources. Aucune
image n'a pu être récupérée. Le dépôt contient donc le registre, le mécanisme de remplacement
gardé par une vérification humaine, et la procédure pour finir depuis un poste non filtré.

## 1. Communes des sites

| Commune | INSEE (à vérifier) | Pages | Sites | Statut | Blasonnement rapporté (non vérifié) | Fichier Commons identifié |
|---|---|---|---|---|---|---|
| La Chambre | 73067 | 3, 4 | Couvent des Cordeliers, Maison de La Tour | `SOURCE_IDENTIFIED_UNVERIFIED` | — | `Blason ville fr La Chambre (Savoie).svg` |
| Sainte-Marie-de-Cuines | 73237 | 5, 6 | Château Joli, Tour de Burgin | `BLAZON_REPORTED_UNVERIFIED` | D'azur à la croix ancrée d'argent chargée en cœur d'une nef de sable et accompagnée au premier canton d'une fleur de lis d'or | — |
| Saint-Étienne-de-Cuines | 73232 | 7, 8, 9 | Tour de Châtel-André, Maison-Forte du Châtelet, Maison Forte de Gruyère | `SOURCE_IDENTIFIED_UNVERIFIED` | D'or au lion de sable ; à la bande de gueules chargée de trois étoiles d'argent brochante | `Blason ville fr Saint-Étienne-de-Cuines 73.svg` |
| Notre-Dame-du-Cruet | 73189 | 10, 11 | Château de Notre-Dame-du-Cruet, Tour de Notre-Dame-du-Cruet | `NO_ARMS_FOUND` | — | — |
| Saint-Rémy-de-Maurienne | 73265 | 12 | Maison Forte de La Landonnière | `SOURCE_IDENTIFIED_UNVERIFIED` | D'azur au sautoir d'or cantonné, en chef et en pointe, de deux étoiles et, aux flancs, de deux losanges, le tout du même | `Blason ville fr Saint-Rémy-de-Maurienne (73).svg` |

Notre-Dame-du-Cruet n'apparaît pas dans l'« Armorial des communes de la Savoie » d'après les
extraits : sans source produite par la mairie, les pages 10 et 11 gardent les armes de La Chambre.
Pages 03 et 04 (La Chambre) : pas de fragment d'armoiries remplaçable (page 04 sous verrou) ; les
armes seigneuriales du canon (page 02, source Amédée de FORAS) y restent. Pages 13 à 15 : armes
seigneuriales conservées (pages non communales), hors demande.

## 2. Mécanisme

- `assets/heraldry/communes/COMMUNES.yaml` : registre (statut, blasonnement et source, fichier
  SVG, SHA-256, licence, auteur, URL source, droits, vérificateur, date).
- `prototypes/page-NN/composition.yaml` (05 à 12) : `communal_arms: {commune, replaces_fragment:
  heraldry_captioned}` + bloc texte `cap_arms` avec `requires_communal_arms: true` (légende
  canonique « Armoiries de <Commune> » ajoutée en fin de `pages/NN.yaml`).
- `scripts/layered_compose.py` : si l'entrée est `VERIFIED` (tous champs présents, SHA exact, droits
  acceptés), le fragment raster des armes de La Chambre n'est pas extrait ; le SVG est rendu par
  cairosvg au gate trait (1200 ppi) dans la zone de l'écu (64 % supérieurs du fragment, 76 % de sa
  largeur, centré ; `shield_bbox_px` pour ajuster) et la légende est composée ; identité du SVG
  dans `fragments.lock.yaml`. Sinon : fragment raster conservé, légende non composée, information
  `communal_arms_pending`.
- `scripts/heraldry_check.py` (`make heraldry-check`, dans `make validate`) et
  `scripts/validate_built_layered.py` (blocs conditionnels ignorés tant que l'entrée n'est pas vérifiée).

Test du 2026-09-10 avec un écu de test hors dépôt marqué VERIFIED sur la page 05 : fragment
remplacé, rendu SVG à 1200 ppi, légende composée, gate inchangé ; état réel (non vérifié) :
fragment conservé, légende ignorée, validation verte.

## 3. Procédure pour finir (poste non filtré, quelques minutes par commune)

1. Ouvrir la page Commons du fichier (`image_candidates.commons_page`) ; relever licence, auteur
   (colonne « Auteur » du fichier), date ; télécharger le SVG (`download_url`) sous
   `assets/heraldry/communes/<slug>.svg`.
2. Confirmer le blasonnement sur fr.wikipedia « Armorial des communes de la Savoie » (ou
   armorialdefrance.fr) et le recopier dans `blazon`, avec `blazon_source`.
3. Renseigner `svg`, `sha256` (`sha256sum`), `licence`, `author`, `source_url`, `rights`
   (`CLEARED` pour une licence libre avec attribution respectée), `verified_by`, `verified_on` ;
   passer `status: VERIFIED`. Pour Sainte-Marie-de-Cuines, trouver d'abord le fichier (page
   Wikipédia de la commune, §Héraldique) ; pour Notre-Dame-du-Cruet, interroger la mairie.
4. `make heraldry-check && make layered-compose && make validate && make build-v3`.
5. Attribution : la licence des fichiers Commons (généralement CC BY-SA) impose de citer l'auteur ;
   prévoir la mention dans le livret (page 15, mentions légales) — décision éditoriale.

## 4. Points d'attention

- Les blasonnements rapportés ici viennent d'extraits de recherche et peuvent être inexacts ; ne
  jamais dessiner un SVG à partir d'eux sans confirmation sur la source.
- Un ajustement de la zone d'écu (`shield_bbox_px`) peut être nécessaire page par page après le
  premier rendu réel ; contrôler l'overlay `dist/layered/page-NN/*-overlay.png`.
- Les SVG Commons complexes (dégradés, filtres) sont rendus par cairosvg en PNG au gate trait ;
  le SVG lui-même reste la source (SHA dans le lock).
