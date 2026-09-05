# Nettoyage avant push GitHub

Le dossier `dist/` est un produit de build et ne doit jamais être versionné.
Les PDF et ZIP sont générés par GitHub Actions puis publiés comme artifacts / assets de release.

Si un gros fichier `dist/...zip` a déjà été ajouté au commit local, `.gitignore` ne suffit pas :

```bash
git rm -r --cached dist 2>/dev/null || true
rm -rf dist
git add .gitignore .github scripts assets pages Makefile requirements-build.txt build-config.yaml style.yaml corrections.yaml manifest.yaml qr_registry.yaml
# puis amender/recréer le commit qui contenait le gros fichier
```

Si le gros ZIP existe dans plusieurs commits locaux, il faut réécrire ces commits avant de pousser.
