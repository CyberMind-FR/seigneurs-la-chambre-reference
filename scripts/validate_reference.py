#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys, yaml
ROOT=Path(__file__).resolve().parents[1]
errors=[]
manifest=yaml.safe_load((ROOT/"manifest.yaml").read_text(encoding="utf-8"))
entries=manifest.get("pages",[])
if manifest.get("page_count") != 15 or len(entries) != 15:
    errors.append("manifest must contain exactly 15 pages")
seen=[]
for e in entries:
    p=int(e["page"]); seen.append(p)
    asset=ROOT/e["file"]
    if not asset.exists():
        errors.append(f"page {p}: missing {e['file']}")
        continue
    actual=hashlib.sha256(asset.read_bytes()).hexdigest()
    if actual != e.get("sha256"):
        errors.append(f"page {p}: manifest hash mismatch")
if sorted(seen) != list(range(1,16)):
    errors.append("manifest page numbers must be 1..15")
config=yaml.safe_load((ROOT/"build-config.yaml").read_text(encoding="utf-8"))
order={int(k):v for k,v in config["source"]["canonical_order"].items()}
if sorted(order) != list(range(1,16)):
    errors.append("build-config canonical order must contain pages 1..15")
# Editorial guards in canonical YAML when present.
for p, forbidden in {4:["Académie de Maurienne"],14:["Collecte Fondation du Patrimoine (75%)","Fabrice GALOPO et Gérald KERMA"],15:["Fondation du Patrimoine 75 %","Fabrice GALOPO & Gérald KERMA"]}.items():
    y=ROOT/"pages"/f"{p:02d}.yaml"
    if y.exists():
        d=yaml.safe_load(y.read_text(encoding="utf-8")) or {}
        t=str(d.get("canonical_text",""))
        for s in forbidden:
            if s in t: errors.append(f"page {p}: obsolete/forbidden content: {s}")
if errors:
    print("REFERENCE VALIDATION FAILED")
    for e in errors: print(" -",e)
    sys.exit(1)
print("REFERENCE VALIDATION OK")
