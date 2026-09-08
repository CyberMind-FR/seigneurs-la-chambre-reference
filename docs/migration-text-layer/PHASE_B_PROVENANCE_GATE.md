# Phase B — gate provenance et droits — lot suivant

Statut : **INVENTAIRE BLOQUANT**. Ce document ne débloque aucun actif à lui seul.

## Objet

Après le lot QR SVG validé, le prochain travail consiste à distinguer les actifs réellement productibles des actifs qui nécessitent encore une preuve de provenance, de droits ou un brief documentaire. Aucune page raster canonique n'est modifiée par ce lot.

La décision de Phase A impose que chaque actif possède une provenance et des droits renseignés, ou reste explicitement bloqué. Elle interdit également de contourner un blocage de provenance/licence/droits et maintient la page 4 hors production.

## Lot déjà débloqué et produit

Les QR déterministes issus de `qr_registry.yaml` constituent le premier lot fonctionnel. Ils sont générés en SVG, verrouillés par SHA-256 et validés par décodage machine. Leur production est couverte par `docs/migration-text-layer/PHASE_B_QR_BATCH.md` et `manifest-v3.yaml`.

## Page 10 — état documentaire précis

| zone | actif | source actuelle | état | action nécessaire |
|---|---|---|---|---|
| `P10-Z02` | Vue principale du Château de Notre-Dame-du-Cruet | `assets/page-10.jpg` comme référence de composition | `READY_AFTER_AMENDMENT_AND_LABEL` dans la spécification validée | Ne rien produire automatiquement. Conserver la nature `reconstitution`; vérifier le brief documentaire avant production. |
| `P10-Z03` | Plan du château fondé sur la source réelle | `assets/reference/page-10-plan-reel.jpg` | `BLOCKED_RIGHTS` | Documenter l'origine institutionnelle et les droits de reproduction avant tout SVG diffusé. La géométrie du plan réel reste l'autorité. |
| `P10-Z07` | QR Google Maps | `qr_registry.yaml` | produit et validé | Aucun déblocage supplémentaire requis tant que le payload ne change pas. |
| autres zones P10 | armoiries, figure mariale, chronologie/pictogrammes, carte/localisation, panorama | principalement `assets/page-10.jpg` comme référence de composition | bloqué provenance/amendement selon `ASSET_SPEC.md` | Ne pas produire tant que la provenance/brief et les droits ne sont pas documentés. |

### Règle spécifique au plan P10-Z03

Le fichier `assets/reference/page-10-plan-reel.jpg` peut être utilisé comme **autorité géométrique interne** pour préparer le travail, mais son statut actuel ne permet pas de conclure à un droit de reproduction/diffusion. Aucun traçage SVG destiné à la release ne doit donc être committé avant résolution de `BLOCKED_RIGHTS`.

## Actifs ornementaux

La nature `ornement` ne suffit pas à lever un blocage. Lorsque `ASSET_SPEC.md` indique seulement le JPEG de page comme référence de composition et signale une provenance documentaire distincte non enregistrée, l'actif reste bloqué. On ne transforme pas silencieusement la référence raster en licence de redessin.

## Page 4

`PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` reste bloquant. Inventaire autorisé uniquement. Aucun actif éditorial ou architectural nouveau ne doit être produit.

## Critère de passage READY

Un actif documentaire ou de reconstitution ne passe à `READY` que si les champs suivants peuvent être remplis sans supposition :

1. `source` ou brief documentaire identifié ;
2. provenance explicite ;
3. licence ou base de droits explicite ;
4. droits de reproduction, impression, web et dérivation explicités selon le cas ;
5. nature (`document`, `reconstitution`, `ornement`, `functional`) confirmée ;
6. classe technique et slot conformes à `assets/ASSET_SPEC.md` ;
7. absence de texte incrusté ;
8. pour un raster, dimension minimale conforme au slot et aux ppi cibles ;
9. SHA-256 calculé après production ;
10. validation globale `pass` avant admission dans une composition.

## Décision du lot

**Aucun actif documentaire supplémentaire n'est déclaré READY par simple inférence.** Le prochain déblocage nécessite soit une source déjà présente dans le dépôt avec droits documentés, soit une décision humaine ajoutant la provenance/licence manquante.

Cette politique est volontairement conservatrice : elle permet de poursuivre la migration sans fabriquer de fausse certitude historique ou juridique.
