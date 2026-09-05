# Colorisation verrouillée - v7

- Les 15 fichiers `assets/page-01.jpg` à `assets/page-15.jpg` constituent la source graphique de release.
- Ordre canonique fixé dans `build-config.yaml`.
- Page 01 : nouvelle couverture colorisée validée.
- Page 10 : utiliser exclusivement l'image du Château de Notre-Dame-du-Cruet validée dans ce paquet.
- Aucune ancienne planche sépia ne doit réapparaître.
- Les QR sont des actifs déterministes ; ils sont superposés aux rasters et aux PDF après tout traitement graphique.
- Le CI valide les 15 hashes, les QR et construit les PDF à partir des assets du commit/tag.
