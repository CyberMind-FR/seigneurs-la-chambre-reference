#!/usr/bin/env python3
"""Compatibility runner for the page-03 layered prototype.

PyYAML folds line breaks inside the single-quoted canonical_text scalar. This runner
rebinds canonical_paragraphs() to split on preserved YAML block breaks, then executes
the deterministic prototype without changing the canonical source.
"""
import re
import yaml
import prototype_page03_layers as p


def canonical_paragraphs_block_aware():
    spec = yaml.safe_load(p.PAGE_SPEC.read_text())
    text = spec["canonical_text"]
    blocks = [p.normalize_ws(x) for x in re.split(r"\n+", text) if p.normalize_ws(x)]
    expected_prefix = [
        "Le Couvent des Cordeliers",
        "Le testament spirituel des Seigneurs de La Chambre",
        "La vision d'un seigneur (1365)",
    ]
    if blocks[:3] != expected_prefix:
        raise SystemExit(f"unexpected canonical block structure: {blocks[:5]}")
    if len(blocks) != 25:
        raise SystemExit(f"canonical block count changed: got {len(blocks)}, expected 25; blocks={blocks}")
    return blocks


p.canonical_paragraphs = canonical_paragraphs_block_aware
p.main()
