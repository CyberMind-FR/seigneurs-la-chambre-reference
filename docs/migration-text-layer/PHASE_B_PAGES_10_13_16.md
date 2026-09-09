# Phase B — pages 10 et 13 à 16 : composition multicouche et validation

## Statut

**COMPOSÉ ET VALIDÉ le 2026-09-09 (gkerma, « Go, page 10 puis 13 à 16 »)** — pages 10, 13, 14, 15 en
`PASS_WITH_RESOLUTION_WAIVER` (dérogation A5), page 16 en `PASS_WITH_RESOLUTION_BLOCKER`
(raster 768×1024, 131,8 ppi, sous la dérogation de 180 ppi : blocage rapporté, aucun upscale).

Avec ce lot, **15 pages sur 16 sont composées** par le compositeur générique (03, 05–16).
Restent la couverture (01), la page dynastique (02) et la page 04 sous verrou éditorial.

## 1. Verrous respectés

- **Page 10** : aucune nouvelle reconstitution. Le plan et les vues sont des fragments de la page
  canonique validée ; les libellés du plan (Tour de guet, Basse cour, Porte d'entrée, Tour porte,
  Tour ronde, Tour carrée, Cour haute, Logis, Donjon, Fossé) sont intrinsèques au document et
  conformes au plan réel. `P10-Z03` (tracé du plan réel) reste `BLOCKED_RIGHTS`, non utilisé.
- **Page 13** : six QR SVG du registre, décodés depuis le rendu final avec payload exact, alignés
  sur les coordonnées canoniques normalisées, rendus en dernier.
- **Page 14** : l'ancien emplacement du portrait reste vide (aucun fragment, aucun remplacement) ;
  le nom « Philippe DEMARIO » du canon est composé sous le bandeau ; les trois couvertures
  d'ouvrages (`P14-Z07..Z09`, droits non documentés) sont inventoriées, **non extraites**.
