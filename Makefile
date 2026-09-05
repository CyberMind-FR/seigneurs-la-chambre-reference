.PHONY: help sync validate build validate-build clean

PYTHON ?= python3
DIST ?= dist

help:
	@echo "make sync           - synchronise les SHA des pages dans les manifests/YAML"
	@echo "make validate       - valide le référentiel et les QR sources"
	@echo "make build          - construit les PDF puis valide les QR du PDF final"
	@echo "make validate-build - valide les QR réinjectés dans le PDF final"

sync:
	$(PYTHON) scripts/sync_hashes.py

validate:
	$(PYTHON) scripts/validate_reference.py
	$(PYTHON) scripts/validate_qr.py

validate-build:
	$(PYTHON) scripts/validate_built_pdfs.py

build: validate
	$(PYTHON) scripts/build_pdfs.py --config build-config.yaml --out $(DIST)
	$(MAKE) validate-build

clean:
	rm -rf $(DIST)
