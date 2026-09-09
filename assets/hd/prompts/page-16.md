# Page 16 — prompts HD

> Généré par `scripts/hd_prompt_pack.py` — ne pas éditer à la main.

1 illustration(s) à régénérer par prompt ; 7 fragment(s) par une autre voie (voir tableau final).

## P16-landscape

- Fichier attendu : `assets/hd/page-16/landscape.png`
- Référence à joindre : `reference/page-16/landscape.png` (crop canonique 734×347 px)
- Ratio L/H : 2.1153 — canevas natif conseillé : landscape 1536×1024 → recadrage centré 1536×726 px
- Gate 300.0 ppi (continuous_tone) — couverture au canevas natif : A5 ✘(≥1671 px) A4 ✘(≥2363 px) A2 ✘(≥3342 px) A1 ✘(≥4726 px)
- Sans légende raster

```text
Redessine l'illustration jointe en haute définition, en conservant exactement le même sujet, le même point de vue, le même cadrage et la même composition (mêmes positions des éléments principaux). Ne rajoute aucun élément historique ou architectural absent de la référence.
Sujet : Panorama alpin avec chapelle sur un promontoire, cyprès, vallée et sommets enneigés.
Style : Illustration à l'encre et à l'aquarelle, style carnet de voyage / gravure aquarellée : traits d'encre fins brun sépia, lavis d'aquarelle doux et lumineux, palette chaude et naturelle (ocre, beige parchemin, gris pierre, vert olive et vert mousse, bleus pâles pour les ciels et les sommets enneigés), fond de papier crème uni (#FFFDF7) sans texture marquée, lumière diffuse, pas de contours noirs épais, pas de rendu photographique ni 3D.
À ne pas reproduire : texte du logo en haut; fleuron et filet en bas. Aucun texte, lettre, chiffre, signature, filigrane, logo, flèche, cartouche, cadre, bordure ornementale, bulle ou étiquette. Aucun personnage ou objet moderne (véhicule, câble, panneau) sauf indication contraire. Pas de texture de papier vieilli ni de taches. Pas de bordure ni de vignettage : le dessin s'estompe naturellement dans le papier crème.
Format : paysage (plus large que haut), ratio largeur/hauteur ≈ 2.12. Le sujet doit rester entièrement dans le cadre avec une légère marge de papier crème uni sur les bords (l'image sera recadrée au centre à ce ratio exact, sans agrandissement). Produis la plus grande taille disponible (au minimum 1536×1024 px).
```

## Fragments hors voie « prompt image »

| Fragment | Rôle | Voie |
|---|---|---|
| `corner_tl` | `ornament` | `vector_svg` |
| `corner_tr` | `ornament` | `vector_svg` |
| `corner_bl` | `ornament` | `vector_svg` |
| `corner_br` | `ornament` | `vector_svg` |
| `title_ornament` | `ornament` | `vector_svg` |
| `logo_raster` | `canonical_raster_text_absent_from_yaml` | `editorial_text_to_canon` |
| `qr_caption_raster` | `canonical_raster_text_absent_from_yaml` | `editorial_text_to_canon` |
