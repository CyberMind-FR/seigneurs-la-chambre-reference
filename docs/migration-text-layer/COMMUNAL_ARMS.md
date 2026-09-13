# Armoiries communales — registre, mécanisme et procédure (2026-09-10)

## Statut

**2026-09-11 — SVG OFFICIELS AU DÉPÔT, MÉCANISME PROUVÉ SUR LES DESSINS RÉELS, COMPOSITION EN
ATTENTE DU CRÉDIT CC BY-SA (décision éditoriale).** Le propriétaire a récupéré depuis un poste
non filtré les trois blasons disponibles sur Wikimedia Commons et documenté leur provenance
(`assets/svg/blasons/REGISTRY.yaml`, PR #22, commit `bd5b2b9`) : La Chambre, Saint-Étienne-de-Cuines,
Saint-Rémy-de-Maurienne. Sainte-Marie-de-Cuines et Notre-Dame-du-Cruet : aucun blason connu
(mairies à interroger). Les trois dessins sont sous **CC BY-SA** : leur reproduction impose de
créditer auteur, source et licence, et la mention « © 2025 — Tous droits réservés » de la page 15
ne peut pas les couvrir (`REGISTRY.yaml` → `droits.tension_a_resoudre`). Le registre technique
(`assets/heraldry/communes/COMMUNES.yaml`) les porte au statut `VERIFIED_CREDITS_PENDING` :
provenance complète et contrôlée, composition refusée tant que la ligne de crédit n'est pas inscrite
au canon (§5). Ce dépôt ne modifie pas le canon.

Historique 2026-09-10 : demande du propriétaire (« lister les communes, renseigner les armoiries de
chaque commune quand elles sont présentes et récupérer les images, compléter le guide, et mettre
leurs armoiries en lieu et place de celles de La Chambre en haut à gauche des pages des villes ») ;
depuis l'environnement de travail, toutes les sources héraldiques étaient bloquées par le proxy de
sortie ; registre, mécanisme gardé par vérification humaine et procédure livrés sans image.

## 1. Communes des sites

| Commune | INSEE | Pages | Sites | Statut (COMMUNES.yaml) | Blasonnement (source REGISTRY.yaml) | Fichier | Licence / auteur |
|---|---|---|---|---|---|---|---|
| La Chambre | 73067 | 3, 4 | Couvent des Cordeliers, Maison de La Tour | `VERIFIED_CREDITS_PENDING` (pas de fragment remplaçable) | D'azur, semé de fleurs de lis d'or, à la bande de gueules brochant sur le tout | `assets/svg/blasons/73067-la-chambre.svg` | CC BY-SA 3.0 — Spedona / Commons |
| Sainte-Marie-de-Cuines | 73255 | 5, 6 | Château Joli, Tour de Burgin | `BLAZON_REPORTED_UNVERIFIED` | aucun blason connu (propriétaire) ; blasonnement d'extrait non vérifié conservé à titre de piste | — | — |
| Saint-Étienne-de-Cuines | 73231 | 7, 8, 9 | Tour de Châtel-André, Maison-Forte du Châtelet, Maison Forte de Gruyère | `VERIFIED_CREDITS_PENDING` | D'or au lion de sable ; à la bande de gueules chargée de trois étoiles d'argent brochante | `assets/svg/blasons/73231-saint-etienne-de-cuines.svg` | CC BY-SA 4.0 — Chatsam / Commons |
| Notre-Dame-du-Cruet | 73189 | 10, 11 | Château de Notre-Dame-du-Cruet, Tour de Notre-Dame-du-Cruet | `NO_ARMS_FOUND` | aucun blason connu (propriétaire) | — | — |
| Saint-Rémy-de-Maurienne | 73278 | 12 | Maison Forte de La Landonnière | `VERIFIED_CREDITS_PENDING` | D'azur au sautoir cantonné, en chef et en pointe, de deux étoiles et, aux flancs, de deux losanges, le tout d'or | `assets/svg/blasons/73278-saint-remy-de-maurienne.svg` | CC BY-SA 3.0 — Odejea / Commons |

Statut officiel des trois blasons : « à déterminer » (mairies), cf. `REGISTRY.yaml`.
Notre-Dame-du-Cruet : aucune source ; les pages 10 et 11 gardent les armes de La Chambre.
Pages 03 et 04 (La Chambre) : pas de fragment d'armoiries remplaçable (page 04 sous verrou) ; les
armes seigneuriales du canon (page 02, source Amédée de FORAS) y restent. Pages 13 à 15 : armes
seigneuriales conservées (pages non communales), hors demande.

## 2. Mécanisme

- `assets/svg/blasons/REGISTRY.yaml` (propriétaire) : registre documentaire — blasonnement et
  références, fichier Commons, auteur, licence, URL de licence, ligne de crédit, SHA-256.
- `assets/heraldry/communes/COMMUNES.yaml` (technique, lu par le compositeur) : statut, provenance
  reprise du registre du propriétaire (`owner_registry`), droits, `credit_line`, vérificateur, date.
  `make heraldry-check` vérifie que chemin et SHA-256 concordent entre les deux registres (clé INSEE).
- Statuts : `VERIFIED` (composé) ; `VERIFIED_CREDITS_PENDING` (provenance complète et contrôlée —
  fichier, SHA, licence, auteur, source, blasonnement sourcé, vérificateur, rendu cairosvg — mais
  ligne de crédit non inscrite au canon : non composé) ; `SOURCE_IDENTIFIED_UNVERIFIED`,
  `BLAZON_REPORTED_UNVERIFIED`, `NO_ARMS_FOUND`, `UNKNOWN` (non composés).
- Droits : `CLEARED`, `PROJECT_INTERNAL`, `ASSOCIATION_PROVIDED` (sans condition) ;
  `ATTRIBUTION_SHAREALIKE` (CC BY-SA) : composition autorisée **seulement** si `credit_line` figure
  mot pour mot dans le `canonical_text` d'une page (`scripts/heraldry_check.py:credit_inscribed_in_canon`,
  même contrôle dans `scripts/layered_compose.py`, qui refuse de composer sinon).
