#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, yaml

ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/'manifest.yaml'
manifest=yaml.safe_load(manifest_path.read_text(encoding='utf-8')) or {}
entries=manifest.get('pages',[])

for e in entries:
    p=int(e['page'])
    asset=ROOT/e['file']
    if not asset.exists():
        raise SystemExit(f'missing asset for page {p}: {e["file"]}')
    digest=hashlib.sha256(asset.read_bytes()).hexdigest()
    e['sha256']=digest
    ypath=ROOT/'pages'/f'{p:02d}.yaml'
    if ypath.exists():
        d=yaml.safe_load(ypath.read_text(encoding='utf-8')) or {}
        d['visual_reference']=e['file']
        d['visual_reference_sha256']=digest
        ypath.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=120),encoding='utf-8')

manifest_path.write_text(yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False,width=120),encoding='utf-8')
mirror=[{'page':int(e['page']),'file':e['file'],'sha256':e['sha256']} for e in entries]
(ROOT/'manifest-pages.json').write_text(json.dumps(mirror,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
print('HASH SYNC OK')
