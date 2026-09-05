# RÈGLES DE RÉGÉNÉRATION — Les Seigneurs de La Chambre

Ce fichier fait partie de la source de vérité du projet. La charte actuelle est **SpiritualCept Colorisé**.

## 1. Principe absolu

Le contenu éditorial, la structure d'une page, les données historiques, les plans, les cartes, les coordonnées et les QR sont verrouillés. La colorisation est un traitement visuel, pas une autorisation de réécrire ou d'inventer.

Deux cas seulement sont admis :

1. **Correction ponctuelle** : partir du visuel validé et ne modifier que la zone demandée.
2. **Régénération/colorisation complète explicitement demandée** : conserver le contenu, l'ordre des blocs, la hiérarchie et les zones fonctionnelles, puis appliquer la charte colorisée décrite dans `style.yaml`.

## 2. Ordre des sources

Toujours résoudre un conflit dans cet ordre :

1. `corrections.yaml`
2. `pages/NN.yaml` et son `canonical_text`
3. `assets/page-NN.jpg`, référence visuelle actuellement validée
4. `qr_registry.yaml` pour tout QR
5. `assets/reference/*` pour plans, documents et images sources réelles
6. aucune autre source sans validation explicite

Une image générée n'est jamais une source historique. Elle n'est qu'un rendu.

## 3. Interdictions

- Ne jamais inventer de personne, nom, fonction, catégorie, citation, date, lieu, source, prix, taux ou événement.
- Ne jamais ajouter de texte absent du canon.
- Ne jamais remplacer une donnée réelle par une approximation graphique.
- Ne jamais modifier un plan réel pour le rendre plus « joli ».
- Ne jamais styliser, redessiner ou inventer un QR.
- Ne jamais appliquer de filtre global qui détériore texte, cartes, plans ou QR.
- Ne jamais ajouter de portrait moderne ou photographique non demandé.
- Page Association : aucun portrait/photo de Philippe DEMARIO. Son nom et sa bibliographie restent dans le contenu canonique.

## 4. Nouvelle colorisation verrouillée

La nouvelle référence graphique est une affiche patrimoniale colorisée, sur papier ivoire patiné :

- **Plume / gravure sépia** pour architecture, contours, plans, cartes et légendes graphiques.
- **Fusain léger** pour ombres, ruines et profondeur.
- **Aquarelle transparente** pour ciel, montagnes et paysages.
- **Pastel et craie** pour volumes, végétation, lumière et petites touches de couleur.
- Titres et intertitres rouge-brun.
- Armoiries en bleu profond, rouge et or distincts.
- Ciel bleu gris ou bleu de Savoie pâle, jamais cyan vif.
- Végétation olive, sauge, mousse et brun-vert.
- Pierre en ocre clair, beige, gris chaud et terre d'ombre.
- Saturation douce à modérée, aucune couleur néon ou effet numérique brillant.

La colorisation doit améliorer la lecture de l'image **sans concurrencer le texte**. Le texte reste sombre, net et très contrasté sur fond clair.

## 5. Règle Château de Notre-Dame-du-Cruet, page 10

La dernière version colorisée validée devient la référence d'orientation du château.

- Conserver l'orientation inspirée de la vue depuis le Couvent des Cordeliers.
- Ne pas revenir à l'orientation antérieure erronée.
- Respecter le plan réel fourni et ses formes : tour de guet, tour-porte, porte d'entrée, tour ronde, tour carrée, basse cour, cour haute, logis, donjon, fossé.
- La mention **« Vous êtes ici » est interdite** sur le plan.
- Toute nouvelle vue en perspective doit rester compatible avec la géométrie de ce plan.

## 6. Politique QR

`qr_registry.yaml` est l'unique source de vérité.

1. Le payload est copié exactement depuis le registre.
2. Le QR est conservé en PNG noir sur fond blanc/ivoire très clair.
3. Il est réinjecté **après** toute colorisation ou traitement graphique.
4. La CI décode chaque actif QR et compare le résultat caractère pour caractère avec le registre.
5. Les PDF sont construits avec ces actifs QR déterministes, indépendamment d'un éventuel QR visible dans l'illustration raster.

## 7. Construction des PDF

La production est reproductible :

```bash
python -m pip install -r requirements-build.txt
make validate
make build
```

`make build` appelle `scripts/build_pdfs.py` et produit dans `dist/` :

- le PDF séquentiel 15 pages ;
- le livret A5 16 pages ;
- l'imposition A4 recto-verso ;
- les panneaux A2 15 pages ;
- les panneaux A1 15 pages ;
- un ZIP d'impression ;
- `SHA256SUMS.txt` et `build-report.json`.

Les formats A2/A1 agrandissent les sources raster mais n'inventent aucun détail. Le rapport de construction indique la résolution effective.

## 8. Validation avant publication

Avant de publier :

1. valider le manifest et les 15 pages ;
2. valider les données éditoriales interdites dans `corrections.yaml` ;
3. valider tous les actifs QR ;
4. construire les PDF ;
5. vérifier l'ordre des pages ;
6. conserver les checksums ;
7. sur un tag `v*`, laisser la CI créer la Release GitHub et y joindre les PDF, le ZIP, le rapport et les sommes SHA-256.

La règle est simple : **on peut enrichir la couleur, jamais le contenu**.
