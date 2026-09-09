# WORK HANDOFF — Les Seigneurs de La Chambre

## Mission
Migrer le livret/exposition vers une composition reproductible à couche texte sans dérive éditoriale ni visuelle. Le dépôt GitHub est l’unique source de vérité.

## Décision méthodologique active
La méthode prioritaire de la v3 est la **composition multicouche à partir des pages canoniques décomposées**.

On ne redessine plus systématiquement les illustrations en SVG. On repart des pages validées et on recompose :

1. fond/trame papier indépendant ;
2. fragments raster documentaires extraits des pages canoniques ;
3. vecteurs réellement utiles ;
4. texte canonique en vraie couche texte ;
5. QR et éléments fonctionnels déterministes en overlay final.

Les `assets/page-NN.jpg` restent les références de comparaison et servent, lorsque leur qualité et leur statut le permettent, de sources de fragments. Ils ne sont pas les pages finales aplaties de la v3.

## Ordre de lecture obligatoire
1. `REGENERATION_RULES.md`
2. `corrections.yaml`
3. `manifest.yaml`, `manifest-pages.json`, `manifest-v3.yaml`
4. `sources/PROVENANCE_INDEX.yaml`
5. `assets/ASSET_INDEX_V3.yaml`
6. `assets/ASSET_SPEC.md`
7. `pages/NN.yaml`
8. `qr_registry.yaml`
9. `assets/page-NN.jpg`
10. `docs/migration-text-layer/PHASE_A_APPROVAL.md`
11. `docs/migration-text-layer/PHASE_B_PAGE03_LAYERED_PROTOTYPE.md`

## Canon actuel
- 16 pages, `assets/page-01.jpg` à `assets/page-16.jpg`.
- Page 10 = Château de Notre-Dame-du-Cruet, version réorientée validée, QR Google Maps déterministe.
- Page 13 = six QR de ressources numériques alignés.
- Page 14 = portrait de Philippe DEMARIO supprimé, nom et bibliographie conservés.
- Page 16 = QR association enregistré.
- Fondation du Patrimoine = 66 %, jamais 75 %.
- Page 4 = aucune mention « Académie de Maurienne ».
- Auteurs = `Fabrice GALOPO, André GRANGE, Gérald KERMA`.

## Prototype page 03 : méthode validée
Le prototype multicouche de la page 03 a été exécuté de bout en bout.

Run de référence : `34259978419` sur le commit `5eef23415fe41424cb4dc37488225414d139e949`.

Résultats :
- 11 fragments raster réellement découpés depuis `assets/page-03.jpg` ;
- 25 blocs canoniques présents dans le PDF final ;
- vraie couche texte : PASS ;
- QR final décodé machine avec payload exact : PASS ;
- SHA des fragments : PASS ;
- source canonique inchangée : PASS ;
- inspection visuelle effectuée ;
- méthode : **PASS_WITH_RESOLUTION_BLOCKER**.

Rapport : `docs/migration-text-layer/PHASE_B_PAGE03_LAYERED_PROTOTYPE.md`.

### Gate de résolution découvert
La page 03 canonique mesure seulement `1024 × 1536 px`. À l’échelle A5 du prototype, les fragments représentent environ **185,78 ppi**, sous le gate de 300 ppi (demi-teintes) — et très loin du gate de 1200 ppi pour les rasters au trait. Depuis le 2026-09-09 ces deux gates s'appliquent à la taille de placement finale de **tous** les formats (A5, A2, A1), sans seuil réduit pour les grands formats.

Ce problème est un gate de qualité des actifs, pas un échec de la méthode de composition. Ne jamais le masquer par un upscale présenté comme récupération de détail.

Pour chaque fragment basse résolution, les voies légitimes sont :
1. retrouver une source haute définition ;
2. réduire sa taille de placement ;
3. valider explicitement un seuil inférieur ;
4. vectoriser seulement ce qui peut l’être sans dérive documentaire.

## État au 2026-09-09 : famille « site » composée par le compositeur générique

Rapport : `docs/migration-text-layer/PHASE_B_SITE_FAMILY_INDUSTRIALIZATION.md`.

- Compositeur générique piloté par YAML : `scripts/layered_compose.py` +
  `prototypes/page-NN/composition.yaml` (aucun script par page). Le prototype page 03 est porté
  dans ce format (`prototypes/page-03/composition.yaml`) ; les scripts `prototype_page03_*.py`
  restent comme témoins historiques.
