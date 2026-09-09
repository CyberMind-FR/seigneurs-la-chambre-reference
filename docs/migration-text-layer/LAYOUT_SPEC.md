# Phase 1 — spécification de composition proposée

Statut : **proposition non appliquée**. Les valeurs marquées « à valider » ne deviennent pas canoniques avant accord humain.

## Formats et frontière de sortie

| sortie | boîte finie | rôle | état proposé |
|---|---:|---|---|
| livret séquentiel | A5, 148×210 mm | maître de lecture | activable après prototype validé |
| livret imposé | A4 paysage, 2 pages A5 | impression recto-verso | dérivé du maître, jamais une seconde composition |
| panneau A2 | 420×594 mm | exposition | bloqué tant que chaque actif placé n'atteint pas 300 ppi |
| panneau A1 | 594×841 mm | exposition | bloqué tant que chaque actif placé n'atteint pas 300 ppi |

Fond perdu proposé : 3 mm par bord. Traits de coupe : en dehors du `BleedBox`. Cette valeur doit être remplacée par la spécification de l'imprimeur avant production.

Les sorties panneau utilisent un gabarit responsive dédié. Elles ne sont ni un agrandissement du PDF A5, ni un upscaling des rasters. Aucun format promis n'est supprimé dans cette phase ; A1/A2 restent des sorties bloquées, soumises à arbitrage.

## Grille A5 proposée pour le prototype

| paramètre | valeur proposée | statut |
|---|---:|---|
| marge intérieure | 12 mm | à valider |
| marge extérieure | 10 mm | à valider |
| marge haute | 10 mm | à valider |
| marge basse | 12 mm | à valider |
| colonnes | 6 | à valider |
| gouttière | 3 mm | à valider |
| grille verticale | pas de 4 mm | à valider |
| fond | blanc neutre | imposé par `style.yaml` et `corrections.yaml` |

Les dimensions sont des hypothèses de prototype. Elles n'autorisent ni recadrage ni padding des anciennes pages. La contradiction entre `style.yaml/format_lock` (« proportions de la page source ») et les formats ISO déjà demandés par `build-config.yaml` doit être arbitrée avant phase 3.

## Jetons de style

Les noms sont fixés ; leurs valeurs numériques seront mesurées sur les références validées puis validées au prototype.

```text
paper.white
ink.primary
ink.secondary
accent.title_red_brown
heraldry.blue
heraldry.gold
rule.thin
rule.strong
space.baseline
type.display
type.subtitle
type.body
type.caption
type.micro
```

Aucune couleur hexadécimale du banc d'essai n'est une valeur canonique. Les fontes DejaVu du banc ne sont pas retenues comme fontes de production.

## Gabarits par type

| type | structure autorisée | pages actuelles |
|---|---|---|
| `cover` | identité, titre, sous-titre, illustration dominante, métadonnées du livret | 1 |
| `history` | identité, titre, récit en colonnes, chronologie, carte/illustrations | 2 |
| `site` | armoiries si présentes, titre/sous-titre, récit, illustration dominante, détails, bandeau bas carte/localisation/QR | 3–12, **4 exclue** |
| `synthesis` | titre, carte patrimoniale, repères, ressources et ligne de QR | 13 |
| `association` | titre, mission, actions, ouvrages et crédits | 14 |
| `back_cover` | synthèse des sites, association, mentions/prix/taux issus du canon | 15 |
| `page_finale` | remerciement, identité associative, paysage/document, QR | 16 |

Chaque gabarit ne peut afficher que des segments de `canonical_text`, des QR référencés au registre et des actifs manifestés. Une légende absente du canon n'est pas générée.

## Règles d'actifs

| contenu | format source | règle de build |
|---|---|---|
| texte, légendes, coordonnées | YAML/Markdown | toujours composé, jamais raster |
| blasons, filets, fleurons, cartes, plans, rose des vents, chronologies | SVG | conserver les formes en vecteur |
| QR | SVG généré au build | payload registre exact, noir 100 %, fond blanc, bord ≥ 4 modules |
| trait fin, gravure, lavis, dessin documentaire | PNG ou TIFF lossless | profil déclaré, aucune chaîne JPEG |
| photographie | JPEG source original + dérivé de build | une seule conversion/encodage, qualité élevée, 4:4:4 |

Pour tout raster placé :

```text
ppi_x = largeur_pixels / largeur_placée_en_pouces
ppi_y = hauteur_pixels / hauteur_placée_en_pouces
ppi_effectif = min(ppi_x, ppi_y)
```

Le build échoue si `ppi_effectif < 300` pour la sortie. L'interpolation, l'upscaling et le padding ne changent pas cette mesure source.

## Fontes

Avant ajout d'une fonte : fichier versionné, SHA256, nom/version, auteur, licence, URL de licence, droit de redistribution et droit d'embarquement PDF. `pdffonts` doit indiquer `emb=yes` et `uni=yes` pour chaque fonte utilisée. Le choix de famille reste à valider visuellement et juridiquement.

## Contrôles de sortie obligatoires

1. Le nombre de pages et l'ordre correspondent à la configuration.
2. `pdftotext` extrait page par page le canon exact après une seule normalisation autorisée : retrait de `U+00AD` avec le blanc de rupture, puis compactage des blancs. Aucun retrait d'accent, changement de casse ou tolérance de ponctuation.
3. Chaque QR est rendu depuis le PDF à résolution suffisante, redécodé et comparé caractère par caractère au registre.
4. Chaque image placée est identifiée dans le PDF et son ppi effectif est calculé depuis sa matrice de placement.
5. Toutes les fontes sont embarquées et disposent d'une table Unicode.
6. `TrimBox`, `BleedBox`, `MediaBox`, traits de coupe, OutputIntent et profil ICC correspondent au contrat imprimeur.
7. Deux sorties fonctionnellement identiques sont refusées.
8. `dist/`, PDF et exports restent non suivis par git.

## Politique de page 4

Le moteur produit une erreur contrôlée `PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` s'il lui est demandé de recomposer la page 4. Aucun gabarit, fallback raster ou priorité automatique ne contourne ce verrou.
