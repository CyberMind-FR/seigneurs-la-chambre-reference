# WORK HANDOFF — Les Seigneurs de La Chambre

## Mission
Finaliser et maintenir le livret/exposition sans dérive éditoriale ni visuelle. Le dépôt GitHub est l’unique source de vérité.

## Ordre de lecture obligatoire
1. `REGENERATION_RULES.md`
2. `corrections.yaml`
3. `manifest.yaml`, `manifest-pages.json` et, sur la branche v3, `manifest-v3.yaml`
4. `sources/PROVENANCE_INDEX.yaml`
5. `assets/ASSET_INDEX_V3.yaml`
6. `pages/NN.yaml`
7. `qr_registry.yaml`
8. `assets/page-NN.jpg`
9. `docs/migration-text-layer/PHASE_A_APPROVAL.md` pour toute production v3

## Canon actuel
- 16 pages, `assets/page-01.jpg` à `assets/page-16.jpg`.
- Page 10 = Château de Notre-Dame-du-Cruet, version réorientée validée, avec QR Google Maps réinjecté de façon déterministe. Ne jamais la remplacer par une ancienne version.
- Page 13 = six QR de ressources numériques alignés sur une même ligne et réinjectés depuis `assets/qr/`. Ne jamais styliser ou reconstruire ces QR.
- Page 14 : portrait de Philippe DEMARIO supprimé, nom et bibliographie conservés.
- Page 16 : QR de l'association enregistré et réinjecté de façon déterministe.
- Les 16 pages utilisent un fond papier blanc neutre et des encres renforcées pour la lisibilité ; le contenu et la composition restent verrouillés.
- Taux Fondation du Patrimoine : 66 %, jamais 75 %.
- Page 4 : aucune mention « Académie de Maurienne ».
- Auteurs : `Fabrice GALOPO, André GRANGE, Gérald KERMA`.

## Release v3 — état de migration
- Branche active de production : `release/v3.0-phase-b`.
- Phase A explicitement validée le 2026-09-08 dans `docs/migration-text-layer/PHASE_A_APPROVAL.md`.
- `assets/ASSET_SPEC.md`, l’amendement étroit au canon et le schéma de manifeste v3 bornent la Phase B.
- Premier lot Phase B terminé : **16 QR SVG uniques** produits depuis `qr_registry.yaml` avec `segno==1.6.6` et validation machine exacte.
- Les 17 placements fonctionnels restent représentés par 16 actifs, car le QR `association` est réutilisé en pages 13 et 16.
- Les SVG QR sont sous `assets/qr-svg/`; leurs SHA sont verrouillés dans `assets/qr-svg/manifest.yaml` et intégrés à `manifest-v3.yaml`.
- Rapport machine QR : `docs/migration-text-layer/PHASE_B_QR_BATCH.md` = PASS.
- `manifest.yaml` reste intact pendant la migration ; `manifest-v3.yaml` est le manifeste incrémental de la v3.

## Phase B — lot 2 actif
Le lot 2 porte sur :

1. l’inventaire des sources et provenances ;
2. la qualification des droits et niveaux de confiance ;
3. le déblocage contrôlé des premiers SVG non textuels ;
4. l’ouverture des reconstitutions sourcées ;
5. le maintien de la non-régression des pages canoniques.

Les registres opérationnels sont :

- `sources/PROVENANCE_INDEX.yaml` : provenance, droits, confiance, limites d’usage ;
- `assets/ASSET_INDEX_V3.yaml` : statut de chaque actif produit ou candidat ;
- `manifest-v3.yaml` : enregistrement incrémental des actifs réellement produits.

Le snapshot `docs/migration-text-layer/PHASE_B_SOURCE_INVENTORY.yaml` reste un audit historique, pas le registre opérationnel courant.

## Reconstitutions : règle active
Les reconstitutions sont autorisées si elles :

- sont sans texte ;
- possèdent des `source_refs` résolus ;
- déclarent leur niveau de confiance ;
- n’ajoutent aucun détail historique non soutenu par les sources ;
- restent distinctes d’un document original ;
- portent la mention `Reconstitution graphique à partir des sources documentées.` lorsqu’une ambiguïté est possible.

Cette autorisation ne libère pas les droits de reproduction d’un document source. Une reconstitution non fac-similé peut être produite à partir d’une source enregistrée, tandis qu’un tracé documentaire direct peut rester bloqué par les droits.

## Premier lot SVG non-QR produit
Trois actifs existent désormais sous `assets/svg/` et sont enregistrés dans `assets/ASSET_INDEX_V3.yaml` et `manifest-v3.yaml` :