- Pages 03, 05, 06, 07, 08, 09, 11, 12 : proofs multicouches produits, couche texte exacte,
  QR décodés, SHA des fragments verrouillés (`fragments.lock.yaml`), 0 collision texte/croquis,
  gate `PASS_WITH_RESOLUTION_BLOCKER` (181–186 ppi à la taille A5 contre 300 ppi demi-teintes /
  1200 ppi trait, gates identiques pour tous les formats depuis le 2026-09-09).
- **Validation du 2026-09-09 (gkerma)** : crops `APPROVED` sur les 8 pages, écarts texte ↔ canon
  arbitrés (le canon prévaut, légendes raster conservées dans leurs fragments), dérogation de
  résolution explicite pour la sortie A5 (≥ 180 ppi accepté ; 300/1200 restent la cible et
  bloquent A2/A1) → gate `PASS_WITH_RESOLUTION_WAIVER`. Détail :
  `docs/migration-text-layer/PHASE_B_SITE_FAMILY_VALIDATION.md`.
- Contrôles ajoutés après revue du 2026-09-09 : collision d'encre texte/fragment (rendus
  monocouche), bord de crop traversant un trait, texte dans une zone QR, masque local couleur
  papier des résidus de texte raster (traitement déclaré et journalisé par fragment).
- Écarts texte visible ↔ canon signalés page par page (bandeau courant, légendes d'armoiries,
  callouts, page 11 plus courte que le raster, page 09 `title` ≠ `canonical_text`) : non corrigés,
  à arbitrer.
- `make validate` inclut désormais `validate-layered` (sorties dans `_verify-layered/`, jamais
  committées).

## État au 2026-09-09 (nuit) : pages 01 et 02 composées et validées — 15/16 pages

Rapport : `docs/migration-text-layer/PHASE_B_PAGES_01_02.md`. Seule la page 04 reste hors
production (verrou éditorial). La citation de couverture (blocs 8–9 du canon, absente du raster)
est composée entre la ligne Commission et la frise : emplacement à arbitrer.

## État au 2026-09-09 (soir) : pages 10 et 13–16 composées et validées

Rapport : `docs/migration-text-layer/PHASE_B_PAGES_10_13_16.md`. 15 pages sur 16 sont
composées (03, 05–16) ; restent 01, 02 et la page 04 (verrou). Page 16 : 131,8 ppi, sous la
dérogation A5 → blocage rapporté. Page 14 : couvertures d'ouvrages non extraites (droits).

### Points éditoriaux ouverts (remarques du propriétaire, 2026-09-09)
- **Mention sur les illustrations** : échelle des plans non respectée, vues artistiques non
  nécessairement réalistes (pas d'archive d'époque), état actuel des ruines de certains sites.
  À rédiger, inscrire au canon (`pages/NN.yaml` + `corrections.yaml`) puis composer. Une
  proposition de formulation figure dans le rapport (PROPOSITION, hors canon).
- **Armoiries réelles des communes** : rechercher les blasons officiels et remplacer, quand la
  source et les droits sont établis, les armoiries de La Chambre en tête des pages de sites par
  celles de la commune (Sainte-Marie-de-Cuines 05–06, Saint-Étienne-de-Cuines 07–09,
  Notre-Dame-du-Cruet 10–11, Saint-Rémy-de-Maurienne 12, La Chambre 03–04). Gate provenance /
  droits / SHA avant production ; rendu SVG d'après blasonnement officiel de préférence.

## Industrialisation active : famille des pages « site »
Le prototype page 03 devient le modèle technique de la famille de pages patrimoniales.

Première vague d’industrialisation :
- page 05 — Château Joli ;
- page 06 — Tour de Burgin ;
- page 07 — Tour de Châtel-André ;
- page 08 — Maison-Forte du Châtelet ;
- page 09 — Maison-Forte de Gruyère ;
- page 11 — Tour de Notre-Dame-du-Cruet ;
- page 12 — Maison Forte de La Landonnière.

La page 04 est exclue car bloquée éditorialement. La page 10 est traitée séparément à cause du plan réel et de son verrou géométrique. Les pages 13 à 16 ont des structures spécifiques et seront industrialisées après la famille « site ».

L’industrialisation commence par une mesure déterministe de chaque raster et la production de diagnostics visuels. Les bounding boxes sémantiques restent soumises à revue humaine avant extraction, exactement comme sur la page 03.

## Pipeline cible par page
### A. Cartographier
- lire `pages/NN.yaml` et `assets/ASSET_SPEC.md` ;
- identifier texte, illustrations, cartes, ornements, QR et espaces de fond ;
- comparer avec `assets/page-NN.jpg`.

### B. Mesurer
- vérifier le SHA du raster ;
- mesurer dimensions et densités visuelles sans OCR ;
- produire overlay et planche-contact ;
- ne jamais transformer une détection automatique en crop approuvé sans revue.

