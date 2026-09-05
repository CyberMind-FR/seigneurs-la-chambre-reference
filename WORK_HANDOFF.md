# WORK HANDOFF — Les Seigneurs de La Chambre

## Mission
Finaliser et maintenir le livret/exposition sans dérive éditoriale ni visuelle. Le dépôt GitHub est l’unique source de vérité.

## Ordre de lecture obligatoire
1. `REGENERATION_RULES.md`
2. `corrections.yaml`
3. `manifest.yaml` et `manifest-pages.json`
4. `pages/NN.yaml`
5. `qr_registry.yaml`
6. `assets/page-NN.jpg`

## Canon actuel
- 16 pages, `assets/page-01.jpg` à `assets/page-16.jpg`.
- Page 10 = Château de Notre-Dame-du-Cruet, version réorientée validée. Ne jamais la remplacer par une ancienne version.
- Page 14 : portrait de Philippe DEMARIO supprimé, nom et bibliographie conservés.
- Taux Fondation du Patrimoine : 66 %, jamais 75 %.
- Page 4 : aucune mention « Académie de Maurienne ».
- Auteurs : `Fabrice GALOPO, André GRANGE, Gérald KERMA`.

## Règles de travail
- Une page validée est immuable hors correction explicitement demandée.
- Une correction locale reste locale. Pas de régénération complète pour un détail.
- Aucun texte, nom, date, rôle, lieu, plan, QR ou élément architectural ne peut être inventé.
- Les QR fonctionnels proviennent uniquement de `assets/qr/` et `qr_registry.yaml`.
- Après remplacement d’une page : exécuter `make sync` puis `make validate`. `manifest.yaml` est la référence d’intégrité ; `manifest-pages.json` et les SHA des fiches sont synchronisés automatiquement.
- Après build : `make build` doit aussi valider les QR du PDF final.
- Les PDF, ZIP, planches contact et `dist/` ne sont jamais committés. Ils sont produits par la CI et publiés comme artifacts/releases.

## Procédure sûre pour toute modification
1. Lire le canon et la correction demandée.
2. Créer une branche de travail.
3. Modifier uniquement les fichiers nécessaires.
4. Exécuter `make validate`.
5. Pour une sortie imprimable, exécuter `make build`.
6. Inspecter la planche/page concernée avant merge.
7. Ne merger que si validation et contrôle visuel sont conformes.

## Interdiction de reconstruction par archive
Ne jamais fabriquer une nouvelle source à partir d’un ancien ZIP. Toujours partir du checkout Git courant.
