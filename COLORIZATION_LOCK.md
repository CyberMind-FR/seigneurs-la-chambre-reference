# Regle de construction - colorisation verrouillee

1. `assets/page-01.jpg` a `assets/page-15.jpg` sont la source graphique du build.
2. Une release ne doit jamais melanger ces assets avec une ancienne serie sepia.
3. Toute regeneration graphique doit conserver texte, composition, plans et QR canoniques.
4. Les QR sont des assets deterministes et sont superposes apres le traitement graphique.
5. Le build doit echouer si un des 15 fichiers manque.
6. Les PDF de release sont reconstruits exclusivement depuis les 15 assets presents dans le commit/tag.
