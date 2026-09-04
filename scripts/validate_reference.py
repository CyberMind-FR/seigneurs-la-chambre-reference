#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys, yaml
ROOT=Path(__file__).resolve().parents[1]
errors=[]
manifest=yaml.safe_load((ROOT/"manifest.yaml").read_text(encoding="utf-8"))
if len(manifest.get("pages",[])) != 15:
    errors.append("manifest must contain 15 pages")
for e in manifest.get("pages",[]):
    p=e["page"]
    y=ROOT/e["file"]
    a=ROOT/e["visual_reference"]
    if not y.exists(): errors.append(f"missing {y.relative_to(ROOT)}")
    if not a.exists(): errors.append(f"missing {a.relative_to(ROOT)}")
    if a.exists():
        actual=hashlib.sha256(a.read_bytes()).hexdigest()
        if actual != e["sha256"]: errors.append(f"manifest hash mismatch page {p}")
    if y.exists():
        d=yaml.safe_load(y.read_text(encoding="utf-8"))
        if not d.get("content_locked"): errors.append(f"page {p}: content not locked")
        if d.get("visual_reference_sha256") != e["sha256"]: errors.append(f"page {p}: yaml hash mismatch")
# Explicit forbidden obsolete content.
for p, forbidden in {
    4:["Académie de Maurienne"],
    13:["sdlc.gk2.secubox.in","sdlc.../diaporama","sdlc.../livret.pdf"],
    14:["Collecte Fondation du Patrimoine (75%)","Fabrice GALOPO et Gérald KERMA"],
    15:["Fondation du Patrimoine 75 %","Fabrice GALOPO & Gérald KERMA"],
}.items():
    d=yaml.safe_load((ROOT/"pages"/f"{p:02d}.yaml").read_text(encoding="utf-8"))
    t=str(d.get("canonical_text",""))
    for s in forbidden:
        if s in t: errors.append(f"page {p}: obsolete/forbidden content: {s}")
if errors:
    print("REFERENCE VALIDATION FAILED")
    for e in errors: print(" -",e)
    sys.exit(1)
print("REFERENCE VALIDATION OK")
