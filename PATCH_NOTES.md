# Patch 2026-09-04

Modifications autorisées et uniquement celles-ci:

- Page 14:
  - `Collecte Fondation du Patrimoine (75%)` → `Collecte Fondation du Patrimoine (66%)`
  - signature canonique: `Fabrice GALOPO, André GRANGE, Gérald KERMA`

- Page 15:
  - `Fondation du Patrimoine 75 %` → `Fondation du Patrimoine 66 %`
  - auteurs canoniques: `Fabrice GALOPO, André GRANGE, Gérald KERMA`

Aucun autre contenu ou élément graphique n'a été volontairement modifié.

# Patch 2026-09-08 — fautes imprimées vérifiées

- Page 14 : `contact@couventdeelachambre.fr` → `contact@couventdelachambre.fr`.
  - Bande modifiée : `(346, 642)–(469, 672)`.
  - Dérive mesurée hors bande : 6 pixels avec écart RGB cumulé > 12.
- Page 15 : `valoriser de patrimoine` → `valoriser le patrimoine`.
  - Bande modifiée : `(404, 1126)–(422, 1162)`.
- Page 15 : `Fabrice GALLOPO` → `Fabrice GALOPO`.
  - Bande modifiée : `(344, 1355)–(798, 1378)`.
  - Dérive cumulée mesurée hors des deux bandes page 15 : 4 pixels avec écart RGB cumulé > 12.

Méthode : compositing NumPy local, glyphes prélevés sur la même ligne, aucune fonte système, aucune génération d'image; JPEG réencodés avec leurs tables de quantification d'origine et `subsampling=0`.
