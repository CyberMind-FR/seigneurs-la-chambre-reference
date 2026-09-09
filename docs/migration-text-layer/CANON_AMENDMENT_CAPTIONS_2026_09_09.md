# Amendement du canon — légendes raster inscrites (2026-09-09)

## Statut

**APPLIQUÉ le 2026-09-09 sur ordre du propriétaire** (gkerma : « Go, inscris les 35 légendes au canon »).
Relecture des transcriptions par le propriétaire attendue (voir §3). Entrée de traçabilité :
`corrections.yaml:captions_inscribed_2026_09_09`.

## 1. Portée

Les légendes, callouts et cartouches visibles dans les 35 illustrations régénérables
(rôle `documentary_illustration_with_canonical_raster_caption` et `documentary_detail_with_canonical_raster_caption`,
hors encadré chronologie p10 déjà exclu) deviennent des blocs de `pages/NN.yaml:canonical_text`.
Ils sont ajoutés **en fin de texte canonique** (l'indexation des blocs existants ne change pas),
composés en couche texte (`text_blocks` avec `caption_of`) et le texte raster correspondant est
masqué dans les fragments (`mask_px` avec remplissage `paper` ou `border_median`).

| Pages | Fragments | Blocs ajoutés |
|---|---:|---:|
| 01, 02, 03, 05, 06, 07, 08, 09, 10, 11, 12 | 35 | 68 |

Non concernés : les 11 légendes d'armoiries (`heraldry_with_canonical_raster_caption`, voie SVG),
les bandeaux courants, pieds de page, cartouche association, logo, encadré chronologie p10.

## 2. Méthode

Transcription visuelle de chaque légende à agrandissement ×3 avec grille de coordonnées (jamais
d'OCR comme autorité). Graphies conservées telles que visibles. Les masques ne couvrent que le
texte raster ; les flèches dessinées et les cadres de cartouche restent dans les fragments. Trois
légendes posées sur un lavis masqué (`border_median`) sont déclarées `allow_ink_overlap` : le
remplissage médian est compté comme encre par le contrôle de collision.

Conséquence Phase C : ces 35 fragments passent en voie `prompt_image` (légende au canon) ; leur
approbation HD n'exige plus `caption_resolution` (`assets/hd/prompts`, `scripts/hd_check.py`).

## 3. Points à relire

- **Doublon** p11 : « Le Bugeon » figure deux fois dans le raster et donc deux fois au canon.
- **Ponctuation absente** p03 : « Nef unique de 25 m » / « Riche et pauvre, côte à côte » en deux blocs.
- **Flèches typographiques** p07 : « ← Route du Mont-Cenis », « Vallée des Villards → ».
- **Graphies** : « coeur » (p02), « Ier », « XIVe » sans exposant, « Tour & Maison de La Tour ».
- **Cartouches** p12 : un bloc commune en capitales + un ou deux blocs de sites par cartouche.
- **Rendu provisoire** : les zones masquées sur lavis (p02 village, p05 princesse, p07 donjon,
  p08 panorama, p10 statue mariale, p11 vallée, p12 titre du bandeau) montrent un aplat de la
  couleur médiane jusqu'à l'arrivée des sources HD sans légende.

## 4. Blocs inscrits

| Page | Fragment | Clé | Texte canonique |
|---|---|---|---|
| 01 | `church_captioned` | `cap_church` | Église Notre-Dame-du-Cruet XIVe siècle |
| 01 | `mountains_captioned` | `cap_mountains` | Maurienne Terre de passage et de seigneuries |
| 01 | `seal_captioned` | `cap_seal` | Sceau d'un seigneur de La Chambre XIIIe siècle |
| 01 | `maison_forte_captioned` | `cap_maison_forte` | Maison forte de La Tour |
| 02 | `village_captioned` | `cap_village` | La Chambre, capitale et coeur de la seigneurie. |
| 02 | `bishop_captioned` | `cap_bishop` | L'évêque-comte, maître spirituel et temporel de la Maurienne. |
| 02 | `seal_vicomte_captioned` | `cap_seal_vicomte` | Sceau d'un vicomte de La Chambre (XIIIe siècle) |
| 02 | `knight_captioned` | `cap_knight` | Une lignée chevaleresque, au service de la vallée et de l'Église. |
| 02 | `equestrian_seal_captioned` | `cap_equestrian_seal` | Sceau équestre (XIIe siècle) |
| 02 | `testament_captioned` | `cap_testament` | Testament de Pierre de La Chambre (1261) |
| 02 | `monk_church_captioned` | `cap_monk_church` | Couvent des Cordeliers, fondation de 1365 |
| 02 | `louis_medallion_captioned` | `cap_louis` | Louis Ier de Savoie (1402-1465) |
| 03 | `portal_gothique_captioned` | `cap_portal` | Portail gothique en albâtre blanc (fin XIVe siècle) |
| 03 | `cloister_baroque_captioned` | `cap_cloister` | Cloître baroque (1744) |
| 03 | `salle_capitulaire_captioned` | `cap_salle` | Voûtes d'ogives de la salle capitulaire (fin XIVe siècle) |
| 03 | `valley_cruet_captioned` | `cap_valley` | Vue depuis le Cruet sur la vallée de La Chambre |
| 03 | `nave_captioned` | `cap_nave_1` | Nef unique de 25 m |
| 03 | `nave_captioned` | `cap_nave_2` | Riche et pauvre, côte à côte |
| 03 | `lintel_accolade_captioned` | `cap_lintel` | Linteau en accolade (art flamboyant, XVe siècle) |
| 05 | `hero_captioned` | `cap_hero_1` | Face à face : Château Joli et Château du Cruet |
| 05 | `hero_captioned` | `cap_hero_2` | Le Château Joli domine la vallée de l'Arc et les Villards du sud. |
| 05 | `poype_captioned` | `cap_poype_1` | Tour maîtresse (XIIIe siècle) |
| 05 | `poype_captioned` | `cap_poype_2` | Motte primitive (antérieure au XIe s.) |
| 05 | `poype_captioned` | `cap_poype_3` | Fossé naturel |
| 05 | `poype_captioned` | `cap_poype_4` | Enceinte médiévale |
| 05 | `poype_captioned` | `cap_poype_5` | POYPE FÉODALE |
| 05 | `poype_captioned` | `cap_poype_6` | Éperon rocheux facile à défendre, dominant tous les accès. |
| 05 | `princess_captioned` | `cap_princess` | Agnès de Savoie-Achaïe (v. 1320-v. 1385) épouse de Jean II de La Chambre (v. 1325-v. 1370) |
| 06 | `hero_captioned` | `cap_hero_1` | Manoir de Châtel-André |
| 06 | `hero_captioned` | `cap_hero_2` | Emplacement de la Tour de Burgin |
| 06 | `berthollet_portrait_captioned` | `cap_berthollet` | Claude-Louis Berthollet 1748-1822 |
| 06 | `vestiges_box_captioned` | `cap_vestiges_1` | Vestiges aujourd'hui |
| 06 | `vestiges_box_captioned` | `cap_vestiges_2` | « Réduits à fort peu de choses » (Georges Chapier, 1957) |
| 07 | `hero_captioned` | `cap_hero` | Donjon de Châtel-André (XIIe siècle) |
| 07 | `vassal_scene_captioned` | `cap_vassal` | Le vassal rend hommage à son suzerain |
| 07 | `defensive_box_captioned` | `cap_def_1` | Un système défensif complémentaire |
| 07 | `defensive_box_captioned` | `cap_def_2` | Le Cruet |
| 07 | `defensive_box_captioned` | `cap_def_3` | Châtel-André |
| 07 | `defensive_box_captioned` | `cap_def_4` | ← Route du Mont-Cenis |
| 07 | `defensive_box_captioned` | `cap_def_5` | La Chambre |
| 07 | `defensive_box_captioned` | `cap_def_6` | Vallée des Villards → |
| 07 | `battle_scene_captioned` | `cap_battle` | Reprise de la tour par les troupes savoyardes (1598) |
| 08 | `hero_captioned` | `cap_hero_1` | Magnolia centenaire dans les jardins suspendus |
| 08 | `hero_captioned` | `cap_hero_2` | Maison-Forte du Châtelet, centre du village de Saint-Étienne-de-Cuines |
| 08 | `panorama_captioned` | `cap_pano_1` | Le Châtelet |
| 08 | `panorama_captioned` | `cap_pano_2` | Système défensif des seigneurs de La Chambre |
| 08 | `panorama_captioned` | `cap_pano_3` | Le Cruet |
| 09 | `magnolia_captioned` | `cap_magnolia` | Magnolia séculaire ombrageant la demeure |
| 10 | `marian_figure_captioned` | `cap_marian` | Notre-Dame-du-Cruet, protectrice du château et de la vallée |
| 11 | `tower_ladder_captioned` | `cap_ladder_1` | Porte d'accès au 1er étage |
| 11 | `tower_ladder_captioned` | `cap_ladder_2` | Échelle amovible (retirée en cas d'attaque) |
| 11 | `tower_ladder_captioned` | `cap_ladder_3` | Entrée au rez-de-chaussée |
| 11 | `valley_box_captioned` | `cap_valley_1` | Vue sur la vallée du Bugeon |
| 11 | `valley_box_captioned` | `cap_valley_2` | Le Cruet |
| 11 | `valley_box_captioned` | `cap_valley_3` | Le Bugeon |
| 11 | `valley_box_captioned` | `cap_valley_4` | Le Bugeon |
| 12 | `network_panorama_captioned` | `cap_net_title` | RÉSEAU DES FORTERESSES DES SEIGNEURS DE LA CHAMBRE |
| 12 | `network_panorama_captioned` | `cap_net_1a` | NOTRE-DAME-DU-CRUET |
| 12 | `network_panorama_captioned` | `cap_net_1b` | Château |
| 12 | `network_panorama_captioned` | `cap_net_2a` | LA CHAMBRE |
| 12 | `network_panorama_captioned` | `cap_net_2b` | Tour & Maison de La Tour |
| 12 | `network_panorama_captioned` | `cap_net_3a` | SAINTE-MARIE-DE-CUINES |
| 12 | `network_panorama_captioned` | `cap_net_3b` | Château Joli |
| 12 | `network_panorama_captioned` | `cap_net_4a` | SAINT-ÉTIENNE-DE-CUINES |
| 12 | `network_panorama_captioned` | `cap_net_4b` | Châtel-André |
| 12 | `network_panorama_captioned` | `cap_net_4c` | Châtelet, Gruyère |
| 12 | `network_panorama_captioned` | `cap_net_5a` | SAINT-RÉMY-DE-MAURIENNE |
| 12 | `network_panorama_captioned` | `cap_net_5b` | La Landonnière |
