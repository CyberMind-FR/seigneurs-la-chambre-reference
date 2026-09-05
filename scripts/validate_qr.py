#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, cv2

ROOT=Path(__file__).resolve().parents[1]
reg=yaml.safe_load((ROOT/'qr_registry.yaml').read_text(encoding='utf-8')) or {}
errors=[]
detector=cv2.QRCodeDetector()

for pkey,pdata in reg.get('pages',{}).items():
    page=int(pkey)
    for q in pdata.get('qrs',[]):
        asset=ROOT/q['asset']
        if not asset.exists():
            errors.append(f"page {page} / {q['id']}: missing QR asset {q['asset']}")
            continue
        img=cv2.imread(str(asset),cv2.IMREAD_GRAYSCALE)
        if img is None:
            errors.append(f"page {page} / {q['id']}: unreadable QR asset")
            continue
        img=cv2.resize(img,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST)
        decoded,_,_=detector.detectAndDecode(img)
        if decoded != q['payload']:
            errors.append(f"page {page} / {q['id']}: asset decoded={decoded!r}, expected={q['payload']!r}")

if errors:
    print('QR ASSET VALIDATION FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print('QR ASSET VALIDATION OK')