- **Page 16** : le QR association vient du registre ; le logo visible dans la page canonique est
  repris comme fragment raster (l'actif vectoriel officiel reste `BLOCKED_SOURCE_ASSET`).
- Fondation du Patrimoine : 66 % partout ; auteurs : Fabrice GALOPO, André GRANGE, Gérald KERMA.

## 2. Outils ajoutés au compositeur pour ce lot

- `mask_fill: border_median` — masque d'un ancien texte raster à la couleur échantillonnée du
  cartouche (bandeaux rouges/bleus des pages 14 et 15), texte canonique composé en blanc.
- Césure uniquement aux traits d'union du canon (`embeddedHyphenation`), jamais de coupure
  arbitraire de mot ; ajustement de la taille aussi en largeur (mot le plus long) ; la validation
  de la couche texte accepte une coupure de ligne après un trait d'union canonique.
- Décodage QR sur plusieurs fenêtres/zooms (six QR voisins en page 13).
- Fontes TrueType déclarées dans `prototypes/_shared/text-styles.yaml` (DejaVu Serif pour le
  « ᵉ » U+1D49 du sous-titre page 15, absent de Times base-14).

## 3. Résultat par page

| Page | Titre | Fragments | Bloqués | Blocs canon | Couche texte | QR (n / décodage) | Collisions | ppi min A5 | Gate |
|---|---|---:|---:|---:|---|---|---:|---:|---|
| 10 | Le Château de Notre-Dame-du-Cruet | 18 | 0 | 26 | PASS | 1 / PASS | 0 | 181.06 | `PASS_WITH_RESOLUTION_WAIVER` |
| 13 | Un patrimoine à préserver | 17 | 0 | 20 | PASS | 6 / PASS | 0 | 181.06 | `PASS_WITH_RESOLUTION_WAIVER` |
| 14 | L'Association | 14 | 3 | 26 | PASS | 0 / PASS | 0 | 181.06 | `PASS_WITH_RESOLUTION_WAIVER` |
| 15 | Dos / synthèse | 27 | 0 | 27 | PASS | 0 / PASS | 0 | 181.06 | `PASS_WITH_RESOLUTION_WAIVER` |
| 16 | Merci | 8 | 0 | 11 | PASS | 1 / PASS | 0 | 131.81 | `PASS_WITH_RESOLUTION_BLOCKER` |

## 4. Écarts et décisions consignés

| Page | Type | Fragment | Description |
|---|---|---|---|
| 10 | texte raster hors canon | `running_head_raster` | bandeau courant |
| 10 | texte raster hors canon | `heraldry_captioned` | légende des armoiries |
| 10 | texte raster hors canon | `marian_figure_captioned` | légende « Notre-Dame-du-Cruet, protectrice du château et de la vallée » |
| 10 | texte raster hors canon | `plan_box_captioned` | titre « Plan du château (XIe-XVe siècle) » et libellés du plan (intrinsèques au document) |
| 10 | texte raster hors canon | `chronology_box_captioned` | titre « Chronologie du château », dates et libellés des cinq événements |
| 10 | texte raster hors canon | `map_document` | toponymes intrinsèques de la carte |
| 10 | canon ≠ raster | — | le raster porte « Imposéeevause au XIe siècle » (défaut) là où le canon dit « Imaginez-vous au XIe siècle » : le canon prévaut |
| 10 | canon ≠ raster | — | le raster porte « Paroisse de Notre-Dame-du-Cunet » (défaut) là où le canon dit « Notre-Dame-du-Cruet » : le canon prévaut |
| 13 | texte raster hors canon | `running_head_raster` | bandeau courant |
| 13 | texte raster hors canon | `heraldry_captioned` | légende des armoiries |
| 13 | texte raster hors canon | `map_composite` | toponyme « La Maurienne » et repères numérotés (intrinsèques à la carte) |
| 13 | texte raster hors canon | `association_cartouche` | « LES AMIS DU COUVENT DES CORDELIERS DE LA CHAMBRE » |
| 13 | canon ≠ raster | — | les cinq libellés de sites autour de la carte sont formulés différemment dans le raster (« Couvent des Cordeliers / Maison de La Tour »…) : masqués, les puces canoniques sont composées à leur place |
| 13 | canon ≠ raster | — | les libellés des ressources du raster ne portent pas les domaines (résidus « r », « fo », « g », « fr ») : les blocs canoniques complets (libellé : domaine) sont composés |
| 13 | canon ≠ raster | — | « la Maurienne fut d'abord chambrienne. » est en rouge centré dans le raster ; fin du bloc 2 dans le canon, composé en corps |
| 14 | texte raster hors canon | `heraldry_captioned` | légende des armoiries |
| 14 | texte raster hors canon | `seal_left` | sceau PATRIMOINE MAURIENNE (intrinsèque) |
| 14 | texte raster hors canon | `seal_right` | sceau des Cordeliers (intrinsèque) |
| 14 | canon non visible dans le raster | — | bloc 12 « Philippe DEMARIO » : le nom est dans le canon mais n'apparaît pas en texte dans le raster (portrait supprimé, nom conservé par le canon) ; composé sous le bandeau AUTEUR DE RÉFÉRENCE |
| 14 | droits | — | P14-Z07..Z09 couvertures d'ouvrages : non extraites (BLOCKED_SOURCE_RIGHTS) ; la zone reste vide dans le proof jusqu'à documentation des droits |
| 14 | zone vide verrouillée | — | ancien emplacement du portrait de Philippe DEMARIO : aucun fragment, aucun remplacement (P14-Z06 LOCKED_VOID) |
| 14 | typographie | — | bandeaux rouges à texte blanc : ancien texte masqué à la couleur du cartouche (mask_fill: border_median), titre canonique composé en blanc |
| 15 | texte raster hors canon | `seal_left` | sceau PATRIMOINE MAURIENNE (intrinsèque) |
| 15 | texte raster hors canon | `site_01` | repères numérotés 1..10 intrinsèques aux vignettes |
| 15 | typographie | — | bandeaux colorés à texte blanc : ancien texte masqué à la couleur du cartouche, texte canonique composé en blanc |
| 15 | typographie | — | sous-titre composé en DejaVu Serif (le « ᵉ » U+1D49 n'existe pas dans Times base-14) ; fonte du projet toujours à verrouiller |
| 16 | texte raster hors canon | `logo_raster` | texte intrinsèque du logo |
| 16 | texte raster hors canon | `qr_caption_raster` | « En savoir plus sur l'association et nos actions » |
| 16 | canon non visible dans le raster | — | bloc 8 « Les Amis du Couvent des Cordeliers de La Chambre » n'apparaît qu'à travers le logo dans le raster ; composé sous le logo |
| 16 | résolution | — | raster canonique 768x1024 = 131,8 ppi en A5, sous la dérogation (180) : blocage rapporté, aucun upscale |

## 5. Points éditoriaux ouverts (remarques du 2026-09-09)

1. **Mention sur les illustrations** (à rédiger et valider, non composée) : l'échelle des plans n'est
   pas respectée ; les vues sont des interprétations artistiques, non nécessairement réalistes, en
   l'absence d'archives d'époque ; l'état actuel des ruines de certains sites diffère des vues.
   Proposition de formulation soumise à arbitrage (PROPOSITION, hors canon) :
   > « Les illustrations de ce livret sont des évocations artistiques. En l'absence d'archives
   > iconographiques d'époque, les vues et plans ne sont pas à l'échelle et ne prétendent pas à
   > l'exactitude ; l'état actuel de certains sites, parfois réduits à des ruines, peut différer
   > des vues présentées. »
   Emplacement candidat : page 15 (mentions légales) ou page 16 ; à inscrire dans
   `pages/NN.yaml:canonical_text` et `corrections.yaml` après validation, puis composer.
2. **Armoiries réelles des communes** : rechercher les blasons officiels et, lorsque c'est possible
   (source et droits établis, provenance enregistrée), remplacer les armoiries de La Chambre en tête
   des pages de sites par celles de la commune concernée : Sainte-Marie-de-Cuines (05, 06),
   Saint-Étienne-de-Cuines (07, 08, 09), Notre-Dame-du-Cruet (10, 11), Saint-Rémy-de-Maurienne (12),
   La Chambre (03, 04). Gate : `sources/PROVENANCE_INDEX.yaml` + `assets/ASSET_INDEX_V3.yaml`
   (source, licence, SHA) avant toute production ; rendu SVG d'après blasonnement officiel de
   préférence à la copie d'un dessin externe.

## 6. Prochaines étapes

1. Pages 01 (couverture) et 02 (dynastie / blasonnement) avec le même compositeur.
2. Arbitrage des deux points éditoriaux ci-dessus (mention illustrations, armoiries communales).
3. Sources HD pour la page 16 (132 ppi) ou validation explicite d'un seuil inférieur pour cette page.
4. Droits des couvertures d'ouvrages (page 14) et du logo officiel (page 16).
5. Page 04 : attente de levée du verrou éditorial.
