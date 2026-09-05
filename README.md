# Les Seigneurs de La Chambre - package 100 % colorise v4

Ce paquet corrige le melange constate dans la release v2.0.1.

## Correction
- pages 01 a 09 : versions illustrees/colorisees recuperees depuis la serie generee precedemment ;
- pages 10 a 15 : dernieres versions colorisees validees ;
- QR pages 03 a 09 : reposes depuis les assets QR deterministes du referentiel ;
- aucune page sepia ancienne ne doit etre reutilisee par le build.

## A copier dans le depot
Remplacer le repertoire `assets/` et `manifest.yaml` par ceux de cette archive.
La CI existante reconstruira ensuite tous les PDF depuis ces 15 assets.
