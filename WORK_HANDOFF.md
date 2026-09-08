# WORK HANDOFF — Les Seigneurs de La Chambre

## Mission
Finaliser et maintenir le livret/exposition sans dérive éditoriale ni visuelle. Le dépôt GitHub est l’unique source de vérité.

## Ordre de lecture obligatoire
1. `REGENERATION_RULES.md`
2. `corrections.yaml`
3. `manifest.yaml`, `manifest-pages.json` et, sur la branche v3, `manifest-v3.yaml`
4. `pages/NN.yaml`
5. `qr_registry.yaml`
6. `assets/page-NN.jpg`
7. `docs/migration-text-layer/PHASE_A_APPROVAL.md` pour toute production v3

## Canon actuel
- 16 pages, `assets/page-01.jpg` à `assets/page-16.jpg`.
- Page 10 = Château de Notre-Dame-du-Cruet, version réorientée validée, avec QR Google Maps réinjecté de façon déterministe. Ne jamais la remplacer par une ancienne version.
- Page 13 = six QR de ressources numériques alignés sur une même ligne et réinjectés depuis `assets/qr/`. Ne jamais styliser ou reconstruire ces QR.
- Page 14 : portrait de Philippe DEMARIO supprimé, nom et bibliographie conservés.
- Page 16 : QR de l'association enregistré et réinjecté de façon déterministe.
- Les 16 pages utilisent un fond papier blanc neutre et des encres renforcées pour la lisibilité; le contenu et la composition restent verrouillés.
- Taux Fondation du Patrimoine : 66 %, jamais 75 %.
- Page 4 : aucune mention « Académie de Maurienne ».
- Auteurs : `Fabrice GALOPO, André GRANGE, Gérald KERMA`.

## Release v3 — état de migration
- Branche active de production : `release/v3.0-phase-b`.
- Phase A explicitement validée le 2026-09-08 dans `docs/migration-text-layer/PHASE_A_APPROVAL.md`.
- `assets/ASSET_SPEC.md`, l’amendement étroit au canon et le schéma de manifeste v3 sont les documents approuvés qui bornent la Phase B.
- Premier lot Phase B terminé : **16 QR SVG uniques** produits depuis `qr_registry.yaml` avec `segno==1.6.6`, noir pur, fond blanc, zone de silence de 4 modules.
- Les 17 placements fonctionnels restent représentés par 16 actifs, car le QR `association` est réutilisé en pages 13 et 16.
- Les SVG sont sous `assets/qr-svg/`; leurs SHA sont verrouillés dans `assets/qr-svg/manifest.yaml` et intégrés à `manifest-v3.yaml`.
- Rapport machine : `docs/migration-text-layer/PHASE_B_QR_BATCH.md` = PASS, décodage exact caractère par caractère de chaque actif.
- `make validate` contrôle désormais le référentiel historique, les QR bitmap sources et le lot QR SVG.
- Le workflow one-shot ayant produit ce lot a été retiré après succès : aucun générateur temporaire ne reste dans `.github/workflows/`.
- `manifest.yaml` reste intact pendant la migration ; `manifest-v3.yaml` est le manifeste incrémental de la v3.

## Règles de travail
- Une page validée est immuable hors correction explicitement demandée.
- Une correction locale reste locale. Pas de régénération complète pour un détail.
- Aucun texte, nom, date, rôle, lieu, plan, QR ou élément architectural ne peut être inventé.
- Les QR fonctionnels proviennent uniquement de `qr_registry.yaml`; les PNG historiques restent sous `assets/qr/` et les nouveaux SVG déterministes sous `assets/qr-svg/`.
- Aucun QR n’est généré ou stylisé par un modèle d’image.
- Toute illustration v3 produite doit être sans texte et respecter l’amendement validé, `assets/ASSET_SPEC.md`, la provenance et les droits enregistrés.
- Toute normalisation colorimétrique globale doit utiliser `scripts/normalize_white_background.py`, qui réinjecte les QR en dernier pour les rasters hérités.
- Après remplacement d’une page historique : exécuter `make sync` puis `make validate`.
- Après production d’un lot v3 : recalculer les SHA dans `manifest-v3.yaml`, exécuter les validateurs propres au lot, puis `make validate`.
- Après build : `make build` doit aussi valider les QR du PDF final.
- Les PDF, ZIP, planches contact et `dist/` ne sont jamais committés. Ils sont produits par la CI et publiés comme artifacts/releases.

## Procédure sûre pour toute modification
1. Lire le canon et la correction demandée.
2. Vérifier l’autorisation et les blocages dans la Phase A validée.
3. Travailler sur la branche de phase appropriée.
4. Modifier ou produire uniquement les actifs autorisés.
5. Enregistrer provenance, licence, droits, SHA et validations dans `manifest-v3.yaml` pour les actifs v3.
6. Exécuter `make validate`.
7. Pour une sortie imprimable, exécuter `make build`.
8. Inspecter visuellement les pages/actifs concernés avant merge.
9. Ne merger que si validation et contrôle visuel sont conformes.

## Blocages toujours actifs
- Page 4 : `PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` pour toute recomposition v3.
- Ancien emplacement du portrait Philippe DEMARIO : rester vide, aucun portrait de substitution.
- Toute source documentaire dont provenance, licence ou droit d’usage ne sont pas établis reste bloquée.
- Page 10 : toute reconstitution doit respecter `assets/reference/page-10-plan-reel.jpg` comme autorité géométrique.

## Interdiction de reconstruction par archive
Ne jamais fabriquer une nouvelle source à partir d’un ancien ZIP. Toujours partir du checkout Git courant.
