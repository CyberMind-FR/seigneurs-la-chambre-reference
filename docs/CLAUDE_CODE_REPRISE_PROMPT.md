# Prompt de reprise pour Claude Code

Tu reprends le projet éditorial **« Les Seigneurs de La Chambre et leur patrimoine en Maurienne »** dans le dépôt GitHub :

`CyberMind-FR/seigneurs-la-chambre-reference`

Branche de référence :

`release/v3.0-phase-b`

Ta mission est de **terminer la migration et la mise en page v3**, en prenant en charge tout ce qui relève du code, de la composition, du découpage déterministe, des mesures, des PDF, de la CI et des validations.

ChatGPT n'est plus le moteur principal de mise en page. Il reste réservé aux besoins visuels spécifiques : refaire un croquis, une illustration, une reconstitution graphique ou une image qui manque réellement. Tu ne dois donc pas dépendre de ChatGPT pour la composition des pages.

## Règle absolue

Le dépôt GitHub est l'unique source de vérité.

Ne jamais inventer de texte, nom, personne, date, fonction, source, lieu, élément architectural, logo, QR, taux, citation ou contenu documentaire.

Ne jamais modifier silencieusement le canon.

Avant toute intervention, lire obligatoirement dans cet ordre :

1. `REGENERATION_RULES.md`
2. `WORK_HANDOFF.md`
3. `corrections.yaml`
4. `manifest.yaml`
5. `manifest-pages.json`
6. `manifest-v3.yaml`
7. `sources/PROVENANCE_INDEX.yaml`
8. `assets/ASSET_INDEX_V3.yaml`
9. `assets/ASSET_SPEC.md`
10. `pages/NN.yaml`
11. `qr_registry.yaml`
12. `docs/migration-text-layer/PHASE_A_APPROVAL.md`
13. `docs/migration-text-layer/PHASE_B_PAGE03_LAYERED_PROTOTYPE.md`

Inspecte également les branches de prototype existantes, notamment :

- `prototype/v3-page03-object-map`
- `prototype/v3-layered-page-03`

et compare-les avec `release/v3.0-phase-b` avant de reprendre quoi que ce soit.

## État réel du projet

Le prototype multicouche de la page 03 a déjà été exécuté de bout en bout.

État documenté dans `WORK_HANDOFF.md` :

- 11 fragments raster extraits depuis `assets/page-03.jpg` ;
- 25 blocs canoniques présents dans le PDF final ;
- vraie couche texte : PASS ;
- QR final décodé machine : PASS ;
- SHA fragments : PASS ;
- source canonique inchangée : PASS ;
- inspection visuelle effectuée ;
- résultat global : `PASS_WITH_RESOLUTION_BLOCKER`.

Le bloqueur identifié est la résolution des rasters hérités : la page 03 canonique fait seulement 1024 × 1536 px et donne environ 185,78 ppi à l'échelle A5 du prototype, sous le gate 300 ppi.

Ce bloqueur ne remet pas en cause la méthode de composition. Ne jamais faire passer un upscale pour une récupération réelle de détail.

## Méthode de composition à conserver

La v3 repose sur une composition multicouche :

`fond -> fragments raster -> vecteurs utiles -> vraie couche texte -> QR déterministe final`

Le JPEG canonique sert :

- de référence visuelle ;
- de source de fragments lorsque nécessaire ;
- jamais de page finale aplatie.

La structure de page doit rester fidèle à la référence canonique.

## Important : ne pas confondre zones macro et objets réels

Les zones historiques de `assets/ASSET_SPEC.md` sont des zones fonctionnelles de mise en page. Elles ne constituent pas une liste exhaustive d'objets à extraire.

Pour la production, utiliser une granularité :

`page -> régions -> objets -> sous-objets -> couches`

La page 03 a déjà fait l'objet d'une cartographie plus fine dans :

`prototype/v3-page03-object-map/prototypes/page-03/page-03.objects.yaml`

Cette logique doit être généralisée aux autres pages.

## Zones texte

Les zones texte doivent être traitées comme des objets à part entière, indépendants des images.

Pour chaque page :

