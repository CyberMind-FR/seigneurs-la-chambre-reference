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

### Compositeur générique et traitements admis (2026-09-09)
La composition v3 est exécutée par `scripts/layered_compose.py` à partir de
`prototypes/page-NN/composition.yaml` : une page se reconstruit sans toucher au code métier.
Traitements de fragment admis, tous déclarés dans le YAML et journalisés dans `fragments.json` :
- `crop_only` : découpe rectangulaire ;
- `crop_grow_to_clean_edge` : élargissement borné (`max_grow_px`) d'un bord qui coupe un trait ;
- `mask_px` : masquage local d'un résidu de texte raster ou d'un objet voisin inclus dans le crop
  (jamais pour effacer un détail documentaire). Remplissage : couleur du papier mesurée (défaut),
  couleur médiane de l'anneau de bordure du masque (`mask_fill: border_median`, texte d'un cartouche
  coloré recomposé en texte vivant) ou couleur hexadécimale déclarée.
Texte vivant : césure uniquement aux traits d'union présents dans le canon, jamais de coupure
arbitraire ; taille ajustée en hauteur et en largeur dans la boîte déclarée ; fontes TrueType
déclarées dans `prototypes/_shared/text-styles.yaml` lorsque Times base-14 n'a pas le glyphe.
Contrôles bloquants : couche texte exacte, QR décodé, SHA source et fragments, texte dans une zone
QR, **collision d'encre entre texte vivant et fragment**. Contrôles signalés : bord de crop
traversant de l'encre, débordement de bloc, gate de résolution.

### Gates de résolution (décision du 2026-09-09)
Mesurés à la **taille de placement finale**, identiques pour tous les formats de sortie (A5, A2, A1) :
- **300 ppi** pour les rasters en demi-teintes (illustrations, cartes, photos, lavis) ;
- **1200 ppi** pour les rasters au trait (icônes, ornements, croix, marques bitonales).
Le texte et les QR sont vectoriels (couche texte réelle, SVG déterministes) et ne relèvent pas de ces
gates. Chaque fragment déclare (ou hérite de son rôle) `raster_kind: continuous_tone | line_art`.
Ces gates remplacent les seuils 300 A5 / 180 A2 / 150 A1 de `assets/ASSET_SPEC.md` §2 (document
validé en Phase A : sa modification exige une nouvelle validation humaine, il n'est donc pas réécrit ici).
Un raster sous le gate n'est jamais « récupéré » par upscale : source HD, réduction de placement,
validation explicite d'un seuil inférieur, ou vectorisation sans dérive.

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

## Phase B — lot 2 : sources, provenances et premiers SVG documentaires
Le lot 2 formalise l'inventaire documentaire et le déblocage contrôlé des premiers actifs vectoriels non textuels.

Les registres opérationnels sont :
- `sources/PROVENANCE_INDEX.yaml` pour la provenance, les droits, les niveaux de confiance et les limites d'usage ;
- `assets/ASSET_INDEX_V3.yaml` pour l'état des actifs atomiques produits, candidats ou bloqués ;
- `manifest-v3.yaml` pour les actifs effectivement produits et enregistrés dans le pipeline v3.

Tout nouvel actif documentaire ou reconstruit doit renseigner au minimum :
- `id` ;
- `type` ou `class` / `kind` ;
- `status` ;
- `source_refs` ;
- `source_kind` lorsque pertinent ;
- `rights_status` ou la section `rights` ;
- `confidence` lorsque l'actif comporte une interprétation ;
- `text_free_required` ;
- `must_be_labeled_reconstruction` lorsqu'il s'agit d'une restitution ;
- `sha256` dès que le fichier existe ;
- l'état des validations et les éventuels blocages.

Le fait qu'une source soit présente dans le dépôt ne vaut jamais, à lui seul, autorisation de reproduction directe. Une reproduction documentaire directe exige que les droits soient explicitement établis. En revanche, une reconstitution non fac-similé peut être autorisée lorsqu'elle est fondée sur des `source_refs` identifiés, que son niveau de confiance est déclaré et qu'elle ne copie pas directement une source dont les droits restent inconnus.

### Matrice de déblocage active
À la date de ce lot :
- les 16 QR SVG uniques sont produits et fonctionnels ;
- `assets/svg/spiritualcept-ornaments.svg` est produit et validé pour son usage ornemental non textuel ;
- `assets/svg/heraldry-la-chambre.svg` est produit mais reste en attente de revue héraldique avant promotion ;
- `assets/svg/page-10-castle-reconstruction.svg` est produit mais reste en attente de revue géométrique avant promotion ;
- le tracé documentaire direct du plan réel de la page 10 reste bloqué tant que les droits de reproduction du plan source ne sont pas documentés ;
- le SVG du logo de l'association reste bloqué tant que l'actif source validé n'est pas committé ou référencé par un chemin canonique du dépôt.

Ce lot n'autorise pas, à lui seul, la recomposition complète d'une page ni la promotion automatique d'un actif encore marqué `pending`, `blocked` ou équivalent.

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