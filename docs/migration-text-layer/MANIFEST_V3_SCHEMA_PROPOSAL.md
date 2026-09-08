# Release v3.0 — proposition de schéma du manifeste

> **Statut : PROPOSITION À VALIDER — NON APPLIQUÉE À `manifest.yaml`.**
>
> Ce document décrit l’extension de schéma nécessaire à la Phase A. Il ne modifie pas encore le manifeste canonique actuel. La migration effective du fichier `manifest.yaml` ne pourra intervenir qu’après validation humaine de la Phase A et de l’amendement au canon.

## 1. Objectifs du schéma v3

Le manifeste v3 doit permettre de répondre, pour chaque actif, à cinq questions sans inférence :

1. **Qu’est-ce que c’est ?** — classe technique et nature documentaire ;
2. **D’où cela vient-il ?** — provenance et sources ;
3. **A-t-on le droit de l’utiliser ?** — licence et droits ;
4. **Est-il techniquement suffisant ?** — dimensions, placement maximal et ppi ;
5. **Peut-il entrer dans la release ?** — état des validations et blocages.

Le schéma est une **extension** du manifeste actuel. Les 16 entrées de pages et leurs SHA-256 restent conservés pendant la transition.

## 2. Structure top-level proposée

```yaml
schema_version: 3
project: Les Seigneurs de La Chambre
release: v3.0.0
status: proposal

pages:
  - page: 1
    file: assets/page-01.jpg
    sha256: "<sha256 existant>"
    role: reference_raster
  # ... pages 2 à 16, sans changement de contenu canonique

assets:
  <asset_id>:
    # fiche d'actif, voir section 3

qr:
  registry: qr_registry.yaml
  generator: segno
  output: svg
  dark: "#000000"
  light: "#FFFFFF"
  quiet_zone_modules: 4

fonts:
  <font_id>:
    # fiche de fonte, voir section 8

build_contract:
  text_source: pages/NN.yaml:canonical_text
  illustrations_must_be_text_free: true
  qr_payload_source: qr_registry.yaml
  unknown_metadata_policy: block
```

`status: proposal` est retiré ou remplacé uniquement lorsque le schéma et ses données sont effectivement validés.

## 3. Fiche d’actif atomique

Chaque objet graphique réellement placé doit avoir un identifiant stable. Une zone visuelle composite peut donc référencer plusieurs actifs atomiques.

```yaml
assets:
  page_10_castle_main:
    id: page_10_castle_main
    pages: [10]
    zones: [P10-Z02]

    nature: reconstitution        # document | reconstitution | ornement | functional
    class: raster                 # raster | svg | qr
    kind: illustration            # illustration | photo | plan | map | heraldry | ornament | timeline | qr | other

    path: assets/illus/page-10-castle-main.tif
    sha256: null

    production:
      method: null                # generated | redrawn | restored | traced | captured | supplied | deterministic
      brief: null
      text_free_required: true
      generated_at: null
      toolchain: []

    provenance:
      status: missing             # verified | partial | missing | not_applicable
      sources:
        - path: assets/reference/page-10-plan-reel.jpg
          role: geometry_reference
          reference: null
          institution: null
          author: null
          date: null
          notes: null

    licence:
      status: missing             # verified | missing | not_applicable
      identifier: null
      text_or_url: null
      holder: null

    rights:
      status: missing             # cleared | restricted | missing | not_applicable
      redistribution: null
      print_authorized: null
      web_authorized: null
      derivative_authorized: null
      notes: null

    dimensions:
      pixel_width: null
      pixel_height: null
      placement_max_mm: 360
      ppi_cible:
        A5: 300
        A2: 180
        A1: 150
      required_width_px_with_margin: 3189
      safety_factor: 1.5

    color:
      source_space: null
      source_icc: null
      print_derivative_space: null
      print_icc: null

    validation:
      documentary: pending
      rights: pending
      text_free: pending
      sha256: pending
      resolution: pending
      visual: pending
      overall: blocked
      blockers:
        - PROVENANCE_REQUIRED
        - RIGHTS_REQUIRED
```

Les valeurs `null`, `missing` et `pending` sont des états explicites. Elles ne doivent jamais être complétées automatiquement avec une supposition.

## 4. Champs obligatoires

### 4.1 Toujours obligatoires

