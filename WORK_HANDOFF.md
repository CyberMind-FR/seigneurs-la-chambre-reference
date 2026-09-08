# WORK HANDOFF — Les Seigneurs de La Chambre

## Mission
Migrer le livret/exposition vers une composition reproductible à couche texte sans dérive éditoriale ni visuelle. Le dépôt GitHub est l’unique source de vérité.

## Décision méthodologique active
La méthode prioritaire de la v3 est désormais la **composition multicouche à partir des pages canoniques décomposées**.

On ne cherche plus à redessiner systématiquement les illustrations en SVG. On repart des 16 pages validées, on en extrait les morceaux visuels utiles, on crée une trame de fond indépendante, puis on recompose :

1. fond/trame papier ;
2. fragments raster documentaires et illustrations validées ;
3. vecteurs réellement utiles ;
4. texte canonique en couche texte ;
5. QR et éléments fonctionnels en overlay final.

Les `assets/page-NN.jpg` restent les références de comparaison et deviennent aussi, lorsque les droits et la qualité le permettent, une source de fragments graphiques. Ils ne sont pas destinés à rester les pages finales aplaties de la v3.

## Ordre de lecture obligatoire
1. `REGENERATION_RULES.md`
2. `corrections.yaml`
3. `manifest.yaml`, `manifest-pages.json`, `manifest-v3.yaml`
4. `sources/PROVENANCE_INDEX.yaml`
5. `assets/ASSET_INDEX_V3.yaml`
6. `assets/ASSET_SPEC.md`
7. `pages/NN.yaml`
8. `qr_registry.yaml`
9. `assets/page-NN.jpg`
10. `docs/migration-text-layer/PHASE_A_APPROVAL.md`

## Canon actuel
- 16 pages, `assets/page-01.jpg` à `assets/page-16.jpg`.
- Page 10 = Château de Notre-Dame-du-Cruet, version réorientée validée, QR Google Maps déterministe.
- Page 13 = six QR de ressources numériques alignés.
- Page 14 = portrait de Philippe DEMARIO supprimé, nom et bibliographie conservés.
- Page 16 = QR association enregistré.
- Fondation du Patrimoine = 66 %, jamais 75 %.
- Page 4 = aucune mention « Académie de Maurienne ».
- Auteurs = `Fabrice GALOPO, André GRANGE, Gérald KERMA`.

## Phase B — lot 2 : état opérationnel
Le lot 2 porte sur l'inventaire des sources/provenances et sur le déblocage contrôlé des premiers actifs SVG non textuels.

Les deux registres opérationnels sont maintenant :
- `sources/PROVENANCE_INDEX.yaml` : provenance, droits, confiance et limites d'usage ;
- `assets/ASSET_INDEX_V3.yaml` : actifs atomiques produits, candidats, validés ou bloqués.

`manifest-v3.yaml` reste le registre incrémental des actifs réellement produits dans le pipeline v3.

État actuel du front SVG :
- 16 QR SVG uniques : produits, validés et fonctionnels ;
- `assets/svg/spiritualcept-ornaments.svg` : produit et validé pour un usage ornemental non textuel ;
- `assets/svg/heraldry-la-chambre.svg` : produit, mais revue héraldique encore nécessaire avant promotion ;
- `assets/svg/page-10-castle-reconstruction.svg` : produit, mais revue géométrique encore nécessaire avant promotion ;
- `page_10_plan_documentary_trace_svg` : bloqué pour reproduction documentaire directe tant que les droits du plan source ne sont pas établis ;
- `association_logo_svg` : bloqué tant que l'actif source validé n'est pas committé ou référencé par un chemin canonique du dépôt.

Le fait qu'une source soit présente dans le dépôt ne vaut pas autorisation de reproduction directe. Les reconstitutions non fac-similé restent autorisées lorsqu'elles sont sourcées, traçables, sans texte généré, avec confiance et limites d'interprétation déclarées.

Le prototype déterministe de décomposition/recomposition engagé sur la page 03 sert de banc d'essai technique. Il ne lève aucun verrou éditorial et ne transforme aucune page recomposée en nouveau canon sans validation humaine explicite.

## Pipeline cible par page
Pour chaque page NN :

### A. Cartographier
- lire `pages/NN.yaml` et `assets/ASSET_SPEC.md` ;
- identifier les zones texte, illustrations, documents, ornements, QR et espaces de fond ;
- comparer avec `assets/page-NN.jpg`.

### B. Extraire
Créer des fragments indépendants uniquement pour les zones utiles :
- illustrations ;
- photos ;
- gravures ;
- cartes/plans lorsque leur réutilisation est autorisée ;
- éléments graphiques particuliers.

