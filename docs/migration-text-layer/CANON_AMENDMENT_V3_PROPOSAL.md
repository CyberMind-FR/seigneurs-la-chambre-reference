# Release v3.0 — projet d’amendement étroit au canon

> **Statut : PROPOSITION À VALIDER HUMAINEMENT — NON APPLIQUÉE.**
>
> Ce document ne modifie ni `REGENERATION_RULES.md`, ni `style.yaml`, ni les pages canoniques. Il définit l’amendement minimal qui serait nécessaire pour autoriser la production des actifs de la release v3.0. Tant qu’il n’est pas explicitement validé, les règles actuelles restent intégralement en vigueur.

## 1. Objet

La migration vers un pipeline à couche texte impose de séparer les illustrations des pages raster aplaties. L’objectif de cet amendement est d’autoriser **uniquement** la génération, la refonte ou le redessin d’illustrations **sans aucun texte**, dans des zones d’actifs explicitement spécifiées et manifestées.

Le texte reste exclusivement issu de `pages/NN.yaml` / `canonical_text` et est composé par le moteur de mise en page. Un modèle d’image ne peut jamais produire le texte final.

## 2. Autorisation proposée

Après validation humaine de la Phase A, seraient autorisés :

- la génération ou la refonte d’une **illustration sans texte** destinée à un slot défini dans `assets/ASSET_SPEC.md` ;
- le redessin vectoriel sans texte de plans, cartes, blasons, filets, fleurons, chronologies, roses des vents et autres éléments graphiques lorsque leur source et leur statut documentaire sont enregistrés ;
- la production déterministe d’ornements sans texte qui ne portent aucune affirmation historique ;
- le détourage, nettoyage, restauration ou conversion déterministe d’un actif documentaire existant, dans les limites des droits enregistrés ;
- la création de dérivés techniques nécessaires au build, notamment conversion colorimétrique, redimensionnement sans prétendre créer de détail source, et préparation au profil ICC validé.

Cette autorisation ne concerne **jamais** une page complète ni un fragment de page composé.

## 3. Interdictions maintenues sans exception

Restent interdits :

- générer ou régénérer une page complète ;
- générer un fragment de page contenant une composition éditoriale ;
- dessiner ou incruster un titre, un paragraphe, une légende, un cartouche, une cote, un toponyme, une signature ou tout autre caractère dans une illustration ;
- générer, styliser, redessiner ou interpréter un QR avec un modèle d’image ;
- utiliser une génération d’image pour corriger une faute de texte ;
- réécrire `canonical_text` afin de le faire correspondre à un raster fautif ;
- ajouter un bâtiment, une tour, un mur, un blason, une inscription, une date, une personne, un objet ou une relation historique qui ne figure pas dans le canon ou dans une source explicitement citée et validée ;
- publier une reconstitution comme s’il s’agissait d’un document d’archive ;
- utiliser l’upscaling comme preuve de conformité de résolution ;
- contourner une page bloquée par un fallback raster ou une reconstruction automatique.

## 4. Honnêteté documentaire obligatoire

Chaque actif illustratif produit pour la v3.0 doit être classé dans le manifeste avec une `nature` explicite :

- `document` : reproduction, restauration ou traçage directement fondé sur une source identifiée ;
- `reconstitution` : représentation graphique reconstruite à partir d’informations documentées, sans prétention à être une archive ;
- `ornement` : élément graphique sans assertion historique.

Un actif dont la nature, la provenance ou les droits ne sont pas établis reste bloqué et ne peut pas entrer dans une release de production.

### 4.1 Reconstitutions de monuments

Toute reconstitution d’un monument doit :

1. référencer les sources utilisées dans le manifeste ;
2. respecter strictement les éléments documentés ;
3. ne pas compléter les lacunes par des détails présentés comme certains ;
4. recevoir dans le document composé une mention visible indiquant son statut de reconstitution ;
5. rester dépourvue de tout texte incrusté dans le fichier image lui-même.

### 4.2 Formulation proposée à la Commission

Formulation candidate, **non canonique tant qu’elle n’est pas validée** :

> **Reconstitution graphique à partir des sources documentées.**