- `assets/svg/heraldry-la-chambre.svg`
  - statut : `PRODUCED_PENDING_HERALDIC_REVIEW`
  - source : blasonnement canonique de `pages/02.yaml`
  - aucun texte ni raster embarqué
  - revue visuelle/héraldique humaine encore requise avant usage final

- `assets/svg/page-10-castle-reconstruction.svg`
  - statut : `PRODUCED_PENDING_GEOMETRY_REVIEW`
  - reconstitution non fac-similé liée à `assets/reference/page-10-plan-reel.jpg`
  - aucun texte ni raster embarqué
  - revue géométrique humaine contre le plan réel obligatoire avant usage final

- `assets/svg/spiritualcept-ornaments.svg`
  - statut : `PRODUCED_VALIDATED`
  - actif ornemental sans assertion historique
  - utilisable dans le pipeline v3

Rapport structurel : `docs/migration-text-layer/PHASE_B_SVG_BATCH.md` = **PASS**.

`make validate` exécute maintenant également `scripts/validate_phase_b_svg.py`. Aucun de ces actifs n’est autorisé à modifier automatiquement une page canonique.

## Toujours bloqués
- `page_10_plan_documentary_trace_svg` : `BLOCKED_RIGHTS` pour une reproduction/tracé direct du plan source.
- `association_logo_svg` : `BLOCKED_SOURCE_MISSING` jusqu’à ce que l’actif source validé ait un chemin canonique dans le dépôt.
- Page 4 : `PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` pour toute recomposition v3.
- Ancien emplacement du portrait Philippe DEMARIO : rester vide, aucun portrait de substitution.

## Règles de travail
- Une page validée est immuable hors correction explicitement demandée.
- Une correction locale reste locale. Pas de régénération complète pour un détail.
- Aucun texte, nom, date, rôle, lieu, plan, QR ou élément architectural ne peut être inventé.
- Les QR fonctionnels proviennent uniquement de `qr_registry.yaml` ; les PNG historiques restent sous `assets/qr/` et les nouveaux SVG déterministes sous `assets/qr-svg/`.
- Aucun QR n’est généré ou stylisé par un modèle d’image.
- Toute illustration v3 doit respecter `REGENERATION_RULES.md`, `sources/PROVENANCE_INDEX.yaml`, `assets/ASSET_INDEX_V3.yaml` et `assets/ASSET_SPEC.md`.
- Pour une reproduction documentaire directe, les droits doivent être établis.
- Pour une reconstitution, les sources et la confiance doivent être explicites ; les droits du document source ne sont pas extrapolés.
- Toute normalisation colorimétrique globale des rasters hérités doit utiliser `scripts/normalize_white_background.py`, qui réinjecte les QR en dernier.
- Après remplacement d’une page historique : exécuter `make sync` puis `make validate`.
- Après production d’un lot v3 : recalculer les SHA, synchroniser les registres puis exécuter les validateurs propres au lot et `make validate`.
- Après build : `make build` doit aussi valider les QR du PDF final.
- Les PDF, ZIP, planches contact et `dist/` ne sont jamais committés.

## Procédure sûre pour toute modification
1. Lire le canon et la correction demandée.
2. Résoudre les `source_refs` dans `sources/PROVENANCE_INDEX.yaml`.
3. Vérifier le statut de l’actif dans `assets/ASSET_INDEX_V3.yaml`.
4. Travailler sur `release/v3.0-phase-b` ou une sous-branche dédiée.
5. Produire uniquement un actif autorisé, sans texte.
6. Enregistrer SHA, provenance, confiance et validation.
7. Synchroniser `manifest-v3.yaml` lorsque l’actif devient réellement produit.
8. Exécuter `make validate`.
9. Pour une sortie imprimable, exécuter `make build`.
10. Inspecter visuellement l’actif et les pages concernées avant merge.

## Priorité d’exécution suivante
Ordre recommandé :

1. effectuer la revue humaine du blason SVG ;
2. effectuer la revue géométrique du SVG page 10 contre le plan réel ;
3. committer le logo association source validé pour débloquer sa vectorisation ;
4. préparer le prochain sous-lot d’actifs documentaires/reconstitutions seulement après ces gates ;
5. ne produire le tracé documentaire direct du plan page 10 qu’après résolution des droits.

## Interdiction de reconstruction par archive
Ne jamais fabriquer une nouvelle source à partir d’un ancien ZIP. Toujours partir du checkout Git courant.
