# Release v3.0 — validation de la Phase A et autorisation de la Phase B

> **Statut : VALIDÉ — PHASE B AUTORISÉE.**
>
> Date de validation humaine : **2026-09-08**.
> Autorité : validation explicite du responsable du projet.

## 1. Documents validés

La validation porte exactement sur les trois documents présents sur la branche `release/v3.0-phase-a` :

1. `assets/ASSET_SPEC.md`
   - blob Git : `d4297a9558f70bf7b2ad334d3ea42bfe5010aeec`
   - rôle : spécification des 135 zones, classification technique, dimensionnement et blocages documentaires.

2. `docs/migration-text-layer/CANON_AMENDMENT_V3_PROPOSAL.md`
   - blob Git : `faa55cc38347f9ae202f21b4d20804a1c7d6266b`
   - rôle : amendement étroit autorisant la production d’illustrations indépendantes sans texte.

3. `docs/migration-text-layer/MANIFEST_V3_SCHEMA_PROPOSAL.md`
   - blob Git : `e4d8b9e42b825427fcf2de6e06d8bfbb22ce3056`
   - rôle : schéma cible v3 du manifeste, avec provenance, droits, nature documentaire, classe technique, SHA-256, placements et ppi.

Toute modification ultérieure de l’un de ces trois fichiers annule l’identité de cette validation pour le fichier modifié et exige une nouvelle validation humaine de sa nouvelle version.

## 2. Effet de la validation

L’amendement étroit au canon est **approuvé pour la release v3.0** et devient applicable sur la lignée de production v3.0.

Il ne constitue pas une autorisation générale de régénération des pages. Il autorise uniquement la production, la refonte, le détourage, la restauration ou le redessin d’**actifs d’illustration indépendants sans texte**, dans les slots spécifiés et sous les contraintes documentaires du manifeste.

Les statuts historiques « proposition » présents dans les trois documents validés décrivent leur état avant cette décision. Le présent fichier constitue la décision de validation qui les rend exécutoires pour la Phase B.

## 3. Phase B autorisée

La **Phase B — production des actifs** est autorisée à compter de cette validation.

Sont autorisés :

- production des SVG prévus par `assets/ASSET_SPEC.md` ;
- production des raster sans texte aux dimensions calculées ;
- détourage et restauration déterministes de documents existants lorsque provenance et droits le permettent ;
- génération déterministe des QR en SVG exclusivement depuis `qr_registry.yaml` ;
- création des entrées d’actifs du manifeste v3 avec SHA-256, provenance, licence, droits, nature, classe, placement maximal et ppi cible ;
- création des dérivés techniques nécessaires au build, sans les committer lorsqu’ils relèvent de `dist/` ou d’un cache de production.

Ne sont pas autorisés en Phase B :

- composer ou régénérer une page complète ;
- générer du texte dans une image ;
- dessiner un titre, une légende, un toponyme, une cote, une signature ou un QR par modèle d’image ;
- inventer une architecture, une personne, un blason, une inscription, une datation, un plan ou une source ;
- contourner un blocage de provenance, de licence ou de droit ;
- traiter la page 4 avant arbitrage éditorial.

## 4. Verrous maintenus

### Page 4

`PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` reste **bloquant**. La page peut être inventoriée mais aucun actif éditorial ou architectural nouveau ne doit être produit pour elle avant décision humaine.

### Page 10

`assets/reference/page-10-plan-reel.jpg` reste l’autorité géométrique de référence. Toute reconstitution doit rester compatible avec ce plan et être manifestée comme `nature: reconstitution` lorsqu’elle n’est pas un document source.

### Page 14

L’ancien emplacement du portrait de Philippe DEMARIO reste une **zone vide verrouillée**. Aucun portrait de remplacement ne doit être créé ou réintroduit.

### QR

Les payloads proviennent uniquement de `qr_registry.yaml`. Les QR sont produits de façon déterministe en noir pur sur fond blanc, avec zone de silence conforme, puis contrôlés par décodage machine.

### Texte

Aucun actif de Phase B ne contient de texte incrusté. Le texte final provient exclusivement du `canonical_text` des fichiers `pages/NN.yaml` et sera composé lors d’une phase ultérieure.

## 5. Contrôles bloquants de Phase B

Chaque lot d’actifs doit satisfaire avant acceptation :

1. correspondance avec un slot validé de `assets/ASSET_SPEC.md` ;
2. provenance et droits renseignés ou état explicitement bloqué ;
3. SHA-256 enregistré ;
4. classe `svg` ou `raster` cohérente avec la spécification ;
5. dimension raster calculée depuis le placement maximal et le ppi cible ;
6. absence de texte incrusté dans les illustrations produites ;
7. absence de modification des pages raster canoniques ;
8. pour les QR, payload décodé strictement identique au registre.

Un actif qui ne satisfait pas ces contrôles reste `BLOCKED` et ne peut pas entrer dans une composition de release.

## 6. Frontière de la présente autorisation

Cette décision **ouvre la Phase B uniquement**. Elle n’autorise pas automatiquement la Phase C de composition, ni la publication d’une release v3.0. La composition reste soumise aux critères et contrôles définis dans le cahier des charges et l’ADR de composition.

La Phase B peut désormais commencer.