Pour tout actif :

- `id`
- `pages`
- `zones`
- `nature`
- `class`
- `kind`
- `path` ou, pour un QR, une dérivation explicite depuis le registre
- `sha256` dès que le fichier existe
- `production.method`
- `provenance.status`
- `licence.status`
- `rights.status`
- `validation.overall`

### 4.2 Obligatoires pour un raster

- `dimensions.pixel_width`
- `dimensions.pixel_height`
- `dimensions.placement_max_mm`
- `dimensions.ppi_cible`
- `dimensions.required_width_px_with_margin`
- `dimensions.safety_factor`
- espace colorimétrique source connu ou statut bloquant explicite

### 4.3 Obligatoires pour un SVG

- SHA-256 du SVG final ;
- `text_free_required: true` ;
- validation garantissant l’absence de texte littéral et de glyphes convertis artificiellement pour contourner cette règle ;
- provenance et droits lorsque le SVG reproduit une source documentaire.

### 4.4 Obligatoires pour une reconstitution

- `nature: reconstitution` ;
- au moins une source ou un brief documentaire validé ;
- statut documentaire `verified` ou `partial` explicitement accepté humainement ;
- mention de reconstitution activée dans la composition ;
- validation qu’aucun détail historique non sourcé n’a été ajouté.

## 5. Nature documentaire

Valeurs proposées :

```yaml
nature:
  enum:
    - document
    - reconstitution
    - ornement
    - functional
```

Interprétation :

- `document` : reproduction/restauration/traçage fondé sur une source identifiée ;
- `reconstitution` : interprétation graphique explicitement déclarée ;
- `ornement` : élément non documentaire, sans assertion historique ;
- `functional` : actif technique, notamment QR.

`functional` n’est pas une autorisation de génération graphique libre : les QR restent dérivés de façon déterministe du registre.

## 6. Provenance, licence et droits

La provenance, la licence et les droits sont séparés pour éviter les raccourcis du type « source connue donc usage autorisé ».

### Provenance

```yaml
provenance:
  status: verified | partial | missing | not_applicable
  sources:
    - path: null
      url: null
      reference: null
      institution: null
      author: null
      date: null
      role: source | geometry_reference | composition_reference | brief_reference
      notes: null
```

Une référence raster de page aplatie peut être indiquée comme `composition_reference`, mais cela ne suffit pas à établir une provenance documentaire pour ce qu’elle représente.

### Licence

```yaml
licence:
  status: verified | missing | not_applicable
  identifier: null
  text_or_url: null
  holder: null
```

### Droits

```yaml
rights:
  status: cleared | restricted | missing | not_applicable
  redistribution: true | false | null
  print_authorized: true | false | null
  web_authorized: true | false | null
  derivative_authorized: true | false | null
  notes: null
```

Pour une sortie imprimée, `print_authorized: true` est requis pour tout actif documentaire soumis à droits. Une valeur `null` bloque le build de release.

## 7. Résolution et placement

Le manifeste stocke le **placement physique maximal**, et non un simple objectif abstrait de pixels.

```yaml
dimensions:
  pixel_width: 3189
  pixel_height: 2400
  placement_max_mm: 360
  ppi_cible:
    A5: 300
    A2: 180
    A1: 150
  safety_factor: 1.5
  required_width_px_with_margin: 3189
```

Formule de Phase A :

```text
required_width_px_with_margin =
  ceil(placement_max_mm / 25.4 × ppi_du_support × safety_factor)
```

Le manifeste documente la cible ; le build mesure ensuite le **ppi effectif réel après placement**. Un upscaling ne modifie jamais le nombre de pixels source utilisé pour ce contrôle.

## 8. Fontes

Les fontes doivent également devenir des actifs manifestés :

```yaml
fonts:
  body_serif:
    path: fonts/<fichier>.ttf
    sha256: null
    family: null
    version: null
    author: null
    licence:
      identifier: null
      text_or_url: null
      redistribution: null
      pdf_embedding: null
    validation:
      embedded: pending
      unicode_map: pending
      rights: pending
      overall: blocked
```

Aucune famille de production n’est choisie par ce schéma. Les fontes du banc d’essai de Phase 1 ne deviennent pas automatiquement canoniques.

## 9. QR

`qr_registry.yaml` reste l’unique source des payloads.

