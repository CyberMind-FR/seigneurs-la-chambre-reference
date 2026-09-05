#!/usr/bin/env python3
from pathlib import Path
import sys, yaml, cv2
ROOT=Path(__file__).resolve().parents[1]
reg=yaml.safe_load((ROOT/"qr_registry.yaml").read_text(encoding="utf-8"))
cfg=yaml.safe_load((ROOT/"build-config.yaml").read_text(encoding="utf-8"))
ref=cfg["source"]["qr_reference_canvas"]
ref_w,ref_h=float(ref["width"]),float(ref["height"])
errors=[]
for pkey,pdata in reg.get("pages",{}).items():
    page=int(pkey); qrs=pdata.get("qrs",[])
    if not qrs: continue
    image_path=ROOT/"assets"/f"page-{page:02d}.jpg"
    img=cv2.imread(str(image_path))
    if img is None:
        errors.append(f"page {page}: image missing"); continue
    H,W=img.shape[:2]; sx,sy=W/ref_w,H/ref_h
    detector=cv2.QRCodeDetector()
    for q in qrs:
        b=q["placement_px"]
        x=int(round(b["x"]*sx)); y=int(round(b["y"]*sy)); w=int(round(b["w"]*sx)); h=int(round(b["h"]*sy))
        pad=max(8,int(round(20*min(sx,sy))))
        crop=img[max(0,y-pad):min(H,y+h+pad),max(0,x-pad):min(W,x+w+pad)]
        crop=cv2.resize(crop,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST)
        decoded,pts,_=detector.detectAndDecode(crop)
        if decoded != q["payload"]:
            errors.append(f"page {page} / {q['id']}: decoded={decoded!r}, expected={q['payload']!r}")
if errors:
    print("QR VALIDATION FAILED")
    for e in errors: print(" -",e)
    sys.exit(1)
print("QR VALIDATION OK")
