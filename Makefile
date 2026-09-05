.PHONY: help validate build clean

PYTHON ?= python3
DIST ?= dist

help:
	@echo "make validate  - valide le référentiel et les QR"
	@echo "make build     - construit tous les PDF et le bundle d'impression"
	@echo "make clean     - supprime les sorties de construction"

validate:
	$(PYTHON) scripts/validate_reference.py
	$(PYTHON) scripts/validate_qr.py

build: validate
	$(PYTHON) scripts/build_pdfs.py --config build-config.yaml --out $(DIST)

clean:
	rm -rf $(DIST)
