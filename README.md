# Les Seigneurs de La Chambre — paquet de référence

Ce dossier est la source de régénération de la série SpiritualCept Research Notebook.

## Architecture
- `style.yaml` : ADN graphique et règles d'impression.
- `manifest.yaml` : index des 15 planches et empreintes SHA-256 des références visuelles.
- `corrections.yaml` : corrections éditoriales qui prévalent sur les anciens rendus.
- `pages/NN.yaml` : fiche canonique de chaque page, avec texte verrouillé, rôle, structure et garde-fous.
- `assets/page-NN.jpg` : référence visuelle HQ de la page correspondante.

## Règle de régénération
1. Charger `style.yaml`.
2. Charger la fiche `pages/NN.yaml`.
3. Utiliser `assets/page-NN.jpg` comme référence de composition, pas comme source éditoriale.
4. Le champ `canonical_text` est intouchable.
5. Appliquer `corrections.yaml`.
6. Réinjecter les QR codes validés après les traitements graphiques.
7. Comparer le rendu au master: format, contenu, hiérarchie, positions fonctionnelles et lisibilité.
8. Préflight impression et scan de tous les QR codes.

## Important
Le paquet distingue volontairement le **contenu canonique** de la **référence visuelle**. Cela permet de changer contraste, texture ou technique de dessin sans faire muter l'histoire.


## Registre QR verrouillé

`qr_registry.yaml` est désormais la source de vérité de tous les QR codes.

- Les pages 3 à 12 reprennent **les payloads exacts décodés du livret source original** pour Google Maps.
- La page 13 n'utilise plus les anciennes destinations `sdlc...` non vérifiées. Ses six ressources sont des pages actuelles vérifiées.
- Les QR sont générés de façon déterministe en noir sur blanc, jamais par IA.
- `scripts/validate_qr.py` redécode chaque QR dans les JPEG finaux et compare le résultat au registre.
- Toute future modification d'un QR exige une mise à jour explicite de `qr_registry.yaml` et une nouvelle validation.

Le plan réel du Château de Notre-Dame-du-Cruet fourni pour la reconstitution visuelle est conservé sous
`assets/reference/page-10-plan-reel.jpg`.
