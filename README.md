# Les Seigneurs de La Chambre — référentiel colorisé

Référentiel maître des 15 planches de l'exposition, avec charte **SpiritualCept Colorisé** : papier ivoire patiné, plume et sépia, fusain léger, aquarelle, pastels et craies, avec une lisibilité forte du texte et une colorisation documentaire mesurée.

Le principe reste strict : **la couleur peut évoluer, jamais le contenu canonique sans correction éditoriale explicite**.

## Sources de vérité

- `corrections.yaml` : corrections éditoriales et visuelles prioritaires.
- `pages/01.yaml` à `pages/15.yaml` : contenu canonique page par page.
- `assets/page-01.jpg` à `assets/page-15.jpg` : références visuelles validées.
- `style.yaml` : charte graphique et profil de colorisation verrouillé.
- `REGENERATION_RULES.md` : règles de modification et de régénération.
- `qr_registry.yaml` : payloads QR réels et validés.
- `build-config.yaml` : ordre canonique des pages et sorties PDF.

## Règles visuelles importantes

La colorisation doit rester douce : bleu gris pour ciel et montagnes, olive/sauge pour la végétation, ocre et gris chaud pour la pierre, rouge-brun pour les titres, bleu/rouge/or pour l'héraldique. Les textes, plans et QR ne reçoivent jamais de filtre artistique global.

Pour le **Château de Notre-Dame-du-Cruet**, la dernière version colorisée validée fixe l'orientation du château. Le plan réel doit être respecté et la mention « Vous êtes ici » est interdite. Pour la page **Association**, aucun portrait ou photographie de Philippe DEMARIO ne doit être affiché ; son nom et ses ouvrages restent présents dans la bibliographie canonique.

## Construction locale

```bash
python -m pip install -r requirements-build.txt
make validate
make build
```

Les sorties sont créées dans `dist/` :

- `Seigneurs_La_Chambre_15_pages_Colorise.pdf`
- `Seigneurs_La_Chambre_Livret_A5_16p_Colorise.pdf`
- `Seigneurs_La_Chambre_Livret_A4_Impose_RectoVerso_Colorise.pdf`
- `Seigneurs_La_Chambre_Panneaux_A2_15p_Colorise.pdf`
- `Seigneurs_La_Chambre_Panneaux_A1_15p_Colorise.pdf`
- `Seigneurs_La_Chambre_Print_PDFs.zip`
- `SHA256SUMS.txt`
- `build-report.json`

Le constructeur réinjecte les QR déterministes du registre au-dessus des planches raster lors de la création des PDF.

## CI GitHub

Deux workflows sont présents :

- **Validate reference package** : vérifie le manifest, les 15 descripteurs, la charte colorisée, les corrections et tous les actifs QR.
- **Build and release print PDFs** : construit toutes les sorties PDF et publie un artifact GitHub à chaque build concerné.

Sur un tag de version `v*` (par exemple `v2.0.0`), le second workflow crée automatiquement une **GitHub Release** contenant les cinq PDF, le ZIP d'impression, `SHA256SUMS.txt` et `build-report.json`.

Pour produire une release :

```bash
git tag v2.0.0
git push origin v2.0.0
```

Le PDF est donc désormais une sortie reproductible du dépôt, et non un fichier fabriqué manuellement.
