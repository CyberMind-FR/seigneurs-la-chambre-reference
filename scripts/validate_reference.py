#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys, yaml

ROOT=Path(__file__).resolve().parents[1]
errors=[]
manifest=yaml.safe_load((ROOT/'manifest.yaml').read_text(encoding='utf-8')) or {}
entries=manifest.get('pages',[])
count=int(manifest.get('page_count',0))

if count != 16 or len(entries) != 16:
    errors.append('manifest must contain exactly 16 pages')

seen=[]
manifest_map={}
for e in entries:
    p=int(e['page']); seen.append(p); manifest_map[p]=e
    asset=ROOT/e['file']
    if not asset.exists():
        errors.append(f"page {p}: missing {e['file']}")
        continue
    actual=hashlib.sha256(asset.read_bytes()).hexdigest()
    if actual != e.get('sha256'):
        errors.append(f'page {p}: manifest hash mismatch')
    y=ROOT/'pages'/f'{p:02d}.yaml'
    if not y.exists():
        errors.append(f'page {p}: missing pages/{p:02d}.yaml')
    else:
        d=yaml.safe_load(y.read_text(encoding='utf-8')) or {}
        if d.get('visual_reference') != e['file']:
            errors.append(f'page {p}: YAML visual_reference mismatch')

if sorted(seen) != list(range(1,17)):
    errors.append('manifest page numbers must be 1..16')

# manifest-pages.json is a compatibility mirror and must match manifest.yaml.
mirror_path=ROOT/'manifest-pages.json'
if not mirror_path.exists():
    errors.append('missing manifest-pages.json')
else:
    mirror=json.loads(mirror_path.read_text(encoding='utf-8'))
    mirror_map={int(e['page']):e for e in mirror}
    if sorted(mirror_map) != list(range(1,17)):
        errors.append('manifest-pages.json page numbers must be 1..16')
    for p,e in manifest_map.items():
        m=mirror_map.get(p)
        if not m or m.get('file') != e.get('file') or m.get('sha256') != e.get('sha256'):
            errors.append(f'page {p}: manifest-pages.json mismatch')

config=yaml.safe_load((ROOT/'build-config.yaml').read_text(encoding='utf-8')) or {}
order={int(k):v for k,v in config['source']['canonical_order'].items()}
if sorted(order) != list(range(1,17)):
    errors.append('build-config canonical order must contain pages 1..16')

# Repository cleanliness: generated outputs never belong in the source tree.
for pattern,label in [
    ('Seigneurs_La_Chambre_*.pdf','generated PDF'),
    ('Seigneurs_La_Chambre_*.zip','generated ZIP'),
    ('Seigneurs_La_Chambre_Contact_*.jpg','generated contact sheet'),
    ('UPDATE_NOTES_*.md','historical update note'),
]:
    for p in ROOT.glob(pattern):
        errors.append(f'{label} tracked at repository root: {p.name}')
if (ROOT/'dist').exists():
    errors.append('dist/ must not be present in source checkout')
if (ROOT/'build-report.json').exists():
    errors.append('build-report.json is generated output and must not be tracked at root')
if (ROOT/'QR_VALIDATION_REPORT.md').exists():
    errors.append('QR_VALIDATION_REPORT.md is generated/stale output and must not be tracked at root')

# Editorial guards in canonical YAML.
for p, forbidden in {
    4:['Académie de Maurienne'],
    14:['Collecte Fondation du Patrimoine (75%)','Fabrice GALOPO et Gérald KERMA'],
    15:['Fondation du Patrimoine 75 %','Fabrice GALOPO & Gérald KERMA'],
}.items():
    y=ROOT/'pages'/f'{p:02d}.yaml'
    if y.exists():
        d=yaml.safe_load(y.read_text(encoding='utf-8')) or {}
        t=str(d.get('canonical_text',''))
        for s in forbidden:
            if s in t:
                errors.append(f'page {p}: obsolete/forbidden content: {s}')

if errors:
    print('REFERENCE VALIDATION FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print('REFERENCE VALIDATION OK')
