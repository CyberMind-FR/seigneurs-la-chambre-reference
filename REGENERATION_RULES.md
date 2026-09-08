# RÈGLE DE RÉGÉNÉRATION STRICTE — Les Seigneurs de La Chambre

Ce fichier fait partie de la source de vérité du projet.

## Principe absolu
Une page déjà validée visuellement n'est jamais recréée librement pour une correction ponctuelle.
Elle reste la référence canonique de contrôle. Pour la migration v3, elle peut aussi servir de **gisement de fragments visuels validés** : les zones utiles sont découpées, nettoyées localement et recomposées sur une trame de fond contrôlée, puis le texte canonique est composé séparément en couche texte.

La stratégie v3 n'est donc plus de redessiner systématiquement les illustrations. Elle privilégie la **décomposition déterministe de la page canonique en couches** et la réutilisation de ses fragments réels.

## Architecture de composition v3 — méthode prioritaire
Une page v3 doit être pensée comme une pile de couches indépendantes :

1. `background` : trame papier/fond SpiritualCept reproductible ;
2. `raster_fragments` : illustrations, photos, gravures, cartes ou éléments visuels découpés depuis les références canoniques lorsque leur réutilisation est licite et techniquement propre ;
3. `documentary_vectors` : QR, filets, ornements, plans ou autres éléments vectoriels réellement justifiés ;
4. `text_layer` : titres, paragraphes, légendes et mentions provenant exclusivement de `pages/NN.yaml:canonical_text` ;
5. `functional_overlay` : QR et éléments fonctionnels déterministes, injectés en dernier.

Le raster canonique complet reste une **référence de comparaison**, pas le support final aplati de la v3.

## Politique d'extraction des fragments
L'extraction d'un fragment depuis `assets/page-NN.jpg` est autorisée lorsqu'elle permet de conserver fidèlement un visuel déjà validé.

Chaque fragment doit :
- référencer la page et la zone source ;
- conserver sa provenance dans `sources/PROVENANCE_INDEX.yaml` / `assets/ASSET_INDEX_V3.yaml` ;
- recevoir un SHA-256 une fois produit ;
- être sans texte éditorial lorsque le texte peut être recomposé dans `text_layer` ;
- être nettoyé uniquement de façon locale et déterministe ;
- ne pas être complété par des détails inventés ;
- conserver le cadrage utile ou documenter explicitement son recadrage.

Le détourage, le masquage de l'ancien texte, la restauration locale du fond autour d'un fragment et la correction colorimétrique non destructive sont autorisés. Une génération libre de remplacement n'est pas la méthode par défaut.

## Politique de trame de fond
Le fond de page devient un actif indépendant et reproductible.
Il doit respecter `style.yaml` et le langage SpiritualCept : papier blanc/ivoire très clair, grain discret, contraste d'impression élevé, aucune information documentaire encodée dans la texture.

Une même trame peut être réutilisée sur plusieurs pages. Les variations doivent être déterministes et documentées, jamais utilisées pour masquer une dérive de contenu.

## Politique de couche texte
Tout texte éditorial v3 est composé comme texte réel, sélectionnable et vectoriel dans le PDF final lorsque le moteur de composition le permet.

Source unique : `pages/NN.yaml:canonical_text` et corrections explicitement validées.

Interdictions :
- OCR utilisé comme autorité éditoriale ;
- texte rasterisé volontairement lorsqu'une couche texte est possible ;
- texte généré dans une illustration ;
- réécriture automatique du canon ;
- récupération d'un texte visuellement présent dans l'ancien JPEG pour contourner le YAML canonique.

## Politique SVG révisée
Le SVG est un outil, pas un objectif.

Produire un SVG uniquement lorsqu'il apporte une valeur réelle :
- QR déterministe ;
- ornement réutilisable ;
- forme géométrique simple ;
- héraldique correctement spécifiée ;
- plan/document dont la vectorisation est justifiée et autorisée.

