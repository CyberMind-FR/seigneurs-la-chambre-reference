# Rapport de validation QR

Date de validation : **2026-09-04**

Chaque QR a été redécodé directement depuis le JPEG final et comparé caractère pour caractère au payload verrouillé dans `qr_registry.yaml`.

| Page | QR | Validation | Payload |
|---:|---:|:---:|---|
| 3 | 1 | OK | `https://www.google.com/maps?q=45.3561,6.3033` |
| 4 | 1 | OK | `https://www.google.com/maps?q=45.3565,6.3025` |
| 5 | 1 | OK | `https://www.google.com/maps?q=45.3485,6.318` |
| 6 | 1 | OK | `https://www.google.com/maps?q=45.3555,6.305` |
| 7 | 1 | OK | `https://www.google.com/maps?q=45.352,6.324` |
| 8 | 1 | OK | `https://www.google.com/maps?q=45.3505,6.3195` |
| 9 | 1 | OK | `https://www.google.com/maps?q=45.349,6.321` |
| 10 | 1 | OK | `https://www.google.com/maps?q=45.3715,6.3095` |
| 11 | 1 | OK | `https://www.google.com/maps?q=45.3699,6.3109` |
| 12 | 1 | OK | `https://www.google.com/maps?q=45.338,6.275` |
| 13 | 1 | OK | `https://www.couventdelachambre.fr/` |
| 13 | 2 | OK | `https://www.couventdelachambre.fr/pages/nouvelles/retrospective/etape-de-pelerins-franciscain-aout-2025.html` |
| 13 | 3 | OK | `https://drone-de-regard.fr/VR/La-Chambre/couvent/` |
| 13 | 4 | OK | `https://www.fondation-patrimoine.org/les-projets/couvent-des-cordeliers-a-la-chambre-en-savoie/104155` |
| 13 | 5 | OK | `https://la-chambre.fr/patrimoine-et-labels/` |
| 13 | 6 | OK | `https://www.couventdelachambre.fr/pages/le-couvent/documents.html` |

**Résultat final : 16/16 QR valides.**