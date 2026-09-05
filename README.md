# Les Seigneurs de La Chambre

Référentiel canonique du livret et des panneaux d’exposition.

- 16 pages sources dans `assets/`.
- contenu canonique dans `pages/`.
- corrections éditoriales dans `corrections.yaml`.
- QR verrouillés dans `qr_registry.yaml` et `assets/qr/`.
- règles strictes dans `REGENERATION_RULES.md`.
- consignes de reprise dans `WORK_HANDOFF.md`.
- PDF/ZIP générés uniquement par GitHub Actions dans les artifacts/releases.

Validation locale : `make validate`
Build + contrôle QR final : `make build`
