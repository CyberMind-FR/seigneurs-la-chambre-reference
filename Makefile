.PHONY: help sync qr-svg validate-qr-svg manifest-v3 validate build validate-build clean

PYTHON ?= python3
DIST ?= dist

help:
	@echo "make sync           - synchronise les SHA des pages dans les manifests/YAML"
	@echo "make qr-svg         - régénère les QR SVG depuis qr_registry.yaml"
	@echo "make validate-qr-svg - redécode les QR SVG et vérifie leurs SHA"
	@echo "make manifest-v3    - reconstruit le manifeste v3 incrémental"
	@echo "make validate       - valide le référentiel, les QR sources et les QR SVG"
	@echo "make build          - construit les PDF puis valide les QR du PDF final"
	@echo "make validate-build - valide les QR réinjectés dans le PDF final"

sync:
	$(PYTHON) scripts/sync_hashes.py

qr-svg:
	$(PYTHON) scripts/generate_qr_svg.py

validate-qr-svg:
	$(PYTHON) scripts/validate_qr_svg.py

manifest-v3:
	$(PYTHON) scripts/bootstrap_manifest_v3.py

validate:
	$(PYTHON) scripts/validate_reference.py
	$(PYTHON) scripts/validate_qr.py
	$(PYTHON) scripts/validate_qr_svg.py

validate-build:
	$(PYTHON) scripts/validate_built_pdfs.py

build: validate
	$(PYTHON) scripts/build_pdfs.py --config build-config.yaml --out $(DIST)
	$(MAKE) validate-build

clean:
	rm -rf $(DIST)