- détecter et cartographier les blocs texte visuels ;
- associer chaque bloc à son contenu canonique dans `pages/NN.yaml:canonical_text` ;
- conserver titre, sous-titre, intertitres, paragraphes, légendes, coordonnées, mentions pratiques et sources comme vraie couche texte ;
- ne jamais utiliser l'OCR comme autorité éditoriale ;
- ne jamais conserver du texte raster si le même texte peut être recomposé proprement ;
- ne jamais recopier visuellement un texte absent du YAML sans validation explicite ;
- toute différence entre texte visible et texte canonique doit être signalée, pas corrigée silencieusement.

Pour les textes intrinsèques à un document graphique, par exemple une carte ancienne, les conserver dans le raster si cela fait partie du document lui-même.

## QR

Les QR sont fonctionnels et déterministes.

Règles :

- source unique des payloads : `qr_registry.yaml` ;
- utiliser les SVG présents dans `assets/qr-svg/` ;
- ne jamais recadrer ou styliser un QR depuis un JPEG ;
- rendre le QR en dernier ;
- décoder le QR depuis le rendu PDF final ;
- vérifier l'égalité exacte du payload.

## Pages canoniques et verrous

Ordre final des 16 pages :

1. Cover
2. Les Seigneurs de La Chambre
3. Le Couvent des Cordeliers
4. La Maison de La Tour
5. Le Château Joli
6. La Tour de Burgin
7. La Tour de Châtel-André
8. La Maison-Forte du Châtelet
9. La Maison-Forte de Gruyère
10. Le Château de Notre-Dame-du-Cruet
11. La Tour de Notre-Dame-du-Cruet
12. La Maison Forte de La Landonnière
13. Un patrimoine à préserver
14. L’Association
15. Back / résumé exposition
16. Merci / remerciements

Verrous :

### Page 4

`PAGE_04_EDITORIAL_ARBITRATION_REQUIRED`

Ne pas recomposer cette page tant que le verrou n'est pas explicitement levé.

Aucune mention :

- `Académie de Maurienne`
- `Université de Maurienne`

Texte canonique prévu :

`Aujourd'hui, la Maison de La Tour demeure un remarquable témoin de l'histoire administrative de la Maurienne.`

### Page 10

Le plan réel :

`assets/reference/page-10-plan-reel.jpg`

reste l'autorité géométrique.

Toute nouvelle reconstitution doit respecter :

- Tour de guet
- Basse cour
- Porte d’entrée
- Tour porte
- Tour ronde
- Tour carrée
- Cour haute
- Logis
- Donjon
- Fossé

Dimensions canoniques à respecter lorsqu'elles sont utilisées :

- donjon : 16 × 11,5 m ;
- murs : 2,5 m ;
- tour-porte : 8 m.

Ne jamais inventer de volumétrie ou de décor architectural non sourcé.

### Page 13

Six QR ressources, déterministes, alignés, payloads exacts du registre.

### Page 14

Le portrait de Philippe DEMARIO reste supprimé.

Ne jamais le réintroduire ni mettre un portrait de remplacement.

### Fondation du Patrimoine

Toujours 66 %, jamais 75 %.

### Auteurs

Toujours :

`Fabrice GALOPO, André GRANGE, Gérald KERMA`

## Famille de pages à industrialiser en priorité

À partir du prototype page 03, terminer d'abord les pages :

- 05
- 06
- 07
- 08
- 09
- 11
- 12

Pour chacune :

1. mesurer le raster canonique ;
2. produire un diagnostic visuel ;
3. créer un inventaire objet par objet ;
4. cartographier séparément toutes les zones texte ;
5. faire valider ou au minimum inspecter les crops sémantiques ;
6. extraire les fragments approuvés ;
7. créer le fond ;
8. recomposer les textes depuis YAML ;
9. injecter le QR SVG final ;
10. produire le PDF de contrôle ;
11. valider texte, QR, SHA, résolution et fidélité visuelle.

## Compositeur

Le prototype page 03 doit devenir un compositeur générique piloté par YAML.

Objectif : éviter un script spécifique par page.

Le compositeur doit accepter au minimum :

- dimensions de page ;
- fond ;
- liste de fragments ;
- bbox source et bbox destination ;
- ordre de couches ;
- styles de texte ;
- blocs de texte ;
- ornements ;
- QR ;
- règles de validation.

