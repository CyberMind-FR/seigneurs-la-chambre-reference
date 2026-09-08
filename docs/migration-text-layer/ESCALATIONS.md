# Escalations avant phase 2

| priorité | décision refusée | preuve | question à poser |
|---|---|---|---|
| bloquante | version historique de la page 4 | `pages/04.yaml` et OCR/inspection de `assets/page-04.jpg` décrivent deux récits incompatibles | « Quelle version, accompagnée de quelles sources validées, devient le canon de la Maison de La Tour ? » |
| bloquante | profil et standard imprimeur | aucun profil ICC de production, cahier prépresse ou OutputCondition n'est versionné | « Quel PDF/X, quel profil ICC nommé, quel fond perdu, quels traits et quelle limite d'encrage l'imprimeur exige-t-il ? » |
| bloquante A1/A2 | iconographie HD | 0 illustration/photo séparée ; rasters à 30,9–63,8 ppi aux formats panneau | « L'association fournit-elle les originaux HD, finance-t-elle une refonte, ou autorise-t-elle le retrait temporaire d'A1/A2 ? » |
| bloquante droits | provenance/licences | manifeste sans provenance, licence ni droits ; seule source distincte page 10 également non documentée | « Qui détient chaque source et quels droits de reproduction/redistribution sont accordés ? » |
| validation design | fontes | 0 fonte et 0 licence dans le dépôt | « Quelle famille visuelle est validée, sous licence autorisant redistribution et embedding ? » |
| validation design | grille et marges | valeurs de phase 1 proposées, non issues d'un fichier canonique | « La Commission valide-t-elle le gabarit A5 proposé après examen du prototype page 11 ? » |
| architecture éditoriale | variables globales | valeurs répétées dans des `canonical_text` verrouillés | « Autorisez-vous une future factorisation vers `data/facts.yaml` sous contrôle d'identité du texte rendu ? » |
| canon technique | ratios | `format_lock` impose les proportions source, tandis que `build-config.yaml` vise A5/A2/A1 ISO | « Le verrou porte-t-il sur les anciens rasters seulement ou sur la géométrie des nouvelles pages composées ? » |
| hygiène git | artefacts suivis | `make validate` échoue ; 21 PDF et 4 planches suivis, environ 490 MiB de PDF | « Autorisez-vous une PR séparée de nettoyage, sans réécriture d'historique ? » |
| validation de sortie | preflight PDF/X | aucun validateur PDF/X certifiant disponible dans l'environnement | « Quel outil de preflight et quel rapport l'imprimeur accepte-t-il comme preuve ? » |

## Point d'arrêt

Aucune phase 2 ne commence sans :

1. validation de l'ADR WeasyPrint ;
2. choix d'une fonte licenciée ou autorisation d'un choix de prototype explicitement non final ;
3. sélection d'une voie A, B ou C pour les actifs de la page 11 ;
4. confirmation du format du prototype et du fond perdu ;
5. maintien explicite de la page 4 hors périmètre.
