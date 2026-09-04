#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, cv2

ROOT=Path(__file__).resolve().parents[1]
reg=yaml.safe_load((ROOT/"qr_registry.yaml").read_text(encoding="utf-8"))
errors=[]

for pkey,pdata in reg["pages"].items():
    page=int(pkey)
    image_path=ROOT/"assets"/f"page-{page:02d}.jpg"
    img=cv2.imread(str(image_path))
    if img is None:
        errors.append(f"page {page}: image missing")
        continue
    detector=cv2.QRCodeDetector()
    for q in pdata.get("qrs",[]):
        b=q["placement_px"]
        x,y,w,h=b["x"],b["y"],b["w"],b["h"]
        pad=12
        crop=img[max(0,y-pad):min(img.shape[0],y+h+pad),
                 max(0,x-pad):min(img.shape[1],x+w+pad)]
        # Upscale nearest-neighbor to make validation resilient while preserving modules.
        crop=cv2.resize(crop,None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST)
        decoded,pts,_=detector.detectAndDecode(crop)
        if decoded != q["payload"]:
            errors.append(f"page {page} / {q['id']}: decoded={decoded!r}, expected={q['payload']!r}")

if errors:
    print("QR VALIDATION FAILED")
    for e in errors:
        print(" -",e)
    sys.exit(1)
print("QR VALIDATION OK")
