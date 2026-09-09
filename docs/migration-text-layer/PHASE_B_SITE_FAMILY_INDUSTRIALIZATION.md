# Phase B — industrialisation de la famille « site » (pages 05, 06, 07, 08, 09, 11, 12)

## Statut

**SITE_FAMILY_COMPOSED — PASS_WITH_RESOLUTION_BLOCKER — revue humaine des crops en attente.**

Date : 2026-09-09. Branche de travail : dérivée de `release/v3.0-phase-b` (`b362e98`).

Ce lot exécute la priorité 1–5 de `WORK_HANDOFF.md` : mesure déterministe, inventaire objet par
objet, compositeur générique piloté par YAML, proof multicouche par page, report automatique de
texte / QR / SHA / ppi. Aucune page raster canonique n'est modifiée (`make sync` sans effet,
SHA vérifiés à chaque run). Aucun texte n'est inventé : la couche texte vient exclusivement de
`pages/NN.yaml:canonical_text`, les QR de `qr_registry.yaml` via `assets/qr-svg/`.

## 1. Diagnostic initial (avant modification)

- `make validate` : OK sur `release/v3.0-phase-b` (référentiel, QR PNG, 16 QR SVG, 3 SVG Phase B).
- `scripts/prototype_page03_run.py` : reproduit localement le résultat documenté (25 blocs, QR exact,
  11 fragments, 185,78 ppi, `PASS_WITH_RESOLUTION_BLOCKER`).
- `scripts/layered_measure.py` v1 : 0 candidat sur les pages 06, 08 et 12 (le détecteur macro fusionnait
  la page entière) → inutilisable comme inventaire.
