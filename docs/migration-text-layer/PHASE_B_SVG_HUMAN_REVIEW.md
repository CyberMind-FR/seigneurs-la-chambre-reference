# Phase B — revue des gates SVG non-QR

Date : 2026-09-08
Branche de revue : `review/phase-b-svg-gates`
Base : `release/v3.0-phase-b`

Cette revue ne modifie aucune page canonique. Elle examine uniquement si les trois premiers SVG non-QR peuvent être promus en usage final au regard du canon et des sources déjà enregistrées.

## 1. `heraldry_la_chambre_svg`

**Décision : À CORRIGER — ne pas promouvoir.**

Le blasonnement canonique de `pages/02.yaml` est : « D'azur, semé de fleurs de lis d'or, à la bande de gueules brochant sur le tout ».

Le SVG respecte les trois éléments sémantiques fondamentaux : champ d'azur, fleurs de lis d'or, bande de gueules brochant sur le champ. La bande suit une diagonale compatible avec une bande héraldique.

Cependant, le rendu actuel dispose un nombre fini de fleurs de lis entièrement contenues dans l'écu. Il ne rend pas sans ambiguïté le caractère **semé**, qui doit visuellement se lire comme un motif indéfini se poursuivant au-delà des limites du champ, avec des meubles coupés par les bords de l'écu. Le gate héraldique n'est donc pas levé.

Correction autorisée : conserver l'écu, les émaux et la bande ; remplacer uniquement la distribution des fleurs de lis par un semé régulier dont certaines fleurs sont coupées par le contour. Aucun texte, cimier, couronne, support ou ornement héraldique supplémentaire ne doit être ajouté.

## 2. `page_10_castle_reconstruction_svg`

**Décision : À CORRIGER — ne pas promouvoir.**

La source géométrique autorisée est `assets/reference/page-10-plan-reel.jpg`, conformément à `pages/10.yaml`. Le canon documente notamment tour de guet, basse cour, porte d'entrée, tour porte, tour ronde, tour carrée, cour haute, logis, donjon et fossé.

Le SVG actuel est une volumétrie perspective libre. Il contient notamment des élévations, ouvertures/fenêtres et formes de toiture qui ne sont pas établies par le plan source enregistré. Ces détails excèdent le niveau de confiance déclaré pour la volumétrie et le détail décoratif. La correspondance géométrique exacte avec le plan réel ne peut donc pas être certifiée à partir de cet actif.

Correction autorisée : repartir de la géométrie du plan réel et produire une reconstitution vectorielle non fac-similé, sans texte, limitée aux emprises et relations spatiales soutenues par le plan. Les élévations, fenêtres, toitures et détails non sourcés doivent être supprimés ou rendus explicitement non affirmatifs. La mention de reconstitution reste obligatoire lors de l'intégration éditoriale.

## 3. `ornament_bundle_svg`

**Décision : VALIDÉ.**

L'actif est non documentaire, sans texte et n'encode aucune affirmation historique. Son statut `PRODUCED_VALIDATED` et `release_ready: true` peut être conservé.

## Décision de lot

- `heraldry_la_chambre_svg` : gate héraldique **FAIL**, correction ciblée requise.
- `page_10_castle_reconstruction_svg` : gate géométrique **FAIL**, correction ciblée requise.
- `ornament_bundle_svg` : **PASS**, utilisable.

Aucune promotion artificielle n'est autorisée pour faire passer les gates. Les deux actifs à corriger restent des reconstitutions et doivent être révisés sans toucher aux rasters canoniques.
