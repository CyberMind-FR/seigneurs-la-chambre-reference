# assets/hd — sources haute définition régénérées (Phase C)

Ce répertoire reçoit les **nouvelles images de base** des croquis et du fond, régénérées par
prompt (ChatGPT, génération d'images) à partir des crops canoniques, **sans modifier les grilles**
travaillées dans `prototypes/page-NN/composition.yaml`.

## Contrat

| Élément | Règle |
|---|---|
| Emplacement | `assets/hd/page-NN/<fragment_id>.png` (fond commun : `assets/hd/common/paper-texture.png`) |
| Format | PNG (ou JPEG), sRGB, sans texte, sans bordure ; alpha accepté |
| Ratio | celui de la bbox du fragment, tolérance 3 % (`validation.hd_aspect_tolerance`) ; recadrage centré automatique au ratio exact |
| Taille | jamais agrandie par le pipeline : la largeur après recadrage doit atteindre le gate (300 ppi demi-teintes, 1200 ppi trait) au moins en A5 — `assets/hd/prompts/page-NN.md` donne les minima par format |
| Déclaration | `prototypes/page-NN/hd-sources.yaml`, écrit par `make hd-ingest` (statut `PENDING_REVIEW`) ; la grille n'est jamais touchée |
| Approbation | édition humaine de `hd-sources.yaml` : `status: APPROVED`, `rights` ∈ {CLEARED, PROJECT_INTERNAL, ASSOCIATION_PROVIDED}, `approved_by`, `approved_on` ; fragments `*_captioned` : `caption_resolution` obligatoire (légende inscrite au canon, ou abandon éditorial motivé) |
| Contrôle | `make hd-check` (dans `make validate`) : prompts à jour, fichiers présents, SHA-256, ratio, gates, approbations, orphelins |
| Composition | `make layered-compose` : une source `APPROVED` remplace le crop canonique du fragment (même bbox, même couche), identité HD inscrite dans `fragments.lock.yaml` |

## Ce qui passe par ce circuit — et ce qui n'y passe pas

| Voie | Fragments | Route |
|---|---|---|
| **Prompt image** | illustrations et détails documentaires (`documentary_illustration*`, `documentary_detail*`) — 91 fragments | `assets/hd/prompts/` |
| Prompt image, légende à inscrire au canon d'abord | dont 35 fragments `*_captioned` | `caption_resolution` avant `APPROVED` |
| Fond de page | texture papier commune (optionnelle) | `BG-paper_texture` |
| **Jamais par génération d'image** | armoiries et blasons (SVG d'après blasonnement officiel), cartes et plans (redessin vectoriel d'après source documentaire ; plan réel page 10 = autorité), ornements et icônes (SVG), textes raster / cartouches / bandeaux / logo (inscription au canon, couche texte, fichier vectoriel de l'association), couvertures d'ouvrages page 14 (droits), QR (registre) | voir tableau final de chaque `page-NN.md` |

## Cycle

```text
make hd-pack            → dist/hd-pack/ (prompts + crops de référence bruts + zip)
[génération ChatGPT]    → dépôt des PNG sous assets/hd/page-NN/<fragment_id>.png
make hd-ingest          → prototypes/page-NN/hd-sources.yaml (PENDING_REVIEW, SHA, prompt)
[revue humaine]         → status APPROVED + rights + approved_by/on (+ caption_resolution)
make hd-check           → contrôle
make layered-compose && make validate && make build-v3
```

Les briefs d'observation (`briefs.yaml`) décrivent ce qui est visible dans chaque crop ; ils ne
sont pas des assertions historiques. Les prompts sont régénérés par `make hd-prompts` ; ne pas
les éditer à la main. Un fragment régénéré est une **reconstitution** (label `reconstitution`
dans `hd-sources.yaml`) : la mention sur les illustrations, à valider, s'applique.