### C. Extraire
Créer uniquement les fragments approuvés : illustrations, photos, gravures, cartes/plans autorisés et éléments graphiques particuliers.

Les légendes réellement présentes dans l’image mais absentes du YAML canonique restent intégrées au fragment raster, sauf décision éditoriale explicite. Elles ne sont ni OCRisées comme source de vérité ni réinventées.

### D. Construire le fond
Utiliser une trame SpiritualCept claire, reproductible et indépendante du contenu documentaire.

### E. Recomposer le texte
Le texte vient uniquement de `pages/NN.yaml:canonical_text` et des corrections validées. Il doit rester du vrai texte dans le PDF final lorsque techniquement possible.

### F. Ajouter les fonctions
Les QR viennent uniquement de `qr_registry.yaml` et des SVG déterministes validés. Leur placement part des coordonnées canoniques normalisées. Ils sont rendus en dernier.

### G. Valider
- SHA source ;
- SHA fragments ;
- présence exacte de tous les blocs de texte canonique ;
- QR décodé depuis le rendu PDF final ;
- résolution effective par fragment ;
- inspection visuelle ;
- comparaison avec la référence canonique.

## SVG : rôle limité et utile
Le SVG reste privilégié pour QR, ornements, filets/formes, héraldique correctement spécifiée et documents dont la vectorisation est justifiée.

Il n’est pas utilisé pour remplacer artificiellement une illustration canonique exploitable.

## Reconstitutions
Elles restent autorisées mais secondaires. Elles servent lorsqu’aucun fragment canonique exploitable n’existe, lorsqu’une nouvelle vue est explicitement souhaitée, ou lorsqu’une restitution hypothétique est un objectif éditorial identifié.

Elles restent sourcées, sans texte, avec confiance et limites déclarées.

## Verrous
### Page 4
`PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` reste actif pour toute recomposition v3.

### Page 10
Le plan réel reste l’autorité pour toute nouvelle reconstitution. La composition v3 privilégie les fragments validés de la page canonique plutôt qu’une nouvelle architecture spéculative.

### Page 13
QR déterministes, alignés et réinjectés en dernier.

### Page 14
Aucun portrait de Philippe DEMARIO, y compris sous forme de fragment extrait.

## Registres
- `sources/PROVENANCE_INDEX.yaml` : provenance/droits/confiance ;
- `assets/ASSET_INDEX_V3.yaml` : actifs atomiques ;
- `manifest-v3.yaml` : actifs réellement produits ;
- `assets/ASSET_SPEC.md` : cartographie des zones et besoins de production.

Chaque fragment raster produit doit enregistrer : page source, zone/bounding box source, traitement, dimensions, résolution effective, SHA-256, statut de droits et état de validation.

## Règles de travail
- Ne jamais inventer de contenu.
- Ne jamais faire d’une reconstruction générative la solution par défaut.
- Préférer un fragment canonique fidèle lorsqu’il est exploitable.
- Le texte est une couche indépendante.
- Le fond est une couche indépendante.
- Les QR sont une couche fonctionnelle indépendante et déterministe.
- Une retouche d’un fragment reste locale et traçable.
- Les PDF, ZIP, planches contact et `dist/` ne sont jamais committés.

## Priorité d’exécution
1. ~~mesurer en CI les pages 05, 06, 07, 08, 09, 11 et 12~~ — fait (`layered-site-compose.yml`) ;
2. ~~revoir visuellement les diagnostics et approuver les crops sémantiques~~ — validé le 2026-09-09 ;
3. ~~généraliser le compositeur page 03 en compositeur piloté par YAML~~ — fait ;
4. ~~produire un proof multicouche par page de la famille~~ — fait ;
5. ~~reporter automatiquement texte, QR, SHA et ppi~~ — fait ;
6. ~~arbitrer les écarts texte visible ↔ canon et le gate de résolution~~ — validé le 2026-09-09 (canon prévaut ; dérogation A5) ;
7. ~~traiter ensuite page 10, puis les structures spécifiques 13–16~~ — fait et validé le 2026-09-09 ;
8. ~~composer les pages 01 et 02~~ — fait et validé le 2026-09-09 ; arbitrer la mention illustrations et les armoiries communales ;
9. laisser page 04 hors production jusqu’à levée explicite du verrou éditorial.

## Validation
Après modification d’une référence historique : `make sync && make validate`.

Après production d’actifs v3 : enregistrer les SHA/provenances puis `make validate`.

Après composition imprimable : `make build`, validation QR finale et contrôle de la couche texte.

## Interdiction de reconstruction par archive
Toujours partir du checkout Git courant. Aucun ancien ZIP ne devient source de vérité.