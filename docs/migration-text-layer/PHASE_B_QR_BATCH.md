# Phase B — lot QR SVG — rapport de validation

Source fonctionnelle unique : `qr_registry.yaml`.
Actifs SVG uniques : **16**. Les placements peuvent être plus nombreux lorsqu’un même actif est réutilisé.

| registre | SVG | SHA-256 | SHA lock | décodage exact | rendu validant | structures interdites |
|---|---|---|:---:|:---:|---:|---|
| `03/google_maps` | `page-03-google-maps.svg` | `ed1daee27d44ab09b2df0c56e9ccfab31352c1324384adfc06b341087827630a` | OK | OK | 600 px | `none` |
| `04/google_maps` | `page-04-google-maps.svg` | `2121081aabdb0259dcb5c3295cb1b982f3957216fc51fa499d17fa9b6a7e52ee` | OK | OK | 600 px | `none` |
| `05/google_maps` | `page-05-google-maps.svg` | `f2eef67e4ecf11360f7f151c93d71dcacc93f3670343a30187f1479cf0e04890` | OK | OK | 600 px | `none` |
| `06/google_maps` | `page-06-google-maps.svg` | `4906e793489446088eec4603d8ae7062c8f0ceb1f1ba950ba1bac99cb222ae30` | OK | OK | 600 px | `none` |
| `07/google_maps` | `page-07-google-maps.svg` | `cb454fb617706fb0a58a92626cf64922b35236862381b480208242ce87510d7f` | OK | OK | 600 px | `none` |
| `08/google_maps` | `page-08-google-maps.svg` | `004caa9aa4f0ddc930245963710e608159be6c06def4b56b2e9f6155956fe270` | OK | OK | 600 px | `none` |
| `09/google_maps` | `page-09-google-maps.svg` | `f99e5c25e62f50abcae2baff51f20da40e1bae78412b70a8e2d60e4e16ad7c34` | OK | OK | 600 px | `none` |
| `10/google_maps` | `page-10-google-maps.svg` | `fc9b27faf312c5c64f46ead4d03ad5501da0a36774329a89e7bcdffe58bfeb2c` | OK | OK | 600 px | `none` |
| `11/google_maps` | `page-11-google-maps.svg` | `49b904d76cdc17282af7b700c34eb16c1c49933b0acdc62e2398bef4ef421e14` | OK | OK | 600 px | `none` |
| `12/google_maps` | `page-12-google-maps.svg` | `e537a65f6ab827f4a55dce46039065941a2e93146497946b2d2f56ce68c8f3a3` | OK | OK | 600 px | `none` |
| `13/association, 16/association` | `page-13-01-association.svg` | `0ca65370ac6536a4deef0e2296606edbea0c1de53ec0dd34b69efdcd2899ccab` | OK | OK | 600 px | `none` |
| `13/videos` | `page-13-02-videos.svg` | `e1008918ccb3cdc045307bab6eb8fcaeaf4691dad442cb41b8fd47ccc8678e26` | OK | OK | 600 px | `none` |
| `13/virtual_visit` | `page-13-03-virtual_visit.svg` | `a57c24aa3ea01c672d054fd9f4ab630a1d2e64ecab7202e2155258cf317387a2` | OK | OK | 600 px | `none` |
| `13/fondation` | `page-13-04-fondation.svg` | `b9d2f6c453438946326c5dd48b695bbd00c7f67f8df176af9cb8c8eb47520634` | OK | OK | 600 px | `none` |
| `13/commune` | `page-13-05-commune.svg` | `525df82f60cd334830c1e32f587b702d0a049ae68a72740d8e75f0e9b06c80a6` | OK | OK | 600 px | `none` |
| `13/documents` | `page-13-06-documents.svg` | `edc95ba3bd1ca98ada59ec822ae3212fc511b96cbe79531e74005232755e9078` | OK | OK | 600 px | `none` |

Résultat : **PASS**.

Le validateur rend chaque SVG en PNG à plusieurs tailles et n’accepte qu’un payload décodé strictement identique au registre.