Emplacement proposé : dans la légende composée associée à l’illustration, immédiatement sous ou à proximité du visuel, dans le style `type.caption`. La mention est du texte composé par le moteur, jamais intégrée à l’image.

Une formulation plus précise peut être retenue actif par actif, par exemple `Reconstitution graphique d’après le plan documenté`, uniquement si la Commission valide cette rédaction et que le manifeste identifie effectivement le plan concerné.

## 5. Cas particuliers verrouillés

### Page 4 — Maison de La Tour

La page 4 reste bloquée par l’arbitrage éditorial identifié dans la migration. Cet amendement **n’autorise aucune illustration, recomposition ou harmonisation** de cette page tant que la Commission n’a pas tranché le conflit de récit.

Code de blocage proposé :

`PAGE_04_EDITORIAL_ARBITRATION_REQUIRED`

### Page 10 — Château de Notre-Dame-du-Cruet

La page 10 n’est pas bloquée éditorialement. Toute illustration ou reconstitution du château doit respecter la géométrie documentée par :

`assets/reference/page-10-plan-reel.jpg`

Cette source fait foi pour les éléments géométriques déjà verrouillés par `corrections.yaml/page_10`. Aucun élément architectural supplémentaire ne peut être inventé pour « compléter » le château.

### Page 14 — ancien portrait Philippe DEMARIO

L’ancien emplacement du portrait reste **vide/verrouillé**. Cet amendement n’autorise ni portrait de remplacement, ni personnage générique, ni silhouette de substitution.

## 6. QR

Les QR restent hors du périmètre de génération illustrative.

Ils sont générés de manière déterministe au build depuis `qr_registry.yaml`, sous forme vectorielle, avec :

- payload exact du registre ;
- noir pur ;
- fond blanc ;
- zone de silence minimale de 4 modules ;
- contrôle par redécodage depuis le PDF final.

Aucun payload ne peut être recopié manuellement dans un brief d’image ou confié à un modèle génératif.

## 7. Texte et légendes

Le texte final est toujours issu des sources structurées du dépôt. Les illustrations livrées doivent contenir **zéro caractère**.

Le contrôle bloquant prévu pour la Phase B est :

- OCR de chaque actif raster produit ;
- inspection des SVG pour détecter les nœuds `text`, `tspan` ou équivalents et, si nécessaire, OCR du rendu du SVG ;
- rejet de tout actif dans lequel un caractère est détecté, sauf faux positif explicitement diagnostiqué et validé humainement avant intégration.

Aucun résultat OCR ne peut servir à corriger ou enrichir le `canonical_text`.

## 8. Traçabilité obligatoire

Avant qu’un actif puisse être déclaré `READY`, le manifeste v3 doit enregistrer au minimum :

- identifiant stable ;
- page(s) et zone(s) d’utilisation ;
- `nature` ;
- classe technique `svg` / `raster` / `qr` ;
- chemin ;
- SHA-256 ;
- provenance ;
- source ou brief de production ;
- licence ;
- droits de redistribution et d’impression ;
- placement physique maximal ;
- cible de résolution lorsque l’actif est raster ;
- statut de validation documentaire et graphique.

Une valeur inconnue n’est jamais inventée : elle rend l’actif bloquant jusqu’à résolution.

## 9. Portée de l’amendement

L’amendement proposé ne remplace pas le principe de retouche chirurgicale pour les références raster historiques. Il crée une exception **uniquement pour la nouvelle chaîne à couche texte**, dans laquelle les illustrations sont des actifs indépendants et le texte est composé séparément.

Il ne donne aucune autorisation générale de « réimaginer » le livret.

## 10. Décision humaine requise

Avant Phase B, la Commission doit valider explicitement :

1. le principe de génération/refonte d’illustrations sans texte ;
2. les catégories `document`, `reconstitution`, `ornement` ;
3. la formulation et l’emplacement de la mention de reconstitution ;
4. la classification des actifs de `assets/ASSET_SPEC.md` ;
5. le schéma de manifeste v3 proposé dans `docs/migration-text-layer/MANIFEST_V3_SCHEMA_PROPOSAL.md`.

**Sans cette validation, aucun actif de Phase B ne doit être produit.**
