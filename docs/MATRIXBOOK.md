# MatrixBook — Design Document v1.0

## Vision

MatrixBook est une méthodologie éditoriale qui transforme une maquette générée par IA en un livre professionnel, modulaire et durable.

## Pipeline

1. Préparer les contenus
2. Générer une maquette IA complète
3. Découper les zones en assets
4. Créer la matrice des illustrations
5. Reprompter uniquement les éléments nécessaires
6. Recomposer la page en texte vectoriel puis exporter en PDF

## Arborescence

```text
book/
 ├── manuscript/
 ├── prompts/
 ├── assets/
 ├── pages/
 ├── exports/
 └── docs/
```

## Principe fondateur

> Une page = une maquette IA + une bibliothèque d'assets + une composition éditoriale.
