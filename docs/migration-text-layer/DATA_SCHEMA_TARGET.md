# Phase 1 — schéma de données cible

## Principe

Le schéma est une **extension**. Dans la phase suivante, `canonical_text` reste inchangé et constitue l'unique texte rendu. Les métadonnées de composition indiquent où placer des segments ; elles ne recopient pas les phrases.

## Extension proposée d'une page

```yaml
schema_version: 2
page: 11
type: site
content_locked: true
canonical_text: |-
  # valeur existante, strictement inchangée

composition:
  template: site
  segmentation:
    mode: paragraph_index
    roles:
      - {id: title, paragraph: 0}
      - {id: subtitle, paragraph: 1}
      - {id: narrative, paragraphs: [2, 3]}
      - {id: map_and_location, paragraphs: [4]}
      - {id: characteristics, paragraphs: [5]}
  slots:
    - {id: identity, asset_ref: coat_of_arms_la_chambre}
    - {id: hero, asset_ref: page_11_tower_main}
    - {id: map, asset_ref: page_11_map}
    - {id: qr_navigation, qr_ref: "11/google_maps"}

output_policy:
  allowed_formats: [A5, A4_imposed, A2, A1]
  minimum_effective_ppi: 300
  page_04_lock: false
```

Les indices ci-dessus illustrent la mécanique et devront être générés/validés contre le vrai découpage ; ils ne sont pas ajoutés à `pages/11.yaml` dans cette phase.

Pour la page 4 :

```yaml
composition:
  blocked: true
  blocker: PAGE_04_EDITORIAL_ARBITRATION_REQUIRED
```

Pour la page 16, l'extension ajoute `type: page_finale` tout en conservant provisoirement `role: page_finale` pour compatibilité. Cette normalisation ne sera appliquée qu'en phase 2 ou ultérieure.

## Manifeste d'actif cible

```yaml
assets:
  page_11_tower_main:
    path: assets/photos/page-11-tour.tif
    kind: photo
    sha256: "..."
    pixel_size: [0, 0]
    color_space: RGB
    icc_profile: "..."
    source:
      institution: "..."
      reference: "..."
      capture_date: "..."
    rights:
      holder: "..."
      license: "..."
      redistribution: false
      print_authorized: false
    derivatives:
      print_cmyk:
        generated: true
        profile: "nom exact fourni par l'imprimeur"
        encoding: "JPEG 4:4:4 ou TIFF lossless selon kind"
```

Les valeurs `...`, `0` et `false` signifient « données manquantes / non autorisées » ; le build bloque au lieu de les compléter. Aucun exemple de provenance n'est présenté comme fait.

## Registre QR

`qr_registry.yaml` reste l'unique source des payloads. Une page cible ne contient que `qr_ref`. Les champs `payload` et `asset` actuellement dupliqués dans `pages/NN.yaml` restent lisibles pendant la transition, mais un validateur exige leur égalité exacte avec le registre. Ils ne sont pas utilisés au rendu v2.

Schéma logique du registre :

```yaml
qr:
  generator: segno
  error_level: M
  dark: "#000000"
  light: "#FFFFFF"
  quiet_zone_modules: 4
  output: SVG
```

Le niveau de correction devra être validé sur dimensions physiques avant gel ; `M` est celui du banc, pas une décision canonique.

## Données globales et source unique

L'annexe demande qu'un auteur, un taux, un prix ou une adresse n'existe qu'à un endroit. Le dépôt courant contient ces valeurs dans plusieurs `canonical_text`, eux-mêmes verrouillés. Les factoriser maintenant réécrirait le canon et violerait la contrainte de migration.

Décision de phase 1 :

- ne pas factoriser sans autorisation éditoriale ;
- ajouter d'abord des assertions de cohérence sur les occurrences ;
- proposer ultérieurement un fichier `data/facts.yaml` et des expressions de substitution seulement si la Commission autorise cette évolution de la source de vérité ;
- conserver un snapshot signé du texte avant/après et exiger une extraction PDF identique.

Tant que cet arbitrage n'est pas rendu, « corriger une faute = une seule ligne YAML » est démontrable pour une occurrence de page, mais pas pour une valeur globale répétée. Ce critère d'acceptation reste partiellement bloqué.

## Validation de schéma proposée

Le validateur v2 doit refuser :

- une page sans `canonical_text` verrouillé ;
- un segment hors limites ou utilisé deux fois sans déclaration explicite ;
- un texte littéral dans un gabarit ;
- un actif sans SHA, provenance, licence ou droit d'impression ;
- un `qr_ref` absent du registre ;
- une couleur/forme de QR non conforme ;
- un raster déclaré comme texte, carte, plan, blason, filet ou chronologie ;
- une page 4 non bloquée avant arbitrage ;
- une sortie dont le ppi effectif est inférieur au seuil.
