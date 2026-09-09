# Phase B — pages 01 et 02 : composition multicouche et validation

## Statut

**COMPOSÉ ET VALIDÉ le 2026-09-09 (gkerma, « Go, pages 01 et 02 »)** — `PASS_WITH_RESOLUTION_WAIVER`
(dérogation A5). **15 pages sur 16 sont composées** ; seule la page 04 reste hors production
(`PAGE_04_EDITORIAL_ARBITRATION_REQUIRED`).

## 1. Résultat

| Page | Titre | Fragments | Blocs canon | Couche texte | Collisions | ppi min A5 | Gate |
|---|---|---:|---:|---|---:|---:|---|
| 01 | Couverture | 17 | 10 | PASS | 0 | 185.78 | `PASS_WITH_RESOLUTION_WAIVER` |
| 02 | Les Seigneurs de La Chambre | 20 | 25 | PASS | 0 | 185.78 | `PASS_WITH_RESOLUTION_WAIVER` |

Pas de QR sur ces pages. Aucune page raster canonique modifiée.

## 2. Écarts et décisions consignés

| Page | Type | Fragment | Description |
|---|---|---|---|
| 01 | texte raster hors canon | `running_head_raster` | bandeau courant |
| 01 | texte raster hors canon | `church_captioned` | « Église Notre-Dame-du-Cruet XIVe siècle » |
| 01 | texte raster hors canon | `mountains_captioned` | « Maurienne Terre de passage et de seigneuries » |
| 01 | texte raster hors canon | `seal_captioned` | « Sceau d'un seigneur de La Chambre XIIIe siècle » |
| 01 | texte raster hors canon | `maison_forte_captioned` | « Maison forte de La Tour » |
| 01 | texte raster hors canon | `fidem_servare_raster` | devise « Fidem servare et jus dicere » |
| 01 | texte raster hors canon | `timeline_and_logo` | frise : XIe s. Origines Vicomtés épiscopales / XIIe-XIIIe s. Âge d'or Mariages et alliances / XIVe s. Fondations Couvent des Cordeliers / XVe s. Crépuscule Passage aux Seyssel ; texte intrinsèque du logo |
| 01 | texte raster hors canon | `footer_raster` | pied de page avec folio |
| 01 | canon non visible dans le raster | — | blocs 8–9 « Le passé n'est pas derrière nous, / il est sous nos pas. » : absents de la page canonique ; composés dans l'espace libre entre la ligne Commission et la frise (position à arbitrer) |
| 02 | texte raster hors canon | `running_head_raster` | bandeau courant (avec un défaut de rendu raster sur « Les ») |
| 02 | texte raster hors canon | `village_captioned` | « La Chambre, capitale et coeur de la seigneurie » |
| 02 | texte raster hors canon | `bishop_captioned` | « L'évêque-comte, maître spirituel et temporel de la Maurienne » |
| 02 | texte raster hors canon | `seal_vicomte_captioned` | « Sceau d'un vicomte de La Chambre (XIIIe siècle) » |
| 02 | texte raster hors canon | `knight_captioned` | « Une lignée chevaleresque, au service de la vallée et de l'Église. » |
| 02 | texte raster hors canon | `equestrian_seal_captioned` | « Sceau équestre (XIIe siècle) » |
| 02 | texte raster hors canon | `testament_captioned` | « Testament de Pierre de La Chambre (1261) » |
| 02 | texte raster hors canon | `monk_church_captioned` | « Couvent des Cordeliers, fondation de 1365 » |
| 02 | texte raster hors canon | `louis_medallion_captioned` | « Louis Ier de Savoie (1402-1465) » |
| 02 | texte raster hors canon | `territory_map` | toponymes intrinsèques de la carte du mandement |
| 02 | texte raster hors canon | `footer_landscape_raster` | pied de page avec folio |
| 02 | canon ≠ raster | — | le paragraphe du comte de Foras est en italique dans le raster ; le canon ne porte pas de marquage : composé en italique (style), texte identique |
| 02 | héraldique | — | P02-Z01 : armoiries reprises de la page canonique ; assets/svg/heraldry-la-chambre.svg reste PRODUCED_PENDING_HERALDIC_REVIEW, non utilisé |

## 3. Points d'attention

- **Page 01** : la citation « Le passé n'est pas derrière nous, / il est sous nos pas. » (blocs 8–9 du
  canon) n'existe pas dans la page canonique ; elle est composée dans l'espace libre entre la ligne
  « Commission Histoire et Patrimoine » et la frise chronologique. Emplacement à arbitrer.
- **Page 02** : le paragraphe du comte de Foras est composé en italique (style), texte identique au
  canon. Les armoiries sont reprises de la page canonique ; le SVG héraldique reste en attente de
  revue et n'est pas utilisé.
- Les bandeaux courants, pieds de page avec folio, légendes et la frise chronologique de la
  couverture restent raster (absents du canon), conformément à l'arbitrage du 2026-09-09.

## 4. État global

15/16 pages composées par `scripts/layered_compose.py` (01–03, 05–16), `make validate` couvre les
15 compositions. Restent : page 04 (verrou éditorial), mention sur les illustrations, armoiries
communales, sources HD (page 16), droits (couvertures page 14, logo page 16), fonte à verrouiller.
