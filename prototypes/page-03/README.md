# Prototype v3 multicouche — page 03

## But
Valider la nouvelle méthode de production avant de l'étendre aux 16 pages.

La page 03, **Le Couvent des Cordeliers**, est utilisée comme page témoin car elle combine narration longue, illustrations documentaires, cartographie/localisation, informations pratiques et QR fonctionnel, sans être soumise au verrou éditorial de la page 04.

## Principe
La référence `assets/page-03.jpg` n'est pas redessinée. Elle est analysée comme un assemblage de matières graphiques validées.

Pipeline cible :

`fond -> fragments raster -> vecteurs utiles -> texte canonique -> QR déterministe`

Le texte est repris exclusivement depuis `pages/03.yaml:canonical_text`. Le QR est repris exclusivement depuis `qr_registry.yaml` via `assets/qr-svg/page-03-google-maps.svg`.

## Ce prototype doit démontrer

1. qu'on peut extraire les illustrations utiles sans refaire artistiquement la page ;
2. qu'on peut reconstruire un fond SpiritualCept propre derrière ces fragments ;
3. que tout le rédactionnel peut redevenir une vraie couche texte ;
4. que le QR reste un objet indépendant et décodable ;
5. que le résultat reste visuellement fidèle à la page canonique ;
6. que les fragments raster gardent une résolution suffisante pour l'impression cible.

## Depuis le 2026-09-09
Le prototype est porté dans le compositeur générique : `composition.yaml` (géométrie, fragments,
styles, blocs, QR, validations) est la définition de référence de la page, exécutée par
`scripts/layered_compose.py 3`. `fragments.lock.yaml` verrouille les SHA des fragments et
`page-03.objects.yaml` est dérivé par `scripts/layered_inventory.py`. Les scripts
`scripts/prototype_page03_*.py` et `fragment-boxes.yaml` restent comme témoins du run `34259978419`.
Deux corrections de revue sont intégrées : le fragment du moine ne contient plus de résidu du titre
et sa légende « Spiritualité franciscaine » est un fragment mesuré séparément ; le titre
« VISITE DU SITE » est composé à sa position canonique sans recouvrir le croquis.

## Fichiers

- `layers.yaml` : contrat de couches et registre du prototype ;
- `assets/page-03.jpg` : référence visuelle canonique, inchangée ;
- `pages/03.yaml` : autorité éditoriale ;
- `assets/qr-svg/page-03-google-maps.svg` : QR fonctionnel ;
- `assets/svg/spiritualcept-ornaments.svg` : vecteurs génériques déjà validés.

Les futurs fragments seront placés sous `prototypes/page-03/fragments/` et devront être enregistrés avec leur bounding box source et leur SHA-256.

## Important
Les bounding boxes des illustrations ne sont **pas inventées dans ce commit**. Elles doivent être mesurées sur le raster canonique avant extraction. Tant que cette mesure n'a pas été exécutée, les fragments restent `BBOX_TO_MEASURE`.

Aucun fichier canonique n'est modifié par ce prototype.

## Gate de sortie
Le prototype n'est validé que lorsque :

- les fragments sont mesurés et extraits ;
- leur provenance est enregistrée ;
- le texte du PDF correspond exactement au YAML canonique ;
- le QR du PDF est décodé machine avec le payload exact ;
- la résolution effective des rasters est mesurée ;
- une comparaison visuelle avec `assets/page-03.jpg` est effectuée ;
- le résultat est jugé suffisamment fidèle pour industrialiser la méthode.