- `prototypes/page-NN/composition.yaml` (05 à 12) : `communal_arms: {commune, replaces_fragment:
  heraldry_captioned}` + bloc texte `cap_arms` avec `requires_communal_arms: true` (légende
  canonique « Armoiries de <Commune> » en fin de `pages/NN.yaml`).
- `scripts/layered_compose.py` : entrée `VERIFIED` et crédit inscrit → le fragment raster des armes
  de La Chambre n'est pas extrait ; le SVG est rendu par cairosvg au gate trait (1200 ppi) dans la
  zone de l'écu (64 % supérieurs du fragment, 76 % de sa largeur, centré ; `shield_bbox_px` pour
  ajuster) et la légende est composée ; identité du SVG, ligne de crédit et pages qui la portent dans
  le rapport et `fragments.lock.yaml`. Sinon : fragment raster conservé, légende non composée,
  information `communal_arms_pending_credits` ou `communal_arms_pending`.
- `scripts/heraldry_check.py` (`make heraldry-check`, dans `make validate`) et
  `scripts/validate_built_layered.py` (blocs conditionnels ignorés tant que l'entrée n'est pas `VERIFIED`).

## 3. Procédure pour finir

1. **Décider le crédit CC BY-SA** (propriétaire) : inscrire au canon les trois lignes de crédit et
   amender la mention globale de la page 15 (proposition §5), ou choisir une autre voie (colophon,
   redessin maison sous licence libre de contrainte — option écartée par le propriétaire pour l'instant).
2. Passer les trois entrées de `COMMUNES.yaml` à `status: VERIFIED` (rien d'autre à renseigner).
3. `make heraldry-check && make layered-compose && make validate && make build-v3` ; contrôler les
   overlays `dist/layered/page-{07,08,09,12}-layered-proof-overlay.png` (zone d'écu).
4. Déclarer les trois actifs dans `manifest-v3.yaml` et lever le blocage provenance des zones
   armoiries dans `ASSET_SPEC.md` (`REGISTRY.yaml` → `a_faire`).
5. Sainte-Marie-de-Cuines et Notre-Dame-du-Cruet : interroger les mairies ; à réception d'un blason
   sourcé, l'ajouter aux deux registres (fichier, SHA, licence, auteur, blasonnement) puis même circuit.

## 4. Points d'attention

- Les blasonnements rapportés ici viennent d'extraits de recherche et peuvent être inexacts ; ne
  jamais dessiner un SVG à partir d'eux sans confirmation sur la source.
- Un ajustement de la zone d'écu (`shield_bbox_px`) peut être nécessaire page par page après le
  premier rendu réel ; contrôler l'overlay `dist/layered/page-NN/*-overlay.png`.
- Les SVG Commons complexes (dégradés, filtres) sont rendus par cairosvg en PNG au gate trait ;
  le SVG lui-même reste la source (SHA dans le lock).

## 5. Crédit CC BY-SA — proposition d'amendement canonique (page 15, mentions légales) — À ARBITRER

Non appliquée : le canon n'est modifié que sur décision explicite du propriétaire (règle « jamais de
modification silencieuse du canon »). Les trois lignes sont celles de `REGISTRY.yaml`
(`credit_ligne`), reprises mot pour mot dans `COMMUNES.yaml` (`credit_line`) ; le contrôle
`credit_inscribed_in_canon` les cherche telles quelles dans `pages/15.yaml:canonical_text`.

Texte proposé, à insérer entre « Date d'édition … » et la mention de copyright (blocs à ajouter en
fin de `canonical_text` de la page 15 pour ne pas renuméroter les blocs existants, composés en
couche texte au style `legal`/`caption` selon la grille page 15) :

```
Blason de La Chambre — Spedona / Wikimedia Commons — CC BY-SA 3.0
Blason de Saint-Étienne-de-Cuines — Chatsam / Wikimedia Commons — CC BY-SA 4.0
Blason de Saint-Rémy-de-Maurienne — Odejea / Wikimedia Commons — CC BY-SA 3.0
```

et amendement de la mention globale (formulation à valider par le propriétaire ; seule contrainte
juridique : exclure ces trois dessins du « tous droits réservés » et ne pas leur ajouter de
restriction) :

```
© 2025 — Tous droits réservés, à l'exception des blasons communaux crédités ci-dessus (CC BY-SA).
Reproduction interdite sans autorisation.
```

Points ouverts pour la décision : (a) page 15 ou colophon ; (b) la mention page 15 est aujourd'hui
un bloc canonique unique « © 2025 — Tous droits réservés. Reproduction interdite sans autorisation. »
(amendement = correction canonique tracée dans `corrections.yaml`) ; (c) le blason de La Chambre
n'est composé sur aucune page (03/04 sans fragment remplaçable) : le créditer seulement s'il est
reproduit ; (d) le partage à l'identique porte sur les dessins, pas sur le livret.

## 6. Test du 2026-09-11 sur les dessins réels (hors dépôt, `_verify-arms/`, non committé)

Registre de test avec les trois entrées en `VERIFIED` / `CLEARED` (contournement du crédit pour le
test uniquement), compositions 07, 08, 09 et 12 pointées sur ce registre :

- les quatre pages composent (`exit 0`) ; fragment `heraldry_captioned` remplacé par le rendu SVG
  (`role: communal_arms_vector`, `source: svg`, 1224.72 ppi ≥ gate trait 1200, `APPROVED`) ;
- écu bien inscrit dans la zone (64 % / 76 %) sur les quatre pages sans `shield_bbox_px` ; légende
  « Armoiries de Saint-Étienne-de-Cuines » sur deux lignes (07, 08, 09), « Armoiries de
  Saint-Rémy-de-Maurienne » sur trois lignes (12, bbox de 140 px), lisibles, sans collision ;
- test du garde-fou : `saint-remy-de-maurienne` en `VERIFIED` avec droits `ATTRIBUTION_SHAREALIKE`
  et crédit absent du canon → le compositeur refuse (`ligne de crédit non inscrite au canon …`).

État réel du dépôt (`VERIFIED_CREDITS_PENDING`) : fragment seigneurial conservé, légende ignorée,
`make heraldry-check` OK (5 communes, 0 active, 3 en attente de crédit), locks inchangés.
