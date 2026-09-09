# Phase B — validation de la famille « site » et du compositeur générique

> **Statut : VALIDÉ.**
> Date de validation humaine : **2026-09-09**. Autorité : propriétaire du projet (`gkerma`), instruction
> « Go, valide tout » donnée après revue de la PR #11 (fusionnée dans `release/v3.0-phase-b`).

## 1. Périmètre validé

1. Le compositeur générique piloté par YAML (`scripts/layered_compose.py`) et ses contrôles
   (couche texte exacte, QR décodé, SHA source/fragments, collisions d'encre, texte dans une zone QR).
2. Les compositions `prototypes/page-NN/composition.yaml` des pages 03, 05, 06, 07, 08, 09, 11, 12 :
   tous les fragments passent de `INSPECTED` à `APPROVED` ; `accept_fragment_statuses: [APPROVED]`.
3. Les inventaires `page-NN.objects.yaml` dérivés (gate de complétude `PASS`).
4. Les locks SHA-256 `fragments.lock.yaml` (inchangés : les bboxes n'ont pas bougé).

## 2. Arbitrages éditoriaux

- Les textes visibles dans les rasters mais absents de `pages/NN.yaml:canonical_text` (bandeau
  courant, légendes d'armoiries, callouts, cartouches, toponymes) **restent raster dans leurs
  fragments**, sans OCR ni retypage. Le canon n'est pas modifié.
- Page 11 : le canon (plus court que le raster) prévaut ; les deux intertitres du raster ne sont pas
  recomposés.
- Page 09 : composé selon `canonical_text` (« La Maison Forte de Gruyère ») ; le champ `title` reste tel quel.
- Ces décisions sont enregistrées dans chaque composition sous `discrepancies.arbitration`.

## 3. Dérogation de résolution

Gates cibles inchangés : **300 ppi** demi-teintes / **1200 ppi** trait à la taille finale, tous formats.
Dérogation explicite (voie « validation explicite d'un seuil inférieur » de `REGENERATION_RULES.md`) :
les rasters canoniques sont acceptés pour la **sortie A5** avec un minimum de **180 ppi**
(`validation.resolution_waiver` dans chaque composition). Les sorties A2/A1 restent bloquées par les
gates. Aucun upscale n'est autorisé par cette dérogation.

| Page | Fragments | ppi min (A5) | Gate |
|---|---:|---:|---|
| 03 | 12 | 185.78 | `PASS_WITH_RESOLUTION_WAIVER` |
| 05 | 13 | 185.78 | `PASS_WITH_RESOLUTION_WAIVER` |
| 06 | 19 | 185.78 | `PASS_WITH_RESOLUTION_WAIVER` |
| 07 | 22 | 185.78 | `PASS_WITH_RESOLUTION_WAIVER` |
| 08 | 17 | 185.78 | `PASS_WITH_RESOLUTION_WAIVER` |
| 09 | 15 | 185.78 | `PASS_WITH_RESOLUTION_WAIVER` |
| 11 | 14 | 181.06 | `PASS_WITH_RESOLUTION_WAIVER` |
| 12 | 18 | 181.06 | `PASS_WITH_RESOLUTION_WAIVER` |

## 4. Effet sur les documents de Phase A

`assets/ASSET_SPEC.md` §2 (300 A5 / 180 A2 / 150 A1) est **remplacé** par la règle 300/1200 ci-dessus.
Le fichier validé en Phase A n'est pas réécrit ; la présente validation vaut décision pour la v3.0.

## 5. Ce que cette validation n'autorise pas

- modification silencieuse d'un `canonical_text` ;
- remplacement d'un fragment canonique par une création générative ;
- page 04 (verrou éditorial) et page 10 (verrou géométrique) : inchangés.
