# RÈGLE DE RÉGÉNÉRATION STRICTE — Les Seigneurs de La Chambre

Ce fichier fait partie de la source de vérité du projet.

## Principe absolu
Une page déjà validée visuellement n'est jamais recréée librement pour une correction ponctuelle.
Elle sert de base immuable et la correction est appliquée chirurgicalement sur la seule zone demandée.

## Interdictions permanentes
- Ne jamais inventer de personne, nom, fonction, catégorie de membre, citation, date, lieu, source, prix, taux ou contenu.
- Ne jamais ajouter un élément éditorial absent du canon.
- Ne jamais réinterpréter librement une page validée ni changer sa composition pour « améliorer » le rendu.
- Ne jamais remplacer une page validée par une nouvelle création IA lorsqu'une retouche déterministe suffit.
- Ne jamais extrapoler un fait historique à partir d'une autre page.
- Ne jamais générer ou styliser un QR avec un modèle d'image.
- Ne jamais intégrer de texte généré dans un actif graphique v3.

## Ordre des sources
1. `corrections.yaml`
2. `pages/NN.yaml` / `canonical_text`
3. `sources/PROVENANCE_INDEX.yaml` pour provenance, droits, confiance et limites d'usage
4. `assets/ASSET_INDEX_V3.yaml` pour le statut opérationnel des actifs v3
5. référence visuelle `assets/page-NN.jpg`
6. aucune autre source sans validation explicite

## Politique de modification locale
Pour une correction de texte, de nombre ou de nom :
1. partir du fichier visuel validé ;
2. identifier précisément la zone impactée ;
3. modifier uniquement cette zone ;
4. préserver tous les autres pixels autant que techniquement possible ;
5. vérifier que le texte final correspond mot pour mot au canon ;
6. recalculer le SHA-256 de la nouvelle référence ;
7. mettre à jour la fiche YAML et `corrections.yaml` si nécessaire ;
8. vérifier visuellement avant livraison.

## Phase B v3 — reconstitutions désormais autorisées
Les reconstitutions graphiques sont autorisées à partir de la Phase B lorsqu'elles respectent simultanément les règles suivantes :

- elles sont indépendantes des pages raster et ne remplacent pas silencieusement une page canonique ;
- elles sont sans texte ;
- elles possèdent des `source_refs` résolus dans `sources/PROVENANCE_INDEX.yaml` ;
- leur niveau de confiance est déclaré ;
- leur périmètre d'interprétation est explicite ;
- aucun détail historique non soutenu par les sources n'est ajouté ;
- elles sont marquées comme reconstitution lorsqu'une confusion avec un document original est possible.

Mention par défaut :

> **Reconstitution graphique à partir des sources documentées.**

Cette autorisation ne transforme pas une source aux droits inconnus en source librement reproductible. Une reconstitution non fac-similé peut être produite à partir d'une source enregistrée comme référence, mais la copie, le tracé direct ou la redistribution d'un document source restent soumis à son statut de droits.

## Distinction obligatoire des actifs

### Document
Reproduction, restauration ou tracé directement fondé sur un document source.
Le droit de reproduction doit être établi avant diffusion lorsque le document source n'est pas explicitement libre ou autorisé.

### Reconstitution
Interprétation graphique contrôlée fondée sur une ou plusieurs sources identifiées.
Elle peut être produite si les sources, la confiance et les limites d'interprétation sont enregistrées.

### Ornement
Élément graphique sans assertion historique. Il peut être redessiné dans le langage SpiritualCept à condition de rester sans texte ni donnée documentaire implicite.

### Actif fonctionnel
QR et autres actifs techniques. Production déterministe uniquement.

## Déblocage Phase B — lot 2
Les statuts opérationnels sont enregistrés dans `assets/ASSET_INDEX_V3.yaml`.
À la date du présent amendement :

- les 16 QR SVG déterministes sont `READY_FUNCTIONAL` ;
- le rendu héraldique original fondé sur le blasonnement canonique est `READY_RECONSTRUCTION` ;
- la reconstitution architecturale de la page 10 est `READY_RECONSTRUCTION` avec verrou géométrique sur le plan réel ;
- les ornements sans assertion historique sont `READY_ORNAMENT` ;
- le tracé documentaire direct du plan de la page 10 reste `BLOCKED_RIGHTS` ;
- la vectorisation du logo association reste `BLOCKED_SOURCE_MISSING` tant que l'actif source validé n'a pas de chemin canonique dans le dépôt.

## Verrous canoniques

### Page 4
Toute recomposition v3 reste bloquée par `PAGE_04_EDITORIAL_ARBITRATION_REQUIRED`.

### Page 10
`assets/reference/page-10-plan-reel.jpg` reste l'autorité géométrique. Une reconstitution peut être produite, mais elle ne doit pas inventer une géométrie contradictoire ni être présentée comme un relevé original.

### Page 13
Les QR restent alignés et déterministes ; les payloads proviennent exclusivement de `qr_registry.yaml`.

### Page 14
L'ancien emplacement du portrait de Philippe DEMARIO reste vide. Aucun portrait de substitution.

## Validation obligatoire des nouveaux actifs v3
Tout nouvel actif doit, selon son type, satisfaire :

- résolution des `source_refs` ;
- contrôle de droits lorsqu'il s'agit d'une reproduction documentaire directe ;
- absence de texte généré ;
- absence de détail historique non sourcé pour une reconstitution ;
- SHA-256 enregistré lorsque le fichier existe ;
- contrôle visuel ;
- respect de la politique de mention de reconstitution.

Commandes minimales :

- `make sync`
- `make validate`

Lorsque pertinent :

- `make qr-svg`
- `make validate-qr-svg`
- `make manifest-v3`

## Style verrouillé
Le langage graphique SpiritualCept est un carnet de recherches historique / sketchbook documentaire : papier blanc neutre imprimable, encre brun-noir / sépia, gravure et graphite, titres rouge-brun, accents bleu/or héraldiques, ornements fins et forte lisibilité d'impression.

Ce style est un verrou, pas une invitation à inventer du contenu.
