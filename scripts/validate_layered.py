#!/usr/bin/env python3
"""Recompose and validate every page that has a layered composition.

    python scripts/validate_layered.py            # all prototypes/page-NN/composition.yaml
    python scripts/validate_layered.py 3 5        # selected pages

Runs scripts/layered_compose.py per page (without rewriting fragment locks), then asserts
that no methodology gate is FAIL and prints a one-line summary per page. The resolution
blocker (PASS_WITH_RESOLUTION_BLOCKER) is reported, not hidden, and does not fail the run.

Outputs go to _verify-layered/ (a gitignored local QA cache) so that the source checkout stays
free of dist/ during `make validate`, as required by scripts/validate_reference.py.
"""
import shutil
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    pages = [int(a) for a in sys.argv[1:]] or sorted(
        int(p.parent.name.split("-")[1]) for p in ROOT.glob("prototypes/page-*/composition.yaml"))
    out_root = ROOT / "_verify-layered"
    shutil.rmtree(out_root, ignore_errors=True)
    failed = []
    rows = []
    for page in pages:
        out = out_root / f"page-{page:02d}"
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/layered_compose.py"), str(page), "--out", str(out)],
                              capture_output=True, text=True)
        report = out / "proof-validation.json"
        if proc.returncode != 0 or not report.exists():
            failed.append(page)
            print(f"page {page:02d}: composition FAILED\n{proc.stderr[-2000:]}")
            continue
        m = json.loads(report.read_text())
        rows.append(m)
        if m["methodology_gate"] == "FAIL":
            failed.append(page)
        print("page {:02d} gate={} text={} qr={} fragments={} ppi_min={:.2f} collisions={} lock={}".format(
            m["page"], m["methodology_gate"], m["text_layer_pass"], m["qr_decode_pass"], m["fragment_count"],
            m["fragment_effective_ppi_min"], len(m["text_ink_collisions"]), m["fragment_lock"].get("match")))
        for issue in m["issues"]:
            if issue["severity"] == "fail":
                print(f"    FAIL [{issue['code']}] {issue['message']}")
    if failed:
        raise SystemExit(f"layered validation FAILED for pages {failed}")
    print(f"LAYERED VALIDATION OK ({len(rows)} pages)")


if __name__ == "__main__":
    main()