- Branches de prototype : `prototype/v3-page03-object-map` et `prototype/v3-page-03-object-map` existent
  (deux cartographies fines de la page 03, non fusionnées) ; `prototype/v3-layered-page-03` n'existe plus
  (fusionnée par la PR #7) ; `main` contient `release/v3.0-phase-b` en totalité plus le prompt de reprise.
- **Ce qui était industrialisable** : la pile de couches, la vérification SHA, le décodage QR machine, le
  contrôle de la couche texte, les coordonnées normalisées des QR (1920×2880).
- **Ce qui manquait** : un compositeur sans code par page (le prototype page 03 codait bboxes, styles et
  mapping des blocs en dur), un détecteur d'objets utilisable, une cartographie des zones texte, un
  contrôle des collisions texte/croquis et des bords de crop (remarques de revue du 2026-09-09 sur la
  page 03 : « recouvrement du croquis par le texte », « effacement par la marge du texte d'un croquis »),
  la traçabilité SHA des fragments dans les registres.

## 2. Ce qui a été construit

| Fichier | Rôle |
|---|---|
| `scripts/layered_measure.py` | Mesure v2 : couleur du papier, objets graphiques (ouverture morphologique 7 px), zones texte, table de résolution A5/A2/A1, `--probe X,Y,W,H` pour mesurer un objet sans OCR |
| `scripts/layered_compose.py` | Compositeur générique piloté par `prototypes/page-NN/composition.yaml` : fond, fragments (bbox source/destination, `crop_only`, `crop_grow_to_clean_edge`, masques locaux couleur papier), vecteurs, styles, blocs texte ↔ blocs canoniques, QR SVG en dernier, validations |
| `scripts/layered_inventory.py` | Dérive `page-NN.objects.yaml` (page → régions → objets → zones texte → fonctionnel → cadres) depuis la composition et le dernier run |
| `scripts/validate_layered.py` | Recompose et valide toutes les pages ; intégré à `make validate` |
| `prototypes/_shared/text-styles.yaml` | Styles partagés (Times base-14 tant que la fonte n'est pas verrouillée, ASSET_SPEC §7) |
| `prototypes/page-NN/composition.yaml` | Une composition par page, sans code métier |
| `prototypes/page-NN/fragments.lock.yaml` | SHA-256 et bbox finale de chaque fragment (registre) |
| `.github/workflows/layered-site-compose.yml` | CI : mesure + composition + validation + artefacts par page |

Validations exécutées par le compositeur à chaque run : SHA de la page canonique, présence exacte de
chaque bloc canonique dans la couche texte du PDF, affectation de tous les blocs (un seul bloc par
zone), décodage machine du QR depuis le rendu final, SHA de chaque fragment, ppi effectif de chaque
fragment à la taille de placement, **collision d'encre texte/fragment** (calculée sur des rendus
monocouche, donc exacte), texte dans la zone de placement d'un QR, débordement de bloc, bords de crop
traversant des traits (avertissement), concordance avec le lock.

## 3. Résultat par page

| Page | Titre | Fragments | Blocs canon | Couche texte | QR | SHA fragments | Collisions | Bords sales (warn) | Gate | Statut crops |
|---|---|---:|---:|---|---|---|---:|---:|---|---|
| 03 | Le Couvent des Cordeliers | 12 | 25 | PASS | PASS | PASS | 0 | 11 | `PASS_WITH_RESOLUTION_BLOCKER` | PROTOTYPE_PORTED_TO_GENERIC_COMPOSER |
| 05 | Le Château Joli | 13 | 20 | PASS | PASS | PASS | 0 | 11 | `PASS_WITH_RESOLUTION_BLOCKER` | INSPECTED_PENDING_HUMAN_REVIEW |
| 06 | La Tour de Burgin | 19 | 17 | PASS | PASS | PASS | 0 | 16 | `PASS_WITH_RESOLUTION_BLOCKER` | INSPECTED_PENDING_HUMAN_REVIEW |
| 07 | La Tour de Châtel-André | 22 | 21 | PASS | PASS | PASS | 0 | 15 | `PASS_WITH_RESOLUTION_BLOCKER` | INSPECTED_PENDING_HUMAN_REVIEW |
| 08 | La Maison-Forte du Châtelet | 17 | 20 | PASS | PASS | PASS | 0 | 13 | `PASS_WITH_RESOLUTION_BLOCKER` | INSPECTED_PENDING_HUMAN_REVIEW |
| 09 | La Maison-Forte de Gruyère | 15 | 15 | PASS | PASS | PASS | 0 | 11 | `PASS_WITH_RESOLUTION_BLOCKER` | INSPECTED_PENDING_HUMAN_REVIEW |
| 11 | La Tour de Notre-Dame-du-Cruet | 14 | 15 | PASS | PASS | PASS | 0 | 12 | `PASS_WITH_RESOLUTION_BLOCKER` | INSPECTED_PENDING_HUMAN_REVIEW |
| 12 | La Maison Forte de La Landonnière | 18 | 21 | PASS | PASS | PASS | 0 | 14 | `PASS_WITH_RESOLUTION_BLOCKER` | INSPECTED_PENDING_HUMAN_REVIEW |

Les « bords sales » signalent un bord de crop qui touche de l'encre : dans cette famille il s'agit
presque toujours des filets de cadre de la page ou d'objets voisins, à revoir humainement mais sans
effet sur la lisibilité ; les cas de résidus de texte raster ont été traités par masque local.

## 4. Blocage de résolution (gate séparé, non masqué)

Gates (décision du 2026-09-09, à la taille de placement finale, **tous formats**) : **300 ppi** pour
les rasters en demi-teintes, **1200 ppi** pour les rasters au trait (icônes, ornements, croix).
Texte et QR sont vectoriels et hors gate. Chaque fragment porte `raster_kind` (hérité du rôle).

| Page | Raster canonique | ppi effectif A5 | ppi A2 | ppi A1 | fragments demi-teintes (gate 300) | fragments trait (gate 1200) — ppi min |
|---|---|---:|---:|---:|---:|---|
| 03 | 1024 × 1536 | 185.78 | 65.68 | 46.39 | 12 | 0 (—) |
| 05 | 1024 × 1536 | 185.78 | 65.68 | 46.39 | 8 | 5 (185.78) |
| 06 | 1024 × 1536 | 185.78 | 65.68 | 46.39 | 10 | 9 (185.78) |
| 07 | 1024 × 1536 | 185.78 | 65.68 | 46.39 | 10 | 12 (185.78) |
| 08 | 1024 × 1536 | 185.78 | 65.68 | 46.39 | 9 | 8 (185.78) |
| 09 | 1024 × 1536 | 185.78 | 65.68 | 46.39 | 8 | 7 (185.78) |
| 11 | 1055 × 1491 | 181.06 | 63.8 | 45.11 | 9 | 5 (181.06) |
| 12 | 1055 × 1491 | 181.06 | 63.8 | 45.11 | 10 | 8 (181.06) |

Toute la famille est sous le gate 300 en A5 et très loin des gates pour A2/A1 et pour le trait : le
blocage identifié sur la page 03 est **générique**. Aucun upscale n'a été appliqué. Voies légitimes
inchangées : sources HD (raster 300 / 1200 ppi à la taille finale), réduction de la taille de
placement, validation explicite d'un seuil inférieur, vectorisation sans dérive (candidats évidents :
icônes, croix, filets, ornements — déjà `line_art`). Les seuils 300 A5 / 180 A2 / 150 A1 de
`assets/ASSET_SPEC.md` §2 sont remplacés par cette règle ; ce document validé en Phase A devra être
revalidé avec les nouveaux gates.

## 5. Écarts texte visible ↔ canon (signalés, jamais corrigés silencieusement)

| Page | Type | Fragment | Description |
|---|---|---|---|
| 05 | texte raster hors canon | `running_head_raster` | bandeau courant « Les Seigneurs de La Chambre et leur patrimoine en Maurienne » |
| 05 | texte raster hors canon | `heraldry_captioned` | légende des armoiries (voir blasonnement officiel p.2) |
| 05 | texte raster hors canon | `hero_captioned` | callouts de la vue principale (Face à face… / Le Château Joli domine…) |
| 05 | texte raster hors canon | `poype_captioned` | annotations du croquis de la poype et cartouche POYPE FÉODALE |
| 05 | texte raster hors canon | `princess_captioned` | légende du portrait d'Agnès de Savoie-Achaïe (dates) |
| 05 | texte raster hors canon | `map_document` | toponymes intrinsèques de la carte (conservés comme document) |
| 06 | texte raster hors canon | `heraldry_captioned` | légende des armoiries (voir blasonnement officiel p.2) |
| 06 | texte raster hors canon | `hero_captioned` | callouts « Manoir de Châtel-André » et « Emplacement de la Tour de Burgin » |
| 06 | texte raster hors canon | `du_pont_blason_captioned` | cartouche « DU PONT » |
| 06 | texte raster hors canon | `berthollet_portrait_captioned` | légende « Claude-Louis Berthollet 1748-1822 » |
| 06 | texte raster hors canon | `vestiges_box_captioned` | titre « Vestiges aujourd'hui » et citation « Réduits à fort peu de choses » (Georges Chapier, 1957) |
| 06 | texte raster hors canon | `map_document` | toponymes intrinsèques de la carte |
| 06 | structure de paragraphe | bloc 8 | le raster coupe le bloc canonique 8 en deux paragraphes (« …vallée. » / « Jean Truchet devint… ») ; le canon est composé en un seul bloc |
| 06 | typographie | — | titre en petites capitales dans le raster ; composé en Times-Bold (fonte non encore verrouillée, ASSET_SPEC §7) |
| 07 | texte raster hors canon | `running_head_raster` | bandeau courant « Les Seigneurs de La Chambre et leur patrimoine en Maurienne » |
| 07 | texte raster hors canon | `heraldry_captioned` | légende des armoiries (voir blasonnement officiel p.2) |
| 07 | texte raster hors canon | `hero_captioned` | légende « Donjon de Châtel-André (XIIe siècle) » |
| 07 | texte raster hors canon | `vassal_scene_captioned` | légende « Le vassal rend hommage à son suzerain » |
| 07 | texte raster hors canon | `defensive_box_captioned` | titre « Un système défensif complémentaire » et toponymes (Le Cruet, Châtel-André, Route du Mont-Cenis, La Chambre, Vallée des Villards) |
| 07 | texte raster hors canon | `battle_scene_captioned` | légende « Reprise de la tour par les troupes savoyardes (1598) » |
| 07 | texte raster hors canon | `mh_seal` | sceau MONUMENT HISTORIQUE (texte intrinsèque) |
| 07 | texte raster hors canon | `map_document` | toponymes intrinsèques de la carte |
| 08 | texte raster hors canon | `running_head_raster` | bandeau courant |
| 08 | texte raster hors canon | `heraldry_captioned` | légende des armoiries |
| 08 | texte raster hors canon | `hero_captioned` | callouts « Magnolia centenaire dans les jardins suspendus », « Maison-Forte du Châtelet, centre du village de Saint-Étienne-de-Cuines » |
| 08 | texte raster hors canon | `panorama_captioned` | libellés « Le Châtelet », « Système défensif des seigneurs de La Chambre », « Le Cruet » |
| 08 | texte raster hors canon | `map_document` | toponymes intrinsèques de la carte |
| 09 | texte raster hors canon | `running_head_raster` | bandeau courant |
| 09 | texte raster hors canon | `heraldry_captioned` | légende des armoiries |
| 09 | texte raster hors canon | `gruyere_seal` | sceau GRUYÈRE SUISSE (texte intrinsèque) |
| 09 | texte raster hors canon | `magnolia_captioned` | légende « Magnolia séculaire ombrageant la demeure » |
| 09 | texte raster hors canon | `map_document` | toponymes intrinsèques de la carte |
| 09 | champ title ≠ canonical_text | — | pages/09.yaml:title = « La Maison-Forte de Gruyère » (trait d'union, comme le raster) alors que canonical_text commence par « La Maison Forte de Gruyère » ; composé selon canonical_text, à arbitrer |
| 09 | ornement non repris | — | croix ✠ en tête des deux paragraphes (inline dans le raster) non reproduites : pas de retour à la ligne suspendu dans la couche texte |
| 11 | texte raster hors canon | `running_head_raster` | bandeau courant |
| 11 | texte raster hors canon | `heraldry_captioned` | légende des armoiries |
| 11 | texte raster hors canon | `callout_box_captioned` | cartouche « Tour carrée médiévale / 4 étages / Hauteur : environ 12 m » |
| 11 | texte raster hors canon | `tower_ladder_captioned` | annotations de la coupe (Porte d'accès au 1er étage, Échelle amovible (retirée en cas d'attaque), Entrée au rez-de-chaussée) |
| 11 | texte raster hors canon | `valley_box_captioned` | titre « Vue sur la vallée du Bugeon » et toponymes (Le Cruet, Le Bugeon) |
| 11 | texte raster hors canon | `map_document` | toponymes intrinsèques de la carte |
| 11 | canon ≠ raster | — | le raster montre deux intertitres (« Sentinelle au coeur de la vallée », « Un dispositif défensif classique ») absents de canonical_text ; non recomposés |
| 11 | canon ≠ raster | — | le raster prolonge le bloc 2 par « …pour contrôler les voies de communication et protéger leurs terres. » absent du canon ; le canon prévaut |
| 11 | canon ≠ raster | — | le raster coupe le bloc 3 en deux paragraphes ; composé en un bloc |
| 11 | canon ≠ raster | — | le raster porte un résidu « ler » sous le QR (défaut de l'ancienne page) : disparaît, le texte « Scannez pour y aller » est vivant |
| 12 | texte raster hors canon | `running_head_raster` | bandeau courant |
| 12 | texte raster hors canon | `heraldry_captioned` | légende des armoiries |
| 12 | texte raster hors canon | `network_panorama_captioned` | titre « RÉSEAU DES FORTERESSES DES SEIGNEURS DE LA CHAMBRE » et cartouches (Notre-Dame-du-Cruet Château, La Chambre Tour & Maison de La Tour, Sainte-Marie-de-Cuines Château Joli, Saint-Étienne-de-Cuines Châtel-André Châtelet Gruyère, Saint-Rémy-de-Maurienne La Landonnière) |
| 12 | texte raster hors canon | `map_document` | toponymes intrinsèques de la carte |
| 12 | canon ≠ raster | — | le raster coupe le bloc 6 en trois paragraphes ; composé en un bloc à gauche du médaillon |
| 12 | canon ≠ raster | — | le raster montre « Scannez pour y aller » superposé au QR (défaut de l'ancienne page) : disparaît |

Décisions éditoriales attendues : (a) le bandeau courant « Les Seigneurs de La Chambre et leur
patrimoine en Maurienne » et la légende des armoiries sont présents sur toutes les pages « site » mais
absents de tout `canonical_text` — les ajouter au canon (couche texte) ou les laisser raster ;
(b) page 11 : le canon est plus court que la page validée visuellement (deux intertitres et une
proposition en moins) ; (c) page 09 : `title` avec trait d'union vs `canonical_text` sans.

## 6. Blocages éditoriaux ou de droits

- Page 04 : `PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` — non touchée.
- Page 10 : plan réel = autorité géométrique, `P10-Z03` `BLOCKED_RIGHTS` — non touchée ; la composition
  multicouche pourra réutiliser ses fragments canoniques avec le même compositeur.
- Fontes : choix et licence non enregistrés (ASSET_SPEC §7) — Times base-14 en attendant.
- Aucun actif ChatGPT n'a été nécessaire.

## 7. Commandes

```
make layered-measure      # diagnostics + table ppi
make layered-compose      # proofs + locks (dist/layered/page-NN/)
make layered-inventory    # page-NN.objects.yaml
make validate             # inclut validate-layered
```

Chaque `dist/layered/page-NN/` contient le PDF proof, son rendu, un overlay des boîtes (fragments
rouge, texte bleu, QR vert, collisions magenta), une comparaison côte à côte avec la page canonique,
`fragments.json`, `composition-report.json` et `proof-validation.json`.

## 8. Prochaines étapes

1. Revue humaine des crops (`status: INSPECTED` → `APPROVED`) sur les overlays de `dist/layered/`.
2. Arbitrages éditoriaux du §5 (bandeau, légendes d'armoiries, page 11, page 09).
3. Décision sur le gate de résolution (sources HD ou seuil A5 validé explicitement).
4. Page 10 puis pages 13–16 avec le même compositeur (multi-QR déjà supporté par `qr:` liste).
5. Verrouiller la fonte et l'enregistrer dans `manifest-v3.yaml:fonts`.