Le YAML doit permettre de reconstruire une page sans toucher au code métier.

## Style

Respecter `style.yaml` et la référence canonique.

Style SpiritualCept :

- fond blanc/ivoire imprimable ;
- grain discret ;
- sépia / brun-noir ;
- titres rouge-brun ;
- bleu/or uniquement pour l'héraldique ;
- gravure, graphite, fusain, plume ;
- couleurs douces pastel/craie/aquarelle ;
- cadres fins ;
- ornements retenus ;
- forte lisibilité d'impression.

Ne jamais « améliorer » une page au point de changer sa structure ou son identité.

## ChatGPT : rôle limité

Tu dois pouvoir terminer la composition sans ChatGPT.

Faire appel à ChatGPT uniquement lorsqu'un actif visuel doit réellement être créé ou repris :

- croquis ;
- illustration ;
- reconstitution graphique ;
- dessin architectural ;
- restauration visuelle ;
- nouvel actif illustratif validé par le projet.

Dans ce cas :

1. définir un brief précis ;
2. indiquer la page et la zone ;
3. fournir les sources nécessaires ;
4. exiger une image sans texte ;
5. ne jamais demander à ChatGPT de générer un QR ;
6. ne jamais demander à ChatGPT de réécrire le contenu canonique.

Les actifs retournés par ChatGPT restent soumis à validation humaine, provenance, SHA et enregistrement dans les registres.

## Résolution

Pour chaque raster, mesurer la résolution effective à la taille de placement réelle.

Gates actuels :

- A5 : 300 ppi
- A2 : 180 ppi
- A1 : 150 ppi

Si un raster est sous le seuil :

1. rechercher une source HD ;
2. réduire sa taille de placement ;
3. demander une validation explicite d'un seuil inférieur ;
4. vectoriser uniquement si cela peut être fait sans dérive documentaire ;
5. ne jamais tricher avec un upscale présenté comme source HD.

## Validation et CI

Après chaque lot :

- recalculer les SHA ;
- mettre à jour les registres ;
- exécuter `make sync` ;
- exécuter `make validate` ;
- exécuter les validateurs spécifiques aux actifs ;
- produire `make build` pour le contrôle imprimable ;
- valider les QR du PDF final ;
- vérifier que le PDF possède une vraie couche texte ;
- inspecter visuellement le rendu.

Ne jamais committer `dist/`, PDF générés, ZIP ou planches contact sur `main` sauf règle explicite différente déjà présente dans le dépôt.

## Git

Travaille sur des branches dédiées et petites.

Ne merge rien automatiquement dans `main` sans :

- tests verts ;
- validation visuelle ;
- absence de régression canonique ;
- QR vérifiés ;
- texte vérifié ;
- SHA synchronisés.

Avant tout merge final de Phase B, vérifier la divergence avec `main` et rebaser/merger proprement.

## Livrable attendu

Tu dois mener le projet jusqu'à un état où les 16 pages peuvent être générées de façon reproductible depuis le dépôt, avec :

- vraie couche texte ;
- images/fragments séparés ;
- QR déterministes ;
- composition fidèle ;
- validations automatiques ;
- rapports de résolution ;
- manifests à jour ;
- aucune invention documentaire.

## Première action à exécuter

1. `git fetch --all --prune`
2. checkout `release/v3.0-phase-b`
3. lire tous les fichiers de référence listés ci-dessus
4. inspecter le prototype page 03 et `prototype/v3-page03-object-map`
5. exécuter les tests actuels avant modification
6. produire un court diagnostic :
   - ce qui est déjà industrialisable ;
   - ce qui manque au compositeur générique ;
   - état réel des pages 05, 06, 07, 08, 09, 11, 12 ;
   - blocages de résolution ;
   - blocages éditoriaux ou de droits
7. puis commencer immédiatement l'industrialisation de la famille « site » sans attendre une nouvelle validation si aucune contradiction avec le canon n'est détectée.

## Format de compte rendu

À chaque étape importante, répondre sous la forme :

`Fichiers concernés -> modification appliquée -> validations exécutées -> résultat -> prochain blocage éventuel`

Ne jamais annoncer un test ou un commit qui n'a pas réellement été exécuté.