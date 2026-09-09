# Prompts HD — style commun et mode d'emploi

> Fichier généré par `scripts/hd_prompt_pack.py` depuis `assets/hd/briefs.yaml` et les
> `prototypes/page-NN/composition.yaml` (grilles inchangées). Ne pas éditer à la main :
> modifier les briefs puis `make hd-prompts`.

91 illustrations régénérables par prompt sur les pages 01, 02, 03, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16.

## Style commun

Illustration à l'encre et à l'aquarelle, style carnet de voyage / gravure aquarellée : traits d'encre fins brun sépia, lavis d'aquarelle doux et lumineux, palette chaude et naturelle (ocre, beige parchemin, gris pierre, vert olive et vert mousse, bleus pâles pour les ciels et les sommets enneigés), fond de papier crème uni (#FFFDF7) sans texture marquée, lumière diffuse, pas de contours noirs épais, pas de rendu photographique ni 3D.

**Exclusions :** Aucun texte, lettre, chiffre, signature, filigrane, logo, flèche, cartouche, cadre, bordure ornementale, bulle ou étiquette. Aucun personnage ou objet moderne (véhicule, câble, panneau) sauf indication contraire. Pas de texture de papier vieilli ni de taches. Pas de bordure ni de vignettage : le dessin s'estompe naturellement dans le papier crème.

**Mention à porter dans le livret (formulation à valider) :** Vue artistique reconstituée : les proportions, l'échelle et l'état des bâtiments ne sont pas nécessairement fidèles (absence d'archive d'époque ; certains sites sont aujourd'hui en ruine).

## Mode d'emploi (ChatGPT, génération d'images)

1. `make hd-pack` produit `dist/hd-pack/` : ce fichier, un `page-NN.md` par page et les crops de
   référence bruts `reference/page-NN/<fragment>.png` (découpés dans la page canonique, sans upscale).
2. Pour chaque fragment : joindre le crop de référence, coller le prompt tel quel, demander la plus
   grande taille disponible. Ne jamais accepter une image comportant du texte.
3. Enregistrer le résultat sous le nom attendu (`assets/hd/page-NN/<fragment>.png`, PNG, sRGB).
4. `make hd-ingest` inscrit chaque fichier dans `prototypes/page-NN/hd-sources.yaml`
   (statut `PENDING_REVIEW`, SHA-256, taille, identifiant et SHA du prompt).
5. Revue humaine : comparer au crop de référence (même sujet, même cadrage, aucun texte, aucun
   ajout), renseigner `rights`, `approved_by`, `approved_on`, passer le statut à `APPROVED`.
   Pour les fragments `*_captioned`, renseigner d'abord `caption_resolution` (légende inscrite au
   canon ou abandon éditorial motivé) : la légende raster disparaît avec le fragment.
6. `make layered-compose` (le compositeur remplace le crop canonique par la source HD, recadrée au
   centre au ratio exact, jamais agrandie), puis `make validate`, `make build-v3`.

## Tailles et couverture des gates

Les gates sont 300 ppi (demi-teintes) et 1200 ppi (trait) à la taille de placement finale de
chaque format. Les tailles natives connues de ChatGPT plafonnent à 1536 px de grand côté : la
colonne « couverture » de chaque prompt indique les formats atteints sans agrandissement ; un
format non couvert reste sous gate et sera rapporté tel quel (aucun upscale d'une source HD).