Les fragments doivent être nettoyés du texte éditorial qui sera recomposé séparément. Aucun détail manquant n'est inventé pour remplir un détourage.

### C. Construire le fond
Utiliser une trame SpiritualCept claire, reproductible et indépendante du contenu documentaire. Le fond peut recevoir grain, filets et ornements génériques, mais aucune information historique implicite.

### D. Recomposer le texte
Le texte vient uniquement de `pages/NN.yaml:canonical_text` et des corrections validées. Il doit rester du vrai texte dans le PDF final lorsque techniquement possible.

Ne jamais utiliser l'OCR de la page JPEG comme source éditoriale de vérité.

### E. Ajouter les fonctions
Les QR viennent uniquement de `qr_registry.yaml` et des SVG déterministes déjà validés. Ils sont placés en dernier afin de rester parfaitement décodables.

### F. Valider
- comparer la nouvelle composition à la référence canonique ;
- vérifier texte, positions, fragments, résolution d'impression et QR ;
- enregistrer provenance et SHA ;
- exécuter les validateurs ;
- ne promouvoir la page qu'après inspection.

## SVG : nouveau rôle
Le SVG n'est plus la destination systématique des illustrations.

À conserver/privilégier pour :
- QR ;
- ornements ;
- filets/formes ;
- héraldique spécifiée ;
- éléments géométriques simples ;
- documents dont la vectorisation est justifiée.

À éviter pour :
- reconstruction artificielle d'une illustration canonique déjà exploitable ;
- volumétrie architecturale spéculative ;
- remplacement d'une gravure/photo simplement pour « tout vectoriser ».

## Reconstitutions
Elles restent autorisées mais deviennent une voie secondaire. Elles servent lorsqu'il n'existe pas de fragment canonique exploitable, lorsqu'une nouvelle vue est explicitement souhaitée, ou lorsqu'une restitution hypothétique est un objectif éditorial identifié.

Elles restent sourcées, sans texte, avec confiance et limites déclarées.

## Verrous
### Page 4
`PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` reste actif pour la recomposition v3.

### Page 10
Le plan réel reste l'autorité pour toute nouvelle reconstitution. La composition v3 peut réutiliser les fragments validés de la page canonique sans créer une nouvelle architecture.

### Page 13
QR déterministes, alignés et réinjectés en dernier.

### Page 14
Aucun portrait de Philippe DEMARIO, y compris sous forme de fragment extrait.

## Registres
- `sources/PROVENANCE_INDEX.yaml` : provenance/droits/confiance ;
- `assets/ASSET_INDEX_V3.yaml` : actifs atomiques ;
- `manifest-v3.yaml` : actifs réellement produits ;
- `assets/ASSET_SPEC.md` : cartographie des zones et besoins de production.

Les prochains actifs raster découpés devront être enregistrés comme actifs atomiques avec : page source, zone source, bounding box ou masque de découpe, traitement appliqué, dimensions, résolution cible, SHA-256 et statut de droits.

## Règles de travail
- Ne jamais inventer de contenu.
- Ne jamais faire d'une reconstruction générative la solution par défaut.
- Préférer un fragment canonique fidèle lorsqu'il est exploitable.
- Le texte est une couche indépendante, pas une partie de l'image.
- Le fond est une couche indépendante, pas un morceau de page aplatie.
- Les QR sont une couche fonctionnelle indépendante et déterministe.
- Une retouche d'un fragment reste locale et traçable.
- Les PDF, ZIP, planches contact et `dist/` ne sont jamais committés.

## Prochaine priorité d'exécution
Poursuivre le lot 2 sans promouvoir prématurément les actifs expérimentaux :

1. vérifier et compléter la provenance des actifs non textuels réellement mobilisables ;
2. résoudre les blocages de droits ou de source lorsque cela est possible ;
3. faire passer la revue héraldique de `assets/svg/heraldry-la-chambre.svg` ;
4. faire passer la revue géométrique de `assets/svg/page-10-castle-reconstruction.svg` ;
5. conserver le tracé documentaire direct du plan page 10 bloqué tant que les droits de reproduction ne sont pas documentés ;
6. conserver le logo association bloqué tant que sa source canonique n'est pas enregistrée ;
7. poursuivre le prototype page 03 comme test de pipeline multicouche, sans promotion en canon ;
8. ne produire de nouveaux SVG documentaires que lorsqu'ils apportent une valeur réelle et que leur provenance est résolue.

## Validation
Après modification d'une référence historique : `make sync && make validate`.

Après production d'actifs v3 : enregistrer les SHA/provenances puis `make validate`.

Après composition imprimable : `make build`, validation QR finale et contrôle de la couche texte.

## Interdiction de reconstruction par archive
Toujours partir du checkout Git courant. Aucun ancien ZIP ne devient source de vérité.