Le manifeste ne duplique pas les URL. Il référence une clé du registre :

```yaml
assets:
  qr_page_10_google_maps:
    id: qr_page_10_google_maps
    pages: [10]
    zones: [P10-Z08]
    nature: functional
    class: qr
    kind: qr
    qr_ref: "10/google_maps"
    generated_path: build/qr/page-10-google-maps.svg
    production:
      method: deterministic
      generator: segno
    validation:
      source_payload_match: pending
      pdf_decode_match: pending
      overall: blocked
```

Le fichier SVG QR est un dérivé de build. Son payload ne doit pas être copié dans cette fiche.

## 10. Cas de page bloquée

Une page peut porter un blocage de production sans modifier son `canonical_text` :

```yaml
page_constraints:
  "04":
    production_blocked: true
    blocker: PAGE_04_EDITORIAL_ARBITRATION_REQUIRED
```

La présence d’actifs inventoriés pour la page 4 ne permet pas leur production tant que ce verrou est actif.

## 11. Ancien emplacement du portrait Philippe DEMARIO

L’absence est manifestée comme contrainte de composition, pas comme actif substituable :

```yaml
page_constraints:
  "14":
    forbidden_slots:
      - id: former_philippe_demario_portrait
        rule: KEEP_EMPTY_NO_REPLACEMENT
```

Aucun `asset_id` ne doit être associé à ce slot.

## 12. États de validation

Valeurs proposées pour `validation.overall` :

```yaml
validation_status:
  enum:
    - blocked
    - pending
    - ready
    - rejected
```

Un actif ne devient `ready` que si tous les contrôles applicables sont verts.

Exemples de codes bloquants :

```text
PROVENANCE_REQUIRED
LICENCE_REQUIRED
RIGHTS_REQUIRED
PRINT_RIGHTS_REQUIRED
SOURCE_REQUIRED
TEXT_DETECTED_IN_ASSET
SHA256_MISMATCH
RESOLUTION_INSUFFICIENT
DOCUMENTARY_REVIEW_REQUIRED
RECONSTRUCTION_LABEL_REQUIRED
PAGE_04_EDITORIAL_ARBITRATION_REQUIRED
```

Les codes ne remplacent pas une explication humaine dans les rapports de validation.

## 13. Règles de validation proposées

Le validateur v3 doit refuser :

1. un actif sans identifiant stable ;
2. un fichier existant sans SHA-256 ;
3. un raster sans dimensions et placement maximal ;
4. une reconstitution sans déclaration `nature: reconstitution` ;
5. un actif documentaire sans provenance ;
6. un actif destiné à l’impression sans droits d’impression établis ;
7. un `qr_ref` absent de `qr_registry.yaml` ;
8. un payload QR dupliqué dans le manifeste ;
9. un SVG ou raster illustratif contenant du texte ;
10. une page 4 rendue tant que son blocage est actif ;
11. un actif attaché au slot interdit de l’ancien portrait page 14 ;
12. un raster dont le ppi effectif est sous le seuil du support ;
13. une fonte non embarquable ou sans droits documentés ;
14. toute valeur documentaire inconnue remplacée par une valeur inventée au lieu de `null` / `missing` / `blocked`.

## 14. Compatibilité de migration

La migration proposée doit être progressive :

1. conserver les champs actuels `page`, `file`, `sha256` ;
2. ajouter `schema_version: 3` et les nouvelles sections sans changer les `canonical_text` ;
3. manifester les actifs au fur et à mesure de leur validation ;
4. maintenir les références raster historiques comme `reference_raster` jusqu’à ce que la page correspondante soit recomposée et validée ;
5. ne supprimer aucune donnée de l’ancien manifeste avant démonstration qu’elle est représentée dans le nouveau schéma.

## 15. Point d’arrêt Phase A

La Phase B reste interdite tant que ne sont pas validés ensemble :

- `assets/ASSET_SPEC.md` ;
- `docs/migration-text-layer/CANON_AMENDMENT_V3_PROPOSAL.md` ;
- le présent schéma ;
- la formulation de la mention de reconstitution ;
- les arbitrages documentaires et de droits nécessaires aux premiers actifs à produire.

**Ce document est une proposition de structure. Il ne constitue pas encore `manifest.yaml` v3.**
