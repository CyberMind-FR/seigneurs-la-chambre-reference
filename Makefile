.PHONY: help sync qr-svg validate-qr-svg validate-phase-b-svg manifest-v3 validate validate-layered layered-measure layered-compose layered-inventory layered-register hd-prompts hd-pack hd-ingest hd-check build validate-build build-v3 validate-build-v3 release clean

PYTHON ?= python3
DIST ?= dist
# Pages with a layered v3 composition (prototypes/page-NN/composition.yaml)
LAYERED_PAGES ?= 1 2 3 5 6 7 8 9 10 11 12 13 14 15 16

help:
	@echo "make sync                - synchronise les SHA des pages dans les manifests/YAML"
	@echo "make qr-svg              - régénère les QR SVG depuis qr_registry.yaml"
	@echo "make validate-qr-svg     - redécode les QR SVG et vérifie leurs SHA"
	@echo "make validate-phase-b-svg - valide le premier lot SVG documentaire/reconstitution"
	@echo "make manifest-v3         - reconstruit le manifeste v3 incrémental"
	@echo "make validate            - valide le référentiel, tous les lots SVG actifs et les compositions multicouches"
	@echo "make layered-measure     - mesure déterministe (sans OCR) des pages LAYERED_PAGES"
	@echo "make layered-compose     - compose les proofs multicouches des pages LAYERED_PAGES et écrit les locks de fragments"
	@echo "make layered-inventory   - dérive les inventaires objets (page-NN.objects.yaml) des compositions"
	@echo "make validate-layered    - recompose et valide chaque page multicouche (texte, QR, SHA, ppi, collisions)"
	@echo "make hd-prompts          - régénère les prompts HD (assets/hd/prompts) depuis les briefs et les grilles"
	@echo "make hd-pack             - prompts + crops de référence bruts dans dist/hd-pack (jamais committés)"
	@echo "make hd-ingest           - inscrit les images déposées dans assets/hd/page-NN/ (statut PENDING_REVIEW)"
	@echo "make hd-check            - contrôle prompts à jour, SHA, ratio, gates et approbations des sources HD"
	@echo "make build               - construit les PDF puis valide les QR du PDF final"
	@echo "make validate-build      - valide les QR réinjectés dans le PDF final"
	@echo "make build-v3            - assemble les PDF v3 (compositions multicouches, page 04 en repli raster) puis les valide"
	@echo "make validate-build-v3   - valide les PDF v3 (QR, couche texte, fontes embarquées, chaînes interdites)"
	@echo "make release             - build v2 + build v3"

sync:
	$(PYTHON) scripts/sync_hashes.py

qr-svg:
	$(PYTHON) scripts/generate_qr_svg.py

validate-qr-svg:
	$(PYTHON) scripts/validate_qr_svg.py

validate-phase-b-svg:
	$(PYTHON) scripts/validate_phase_b_svg.py

manifest-v3:
	$(PYTHON) scripts/bootstrap_manifest_v3.py

validate:
	$(PYTHON) scripts/validate_reference.py
	$(PYTHON) scripts/validate_qr.py
	$(PYTHON) scripts/validate_qr_svg.py
	$(PYTHON) scripts/validate_phase_b_svg.py
	$(MAKE) hd-check
	$(MAKE) validate-layered

layered-measure:
	$(PYTHON) scripts/layered_measure.py $(LAYERED_PAGES)

layered-compose:
	@for p in $(LAYERED_PAGES); do $(PYTHON) scripts/layered_compose.py $$p --write-lock >/dev/null || exit 1; done
	@echo "LAYERED COMPOSE OK ($(LAYERED_PAGES))"

layered-inventory:
	@for p in $(LAYERED_PAGES); do $(PYTHON) scripts/layered_inventory.py $$p || exit 1; done

layered-register:
	$(PYTHON) scripts/register_layered.py

validate-layered:
	$(PYTHON) scripts/validate_layered.py $(LAYERED_PAGES)

hd-prompts:
	$(PYTHON) scripts/hd_prompt_pack.py

hd-pack:
	$(PYTHON) scripts/hd_prompt_pack.py --pack --out $(DIST)

hd-ingest:
	$(PYTHON) scripts/hd_ingest.py

hd-check:
	$(PYTHON) scripts/hd_prompt_pack.py --check
	$(PYTHON) scripts/hd_check.py

validate-build:
	$(PYTHON) scripts/validate_built_pdfs.py

build: validate
	$(PYTHON) scripts/build_pdfs.py --config build-config.yaml --out $(DIST)
	$(MAKE) validate-build

build-v3:
	$(PYTHON) scripts/build_layered.py --out $(DIST)
	$(MAKE) validate-build-v3

validate-build-v3:
	$(PYTHON) scripts/validate_built_layered.py

release: build build-v3

clean:
	rm -rf $(DIST) _verify-layered
