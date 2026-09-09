# Phase B — prototype multicouche page 03

## Statut

**PASS_WITH_RESOLUTION_BLOCKER**

Le prototype valide la méthode de composition multicouche sur la page 03, `Le Couvent des Cordeliers`, sans modifier `assets/page-03.jpg`.

## Pipeline réellement exécuté

1. lecture de `pages/03.yaml` comme autorité éditoriale ;
2. contrôle SHA-256 de `assets/page-03.jpg` ;
3. mesure diagnostique sans OCR ;
4. revue visuelle des candidats ;
5. découpe de 11 fragments raster approuvés depuis la page canonique ;
6. composition d'un fond neutre indépendant ;
7. réinsertion des fragments aux coordonnées normalisées de la référence ;
8. composition du texte canonique comme vraie couche texte PDF ;
9. ajout du QR SVG déterministe en dernier ;
10. rendu PNG du PDF final ;
11. extraction/contrôle de la couche texte ;
12. décodage machine du QR depuis le rendu final ;
13. inspection visuelle du rendu ;
14. mesure de la résolution effective des fragments.

## Run de référence

GitHub Actions : `34259978419`

Commit : `5eef23415fe41424cb4dc37488225414d139e949`

Artifact : `prototype-page03-layered-proof`

## Résultats machine

- paragraphes canoniques contrôlés : **25** ;
- paragraphes manquants dans le PDF : **0** ;
- couche texte : **PASS** ;
- QR attendu : `https://www.google.com/maps?q=45.3561,6.3033` ;
- QR décodé dans le rendu final : payload exact ;
- QR : **PASS** ;
- fragments extraits : **11** ;
- SHA fragments : **PASS** ;
- SHA PDF proof : `21a27dfd6da5cb24ac5ddf5b2f98a3704d346ad93638d076cd73e029f6bdbe6f` ;
- résolution effective des rasters à l'échelle A5 : **185,78 ppi** ;
- gate A5 300 ppi : **FAIL**.

## Revue visuelle

Le premier rendu validé machine présentait un retour à la ligne du titre et une collision avec le sous-titre. Le réglage typographique a été corrigé sans modifier le texte canonique. Le run `34259978419` est la première version retenue après cette revue visuelle.

La composition obtenue démontre que la page peut être reconstruite à partir de fragments du raster canonique, de texte vivant et d'un QR indépendant, sans redessiner librement les illustrations.

## Décision méthodologique

Le prototype confirme le pipeline :

`fond -> fragments raster canoniques -> vecteurs utiles -> texte vivant -> fonctions/QR`

La vectorisation systématique des illustrations n'est pas nécessaire.

Les légendes visibles dans la page canonique mais absentes de `pages/03.yaml:canonical_text` restent, pour ce prototype, intégrées aux fragments raster concernés. Elles ne sont pas OCRisées ni réinventées.

## Blocage découvert

La référence canonique page 03 mesure `1024 × 1536 px`. Placée à son échelle de composition A5, elle fournit environ **185,78 ppi**, insuffisants face au gate actuel de **300 ppi**.

Il ne faut pas masquer ce manque par un simple upscale : cela augmenterait le nombre de pixels sans recréer le détail documentaire absent.

### Conséquence

Avant industrialisation finale, il faut choisir pour les fragments raster l'une des voies suivantes :

1. retrouver les sources/rendus plus haute résolution correspondants ;
2. autoriser explicitement une résolution raster inférieure pour certains actifs documentaires ;
3. limiter leur taille physique de placement ;
4. vectoriser uniquement les éléments qui peuvent l'être sans dérive documentaire.

## Gate suivant

La méthode de composition est **validée**. L'industrialisation des 16 pages peut commencer côté structure et couche texte, mais la qualité d'impression raster reste un gate séparé à résoudre actif par actif.

La page 04 reste exclue tant que `PAGE_04_EDITORIAL_ARBITRATION_REQUIRED` n'est pas levé.