Ne pas reconstruire en SVG une illustration raster validée simplement pour obtenir du vectoriel. Si le fragment canonique est de qualité suffisante pour la taille d'impression cible, le fragment raster est préféré à une reconstruction spéculative.

## Reconstitutions
Les reconstitutions restent autorisées, mais deviennent une voie **secondaire** par rapport à l'extraction d'un visuel canonique existant.

Une reconstitution est utilisée lorsque :
- aucun fragment canonique exploitable n'existe ; ou
- une nouvelle vue est explicitement demandée ; ou
- le projet souhaite clairement présenter une restitution hypothétique.

Elle doit rester sourcée, sans texte, avec niveau de confiance et limites d'interprétation déclarés. Mention par défaut lorsqu'une ambiguïté est possible :

> **Reconstitution graphique à partir des sources documentées.**

## Interdictions permanentes
- Ne jamais inventer de personne, nom, fonction, catégorie de membre, citation, date, lieu, source, prix, taux ou contenu.
- Ne jamais ajouter un élément éditorial absent du canon.
- Ne jamais changer silencieusement la composition validée.
- Ne jamais remplacer automatiquement un fragment canonique exploitable par une création générative.
- Ne jamais extrapoler un fait historique à partir d'une autre page.
- Ne jamais générer ou styliser un QR avec un modèle d'image.
- Ne jamais intégrer de texte généré dans un actif graphique v3.

## Ordre des sources
1. `corrections.yaml`
2. `pages/NN.yaml` / `canonical_text`
3. `sources/PROVENANCE_INDEX.yaml`
4. `assets/ASSET_INDEX_V3.yaml`
5. `assets/page-NN.jpg` comme référence visuelle et source potentielle de fragments
6. aucune autre source sans validation explicite

## Corrections ponctuelles des pages historiques
Pour une correction sur le raster historique :
1. partir du fichier visuel validé ;
2. identifier précisément la zone impactée ;
3. modifier uniquement cette zone ;
4. préserver tous les autres pixels autant que techniquement possible ;
5. vérifier le texte contre le canon ;
6. recalculer le SHA-256 ;
7. mettre à jour les métadonnées ;
8. vérifier visuellement.

Cette procédure concerne la maintenance des références historiques. Elle ne doit pas être confondue avec la nouvelle composition multicouche v3.

## Verrous canoniques
### Page 4
Toute recomposition v3 reste bloquée par `PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` tant que l'arbitrage éditorial n'est pas levé.

### Page 10
`assets/reference/page-10-plan-reel.jpg` reste l'autorité géométrique pour toute nouvelle reconstitution. En revanche, la v3 doit préférer l'extraction/réutilisation d'une illustration canonique validée lorsqu'elle existe et convient au format, plutôt qu'une nouvelle volumétrie spéculative.

### Page 13
Les QR restent alignés et déterministes ; les payloads proviennent exclusivement de `qr_registry.yaml` et sont injectés en dernier.

### Page 14
L'ancien portrait de Philippe DEMARIO reste supprimé. Aucun fragment de ce portrait ne doit être extrait ou réintroduit.

## Validation obligatoire v3
Pour chaque page recomposée :
- provenance de chaque fragment résolue ;
- SHA des actifs produits enregistré ;
- texte comparé au canon ;
- aucun texte résiduel parasite dans les fragments graphiques ;
- QR final redécodé ;
- comparaison visuelle avec la page canonique ;
- contrôle de la taille/résolution effective des rasters à l'impression ;
- contrôle des droits lorsqu'un actif documentaire direct l'exige.

Commandes minimales :
- `make sync`
- `make validate`

Après composition imprimable :
- `make build`
- validation du PDF final et de sa couche texte.

## Style verrouillé
Le langage graphique SpiritualCept reste un carnet de recherches historique / sketchbook documentaire : papier blanc neutre imprimable, encre brun-noir / sépia, gravure et graphite, titres rouge-brun, accents bleu/or héraldiques, ornements fins et forte lisibilité d'impression.

Le style est porté par la trame, la typographie, les ornements et le traitement contrôlé des fragments. Il ne justifie jamais l'invention de contenu.