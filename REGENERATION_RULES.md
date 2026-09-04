# RÈGLE DE RÉGÉNÉRATION STRICTE — Les Seigneurs de La Chambre

Ce fichier fait partie de la source de vérité du projet.

## Principe absolu
Une page déjà validée visuellement n'est jamais recréée librement pour une correction ponctuelle.
Elle sert de base immuable et la correction est appliquée chirurgicalement sur la seule zone demandée.

## Interdictions
- Ne jamais inventer de personne, nom, fonction, catégorie de membre, citation, date, lieu, source, prix, taux ou contenu.
- Ne jamais ajouter de bloc, illustration, logo, sceau, portrait, livre, carte ou QR absent de la référence validée.
- Ne jamais réinterpréter la page ni changer sa composition pour « améliorer » le rendu.
- Ne jamais remplacer une page validée par une nouvelle création IA lorsqu'une retouche déterministe suffit.
- Ne jamais extrapoler à partir d'une autre page.

## Ordre des sources
1. `corrections.yaml`
2. `pages/NN.yaml` / `canonical_text`
3. référence visuelle `assets/page-NN.jpg`
4. aucune autre source sans validation explicite

## Politique de modification
Pour une correction de texte, de nombre ou de nom:
1. partir du fichier visuel validé;
2. identifier précisément la zone impactée;
3. modifier uniquement cette zone;
4. préserver tous les autres pixels autant que techniquement possible;
5. vérifier que le texte final correspond mot pour mot au canon;
6. recalculer le SHA-256 de la nouvelle référence;
7. mettre à jour la fiche YAML et `corrections.yaml`;
8. vérifier visuellement avant livraison.

## Style verrouillé
Le langage graphique SpiritualCept est un carnet de recherches historique / sketchbook documentaire:
papier ivoire patiné, encre brun-noir / sépia, gravure et graphite, titres rouge-brun, accents bleu/or héraldiques, ornements fins, forte lisibilité d'impression.

Ce style est un verrou, pas une invitation à réinventer la page.
